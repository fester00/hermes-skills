# Compression Settings Guide

Config keys for context compression and memory limits.

```yaml
compression:
  enabled: true
  target_ratio: 0.20        # Keep 20% after compressing; lower = more aggressive
  hygiene_hard_message_limit: 400   # Force compress after this many messages

context:
  engine: compressor
  memory_char_limit: 2200    # Persistent notes memory budget
  user_char_limit: 1375      # User profile budget
```

## Recommended values by model context size

| Model | Context | target_ratio | hygiene_hard_message_limit |
|-------|---------|-------------|---------------------------|
| Long-context (256K+) | ~256K | **0.3-0.4** | 400 |
| Medium (128K) | ~128K | **0.25** | 400 |
| Short (32-64K) | ~32-64K | **0.15-0.2** | 300-400 |
| Local / small | ≤16K | **0.1-0.15** | 200 |

**Why:** larger context allows less aggressive compression. With 256K you can keep 30-40% of history without hitting token limits. With 16K you need aggressive pruning.

## Memory & profile limits

| Limit | When to increase | When to decrease |
|-------|-----------------|-----------------|
| `memory_char_limit` | ≥95% full, notes get dropped | Excessive, token-hungry memory |
| `user_char_limit` | ≥95% full, profile truncated | Overly verbose user profile |

**Current values warning:** 98% full on both limits means old notes/profile get truncated or dropped. Increase if you rely on long-lived memory.

## Adjusting

```bash
hermes config set compression.target_ratio 0.35
hermes config set compression.hygiene_hard_message_limit 500
hermes config set context.memory_char_limit 3000
hermes config set context.user_char_limit 1500
```

Changes apply on the next session (`/reset` or new chat).

## Warning signs of bad settings

| Symptom | Cause | Fix |
|-----------|-------|-----|
| "Agent forgets the beginning of our conversation" | `target_ratio` too low | Increase to 0.3-0.4 |
| "Too many tokens, requests are expensive" | `target_ratio` too high | Decrease to 0.15-0.2 |
| "My saved notes keep disappearing" | `memory_char_limit` too low | Increase or archive old notes |
| "Profile looks truncated" | `user_char_limit` too low | Increase or consolidate profile |
| "Compression runs too often" | `hygiene_hard_message_limit` too low | Increase to 500+ |
