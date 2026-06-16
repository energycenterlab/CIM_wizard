#!/usr/bin/env python3
"""
Qwen 2.5 32B - Question to Instruction Generator (Unsloth)
Unsloth provides 3-4x faster training than PEFT
"""

import os
from typing import Dict
import torch
import wandb
from tqdm import tqdm
import pandas as pd

from unsloth import FastLanguageModel
from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling, EarlyStoppingCallback, set_seed
from datasets import Dataset
from huggingface_hub import login
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')
if HF_TOKEN:
    login(token=HF_TOKEN)

class Config:
    MODEL_NAME = "Qwen/Qwen2.5-32B-Instruct"
    LOCAL_DATASET_PATH = "/media/space/castangia/Ali_workspace/curated_dataset_ftv2/q2inst_train.jsonl"
    CHECKPOINT_DIR = "/media/space/castangia/Ali_workspace/models/ftv2"
    TARGET_REPO = "taherdoust/qwen25-32b-unsloth-cim-q2inst"
    WANDB_ENTITY = "taherdoust-politecnico-di-torino"
    WANDB_PROJECT = "cim-q2inst-generator"
    WANDB_ENABLED = True
    BATCH_SIZE = 2
    GRADIENT_ACCUMULATION_STEPS = 8
    MAX_SEQ_LENGTH = 2048
    LEARNING_RATE = 1.5e-4
    NUM_EPOCHS = 3
    WARMUP_RATIO = 0.1
    WEIGHT_DECAY = 0.01
    LORA_R = 16
    LORA_ALPHA = 32
    LORA_DROPOUT = 0.1
    SEED = 42

config = Config()
set_seed(config.SEED)

def create_prompt(sample: Dict) -> str:
    system_msg = """You are an expert in spatial SQL reasoning for City Information Modeling (CIM).
Your task is to generate detailed reasoning instructions that explain how to convert natural language questions into PostGIS spatial SQL queries.

Database Schema:
- cim_vector: Building geometries, project scenarios, grid infrastructure
- cim_census: Italian census demographic data (ISTAT 2011)
- cim_raster: DTM/DSM raster data
- cim_network: Electrical grid network data

Generate clear, step-by-step reasoning instructions."""
    
    question = sample['question']
    instruction = sample['instruction']
    
    prompt = f"""<|im_start|>system
{system_msg}<|im_end|>
<|im_start|>user
{question}<|im_end|>
<|im_start|>assistant
{instruction}<|im_end|>"""
    
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
        if pd.isna(row['question']) or pd.isna(row['instruction']):
            continue
        if len(row['question']) < 10 or len(row['instruction']) < 20:
            continue
        texts.append(create_prompt(row))
    
    encodings = tokenizer(texts, truncation=True, padding=False,
                         max_length=config.MAX_SEQ_LENGTH, return_tensors=None)
    return Dataset.from_dict({'input_ids': encodings['input_ids'],
                              'attention_mask': encodings['attention_mask']})

def main():
    print("="*70)
    print("CIM Q2Inst Training - Qwen 2.5 32B (Unsloth)")
    print("="*70)
    
    train_df, val_df, test_df = load_data()
    
    # Load model with Unsloth (much faster than PEFT)
    print("\nLoading model with Unsloth...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=config.MODEL_NAME,
        max_seq_length=config.MAX_SEQ_LENGTH,
        dtype=torch.bfloat16,
        load_in_4bit=True,
    )
    
    # Get LoRA configuration
    model = FastLanguageModel.get_peft_model(
        model,
        r=config.LORA_R,
        lora_alpha=config.LORA_ALPHA,
        lora_dropout=config.LORA_DROPOUT,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        bias="none",
        use_gradient_checkpointing=True,
        use_rslora=True,  # Unsloth-specific: faster LoRA
    )
    
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    train_dataset = tokenize_dataset(train_df, tokenizer)
    val_dataset = tokenize_dataset(val_df, tokenizer)
    
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    
    effective_batch_size = config.BATCH_SIZE * config.GRADIENT_ACCUMULATION_STEPS
    steps_per_epoch = len(train_dataset) // effective_batch_size
    eval_steps = steps_per_epoch // 4
    
    output_dir = f"{config.CHECKPOINT_DIR}/qwen25-32b-unsloth-r{config.LORA_R}-q2inst"
    
    training_args = TrainingArguments(
        output_dir=output_dir, num_train_epochs=config.NUM_EPOCHS,
        per_device_train_batch_size=config.BATCH_SIZE,
        per_device_eval_batch_size=config.BATCH_SIZE,
        gradient_accumulation_steps=config.GRADIENT_ACCUMULATION_STEPS,
        learning_rate=config.LEARNING_RATE, weight_decay=config.WEIGHT_DECAY,
        lr_scheduler_type="cosine", warmup_ratio=config.WARMUP_RATIO,
        bf16=True, gradient_checkpointing=True, optim="paged_adamw_8bit",
        dataloader_num_workers=4, dataloader_pin_memory=True, dataloader_prefetch_factor=2,
        evaluation_strategy="steps", eval_steps=eval_steps,
        save_strategy="steps", save_steps=eval_steps, save_total_limit=3,
        load_best_model_at_end=True, metric_for_best_model="eval_loss",
        logging_steps=50, logging_first_step=True,
        report_to="wandb" if config.WANDB_ENABLED else "none",
        seed=config.SEED, remove_unused_columns=False
    )
    
    if config.WANDB_ENABLED:
        wandb.init(entity=config.WANDB_ENTITY, project=config.WANDB_PROJECT,
                  name=f"qwen25-32b-unsloth-r{config.LORA_R}-q2inst", config=vars(config))
    
    trainer = Trainer(model=model, args=training_args, train_dataset=train_dataset,
                     eval_dataset=val_dataset, data_collator=data_collator,
                     callbacks=[EarlyStoppingCallback(early_stopping_patience=3)])
    
    print(f"\nEval every {eval_steps} steps (4 times per epoch)")
    print("Unsloth: Expect 3-4x faster training than PEFT!\n")
    trainer.train()
    
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    if config.WANDB_ENABLED:
        wandb.finish()

if __name__ == '__main__':
    main()

