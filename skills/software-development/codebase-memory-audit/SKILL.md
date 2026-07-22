---
name: codebase-memory-audit
description: |
  Read-only project intelligence skill. Uses the codebase-memory-mcp server to index
  a project and query its knowledge graph. Activate during Knowledge Discovery before
  design or planning for any project with more than 5 files.
category: software-development
related_skills:
  - superpowers-workflow
  - hermes-software-development-workflow
  - writing-plans
  - subagent-driven-development
---

# codebase-memory-audit

Index and query a project knowledge graph using [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp).

**Core principle:** Understand the codebase structure before changing it.

---

## When to use

Activate during the **Knowledge Discovery** phase when:

- The user asks to study, explore, refactor, or modify an **existing project**.
- The project has **more than 5 files**.
- The user asks architecture, dependency, structure, or "what calls X" questions.
- This is the first exploration of an unfamiliar codebase.

Do NOT run for:
- One-liner shell commands
- Pure explanations without codebase context
- Single scripts or throwaway prototypes
- Projects already audited in this session (cache is per-project in CBM)

---

## Trigger threshold

| Situation | Action |
|---|---|
| Single file / one-liner | Skip CBM; use `read_file` |
| 2–5 files, simple task | Optional — only if user asks structure questions |
| > 5 files | **Recommended:** index and query the graph |
| > 50 files | **Strongly recommended** — run architecture overview |
| > 200 files | Scope queries to relevant subfolder/package |

---

## Prerequisites

The MCP server must be configured in `~/.hermes/config.yaml`:

```yaml
mcp:
  servers:
    codebase-memory:
      command: /home/natan/.local/bin/codebase-memory-mcp
```

When available, this skill uses the native MCP tools. Fallback to CLI is documented below.

---

## Workflow

### Step 1: Confirm project root

Use the `[Workspace::v1: ...]` tag or explicit user path. Verify with:

```bash
pwd
ls -la
```

### Step 2: Index the project

If not already indexed, run:

```bash
codebase-memory-mcp cli index_repository --repo-path <project-root>
```

Or via MCP tool `index_repository` with `repo_path`.

Indexing is fast (pentajunior-v2: ~1s, Liga_vkBot: ~1s). It is safe to re-run;
subsequent calls are incremental.

**Project slug** is derived from the path (e.g. `/home/natan/pentajunior-v2` →
`home-natan-pentajunior-v2`). Confirm the slug with `list_projects` before using
it in queries. See `references/cbm-usage-notes.md` for real examples and output
field reference.

### Step 3: Query the graph

Useful queries:

| Goal | Tool / CLI |
|---|---|
| Architecture overview | `get_architecture` — aspects: all |
| Who calls X? | `trace_path --function-name X --direction inbound` |
| What does X call? | `trace_path --function-name X --direction outbound` |
| Search symbols | `search_graph --label Function --name-pattern ".*Handler.*"` |
| Text search | `search_code --pattern "seo_text"` |
| Cypher-like query | `query_graph --query "MATCH (f:Function)-[:CALLS]->(g) WHERE f.name = 'main' RETURN g.name"` |
| Dead code | `query_graph` with zero in-degree filter |

For exact CLI flag syntax and expected JSON output, see
`references/cbm-usage-notes.md`.

For lessons learned about trying CBM on non-code corpora (e.g. Obsidian vaults),
see `references/non-code-corpora-limitations.md`.

### Step 4: Read and interpret

Key outputs to look for:

- **hotspots** — most referenced functions/modules
- **layers** — entry / internal / core / leaf
- **boundaries** — cross-module call counts
- **clusters** — functional communities
- **entry_points** — top-level routes, scripts, pages

### Step 5: Save summary to Obsidian

Create/update:

```
~/obsidian-memory/Projects/<project-name>/codebase-memory-audit.md
```

Include:
- Project path and CBM version
- Node/edge counts
- Top hotspots
- Layer breakdown
- Boundaries (key cross-module links)
- Notable clusters
- Actionable insights for design/planning

Use the template from `references/cbm-audit-template.md`.

---

## Integration with superpowers-workflow

This skill runs in **Phase 0: Knowledge Discovery**, before design.

After the audit:
1. Load project-specific skill (e.g. `pentajunior-v2-nextjs-sqlite`).
2. Ask clarifying questions informed by hotspots and boundaries.
3. Proceed to design.

---

## Common pitfalls

- **Wrong project root** — indexing a parent directory adds noise.
- **Indexing node_modules/.next/.git** — CBM excludes these by default.
- **Trusting outdated index** — re-index after large changes.
- **Over-querying** — one good `get_architecture` call replaces many greps.
- **Forgetting to save to Obsidian** — insights should persist across sessions.
- **Indexing non-code knowledge bases** — CBM is built for code, not for Markdown/Obsidian vaults. A vault full of notes yields many `Section`/`File` nodes but weak edges and poor `query_graph`/`search_graph` results. Use MCP Obsidian + `search_files`/`read_file` for vaults instead.

---

## CLI fallback

If the MCP tool is unavailable, use the CLI directly:

```bash
codebase-memory-mcp cli index_repository --repo-path <project-root>
codebase-memory-mcp cli get_architecture --project <project-slug> --aspects all
codebase-memory-mcp cli trace_path --project <project-slug> --function-name <name> --direction inbound
```

Project slug is derived from the path (e.g. `/home/natan/pentajunior-v2` → `home-natan-pentajunior-v2`).

---

## Detecting dead CSS

CBM indexes CSS files as `File` nodes but does **not** track which CSS classes are used by TSX/TS components. For dead-CSS analysis use PurgeCSS instead.

See `references/css-dead-code-detection.md` for the exact command and how to interpret false positives from dynamic `className` construction.

---

## Remember

```
Project root → index_repository → get_architecture/trace_path/search_code → Obsidian → design
```

codebase-memory-audit is a read-only map, not a code change.
