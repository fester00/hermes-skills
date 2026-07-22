# codebase-memory-mcp — project slug resolution

CBM derives a project slug from the repository path. Observations from real usage:

| Path | Project slug |
|---|---|
| `/home/natan/pentajunior-v2` | `home-natan-pentajunior-v2` |
| `/tmp/Liga_vkBot` | `tmp-Liga_vkBot` |

Rule of thumb: absolute path segments are joined with `-`, leading `/` is dropped.

## CLI vs MCP invocation

**CLI preferred for direct testing** because MCP tool naming can be auto-discovered only when the server is actually connected. The CLI commands work regardless of Hermes MCP state:

```bash
codebase-memory-mcp cli index_repository --repo-path <project-root>
codebase-memory-mcp cli list_projects
codebase-memory-mcp cli get_architecture --project <slug> --aspects all
codebase-memory-mcp cli trace_path --project <slug> --function-name <name> --direction inbound
codebase-memory-mcp cli search_code --project <slug> --pattern <pattern> --limit 20
codebase-memory-mcp cli query_graph --project <slug> --query '<cypher-like>'
```

**MCP tools** (when server is live): `index_repository`, `get_architecture`, `trace_path`, `search_graph`, `search_code`, `query_graph`, `get_code_snippet`, `get_graph_schema`, `list_projects`, `delete_project`, `index_status`, `detect_changes`, `manage_adr`, `ingest_traces`.

## Size observations

| Project | Files | Nodes | Edges | Index time |
|---|---|---|---|---|
| pentajunior-v2 | ~118 source files | 814 | 1970 | <1 s |
| Liga_vkBot | ~17 source files | 602 | 981 | <1 s |

## Known output fields

`get_architecture(aspects=['all'])` returns:
- `total_nodes`, `total_edges`
- `node_labels` — counts per node type
- `edge_types` — counts per edge type
- `languages` — detected languages and file counts
- `packages` — package/module fan-in/fan-out
- `entry_points` — top-level functions/pages/routes
- `hotspots` — most referenced symbols with `fan_in`
- `boundaries` — cross-package call counts
- `layers` — entry / internal / core / leaf classification
- `clusters` — functional communities with cohesion and top nodes
- `file_tree` — directory tree

Use these fields directly instead of re-running grep.

## Notes on graphify comparison

graphify required `--no-viz --code-only` to avoid LLM-key prompts and produced `GRAPH_REPORT.md` + `graph.json`. CBM replaces that flow with:
- faster indexing
- 14 query tools
- no LLM key required
- persistent SQLite store in `~/.cache/codebase-memory-mcp`
- optional team-shared artifact `.codebase-memory/graph.db.zst`

## Reindex strategy

CBM is incremental. Re-run `index_repository` after:
- large refactors
- adding/removing files
- switching branches
- before important architecture reviews

For throwaway exploration, no reindex is needed if the code did not change.
