# Memory Overflow → Vault Offloading Pattern

## Problem

Hermes has two hard limits on cross-session persistent notes:

| Store | Limit | Typical fill |
|-------|-------|------------|
| `memory` (agent notes) | 2,200 chars | ~90% with project details duplicated from vault |
| `user` (user profile) | 1,375 chars | ~96% with preferences |

When either limit is hit, `memory(action="add")` fails with:
```
Memory at X/Y chars. Adding this entry (N chars) would exceed the limit.
```

## Root Cause

Agents tend to accumulate **duplicates** in short-term memory:
- Full project specs (stack, colors, deploy commands) — already in `Projects/`
- Runbooks and repair patterns — already in `Operations/Runbooks/`
- Course progress and learning notes — already in `Knowledge/`
- Telegram gateway quirks — already in `Operations/`

Short-term memory is injected into every session prompt. Keeping full specs there wastes tokens and blocks new facts.

## Solution: Two-Tier Architecture

### Tier 1 — Short-term Memory (pocket scroll)
**Contains only:** coordinates, pointers, and critical runtime facts.

Example after cleanup:
```
1. Obsidian vault at ~/obsidian-memory is PRIMARY knowledge base.
   Key MOCs: [[MOC — Index]], [[MOC — Projects]], [[MOC — Skills]]
2. Active projects: VIDVIS, Pentajunior, htdata (details in Obsidian Projects/)
3. Rust learning: web backend track, progress in Obsidian Knowledge/Technical/Rust/
4. STT configured: faster-whisper small, local, CPU (gateway config)
5. Host quirks: npm/npx NOT in PATH, Yandex OAuth active
```

### Tier 2 — Obsidian Vault (library)
**Contains:** full specs, runbooks, project histories, research, code snippets, MOCs.

## Cleanup Procedure

1. **List memory entries** — identify duplicates
2. **For each duplicate:** check if it exists in vault via `mcp_obsidian_search_vault` or direct `read_file`
3. **Remove from memory** if vault has authoritative copy
4. **Replace with compact pointer** — "see Obsidian `Projects/vidvis-project.md`"
5. **Reserve ~30% headroom** for new session facts

## Anti-Patterns

- ❌ Storing full deploy scripts in memory
- ❌ Duplicating runbook steps that are in `Operations/Runbooks/`
- ❌ Keeping project color palettes and font names in memory
- ❌ Adding "today we did X" progress logs (belong in `Daily/`)

## When to Add to Memory vs Vault

| Fact type | Destination |
|-----------|-------------|
| User preference (style, tone) | `user` profile |
| Active project names + where details live | `memory` |
| Full project architecture, stack, colors | Obsidian `Projects/` |
| Repair pattern, diagnostic steps | Obsidian `Operations/Runbooks/` |
| Learning progress, course modules | Obsidian `Knowledge/` |
| Today's session log | Obsidian `Daily/` |
| Critical host quirk (npm path, OAuth) | `memory` |
| API credentials, tokens | `.env` file |

## Session Search vs Vault Search

Before answering any task:
1. `session_search(query)` — check past conversations
2. **If topic is documented domain** → check Obsidian MOCs first
3. **If generic or new** → proceed with external research

This prevents regenerating knowledge that already exists in the vault.
