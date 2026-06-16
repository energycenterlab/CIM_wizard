#!/usr/bin/env python3
"""
Llama 3.1 14B - Question to Instruction Generator
"""

import os
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
    MODEL_NAME = "meta-llama/Llama-3.1-14B-Instruct"
    LOCAL_DATASET_PATH = "/media/space/castangia/Ali_workspace/curated_dataset_ftv2/q2inst_train.jsonl"
    CHECKPOINT_DIR = "/media/space/castangia/Ali_workspace/models/ftv2"
    TARGET_REPO = "taherdoust/llama31-14b-cim-q2inst"
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
    
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_msg}<|eot_id|><|start_header_id|>user<|end_header_id|>

{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{instruction}<|eot_id|>"""
    
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
    print("CIM Q2Inst Training - Llama 3.1 14B")
    print("="*70)
    
    train_df, val_df, test_df = load_data()
    
    bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                    bnb_4bit_compute_dtype=torch.bfloat16,
                                    bnb_4bit_use_double_quant=True)
    
    model = AutoModelForCausalLM.from_pretrained(config.MODEL_NAME,
                                                 quantization_config=bnb_config,
                                                 device_map="auto", trust_remote_code=True)
    model = prepare_model_for_kbit_training(model)
    
    lora_config = LoraConfig(r=config.LORA_R, lora_alpha=config.LORA_ALPHA,
                            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                           "gate_proj", "up_proj", "down_proj"],
                            lora_dropout=config.LORA_DROPOUT, bias="none",
                            task_type="CAUSAL_LM")
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    train_dataset = tokenize_dataset(train_df, tokenizer)
    val_dataset = tokenize_dataset(val_df, tokenizer)
    
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    
    effective_batch_size = config.BATCH_SIZE * config.GRADIENT_ACCUMULATION_STEPS
    steps_per_epoch = len(train_dataset) // effective_batch_size
    eval_steps = steps_per_epoch // 4
    
    output_dir = f"{config.CHECKPOINT_DIR}/llama31-14b-r{config.LORA_R}-q2inst"
    
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
                  name=f"llama31-14b-r{config.LORA_R}-q2inst", config=vars(config))
    
    trainer = Trainer(model=model, args=training_args, train_dataset=train_dataset,
                     eval_dataset=val_dataset, data_collator=data_collator,
                     callbacks=[EarlyStoppingCallback(early_stopping_patience=3)])
    
    print(f"\nEval every {eval_steps} steps (4 times per epoch)\n")
    trainer.train()
    
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    if config.WANDB_ENABLED:
        wandb.finish()

if __name__ == '__main__':
    main()
