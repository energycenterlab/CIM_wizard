# Fine-Tuning Version 2 (FTv2)

Optimized fine-tuning scripts for multiple models and training architectures.

## Overview

This directory contains 9 optimized training scripts covering:
- **3 models**: Qwen 2.5 14B (PEFT), Llama 3.1 14B (PEFT), sqlcoder 7b
- **3 architectures**: Q2Inst, QInst2SQL, Q2SQL

## Key Improvements

1. **4 Evaluations Per Epoch**: Balanced feedback without overhead
2. **Optimized Data Loading**: 4 workers, pin memory, prefetch
3. **Larger Batch Size**: Increased from 1 to 2 (still fits 24GB GPU)
4. **Faster Training**: Expected 15-20 hours vs 58 hours (65-75% reduction)
5. **Larger Dataset**: Supports 88K-113K training samples (vs 13.5K)

## Training Scripts

### Qwen 2.5 14B (PEFT)
- `qwen25_14b_q2inst.py` - Question → Instruction
- `qwen25_14b_qinst2sql.py` - Question + Instruction → SQL
- `qwen25_14b_q2sql.py` - Question → SQL (direct)

### Llama 3.1 14B (PEFT)
- `llama31_14b_q2inst.py` - Question → Instruction
- `llama31_14b_qinst2sql.py` - Question + Instruction → SQL
- `llama31_14b_q2sql.py` - Question → SQL (direct)

### Qwen 2.5 32B (Unsloth)
- `qwen25_32b_unsloth_q2inst.py` - Question → Instruction
- `qwen25_32b_unsloth_qinst2sql.py` - Question + Instruction → SQL
- `qwen25_32b_unsloth_q2sql.py` - Question → SQL (direct)

## Training Architectures

### Single-Stage (Q2SQL)
Direct mapping from question to SQL:
```
Question → SQL
```

**Advantages**: Simpler, faster inference, one model to deploy

**Use cases**: Simple queries, fast prototyping

### Two-Stage (Q2Inst + QInst2SQL)
Decomposed reasoning with intermediate instruction:
```
Question → Instruction → SQL
```

**Advantages**: Better accuracy, interpretable reasoning, modular improvement

**Use cases**: Complex queries, production systems requiring explanation

## Dataset Preparation

Use the unified curation script:

```bash
python curate_cim_dataset_ftv2.py \
  ../../ai4db/training_datasets/stage3_augmented_dataset_FINAL_checkpoint.jsonl \
  --output_dir /media/space/castangia/Ali_workspace/curated_dataset_ftv2 \
  --quality_threshold 0.75 \
  --max_question_length 500
```

This generates datasets for all three modes:
- `q2inst_train.jsonl`, `q2inst_val.jsonl`, `q2inst_test.jsonl`
- `qinst2sql_train.jsonl`, `qinst2sql_val.jsonl`, `qinst2sql_test.jsonl`
- `q2sql_train.jsonl`, `q2sql_val.jsonl`, `q2sql_test.jsonl`

## Training Usage

### Option 1: Qwen 2.5 14B (Recommended for SQL)

```bash
# On ipazia126
cd /media/space/castangia/Ali_workspace/txt2ssql/ftv2

# Two-stage approach (best accuracy)
python qwen25_14b_q2inst.py      # Stage 1: ~30-40 hours
python qwen25_14b_qinst2sql.py   # Stage 2: ~30-40 hours

# OR single-stage (faster)
python qwen25_14b_q2sql.py       # Direct: ~30-40 hours
```

### Option 2: Llama 3.1 14B (Stable, well-tested)

```bash
# Two-stage approach
python llama31_14b_q2inst.py     # Stage 1: ~35-45 hours
python llama31_14b_qinst2sql.py  # Stage 2: ~35-45 hours

# OR single-stage
python llama31_14b_q2sql.py      # Direct: ~35-45 hours
```

### Option 3: sqlcoder 7b


## Expected Performance

| Model | Training Time | Expected EX (1st) | Expected EA (agent) | Memory |
|-------|--------------|-------------------|---------------------|--------|
| Qwen 2.5 14B | 30-40h | 85-92% | 90-96% | 22-24GB |
| Llama 3.1 14B | 35-45h | 82-90% | 88-94% | 22-24GB |


## Configuration

All scripts use the same optimized configuration:

```python
BATCH_SIZE = 2                      # Increased from 1
GRADIENT_ACCUMULATION_STEPS = 8     # Reduced from 16
MAX_SEQ_LENGTH = 2048
LEARNING_RATE = 1.5e-4
NUM_EPOCHS = 3
LORA_R = 16
LORA_ALPHA = 32

# Optimizations
dataloader_num_workers = 4          # Parallel loading
dataloader_pin_memory = True        # Faster GPU transfer
dataloader_prefetch_factor = 2      # Pre-load batches
evaluation_strategy = "steps"       # 4 evals per epoch
eval_steps = steps_per_epoch // 4
```

## Model Comparison

### Why Qwen 2.5 14B?
- Best SQL reasoning among 14B models
- Excellent spatial function handling
- Faster convergence than Llama
- Expected: 85-92% EX, 90-96% EA

### Why Llama 3.1 14B?
- More stable/documented
- Proven fine-tuning track record
- Good general performance
- Expected: 82-90% EX, 88-94% EA

### Why Qwen 2.5 32B with Unsloth?
- Best accuracy: 88-96% EX, 92-98% EA
- 3-4x faster than PEFT (20-25h vs 60-90h)
- Fits in 24GB with 4-bit + gradient checkpointing
- Production-ready with highest quality

## Monitoring

All scripts integrate with Weights & Biases:

```bash
# Set environment variables
export WANDB_API_KEY=your_key_here

# Training will log to:
# https://wandb.ai/taherdoust-politecnico-di-torino/cim-{q2inst/qinst2sql/q2sql}-generator
```

## Troubleshooting

### Out of Memory
- Reduce batch size to 1
- Increase gradient accumulation to 16
- Enable gradient checkpointing (already enabled)

### Slow Training
- Check dataloader_num_workers=4 is enabled
- Verify GPU utilization: `nvidia-smi`
- Check disk I/O (dataset on fast storage)

### Unsloth Installation
```bash
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
```

## Next Steps

1. Curate dataset using `curate_cim_dataset_ftv2.py`
2. Choose model and architecture (Qwen 2.5 14B two-stage recommended)
3. Train on ipazia126 GPU server
4. Evaluate using `../assist_cim/evaluate_models.py`
5. Compare performance across different models/architectures

## References

- Original training script: `../fine-tune/train_llama_WORKING.py`
- Evaluation: `../assist_cim/evaluate_models.py`
- Curation v1: `../fine-tune/curate_cim_dataset.py`

