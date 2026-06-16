#!/usr/bin/env python3
"""
Qwen 2.5 14B - Question to Instruction Generator
Training script for first stage of two-stage architecture
"""

import os
import sys
from pathlib import Path
from typing import Dict

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

# Login to HuggingFace
HF_TOKEN = os.getenv('HF_TOKEN')
if HF_TOKEN:
    login(token=HF_TOKEN)

# Configuration
class Config:
    MODEL_NAME = "Qwen/Qwen2.5-14B-Instruct"
    LOCAL_DATASET_PATH = "/media/space/castangia/Ali_workspace/ftv3/downloaded_dataset/q2inst_train.jsonl"
    CHECKPOINT_DIR = "/media/space/castangia/Ali_workspace/models/ftv3"
    TARGET_REPO = "taherdoust/qwen25-14b-cim-q2inst"
    
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

# Create prompt
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

# Load and preprocess data
def load_data():
    print("Loading datasets...")
    
    train_df = pd.read_json(config.LOCAL_DATASET_PATH, lines=True)
    val_path = config.LOCAL_DATASET_PATH.replace('train', 'val')
    test_path = config.LOCAL_DATASET_PATH.replace('train', 'test')
    
    val_df = pd.read_json(val_path, lines=True)
    test_df = pd.read_json(test_path, lines=True)
    
    print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    
    return train_df, val_df, test_df

# Tokenize dataset
def tokenize_dataset(df: pd.DataFrame, tokenizer) -> Dataset:
    print("Creating prompts and tokenizing...")
    
    texts = []
    for _, row in tqdm(df.iterrows(), total=len(df)):
        if pd.isna(row['question']) or pd.isna(row['instruction']):
            continue
        if len(row['question']) < 10 or len(row['instruction']) < 20:
            continue
            
        prompt = create_prompt(row)
        texts.append(prompt)
    
    print(f"Valid samples: {len(texts)}")
    
    # Tokenize
    print("Tokenizing...")
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
    print("="*70)
    print("CIM Q2Inst Training - Qwen 2.5 14B")
    print("="*70)
    
    # Load data
    train_df, val_df, test_df = load_data()
    
    # Setup model
    print("\nLoading model...")
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
    print("\nLoading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME, trust_remote_code=True)
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
    eval_steps = steps_per_epoch // 4
    
    # Training args
    output_dir = f"{config.CHECKPOINT_DIR}/qwen25-14b-r{config.LORA_R}-q2inst"
    
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
        seed=config.SEED,
        remove_unused_columns=False
    )
    
    # WandB
    if config.WANDB_ENABLED:
        wandb.init(
            entity=config.WANDB_ENTITY,
            project=config.WANDB_PROJECT,
            name=f"qwen25-14b-r{config.LORA_R}-q2inst",
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
    print("\n" + "="*70)
    print("STARTING TRAINING")
    print(f"Steps per epoch: {steps_per_epoch}")
    print(f"Eval every: {eval_steps} steps (4 times per epoch)")
    print("="*70 + "\n")
    
    trainer.train()
    
    # Save
    print("\nSaving model...")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print("\nTraining complete!")
    
    if config.WANDB_ENABLED:
        wandb.finish()

if __name__ == '__main__':
    main()


