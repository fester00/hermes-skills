---
name: llm-fine-tuning-workflows
description: "Post-training and fine-tuning LLMs: Axolotl (YAML-driven), TRL (SFT/DPO/PPO/GRPO programmatic), and Unsloth (fast LoRA/QLoRA). Pick the right framework for the task."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [fine-tuning, llm, lora, qlora, dpo, grpo, rlhf, training, mlops]
    related_skills: [serving-llms-vllm, evaluating-llms-harness]
---

# LLM Fine-Tuning Workflows

Post-training and fine-tuning large language models — three frameworks, one workflow.
Use this skill to pick the right tool, write the config or code, and debug the training.

---

## When to Use

- Fine-tune a base model for a custom task (instruction following, summarization, coding)
- Align a model with human preferences (DPO, PPO, GRPO)
- Train a reward model as part of an RLHF pipeline
- Optimize training speed or reduce VRAM usage

## Picking the Right Framework

| Goal | Use | Why |
|------|-----|-----|
| **Declarative YAML configs, 100+ models, multimodal** | **Axolotl** | YAML-driven; minimal code; DeepSpeed/FSDP built-in |
| **Programmatic control, RLHF, preference alignment** | **TRL** | Python-first; SFT → DPO → PPO/GRPO pipelines; HuggingFace native |
| **Maximum speed, minimum VRAM** | **Unsloth** | 2-5x faster LoRA/QLoRA; less memory; drop-in replacements |

---

## 1. Axolotl — YAML-Driven Training

Axolotl is the fastest path from "I have data" to "I have a fine-tuned model."
Write a YAML file, run `axolotl train`, done.

### Quick Start

```bash
pip install axolotl
# or: pip install axolotl[flash-attn,deepspeed]
```

### Minimal Config

```yaml
base_model: meta-llama/Llama-2-7b-hf
model_type: LlamaForCausalLM
load_in_8bit: true
adapter: lora
lora_r: 16
lora_alpha: 32
lora_target_linear: true
sequence_len: 2048
datasets:
  - path: tatsu-lab/alpaca
    type: alpaca
num_epochs: 3
micro_batch_size: 1
eval_batch_size: 1
learning_rate: 0.0002
train_on_inputs: false
group_by_length: false
bf16: auto
fp16: false
output_dir: ./outputs/llama-2-7b-lora
```

Run:
```bash
axolotl train config.yml
```

### Key Concepts

- **`adapter: lora` / `qlora`** — efficient fine-tuning with low-rank updates
- **`datasets[].type`** — data format (alpaca, sharegpt, oasst, etc.)
- **`train_on_inputs: false`** — only train on the "response" part, not the prompt
- **`bf16: auto`** — automatically uses bfloat16 on Ampere+ GPUs

### Common Patterns

**FSDP for multi-GPU:**
```yaml
fsdp:
  - full_shard
  - auto_wrap
fsdp_config:
  fsdp_limit_all_gathers: true
  fsdp_offload_params: false
```

**DeepSpeed ZeRO-3:**
```yaml
deepspeed: deepspeed_configs/zero3.json
```

**Gradient checkpointing + flash attention:**
```yaml
flash_attention: true
gradient_checkpointing: true
```

**Multi-turn chat (ShareGPT format):**
```yaml
datasets:
  - path: Open-Orca/OpenOrca
    type: sharegpt
```

### Pitfalls

- **Dataset format mismatch** — `type: alpaca` expects `instruction`, `input`, `output` columns. If your CSV uses `prompt`/`completion`, use `type: completion` or preprocess.
- **OOM with QLoRA** — Even 4-bit quantization OOMs on long sequences with large batch sizes. Reduce `sequence_len` or `micro_batch_size` first.
- **Missing `trust_remote_code`** — Some models (e.g., Qwen, Falcon) require `trust_remote_code: true` in the YAML.

### References

- `references/axolotl/api.md` — Full Axolotl API and config options
- `references/axolotl/dataset-formats.md` — Supported dataset formats and column mappings
- `references/axolotl/other.md` — DeepSpeed, FSDP, and advanced configuration topics

---

## 2. TRL — Programmatic RLHF & Preference Alignment

TRL (Transformer Reinforcement Learning) is the toolkit for aligning models with human preferences.
It provides Python trainers for the full RLHF pipeline: SFT → Reward Model → PPO/GRPO.

### Quick Start

```bash
pip install trl transformers datasets peft accelerate
```

### Supervised Fine-Tuning (SFT)

```python
from trl import SFTTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")
dataset = load_dataset("trl-lib/Capybara", split="train")

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    tokenizer=tokenizer,
    max_seq_length=2048,
)
trainer.train()
trainer.save_model("./qwen-sft")
```

### Direct Preference Optimization (DPO)

Align with preferences without a reward model:

```python
from trl import DPOTrainer, DPOConfig

config = DPOConfig(output_dir="model-dpo", beta=0.1, per_device_train_batch_size=4)
trainer = DPOTrainer(
    model=model,
    args=config,
    train_dataset=preference_dataset,  # chosen/rejected pairs
    processing_class=tokenizer,
)
trainer.train()
```

### PPO — Full RLHF

```bash
python -m trl.scripts.ppo \
  --model_name_or_path Qwen2.5-0.5B-SFT \
  --reward_model_path Qwen2.5-0.5B-Reward \
  --dataset_name trl-internal-testing/descriptiveness-sentiment-trl-style \
  --output_dir Qwen2.5-0.5B-PPO \
  --learning_rate 3e-6 \
  --per_device_train_batch_size 64 \
  --total_episodes 10000
```

### GRPO — Memory-Efficient Online RL

Group Relative Policy Optimization for RL with minimal memory:

```python
from trl import GRPOConfig, GRPOTrainer

config = GRPOConfig(
    output_dir="grpo-run",
    num_generations=4,
    per_device_train_batch_size=4,
)
trainer = GRPOTrainer(
    model="Qwen/Qwen2-0.5B-Instruct",
    reward_funcs=reward_function,
    args=config,
    train_dataset=dataset,
)
trainer.train()
```

See `references/trl/grpo-training.md` for reward function design, loss behavior, mode collapse detection, and multi-stage patterns. Production-ready starter script: `templates/basic_grpo_training.py`.

### Pitfalls

- **OOM during DPO** — DPO loads both the policy model AND the reference model. Use LoRA/QLoRA or gradient checkpointing.
- **Poor alignment quality** — Tune `beta` (KL penalty). Default `0.1` is conservative; increase for stronger alignment, decrease for more aggressive changes.
- **Reward model not learning** — Check that preference dataset has clear winners. Use `RewardTrainer` with `num_labels=1` for scalar reward scores.
- **PPO instability** — Increase `kl_coef`, decrease `cliprange`. Always start from a well-trained SFT checkpoint.

### References

- `references/trl/sft-training.md` — SFT dataset formats, chat templates, packing
- `references/trl/dpo-variants.md` — IPO, cDPO, RPO, and other DPO loss functions
- `references/trl/reward-modeling.md` — Outcome vs process rewards, Bradley-Terry loss
- `references/trl/online-rl.md` — PPO, GRPO, RLOO, OnlineDPO configurations
- `references/trl/grpo-training.md` — Deep-dive on GRPO training dynamics
- `templates/basic_grpo_training.py` — Production-ready GRPO starter script

---

## 3. Unsloth — Fast LoRA/QLoRA

Unsloth is a drop-in replacement for standard PEFT/Transformers training that runs 2-5x faster with less VRAM.
Use it when you want the same LoRA/QLoRA results, but faster.

### Quick Start

```bash
pip install unsloth
# Also install latest transformers, trl
```

### Minimal Training Loop

```python
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3-8b-bnb-4bit",
    max_seq_length=2048,
    dtype=None,  # Auto-detect
    load_in_4bit=True,
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    use_gradient_checkpointing="unsloth",
)

# Standard TRL SFTTrainer works with unsloth model
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=60,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        output_dir="outputs",
    ),
)
trainer.train()
```

### Key Advantages

- **2-5x faster training** — optimized kernels for LoRA backward pass
- **30% less VRAM** — efficient gradient checkpointing and memory management
- **Drop-in compatible** — works with TRL, PEFT, Transformers without code changes
- **Automatic 4-bit/16-bit** — handles quantization automatically

### Pitfalls

- **Not all models supported** — Check `unsloth` model hub for verified models (Llama, Mistral, Gemma, Qwen).
- **Windows support** — Linux recommended; Windows WSL works but native Windows may have compilation issues.
- **`dtype=None`** — Let Unsloth auto-detect; forcing `torch.float16` on non-compatible GPUs causes errors.

### References

- `references/unsloth/llms-txt.md` — Unsloth documentation and quick-reference
- `references/unsloth/llms.md` — Model compatibility list
- `references/unsloth/llms-full.md` — Full documentation with all optimization options

---

## Decision Guide

| Situation | Recommended Framework |
|-----------|----------------------|
| I want to write a YAML file and train | **Axolotl** |
| I need programmatic control over the training loop | **TRL** |
| I'm doing RLHF (SFT → Reward → PPO) | **TRL** |
| I'm doing preference alignment with DPO | **TRL** or **Axolotl** (both support DPO) |
| I need to save VRAM and train faster | **Unsloth** + **TRL** |
| I'm training on a custom dataset format | **Axolotl** (most format parsers) |
| I need multi-GPU (FSDP/DeepSpeed) | **Axolotl** (best YAML integration) |

---

## Common Issues Across All Frameworks

### OOM (Out of Memory)

1. Reduce `per_device_train_batch_size` to 1
2. Enable gradient checkpointing
3. Use QLoRA (4-bit) instead of LoRA (8-bit)
4. Reduce `max_seq_length`
5. Use DeepSpeed ZeRO-3 or FSDP for multi-GPU sharding

### Slow Training

1. Enable Flash Attention 2 (`flash_attention: true` in Axolotl; `attn_implementation="flash_attention_2"` in TRL)
2. Use Unsloth for optimized kernels
3. Increase gradient accumulation (same effective batch size, less memory)
4. Use `bf16` instead of `fp16` on Ampere+ GPUs

### Dataset Format Errors

- Verify column names match the expected format for your framework
- Preprocess with Python if needed; save as `.jsonl` for fastest loading
- For chat formats, ensure the conversation turns are in the expected structure

---

## References

- `references/axolotl/` — Axolotl-specific documentation
- `references/trl/` — TRL deep-dive guides and training templates
- `references/unsloth/` — Unsloth documentation and compatibility lists
- `templates/basic_grpo_training.py` — Production-ready GRPO training script
