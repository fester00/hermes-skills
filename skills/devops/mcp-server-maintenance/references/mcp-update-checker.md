# MCP Update Checker — Weekly Maintenance Job

## Purpose

Monitor external MCP servers that are not managed by Hermes itself for available updates, and deliver a concise weekly report to the user.

## Sources to monitor

| Server | Installed at | Source of truth |
|---|---|---|
| `codebase-memory-mcp` | `/home/natan/.local/bin/codebase-memory-mcp` | https://github.com/DeusData/codebase-memory-mcp/releases |
| `obsidian-mcp` | `/home/natan/.nvm/versions/node/v24.13.1/lib/node_modules/obsidian-mcp/` | https://registry.npmjs.org/obsidian-mcp |
| Hermes skills | `~/.hermes/skills` | `hermes skills check` |

## Discovery rules

- For GitHub releases, parse the releases page HTML with Python/curl. Do not rely on `api.github.com` — it rate-limits unauthenticated clients quickly.
- Prefer the latest **stable** (non-RC) tag. If no stable newer than installed exists but an RC exists, report the RC as "available for testing".
- For npm packages, use `https://registry.npmjs.org/<package>` (reliable, no auth).

## Output template

- One status line per source: up-to-date / update available / check failed.
- If update available: exact current version, latest version, and the exact upgrade command.
- If nothing newer: brief "All MCP servers and skills are up to date" message.
- If any check fails: say why (GitHub rate limit, network, missing binary, etc.).

## Installed job

Created as cron job `mcp-update-checker`, runs weekly on Mondays at 09:00, delivers to origin chat.

## Commands

```bash
hermes cron list
hermes cron run mcp-update-checker
hermes cron pause mcp-update-checker
hermes cron remove mcp-update-checker
```
