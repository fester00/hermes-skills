---
name: obsidian
description: Read, search, and create notes in the Obsidian vault — via MCP server (preferred) or terminal fallback.
---

# Obsidian Vault

**Location (terminal fallback):** Set via `OBSIDIAN_VAULT_PATH` env var. If unset, defaults to `~/Documents/Obsidian Vault`.

**Preferred method:** MCP server `obsidian-mcp` — gives the agent 11 native tools (`mcp_obsidian_*`) for direct read/write/search/tag operations without shell escaping or path quoting issues.

## MCP Method (Preferred)

If `obsidian-mcp` is installed and configured in `~/.hermes/config.yaml`, use the MCP tools directly:

| Tool | Purpose |
|---|---|
| `mcp_obsidian_list_available_vaults` | List configured vaults |
| `mcp_obsidian_create_note` | Create a new note with frontmatter |
| `mcp_obsidian_read_note` | Read note contents |
| `mcp_obsidian_edit_note` | Append / prepend / replace content |
| `mcp_obsidian_search_vault` | Full-text or filename search |
| `mcp_obsidian_move_note` | Move / rename while preserving links |
| `mcp_obsidian_create_directory` | Create a folder |
| `mcp_obsidian_delete_note` | Delete to `.trash` or permanently |
| `mcp_obsidian_add_tags` | Add tags to frontmatter or content |
| `mcp_obsidian_remove_tags` | Remove tags |
| `mcp_obsidian_rename_tag` | Global tag rename with hierarchy |

**All tools require:** `vault` parameter = the vault name (derived from the last path segment, e.g. `obsidian-memory`).

### Configuration example (obsidian-mcp via nvm)

```yaml
mcp_servers:
  obsidian:
    command: "/home/USER/.nvm/versions/node/v24.13.1/bin/node"
    args: ["/home/USER/.nvm/versions/node/v24.13.1/lib/node_modules/obsidian-mcp/build/main.js", "/home/USER/obsidian-memory"]
    timeout: 120
    connect_timeout: 60
```

> ⚠️ **nvm PATH pitfall**: Hermes spawns MCP subprocesses with a *filtered* PATH. `obsidian-mcp` installed via `nvm` or `npm -g` is often invisible. Use absolute paths to both `node` and the `build/main.js` entrypoint. See `native-mcp` skill for full details.

### Testing the connection

```bash
hermes mcp test obsidian
```

### MCP timeout during knowledge retrieval — fallback rule

If MCP tools (`mcp_obsidian_*`) timeout, hang, or return `ClosedResourceError` **while gathering information** (not during a write operation), do **not** skip the vault lookup. Switch immediately to terminal fallback:

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/obsidian-memory}"
cat "$VAULT/Knowledge/MOC — Index.md"
grep -rli "keyword" "$VAULT" --include="*.md"
find "$VAULT" -name "*.md" -iname "*keyword*"
```

The vault is the primary knowledge base. A broken MCP connection must never cause the agent to fall back to web search or generic answers without checking the vault first.

### If tools fail with `ClosedResourceError` — deep fix

The MCP **client** in the agent session holds a dead stdio pipe. Killing the server process (`obsidian-mcp`) or even restarting the gateway is not always enough — the *client handle* inside the current chat session may still be stale.

**Correct sequence:**

```bash
# 1. Kill stale MCP server processes
pkill -f obsidian-mcp

# 2. Restart gateway (re-spawns the MCP server)
systemctl --user restart hermes-gateway

# 3. Start a NEW chat session in WebUI — /new or refresh page
#    This gives a fresh MCP client handle.
```

> ⚠️ **Why both steps?** The gateway is a systemd service and owns the MCP server process. The WebUI session holds a per-session MCP client that caches the stdio pipe. Restarting gateway gives a fresh server, but the old client handle in the current chat session remains broken. `/reload-mcp` or `/new` creates a new client.

**Quick check if server is alive:**
```bash
ps aux | grep obsidian-mcp | grep -v grep
# Should show: node .../obsidian-mcp/build/main.js .../obsidian-memory
```

---

## Server-side process lifecycle (WebUI + Gateway + MCP)

For environments where WebUI is not a systemd service and MCP breaks across restarts, see: `references/mcp-webui-process-lifecycle.md`.

---

## Automated Context Retrieval — Vault as Agent Memory

The vault (`obsidian-memory`) is the agent's durable, associative memory. It should be consulted **automatically** before answering when the user's query matches a documented domain — without waiting for an explicit command.

### Trigger list — read from vault FIRST

Before answering, check if the query relates to any topic already in the vault. Use `MOC — Index.md` as the entry point, then follow wikilinks to the relevant note.

Common domains already tracked (see `Knowledge/MOC — Index.md`):
- **Infrastructure** → `Server — Ubuntu 24.04 Setup`, `Hermes WebUI Infra`
- **AI / LLM** → `Ollama Provider Setup` (proxy setup, provider pitfalls)
- **Integrations** → `Telegram Integration` (bot token, group "манах", config)
- **Personas / Roles** → `Hermes Personas` (Ugwai, PO, Shifu)
- **Projects** → `MOC — Projects` → individual project notes
- **Obsidian itself** → `Obsidian Vault Setup`, `MCP Server — Obsidian`

### Rule of thumb

> **If the topic exists in `Knowledge/MOC — Index.md` → read the linked note first.**  
> **If the user mentions a project name → read `Projects/MOC — Projects.md`, then the specific project note.**

This prevents redundant research, re-asking questions, and contradicting already-documented facts.

### Two-tier memory: agent + vault

The agent's short-term memory (~2,200 chars) stores **coordinates** — MOC entry points, active project names, and critical facts. The Obsidian vault stores **details** — unlimited depth.

**Short-term memory MUST always contain:**
- The canonical vault MOC paths (e.g. `Knowledge/MOC — Index.md`, `Projects/MOC — Projects.md`)
- A reminder: *"Before creating notes/methodologies from scratch, search the vault via MCP first"*

This prevents duplicating knowledge, regenerating methodologies, and wasting context on facts already documented.

> Full convention: `references/two-tier-memory-model.md`
> When memory fills up, follow offload procedure: `references/memory-optimization-pattern.md`

### Anti-pattern: avoid

- Do **not** full-text search the entire vault for every query — that wastes tokens.
- Do **not** read vault notes when the question is generic or unrelated to tracked domains.
- Do **not** treat vault as a place you "happen to write to" — treat it as the authoritative source of truth for recorded topics.
- Do **not** recreate knowledge that already exists in the vault — **search first, write second.**

---

## Terminal Fallback (When MCP unavailable)

Use when MCP server is not installed, not configured, or the current session's MCP connection is broken.

Note: Vault paths may contain spaces - always quote them.

**GitHub-synced vault:** The vault can be a Git repository (e.g. cloned from a private GitHub repo) that you edit in Obsidian Desktop locally while the agent reads/writes on the server.

## Read a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
cat "$VAULT/Note Name.md"
```

## List notes

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# All notes
find "$VAULT" -name "*.md" -type f

# In a specific folder
ls "$VAULT/Subfolder/"
```

## Search

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# By filename
find "$VAULT" -name "*.md" -iname "*keyword*"

# By content
grep -rli "keyword" "$VAULT" --include="*.md"
```

## Create a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
cat > "$VAULT/New Note.md" << 'ENDNOTE'
# Title

Content here.
ENDNOTE
```

## Append to a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
echo "
New content here." >> "$VAULT/Existing Note.md"
```

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

---

## Importing external archives into the vault

When the user shares a cloud archive (Yandex.Disk, Google Drive, etc.) and asks to add files to the vault:

1. Use the cloud provider's public API to get a direct download URL.  
   For Yandex.Disk public links, see: `references/yandex-disk-public-download.md`
2. Download to `/tmp/`, inspect structure, then batch-copy relevant folders into the vault.
3. Create or update the relevant MOC index notes.
4. Git commit and push.

## Bulk CSV → Obsidian Catalog

When a skill contains large `.csv` datasets and the user wants the full catalog mirrored in Obsidian:
- Use `references/bulk-csv-to-obsidian-catalog.md` for the full workflow, Python template, naming conventions, and sizing guidance.
- Key pitfall: MCP tools timeout on bulk writes — use `write_file` directly.

---

## Importing book/tutorial sources into the vault

When the user wants a freely available technical book or tutorial in the vault for later study:

1. **Prefer source Markdown over PDF.** Many official books (e.g. rust-lang/book) publish their source as Markdown on GitHub. Clone the repo rather than scraping HTML/PDF.
2. **Transform mdBook (or similar static-site) syntax into clean Obsidian Markdown:**
   - Replace `{{#include path[:anchor]}}` with literal code blocks from the referenced files.
   - Remove image-only lines (`![...](...)`).
   - Convert inter-file links `[text](other.md#anchor)` → Obsidian wikilinks `[[other#anchor|text]]`.
   - Strip HTML scaffolding tags (`<Listing ...>`, `<a id="...">`, etc.).
3. **Place under the relevant technology folder**, e.g. `Knowledge/Technical/Rust/The Rust Programming Language/`.
4. **Use `SUMMARY.md` from the source as the table of contents note** inside the book folder.
5. **For PDF books**, follow: `references/pdf-to-obsidian-conversion.md` (TOC-based chapter split, Markdown cleanup, README/SUMMARY generation).

Full conversion recipe and script: `references/import-mdbook-to-obsidian.md` and `references/pdf-to-obsidian-conversion.md`.
