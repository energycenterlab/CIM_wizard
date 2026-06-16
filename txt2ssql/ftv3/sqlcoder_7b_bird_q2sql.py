#!/usr/bin/env python3
"""
SQLCoder 7B-2 (BIRD Pre-trained) - Question to SQL (Direct Single-Stage)
Training script for fine-tuning BIRD-trained model on CIM spatial SQL dataset

Model: defog/sqlcoder-7b-2
Pre-training: Spider, BIRD, and commercial SQL datasets
Purpose: Thesis comparison - generic BIRD model vs domain-specific training
Training: 1 epoch for comparative analysis
"""

import os
import argparse
import shutil
from pathlib import Path
from typing import Dict
import torch
import wandb
from tqdm import tqdm
import pandas as pd

from transformers import (
    AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling,
    EarlyStoppingCallback, set_seed
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset
from huggingface_hub import login
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')
if HF_TOKEN:
    login(token=HF_TOKEN)

class Config:
    MODEL_NAME = "defog/sqlcoder-7b-2" # Bird pre-trained model v3
    LOCAL_DATASET_PATH = "/media/space/castangia/Ali_workspace/nov/curated_q2sql/q2sql_train.jsonl"
    CHECKPOINT_DIR = "/media/space/castangia/Ali_workspace/nov/models/"
    TARGET_REPO = "taherdoust/sqlcoder-7b-cim-q2sql-bird-comparison"
    WANDB_ENTITY = "taherdoust-politecnico-di-torino"
    WANDB_PROJECT = "cim-q2sql-generator-v3"
    WANDB_RUN_NAME = "sqlcoder-7b-bird-pretrained-1epoch"
    WANDB_ENABLED = True
    BATCH_SIZE = 4
    GRADIENT_ACCUMULATION_STEPS = 4
    MAX_SEQ_LENGTH = 2048
    LEARNING_RATE = 2e-4  # Slightly higher for 1 epoch
    NUM_EPOCHS = 1.5  # Single epoch for thesis comparison
    WARMUP_RATIO = 0.1
    WEIGHT_DECAY = 0.01
    LORA_R = 16
    LORA_ALPHA = 32
    LORA_DROPOUT = 0.1
    SEED = 42

config = Config()
set_seed(config.SEED)

def create_prompt(sample: Dict) -> str:
    """
    Create prompt compatible with SQLCoder format
    SQLCoder expects SQL generation without special chat tokens
    """
    system_msg = """You are an expert in PostGIS spatial SQL for City Information Modeling (CIM).
Your task is to generate precise PostGIS spatial SQL queries for the CIM Wizard database.

Database Schema:
- cim_vector: Building geometries, project scenarios, Building properties
  Tables: cim_vector.cim_wizard_building, cim_vector.cim_wizard_building_properties, 
          cim_vector.cim_wizard_project_scenario
- cim_census: Italian census demographic data (ISTAT 2011)
  Tables: cim_census.censusgeo
- cim_raster: DTM/DSM raster data
  Tables: cim_raster.dtm, cim_raster.dsm_sansalva
- cim_network: Electrical grid network data
  Tables: cim_network.network_buses, cim_network.network_lines, cim_network.network_scenarios, cim_network.scenario_buses, cim_network.scenario_lines

IMPORTANT: Always use full schema.table notation (e.g., cim_vector.cim_wizard_building).
Never use table names without schema prefixes.

Generate only the SQL query without explanations."""
    
    question = sample['question']
    sql = sample['sql_postgis']
    
    # SQLCoder format (instruction-style without special tokens)
    prompt = f"""### Task
Generate a SQL query to answer the following question:
`{question}`

### Database Schema
{system_msg}

### SQL
{sql}"""
    
    return prompt

def load_data():
    train_df = pd.read_json(config.LOCAL_DATASET_PATH, lines=True)
    val_df = pd.read_json(config.LOCAL_DATASET_PATH.replace('train', 'val'), lines=True)
    test_df = pd.read_json(config.LOCAL_DATASET_PATH.replace('train', 'test'), lines=True)
    print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    return train_df, val_df, test_df

def tokenize_dataset(df: pd.DataFrame, tokenizer) -> Dataset:
    texts = []
    for _, row in tqdm(df.iterrows(), total=len(df)):
        if pd.isna(row['question']) or pd.isna(row['sql_postgis']):
            continue
        
        # Allow shorter questions for negative samples
        min_question_len = 2 if row.get('sample_dirtiness') in ['AMBIGUOUS', 'OUT_OF_SCOPE'] else 10
        min_sql_len = 5 if row.get('sample_dirtiness') in ['AMBIGUOUS', 'OUT_OF_SCOPE'] else 20
        
        if len(row['question']) < min_question_len or len(row['sql_postgis']) < min_sql_len:
            continue
        texts.append(create_prompt(row))
    
    encodings = tokenizer(texts, truncation=True, padding=False,
                         max_length=config.MAX_SEQ_LENGTH, return_tensors=None)
    return Dataset.from_dict({'input_ids': encodings['input_ids'],
                              'attention_mask': encodings['attention_mask']})

def cleanup_old_checkpoints(checkpoint_dir: Path, keep_count: int):
    """
    Clean up old checkpoint directories, keeping only the N most recent ones.
    
    Args:
        checkpoint_dir: Directory containing checkpoints
        keep_count: Number of checkpoints to keep (0 or -1 = keep all, N = keep N most recent)
    """
    if keep_count <= 0:
        return  # Keep all checkpoints (0 or -1)
    
    if not checkpoint_dir.exists():
        return
    
    # Find all checkpoint directories (checkpoint-XXXX format)
    checkpoint_dirs = [d for d in checkpoint_dir.iterdir() 
                      if d.is_dir() and d.name.startswith('checkpoint-')]
    
    if len(checkpoint_dirs) <= keep_count:
        return  # Not enough checkpoints to clean up
    
    # Sort by modification time (newest first)
    checkpoint_dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    # Keep the N most recent, delete the rest
    checkpoints_to_delete = checkpoint_dirs[keep_count:]
    deleted_count = 0
    for checkpoint_path in checkpoints_to_delete:
        try:
            shutil.rmtree(checkpoint_path)
            deleted_count += 1
            print(f"  Deleted old checkpoint: {checkpoint_path.name}")
        except OSError as e:
            print(f"  Warning: Could not delete {checkpoint_path.name}: {e}")
    
    if deleted_count > 0:
        print(f"\n  Cleaned up {deleted_count} old checkpoint(s), kept {keep_count} most recent")


def main():
    parser = argparse.ArgumentParser(description='Fine-tune SQLCoder 7B-2 on CIM Q2SQL dataset')
    parser.add_argument('--keep_checkpoints', type=int, default=-1,
                       help='Number of checkpoints to keep (0 or -1 = keep all, N = keep N most recent). Default: -1 (keep all)')
    parser.add_argument('--save_steps', type=int, default=300,
                       help='Save checkpoint every N steps. Default: 300 (captures early training dynamics)')
    args = parser.parse_args()
    
    # Validate arguments
    if args.keep_checkpoints < -1:
        parser.error("--keep_checkpoints must be >= -1 (use -1 or 0 to keep all)")
    if args.save_steps < 50:
        parser.error("--save_steps must be >= 50")
    
    print("="*70)
    print("CIM Q2SQL Training - SQLCoder 7B-2 (BIRD Pre-trained)")
    print("Thesis Comparison: Generic BIRD Model vs Domain-Specific Training")
    print(f"Training: {config.NUM_EPOCHS} Epoch(s) for Comparative Analysis")
    print("="*70)
    
    if args.keep_checkpoints <= 0:
        print(f"Checkpoint retention: Keep all checkpoints")
    else:
        print(f"Checkpoint retention: Keep {args.keep_checkpoints} most recent checkpoints")
    
    train_df, val_df, test_df = load_data()
    
    bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                    bnb_4bit_compute_dtype=torch.bfloat16,
                                    bnb_4bit_use_double_quant=True)
    
    print("\nLoading SQLCoder 7B-2 (BIRD pre-trained model)...")
    model = AutoModelForCausalLM.from_pretrained(config.MODEL_NAME,
                                                 quantization_config=bnb_config,
                                                 device_map="auto", trust_remote_code=True)
    model = prepare_model_for_kbit_training(model)
    
    # SQLCoder uses StarCoder architecture (similar target modules to Llama)
    lora_config = LoraConfig(r=config.LORA_R, lora_alpha=config.LORA_ALPHA,
                            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                           "gate_proj", "up_proj", "down_proj"],
                            lora_dropout=config.LORA_DROPOUT, bias="none",
                            task_type="CAUSAL_LM")
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    train_dataset = tokenize_dataset(train_df, tokenizer)
    val_dataset = tokenize_dataset(val_df, tokenizer)
    
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    
    effective_batch_size = config.BATCH_SIZE * config.GRADIENT_ACCUMULATION_STEPS
    steps_per_epoch = len(train_dataset) // effective_batch_size
    total_steps = int(steps_per_epoch * config.NUM_EPOCHS)
    num_checkpoints = total_steps // args.save_steps
    
    output_dir = f"{config.CHECKPOINT_DIR}/sqlcoder-7b-bird-r{config.LORA_R}-q2sql-1epoch"
    output_path = Path(output_dir)
    
    # Determine save_total_limit: use keep_checkpoints if > 0, otherwise None (keep all)
    save_total_limit = args.keep_checkpoints if args.keep_checkpoints > 0 else None
    
    training_args = TrainingArguments(
        output_dir=output_dir, num_train_epochs=config.NUM_EPOCHS,
        per_device_train_batch_size=config.BATCH_SIZE,
        per_device_eval_batch_size=config.BATCH_SIZE,
        gradient_accumulation_steps=config.GRADIENT_ACCUMULATION_STEPS,
        learning_rate=config.LEARNING_RATE, weight_decay=config.WEIGHT_DECAY,
        lr_scheduler_type="cosine", warmup_ratio=config.WARMUP_RATIO,
        bf16=True, gradient_checkpointing=True, optim="paged_adamw_8bit",
        dataloader_num_workers=4, dataloader_pin_memory=True, dataloader_prefetch_factor=2,
        evaluation_strategy="steps", eval_steps=args.save_steps,
        save_strategy="steps", save_steps=args.save_steps,
        save_total_limit=save_total_limit,
        load_best_model_at_end=True, metric_for_best_model="eval_loss",
        logging_steps=50, logging_first_step=True,
        report_to="wandb" if config.WANDB_ENABLED else "none",
        seed=config.SEED, remove_unused_columns=False
    )
    
    if config.WANDB_ENABLED:
        wandb.init(entity=config.WANDB_ENTITY, project=config.WANDB_PROJECT,
                  name=config.WANDB_RUN_NAME, config=vars(config),
                  tags=["bird-pretrained", "thesis-comparison", f"{config.NUM_EPOCHS}-epoch", "sqlcoder"])
    
    trainer = Trainer(model=model, args=training_args, train_dataset=train_dataset,
                     eval_dataset=val_dataset, data_collator=data_collator,
                     callbacks=[EarlyStoppingCallback(early_stopping_patience=5)])
    
    print(f"\nTraining Configuration:")
    print(f"  Base Model: SQLCoder 7B-2 (BIRD pre-trained)")
    print(f"  Epochs: {config.NUM_EPOCHS}")
    print(f"  Effective Batch Size: {effective_batch_size}")
    print(f"  Steps per Epoch: {steps_per_epoch}")
    print(f"  Total Steps: {total_steps}")
    print(f"  Save/Eval every {args.save_steps} steps")
    print(f"  Expected checkpoints: ~{num_checkpoints} (at steps: {args.save_steps}, {args.save_steps*2}, {args.save_steps*3}, ...)")
    print(f"  Purpose: Thesis comparison - BIRD model vs domain-specific")
    print()
    
    trainer.train()
    
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    # Clean up old checkpoints if requested
    if args.keep_checkpoints > 0:
        print(f"\nCleaning up old checkpoints (keeping {args.keep_checkpoints} most recent)...")
        cleanup_old_checkpoints(output_path, args.keep_checkpoints)
    
    print("\n" + "="*70)
    print("Training Complete!")
    print(f"Model saved to: {output_dir}")
    print("Next Steps:")
    print("1. Evaluate on CIM test set")
    print("2. Compare with domain-specific models (Llama, Qwen, DeepSeek)")
    print("3. Analyze PostGIS spatial function accuracy")
    print("4. Document findings in thesis")
    print("="*70)
    
    if config.WANDB_ENABLED:
        wandb.finish()

if __name__ == '__main__':
    main()

