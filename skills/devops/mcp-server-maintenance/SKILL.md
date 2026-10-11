---
name: mcp-server-maintenance
description: Use when maintaining custom MCP servers. Update configs, check health, and fix manually installed servers in Hermes.
category: devops
related_skills: [hermes-agent, native-mcp]
---

# MCP Server Maintenance

How to keep manually installed MCP servers (codebase-memory-mcp, obsidian-mcp, and similar) healthy and up to date.

## Verify origin of an installed binary

A binary may sit in `~/.local/bin/` with no package-manager metadata. To confirm it matches a known project:

1. Read version and help: `/path/to/binary --version` and `/path/to/binary --help`.
2. Compare the tool list and version with the project's README / release notes.
3. For GitHub releases, parse the HTML releases page instead of the API to avoid rate limits.
4. For checksum verification, download the release asset and compare `sha256sum`.

Example for codebase-memory-mcp:
```bash
/home/natan/.local/bin/codebase-memory-mcp --version
/home/natan/.local/bin/codebase-memory-mcp --help
```

## Register a server in Hermes

Hermes uses the top-level `mcp_servers:` block in `~/.hermes/config.yaml`. A server defined only under `mcp.servers` (legacy shape) will not be active.

Register with:
```bash
hermes mcp add <name> --command <path-to-binary>
```

Verify:
```bash
hermes mcp list
hermes mcp test <name>
```

Start a new session after adding — tools are discovered at session start.

## Weekly update check job

Create a cron job that checks each external MCP server for updates and reports exact current version, latest version, and upgrade command.

Sources:
- GitHub releases page HTML (not API, to avoid rate limits) for binaries.
- npm registry (`https://registry.npmjs.org/<package>`) for global npm packages.
- `hermes skills check` for Hermes-managed skills.
- **Hermes WebUI git repository** (if installed separately under `~/hermes-webui` or a symlinked path) — run `git fetch origin master` and report commits behind `origin/master`. Do not auto-pull or restart; only report.

Do not auto-upgrade; only report.

### Example cron prompt

```
You are a weekly update checker for external MCP servers, Hermes skills, and the Hermes WebUI.

Sources:
1. codebase-memory-mcp binary at /home/natan/.local/bin/codebase-memory-mcp — check GitHub releases.
2. obsidian-mcp npm package — check registry.npmjs.org.
3. Hermes skills — run `hermes skills check`.
4. Hermes WebUI git repo at /home/natan/hermes-webui (origin https://github.com/nesquena/hermes-webui.git) — git fetch origin master and report commits behind.

For each source: up-to-date / update available / check failed, with exact versions and upgrade commands. If all are current, respond with [SILENT].
```

Create the job with:
```bash
hermes cron create "0 9 * * 1" --name mcp-update-checker --prompt-file /path/to/prompt.txt
```
## Commands reference

```bash
hermes mcp list
hermes mcp test <name>
hermes mcp add <name> --command <path>
hermes mcp remove <name>
hermes cron list
hermes cron create "0 9 * * 1"
```

## References

- `references/mcp-update-checker.md` — the user's installed weekly job details and output template.
- `references/mcp-legacy-config-trap.md` — why a server defined under `mcp.servers` is not active and how to fix it.
- `references/webui-update-check-cron.md` — adding a WebUI git-update check to the weekly `mcp-update-checker` cron job.
- `references/python-mcp-server-setup.md` — class-level workflow for installing and registering a third-party Python MCP server in Hermes (venv, standalone smoke test, config, activation, transport pitfalls).

## Commands reference