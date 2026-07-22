# codebase-memory-mcp on non-code corpora (Obsidian vault test)

Date: 2026-07-13
Session ID: 20260713_202433

## What we tested

Indexed `/home/natan/obsidian-memory` with `codebase-memory-mcp` after the user
suggested it might speed up daily vault work.

## Results

| Metric | Value |
|---|---|
| Files | 784 |
| Nodes | 32 401 |
| Edges | 32 400 |
| Node labels | Section (30 788), File (784), Module (783), Folder (44), Branch (1), Project (1) |
| RAM used by CBM | ~11 GB |
| Index time | Fast (seconds) |

## What worked

- `search_code --pattern "..."` returned matching vault files quickly, with file
  paths and line numbers.
- `get_architecture --aspects file_tree` confirmed vault structure.

## What did not work

- `query_graph` returned `expected token type 0, got 85 at pos 0` — CBM's query
  parser expects code-graph node types, not Markdown sections.
- `search_graph --query "Hermes skills runbooks"` returned 0 results — BM25 over
  the code graph is not effective for prose.
- `--aspects hotspots` returned only `{total_nodes, total_edges}` with no useful
  hotspots — Markdown has no call/import/inheritance edges to rank.

## Comparison with native vault tools

| Task | CBM | MCP Obsidian + ripgrep |
|---|---|---|
| Full-text search | Fast, raw | Fast, raw |
| Wikilink resolution | Poor | Native |
| MOC navigation | No | Yes |
| Semantic/conceptual search | No | No (both need LLM) |
| RAM cost | ~11 GB held | Minimal |
| Reindex needed | Yes after changes | No |

## Verdict

For an Obsidian vault, CBM is **overkill and underpowered**: it consumes large
RAM, needs periodic reindexing, and gives weaker results than the native MCP
Obsidian / `search_files` stack. It is optimized for code, where AST edges create
a real graph. Prose vaults have no such edges.

## Recommendation

Do **not** use CBM as the primary vault search layer. Keep it for code projects
only. Use MCP Obsidian, `search_files`, and `read_file` for vault queries.

## Cleanup performed

Deleted the vault index from `~/.cache/codebase-memory-mcp/home-natan-obsidian-memory.db`
and removed the temporary `Obsidian Vault — CBM Index.md` note.
