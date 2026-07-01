# Ollama Model Storage Relocation

Session: 2026-06-05 — moving Ollama models from root disk (58 GB, 90% full) to 1 TB mounted disk.

## Problem

Ollama defaults to `~/.ollama/models` (on root partition). A `gemma4:12b` (~7–9 GB) will not fit on a 5.5 GB free root disk.

## Quick checks

```bash
# Where are models now?
ls -la ~/.ollama/models 2>/dev/null || echo "not on root"

# Is there a bigger disk?
lsblk -f -o NAME,SIZE,TYPE,MOUNTPOINT

df -h
```

## Solutions

### A. Manual env var (no sudo)

Kill existing Ollama and restart with custom path:

```bash
# 1. Prepare target directory
mkdir -p /mnt/data/ollama-models/models

# 2. Kill existing service (or run alongside on another port)
pkill ollama

# 3. Start with new model path
OLLAMA_MODELS=/mnt/data/ollama-models ollama serve

# 4. In another terminal
ollama run gemma4:12b
```

### B. Second Ollama instance (does not touch main service)

```bash
# Run a second server on port 11435
OLLAMA_MODELS=/mnt/bigdisk/ollama-models OLLAMA_HOST=127.0.0.1:11435 ollama serve

# Then point CLI at it
OLLAMA_HOST=127.0.0.1:11435 ollama run gemma4:12b
```

### C. Systemd override (persistent, requires sudo)

```bash
sudo systemctl edit ollama
```

Add:
```ini
[Service]
Environment="OLLAMA_MODELS=/mnt/bigdisk/ollama-models"
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### D. Symlink (simplest if you have write access to both locations)

```bash
# Move existing models
mv ~/.ollama/models /mnt/bigdisk/ollama-models/

# Symlink back
ln -s /mnt/bigdisk/ollama-models ~/.ollama/models
```

## Verifying the change

```bash
# List models to confirm they’re being read from the new path
ollama list

# Check disk usage of the target
du -sh /mnt/bigdisk/ollama-models
```

## Pitfall: systemd service runs as `ollama` user

If you symlink, ensure the `ollama` user can read the target directory. If the disk is mounted with `noexec` or restrictive permissions, the service may fail to load models. Use `chmod 755` and `chown` as needed.
