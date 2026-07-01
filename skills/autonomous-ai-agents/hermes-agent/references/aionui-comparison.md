# AionUi vs Hermes Agent — Comparative Analysis

> Context: User asked whether to migrate from Hermes WebUI to AionUi.
> Verdict: **Do NOT migrate**. Different product classes.
> Date: 2026-05-02

---

## What AionUi Is

- **Electron desktop app** (primary), with optional `--webui` server mode
- **Multi-agent frontend** — aggregates Claude Code, Codex, Hermes Agent, OpenClaw, Goose, Cursor Agent, etc. into single UI
- **Built-in Cowork agent** — file R/W, web search, image gen, MCP tools
- **Office assistants** — PPT/Word/Excel generation via OfficeCLI
- **Team Mode** — Leader + Teammate agents, parallel execution via MCP mailbox
- **20+ AI platforms** — Gemini, Claude, OpenAI, DeepSeek, Qwen, Ollama, LM Studio
- **Messaging:** Telegram, Lark, DingTalk, WeChat, WeCom, Slack
- **Cron scheduling, preview panel (PDF/Office/code/images)**

## Why Migration Does NOT Make Sense

| Factor | Hermes (current) | AionUi |
|--------|-----------------|--------|
| **Architecture** | Server backend: gateway + cron + webhook + profiles | Desktop Electron app (server mode secondary) |
| **Target platform** | Headless Ubuntu server 24/7 | macOS/Windows/Linux desktop GUI |
| **Gateway** | Native Telegram/Discord/Slack/Signal/Matrix/... (18 platforms) | Frontend notifications, not full gateway |
| **Agent depth** | One Hermes with skills/memory/delegation/profiles | Many agents shallowly coordinated |
| **Skills** | Full SKILL.md system (.md + scripts/ + references/) | Assistant presets + Extension SDK |
| **Cron** | Native `hermes cron` with delivery to messaging | UI-based scheduling |
| **WebUI** | Server behind nginx reverse proxy 24/7 | `--webui` flag, secondary use case |
| **Obsidian** | Native MCP Obsidian integration | Not supported |

## Key Risks of AionUi for Server Use

1. **Electron on headless server** — requires Xvfb or equivalent, resource overhead
2. **Not a gateway replacement** — messaging integrations are UI notifications, not autonomous gateway
3. **Loses Hermes infra** — profiles, skills, memory, cron, webhook all gone if switching
4. **Desktop-first updates** — docs, bugfixes, community oriented to desktop users
5. **Hermes becomes subordinate** — in AionUi, Hermes runs as one of many CLI agents, not as infrastructure

## When AionUi DOES Make Sense

- Desktop macOS/Windows user wanting GUI for Claude + Codex + Hermes simultaneously
- Need PPT/Word/Excel generation directly from chat (OfficeCLI)
- Want Team Mode — multiple agents in parallel with shared workspace
- Already using multiple CLI agents and want unified frontend

## Recommendation

- **Keep Hermes as primary server infrastructure** (WebUI + gateway + cron)
- **Optionally install AionUi locally on laptop** as secondary GUI for multi-agent desktop work
- Do not replace one with the other — they serve different layers
