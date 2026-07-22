# Session: Graphify-Labs/graphify evaluation

Date: 2026-07-13
Session ID: 20260713_202433
Trigger: User asked to study `https://github.com/Graphify-Labs/graphify?ysclid=mrjo5ky7ox677149179` and compare it with existing code-intelligence tooling.

## TL;DR

Graphify is a polished, heavily marketed Python CLI/skill for building queryable knowledge graphs from code, docs, images, and video. It is free for code (tree-sitter AST, no LLM credits), MIT-licensed, and has a very large community (84k+ stars). However, for our existing Hermes + `codebase-memory-mcp` stack it is **mostly redundant and weaker on raw code-intelligence**: slower indexing, fewer query primitives, no native MCP tool surface, and smaller language coverage. We already executed a replacement of our older `graphify-project-audit` skill with `codebase-memory-audit`; Graphify would be a lateral/backward move, not an upgrade.

## Surface signals

| Signal | Value |
|---|---|
| Stars | 84,467 |
| Forks | 8,330 |
| Open issues | 500 |
| License | MIT |
| Language | Python |
| Last updated | 2026-07-13 (very active) |
| Created | 2026-04-03 (young, explosive growth) |
| Package | `graphifyy` on PyPI (note double-y) |

## What graphify does

- `detect → extract → build_graph → cluster → analyze → report → export` pipeline.
- Code extraction via tree-sitter AST across ~40 languages.
- Outputs `graph.html`, `GRAPH_REPORT.md`, `graph.json`, and optional Obsidian/wiki export.
- Commands: `graphify`, `graphify explain`, `graphify path`, `graphify query`.
- Also supports docs/PDFs/images/video through optional LLM-based semantic pass (not free).
- Has a thin MCP server (`graphify-mcp`) but it only exposes the built graph, not full indexing/query tools.

## Strengths

- **Zero-cost code graphs**: AST-only extraction needs no API key.
- **Excellent marketing/UX**: `graphify install` registers assistant-specific skills; 30+ translations; big Discord/LinkedIn presence.
- **Good benchmarks**: recall@10 0.497 on LOCOMO, ~10× mem0; LongMemEval-S 76%, tied with dense RAG.
- **Rich reporting**: god nodes, communities, surprising connections, suggested questions.
- **Obsidian export built-in**.

## Red flags / concerns

- **Explosive, very young repo**: 84k+ stars in ~3 months smells of artificial inflation or YC-fueled hype; sustainability unknown.
- **Polished README vs code reality**: heavily AI-generated docs, many optional extras (`all` dependency group is enormous).
- **Dependency weight**: 245 Python files, optional groups for Neo4j, FalkorDB, Whisper, yt-dlp, multiple LLM providers, office parsers — install surface is large.
- **MCP is secondary**: `serve.py` just loads a pre-built `graph.json`; not a first-class MCP code-intelligence server.
- **Language coverage**: ~40 languages via tree-sitter vs 158 languages claimed by `codebase-memory-mcp`.
- **Speed**: Python + tree-sitter; `codebase-memory-mcp` binary indexed `pentajunior-v2` in seconds.

## Comparison with our current tool: codebase-memory-mcp

| Criterion | Graphify | codebase-memory-mcp |
|---|---|---|
| Speed of indexing | Medium (Python) | Fast (single 257 MB Rust binary) |
| Languages | ~40 tree-sitter | 158 |
| Query tools | CLI + thin MCP | 14 MCP tools: `get_architecture`, `trace_path`, `search_code`, semantic search, dead-code detection |
| Cost for code | $0 | $0 |
| Native Hermes integration | Skill-based install | Native MCP server in `~/.hermes/config.yaml` |
| Obsidian export | Built-in | Not built-in; can be scripted |
| UI | 2D/3D HTML | None (data-first) |
| Dependency footprint | Large Python env | One binary |
| Benchmark rigor | Published harness with judge validation | Not independently benchmarked by us |

## Mapping to our context

- We already replaced `graphify-project-audit` with `codebase-memory-audit` after head-to-head testing showed CBM was faster and richer for query operations.
- Graphify would require us to revert or parallel that tooling with no clear functional gain.
- Graphify's assistant-skill installer is optimized for Claude Code/Cursor/Codex workflows, not Hermes; Hermes already has skills and MCP.

## Verdict

**Do not adopt Graphify.** Keep `codebase-memory-mcp` as the primary code-intelligence layer. Graphify is a valid reference for UX/docs/benchmarking discipline, but not a tool we should switch to.

If we ever want graphify-like visualization or free AST-only reporting, we can borrow its export/report ideas and add a thin wrapper around CBM output instead of installing graphify itself.

## Network note

This evaluation required routing GitHub through a local xray SOCKS5 proxy (`127.0.0.1:10808`) because direct TLS to GitHub timed out. Captured in `github-repo-evaluation` skill as a general pitfall.

## Files examined

- `README.md` (852 lines)
- `ARCHITECTURE.md`
- `BENCHMARKS.md`
- `AGENTS.md`
- `pyproject.toml`
- Repo file tree and test structure

## Recommendation

Close the Graphify thread. No integration work needed. Continue using `codebase-memory-audit` skill + `codebase-memory-mcp` server.
