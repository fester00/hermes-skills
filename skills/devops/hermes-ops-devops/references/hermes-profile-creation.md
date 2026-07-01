---
title: Hermes Profile Creation & Workdir Configuration
date: 2026-06-10
tags: [hermes, profile, devops, setup]
---

# Hermes Profile Creation & Workdir Configuration

**Trigger:** User wants a new Hermes profile with a dedicated working directory, different personality, or isolated state.

**Core principle:** Profiles share infrastructure (API key, model, MCP servers) but have **isolated** memory, state.db, and SOUL.md. A profile is a directory under `~/.hermes/profiles/<name>/`, not a separate API account.

---

## 1. Creating a Profile

### From CLI (recommended)

```bash
# Clone from active or another profile
hermes profile create <name> --clone-from default --clone-all \
  --description "What this profile is for"
```

Flags:
| Flag | Meaning |
|------|---------|
| `--clone` | Copy only config.yaml, .env, SOUL.md |
| `--clone-all` | Full copy: skills, memory, state, everything |
| `--clone-from SOURCE` | Source profile (default: currently active) |
| `--no-skills` | Empty profile, no bundled skills |
| `--description TEXT` | Used by Kanban orchestrator for task routing |

Hermes auto-creates:
- `~/.hermes/profiles/<name>/config.yaml`
- `~/.hermes/profiles/<name>/SOUL.md`
- `~/.local/bin/<name>` wrapper script
- `~/.hermes/profiles/<name>/state.db`
- `~/.hermes/profiles/<name>/memory.json`

### Verifying creation

```bash
hermes profile list
ls -la ~/.hermes/profiles/
```

---

## 2. Custom Working Directory (CLI)

**Problem:** The wrapper script `~/.local/bin/<name>` runs `hermes -p <name>` from wherever the user invoked it. There is **no native `workdir` field in `config.yaml`** that changes the startup cwd.

**Solution:** Patch the wrapper script to `cd` before exec.

```bash
# After profile creation, edit the wrapper
cat > ~/.local/bin/maximus << 'EOF'
#!/bin/sh
cd /home/natan/zhopa || exit 1
exec hermes -p maximus "$@"
EOF
chmod +x ~/.local/bin/maximus
```

**Effect:**
- `maximus chat` → starts in `/home/natan/zhopa`
- `maximus -z "task"` → runs task from `/home/natan/zhopa`
- Subagents launched from this CLI session inherit the cwd

**Limitation:** This only works for CLI invocations. The WebUI does **not** use the wrapper script — it spawns sessions directly. WebUI cwd is controlled by the WebUI process itself, not by the profile.

---

## 3. Profile Anatomy

```
~/.hermes/profiles/<name>/
├── config.yaml          ← model, provider, MCP servers, toolsets
├── SOUL.md              ← system prompt / personality
├── .env                 ← API keys (optional, overrides global)
├── memory.json          ← short-term memory (~2200 chars)
├── user_profile.json    ← user profile (~1375 chars)
├── state.db             ← session history (SQLite)
├── auth.lock            ← auth state
├── webui_state/         ← WebUI-specific state
└── skills/              ← bundled skills (optional)
    └── .bundled_manifest
```

**What is shared across profiles:**
- Gateway process (systemd user service)
- Ollama / model provider
- MCP servers (Obsidian, etc.)
- API keys (unless `.env` overrides)
- Global skills (`~/.hermes/skills/`)

**What is isolated per profile:**
- Memory (agent notes)
- User profile (user preferences)
- Session state (chat history)
- Personality (SOUL.md)
- Bundled skills (`profiles/<name>/skills/`)

---

## 4. Switching Profiles

### CLI
```bash
hermes profile use <name>    # sticky default
hermes -p <name>             # one-shot override
<name> chat                  # via wrapper
```

### WebUI
- Click **Switch Profile** in the UI
- Select profile from dropdown
- New session starts with that profile's config + personality
- WebUI process itself stays the same (gateway unchanged)

---

## 5. Deleting a Profile

```bash
hermes profile delete <name>
# Or manually:
rm -rf ~/.hermes/profiles/<name>
rm -f ~/.local/bin/<name>
```

Check first that nothing important is in its memory or state:
```bash
cat ~/.hermes/profiles/<name>/memory.json
cat ~/.hermes/profiles/<name>/user_profile.json
```

---

## 6. Common Pitfalls

| Pitfall | Why it happens | Prevention |
|---------|---------------|------------|
| **WebUI ignores wrapper `cd`** | WebUI spawns sessions directly, not via `~/.local/bin/<name>` | WebUI cwd = WebUI process cwd; change WebUI's `WorkingDirectory` in systemd if needed |
| **Profile still uses old API key after `.env` edit** | Gateway caches env; needs restart | `systemctl --user restart hermes-gateway` |
| **Skills created in default but expected in profile** | `skill_manage(action='create')` writes to `~/.hermes/skills/` by default | Check active profile before creating; use `--profile <name>` if available |
| **Memory not syncing between profiles** | Each profile has its own `memory.json` | This is by design — profiles are isolated |
| **High disk usage from state.db** | SQLite grows with long session history | `hermes profile delete <name>` or manual `rm ~/.hermes/profiles/<name>/state.db` |

---

## Quick Commands Cheat Sheet

```bash
# Create
hermes profile create mybot --clone-from default --clone-all --description "Bot for X"

# List
hermes profile list

# Use
hermes profile use mybot

# Custom workdir (CLI only)
cat > ~/.local/bin/mybot << 'EOF'
#!/bin/sh
cd /path/to/workdir || exit 1
exec hermes -p mybot "$@"
EOF
chmod +x ~/.local/bin/mybot

# Info
hermes profile info mybot
hermes profile show mybot

# Delete
hermes profile delete mybot
```

---

## Related

- [[hermes-ops-devops/SKILL.md]] — system health, gateway, systemd
- [[hermes-agent-skill-authoring/SKILL.md]] — creating skills
- `references/skill-profile-sync.md` — syncing skills between profiles
