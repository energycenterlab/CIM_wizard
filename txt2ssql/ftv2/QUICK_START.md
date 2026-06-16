# FTv2 Quick Start Guide

Execute these commands to start training with optimized FTv2 pipeline.

## Prerequisites

```bash
# On ipazia126
conda activate ai4cimdb
cd /media/space/castangia/Ali_workspace
```

## Step 1: Curate Dataset (15-30 minutes)

```bash
cd txt2ssql/ftv2

python curate_cim_dataset_ftv2.py \
  ../../ai4db/training_datasets/stage3_augmented_dataset_FINAL_checkpoint.jsonl \
  --output_dir /media/space/castangia/Ali_workspace/curated_dataset_ftv2

# Output: 9 JSONL files (3 modes x 3 splits)
# Expected: 88K-113K training samples per mode
```

## Step 2: Choose Your Model

### Option A: Qwen 2.5 14B (RECOMMENDED)
Best value for performance/time ratio.

**Two-Stage (Best Accuracy):**
```bash
# Stage 1: Question → Instruction (30-40 hours)
nohup python qwen25_14b_q2inst.py > logs/qwen14b_q2inst.log 2>&1 &

# After Stage 1 completes:
# Stage 2: Question + Instruction → SQL (30-40 hours)
nohup python qwen25_14b_qinst2sql.py > logs/qwen14b_qinst2sql.log 2>&1 &
```

**Single-Stage (Simpler):**
```bash
# Direct: Question → SQL (30-40 hours)
nohup python qwen25_14b_q2sql.py > logs/qwen14b_q2sql.log 2>&1 &
```

### Option B: Qwen 2.5 32B Unsloth (BEST PERFORMANCE)
Highest accuracy with fastest training.

**Install Unsloth first:**
```bash
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
```

**Two-Stage:**
```bash
# Stage 1: Question → Instruction (20-25 hours)
nohup python qwen25_32b_unsloth_q2inst.py > logs/qwen32b_q2inst.log 2>&1 &

# Stage 2: Question + Instruction → SQL (20-25 hours)
nohup python qwen25_32b_unsloth_qinst2sql.py > logs/qwen32b_qinst2sql.log 2>&1 &
```

**Single-Stage:**
```bash
# Direct: Question → SQL (20-25 hours)
nohup python qwen25_32b_unsloth_q2sql.py > logs/qwen32b_q2sql.log 2>&1 &
```

### Option C: Llama 3.1 14B (MOST STABLE)
Proven reliability with good performance.

**Two-Stage:**
```bash
# Stage 1 (35-45 hours)
nohup python llama31_14b_q2inst.py > logs/llama14b_q2inst.log 2>&1 &

# Stage 2 (35-45 hours)
nohup python llama31_14b_qinst2sql.py > logs/llama14b_qinst2sql.log 2>&1 &
```

**Single-Stage:**
```bash
# Direct (35-45 hours)
nohup python llama31_14b_q2sql.py > logs/llama14b_q2sql.log 2>&1 &
```

## Step 3: Monitor Training

```bash
# Watch logs
tail -f logs/qwen14b_q2inst.log

# Monitor GPU
watch -n 5 nvidia-smi

# Check WandB
# https://wandb.ai/taherdoust-politecnico-di-torino/cim-q2inst-generator
```

## Step 4: Evaluate Models

After training completes, evaluate on local machine:

```bash
# On eclab (local machine)
cd /home/ali/Desktop/HDD_Volume/000products/coesi/assist_cim

# First-shot accuracy (EX)
python evaluate_models.py \
  --benchmark ../ai4db/evaluation_benchmark.jsonl \
  --model hf:taherdoust/qwen25-14b-cim-qinst2sql \
  --metric EX \
  --output results/qwen25_14b_ex.json

# Agent mode accuracy (EA)
python evaluate_models.py \
  --benchmark ../ai4db/evaluation_benchmark.jsonl \
  --model hf:taherdoust/qwen25-14b-cim-qinst2sql \
  --metric EA \
  --agent_mode \
  --output results/qwen25_14b_ea.json
```

## Quick Reference

### Model Comparison

| Model | Training Time | Accuracy | Best For |
|-------|--------------|----------|----------|
| Qwen 2.5 14B | 30-40h/mode | 85-92% | Best value |
| Llama 3.1 14B | 35-45h/mode | 82-90% | Most stable |
| Qwen 2.5 32B | 20-25h/mode | 88-96% | Best overall |

### Architecture Comparison

| Architecture | Inference | Accuracy | Interpretability |
|--------------|-----------|----------|------------------|
| Two-Stage | 2 calls | Higher | Explainable |
| Single-Stage | 1 call | Good | Black box |

### My Recommendation

**For Research/Production**: Qwen 2.5 14B Two-Stage
- Expected: 85-92% EX, 90-96% EA
- Total time: 60-80 hours (both stages)
- Good balance of speed, accuracy, stability

**For Best Results**: Qwen 2.5 32B Unsloth Two-Stage
- Expected: 88-96% EX, 92-98% EA
- Total time: 40-50 hours (fastest!)
- Highest accuracy available

## Troubleshooting

**Out of Memory**: Reduce BATCH_SIZE to 1, increase GRADIENT_ACCUMULATION_STEPS to 16

**Slow Training**: Check GPU utilization with `nvidia-smi`, verify dataloader workers enabled

**Import Errors**: `pip install transformers peft bitsandbytes wandb`

**Unsloth Errors**: `pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"`

---

**Ready to train!** Choose your model and run the command above.

