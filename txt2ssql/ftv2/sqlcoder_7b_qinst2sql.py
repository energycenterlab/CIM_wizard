#!/usr/bin/env python3
"""
SQLCoder 7B - Question + Instruction to SQL Generator (QInst2SQL)
Second stage of two-stage architecture - takes question + instruction as input
"""

import os
import sys
from pathlib import Path
from typing import Dict
import logging

import torch
import wandb
from tqdm import tqdm
import pandas as pd

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback,
    set_seed
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset
from huggingface_hub import login

from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/media/space/castangia/Ali_workspace/logs/ftv3/sqlcoder_qinst2sql_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Login to HuggingFace
HF_TOKEN = os.getenv('HF_TOKEN')
if HF_TOKEN:
    login(token=HF_TOKEN)

# Configuration
class Config:
    MODEL_NAME = "defog/sqlcoder-7b-2"
    LOCAL_DATASET_PATH = "/media/space/castangia/Ali_workspace/ftv3/datasets/qinst2sql_train.jsonl"
    CHECKPOINT_DIR = "/media/space/castangia/Ali_workspace/models/ftv3"
    TARGET_REPO = "taherdoust/sqlcoder-7b-cim-qinst2sql"
    
    WANDB_ENTITY = "taherdoust-politecnico-di-torino"
    WANDB_PROJECT = "cim-qinst2sql-generator"
    WANDB_ENABLED = True
    
    BATCH_SIZE = 2
    GRADIENT_ACCUMULATION_STEPS = 8
    MAX_SEQ_LENGTH = 2048
    LEARNING_RATE = 2e-4
    NUM_EPOCHS = 3
    WARMUP_RATIO = 0.1
    WEIGHT_DECAY = 0.01
    
    LORA_R = 16
    LORA_ALPHA = 32
    LORA_DROPOUT = 0.1
    
    SEED = 42

config = Config()
set_seed(config.SEED)

# Create prompt
def create_prompt(sample: Dict) -> str:
    """
    Creates a prompt with question + instruction as input, SQL as output.
    Uses generic instruction-style format (no special tokens for SQLCoder).
    """
    system_msg = """You are an expert in PostGIS spatial SQL for City Information Modeling databases.
Generate SQL queries based on the provided reasoning instructions.

Database Schema:
- cim_vector: Building geometries, project scenarios, grid infrastructure
- cim_census: Italian census demographic data (ISTAT 2011)
- cim_raster: DTM/DSM raster data
- cim_network: Electrical grid network data"""
    
    question = sample['question']
    instruction = sample['instruction']
    sql = sample['sql_postgis']
    
    # Generic instruction format (SQLCoder doesn't use special tokens)
    prompt = f"""### System
{system_msg}

### Question
{question}

### Reasoning Instructions
{instruction}

### SQL Query
{sql}"""
    
    return prompt

# Load and preprocess data
def load_data():
    logger.info("Loading datasets...")
    
    train_df = pd.read_json(config.LOCAL_DATASET_PATH, lines=True)
    val_path = config.LOCAL_DATASET_PATH.replace('train', 'val')
    test_path = config.LOCAL_DATASET_PATH.replace('train', 'test')
    
    val_df = pd.read_json(val_path, lines=True)
    test_df = pd.read_json(test_path, lines=True)
    
    logger.info(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    
    return train_df, val_df, test_df

# Tokenize dataset
def tokenize_dataset(df: pd.DataFrame, tokenizer) -> Dataset:
    logger.info("Creating prompts and tokenizing...")
    
    texts = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing samples"):
        if pd.isna(row['question']) or pd.isna(row['instruction']) or pd.isna(row['sql_postgis']):
            continue
        if len(row['question']) < 10 or len(row['instruction']) < 20 or len(row['sql_postgis']) < 10:
            continue
            
        prompt = create_prompt(row)
        texts.append(prompt)
    
    logger.info(f"Valid samples: {len(texts)}")
    
    # Tokenize
    logger.info("Tokenizing...")
    encodings = tokenizer(
        texts,
        truncation=True,
        padding=False,
        max_length=config.MAX_SEQ_LENGTH,
        return_tensors=None
    )
    
    dataset = Dataset.from_dict({
        'input_ids': encodings['input_ids'],
        'attention_mask': encodings['attention_mask']
    })
    
    return dataset

# Main training
def main():
    logger.info("="*70)
    logger.info("CIM QInst2SQL Training - SQLCoder 7B (Two-Stage Architecture)")
    logger.info("="*70)
    
    # Load data
    train_df, val_df, test_df = load_data()
    
    # Setup model
    logger.info("\nLoading SQLCoder 7B-2 (BIRD pre-trained model)...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        config.MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    
    model = prepare_model_for_kbit_training(model)
    
    # LoRA
    lora_config = LoraConfig(
        r=config.LORA_R,
        lora_alpha=config.LORA_ALPHA,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=config.LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Tokenizer
    logger.info("\nLoading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    # Tokenize datasets
    train_dataset = tokenize_dataset(train_df, tokenizer)
    val_dataset = tokenize_dataset(val_df, tokenizer)
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Calculate eval steps for 4 evals per epoch
    effective_batch_size = config.BATCH_SIZE * config.GRADIENT_ACCUMULATION_STEPS
    steps_per_epoch = len(train_dataset) // effective_batch_size
    eval_steps = max(steps_per_epoch // 4, 100)  # At least 100 steps between evals
    
    # Training args
    output_dir = f"{config.CHECKPOINT_DIR}/sqlcoder-7b-bird-r{config.LORA_R}-qinst2sql"
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=config.NUM_EPOCHS,
        per_device_train_batch_size=config.BATCH_SIZE,
        per_device_eval_batch_size=config.BATCH_SIZE,
        gradient_accumulation_steps=config.GRADIENT_ACCUMULATION_STEPS,
        learning_rate=config.LEARNING_RATE,
        weight_decay=config.WEIGHT_DECAY,
        lr_scheduler_type="cosine",
        warmup_ratio=config.WARMUP_RATIO,
        bf16=True,
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",
        
        # Optimized settings
        dataloader_num_workers=4,
        dataloader_pin_memory=True,
        dataloader_prefetch_factor=2,
        
        evaluation_strategy="steps",
        eval_steps=eval_steps,
        save_strategy="steps",
        save_steps=eval_steps,
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        logging_steps=50,
        logging_first_step=True,
        report_to="wandb" if config.WANDB_ENABLED else "none",
        run_name=f"sqlcoder-7b-bird-r{config.LORA_R}-qinst2sql",
        seed=config.SEED,
        remove_unused_columns=False
    )
    
    # WandB
    if config.WANDB_ENABLED:
        wandb.init(
            entity=config.WANDB_ENTITY,
            project=config.WANDB_PROJECT,
            name=f"sqlcoder-7b-bird-r{config.LORA_R}-qinst2sql",
            config=vars(config)
        )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )
    
    # Train
    logger.info("\n" + "="*70)
    logger.info("STARTING TRAINING")
    logger.info(f"Base Model: SQLCoder 7B-2 (BIRD pre-trained)")
    logger.info(f"Task: QInst2SQL (Question + Instruction → SQL)")
    logger.info(f"Epochs: {config.NUM_EPOCHS}")
    logger.info(f"Effective Batch Size: {effective_batch_size}")
    logger.info(f"Steps per Epoch: {steps_per_epoch}")
    logger.info(f"Eval every {eval_steps} steps (4 times per epoch)")
    logger.info("="*70 + "\n")
    
    trainer.train()
    
    # Save
    logger.info("\nSaving model...")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    logger.info("\n" + "="*70)
    logger.info("Training Complete!")
    logger.info(f"Model saved to: {output_dir}")
    logger.info("Next Steps:")
    logger.info("1. Combine with Q2Inst model for two-stage evaluation")
    logger.info("2. Compare with single-stage Q2SQL models")
    logger.info("3. Analyze instruction-guided SQL generation quality")
    logger.info("="*70)
    
    if config.WANDB_ENABLED:
        wandb.finish()

if __name__ == '__main__':
    main()

