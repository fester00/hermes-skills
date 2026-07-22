# Case Study — Evaluating Graphify-Labs/graphify

**Date:** 2026-07-10
**External repo:** https://github.com/Graphify-Labs/graphify
**Decision:** Do not install as a plugin; create a local read-only audit skill that uses the graphify CLI.

## What the repo offers

Graphify (81.5k stars) turns any folder of code, docs, papers, images, and
videos into a queryable knowledge graph. It parses code with tree-sitter AST
(no LLM, no API cost) and produces:

- `graph.json` — full graph
- `GRAPH_REPORT.md` — summary with god nodes, communities, surprising connections
- `graph.html` — interactive visualization

It supports Hermes via `graphify install --platform hermes`.

## Critical observation

Graphify is a **local-first tool** for project understanding. It does not
require an external service for code-only extraction. This makes it a good fit
for the local workflow. However, installing it as a Hermes plugin would
override/duplicate the existing skill orchestration. Better to wrap it in a
read-only class-level skill that fits into the existing workflow.

## Local integration

Created `graphify-project-audit`:

- Category: `software-development`
- Trigger: Knowledge Discovery phase, project > 50 files or architecture
  questions
- Behavior: run `graphify . --no-viz --code-only`, read `GRAPH_REPORT.md`,
  save summary to `~/obsidian-memory/Projects/<project>/graphify-audit.md`
- Cost: 0 tokens for code-only extraction

Updated:
- `superpowers-workflow` — Phase 0 audit step
- `hermes-software-development-workflow` — Step 0d optional audit
- `MOC — Skills` — index entry
- `Hermes — Loaded Skills Reference` — quick reference

## Test result

Ran on `/tmp/Liga_vkBot`:

| Metric | Value |
|---|---|
| Nodes | 72 |
| Edges | 151 |
| Communities | 15 |
| Code files | 16 |
| Extraction | 100% EXTRACTED |
| Token cost | 0 |

God nodes: `CrmClient` (25 edges), `get_main_keyboard()` (14 edges),
`get_cables_labeler()` (10 edges).

## Lesson

For local-first, read-only code intelligence tools, prefer a wrapper skill
that fits the existing workflow over a plugin install. Keep the tool's
output in Obsidian so it becomes part of the persistent knowledge base.
