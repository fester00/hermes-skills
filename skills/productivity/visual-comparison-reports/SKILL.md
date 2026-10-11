---
name: visual-comparison-reports
description: Use when comparing options for a visual HTML report.
version: 1.0.0
tags: [reporting, comparison, html, research, deliverable, visual]
---

# Visual comparison reports

Turning "compare A, B, C and let me see it clearly" into one reviewed HTML file the user can open, print and trust — with every number traceable.

## When to use

- "сравни X, Y, Z", "сделай сводку", "наглядно", "чтобы оценить" — any N-option decision the user wants to evaluate visually.
- A model / provider / tool / hardware comparison (for LLM-specific evidence sources also load `llm-inference-and-selection`).
- Not for a single-fact lookup: this is for decisions that need a table, a chart and a verdict.

## Procedure

1. **Fix the decision axes before researching.** Write down what the user will actually decide from the report (price? language support? can he run it himself? context size?). Research without axes produces an unrankable pile of benchmark numbers.
2. **Inventory the user's own environment first.** What is already installed / authenticated / purchased decides more than any spec sheet. A candidate he cannot reach is a separate decision line, never part of the main verdict.
3. **Gather evidence one field per source** using the hierarchy below; record the URL next to each number as you take it, not afterwards from memory.
4. **Collect conflicts explicitly** while researching — the "what is unverified" section is planned, not patched on at the end.
5. **Build the file from a Python builder script** (`templates/report_builder.py`): data in lists, tables and bar widths computed, nothing hand-typed. Print the output path and byte size as a build receipt.
6. **Verify by rendering** (`scripts/verify_report.py`), then report the path, the size, and what verification returned.

## Source hierarchy — trust order, not an average

| Rank | Source | Use it for |
|---|---|---|
| 1 | Official product page, vendor docs, model card / raw README (`https://huggingface.co/<org>/<model>/raw/main/README.md`) | Architecture, limits, license, official prices |
| 2 | Vendor benchmarks / release blog | Performance claims — always label *vendor* |
| 3 | Independent aggregators (Artificial Analysis, BenchLM, Vals, leaderboards with vote counts) | Cross-check; label *third-party* and name the snapshot |
| 4 | Review / SEO sites | Discovery and prices only; confirm every price on the provider's own page |

Rules from real comparisons:
- **Never rank values taken from different versions of the same-named index.** Several generations circulate under one name; the same item can read ~29 and ~55 depending on the version. Rank only inside one snapshot and print its date.
- **Specs: prefer the tech report / model card.** When aggregators disagree, show the disagreement instead of silently choosing a side.
- **A per-language or per-segment leaderboard is separate evidence.** Absence from it means "no crowd-sourced data here" — a finding, not a pass.

## Conflict handling

| Conflict | How to present it |
|---|---|
| Same metric, two index generations | Show both with scale / snapshot labels |
| Sources disagree on specs | Both values + "unresolved", naming who says what |
| Vendor claim vs weak independent rating | Report the gap; never average |
| Promo / off-peak / tiered pricing | Show the multiplier and the condition; never quote a promo as the standing price |
| Review-site price ≠ provider price | Provider wins; note the discrepancy |

A short **"conflicting data / what to re-verify"** section is mandatory — it is the part that makes the report trustworthy.

## Report structure

1. Header: date kicker, title naming the candidates, subtitle with the axes, meta chips (sources used, unit/currency, "checked <date>").
2. **TL;DR block first** — one bullet per candidate, each naming the axis it wins or loses on. Decision before evidence.
3. Spec table: one row per candidate, one column per axis from step 1, plus reachability in the user's setup.
4. Charts (below).
5. Detailed metric table with a **source + source-class column** on every row.
6. Cost / score model on the **user's own scenarios**, computed, cheapest-or-best cell per row highlighted.
7. Per-item cards: hard specs, strengths vs limitations in two columns, then a bolded "under your tasks" line.
8. Scenario verdicts: one bordered row per task type, naming the winner and the condition under which the runner-up wins.
9. Risks / what to re-verify.
10. Numbered source list with exact URLs.

## Chart rules (no chart library)

Horizontal bars as plain divs are reproducible, print-safe and readable as text — see `templates/report_builder.py`.
- Set an explicit scale maximum for score charts, so a subset of candidates does not stretch to full width and imply dominance.
- Sort bars by value; print the number plus its qualifier (`(promo)`, `(off-peak)`, `· #6`) at the row end.
- Label each chart with the question it answers and the direction of "better" ("less is better").
- Never draw a bar for a candidate with no data — write "not in this ranking" under the chart instead.

## Verification

1. Structural pass: tag balance, consistent cell count per table row, no `nan` / `None` leaking from the builder.
2. Real render: headless Chrome screenshot of the `file://` path; check the PNG is valid and sanely dimensioned.
3. Zoom into one chart region and confirm the longest bar belongs to the largest printed value — source can be clean while the render is wrong.
4. Report path + size + verification result; never call the report done from the source alone.

`scripts/verify_report.py <path.html>` does steps 1–2 in one command.

## Standing preferences for this user

- Answer and deliver in **Russian**; the report itself is Russian-language.
- Visual style: **warm cream editorial** (off-white paper, serif headings, restrained accent), not a dark dashboard.
- Numbers must be computed by a script, never hand-typed; a stated unit and a date belong next to every price.
- He values traceability over polish: keep the numbered source list and the conflict section even if the page grows.
- He will push back on unverified ranking — never present a single global "winner" without naming the scenario.

## Pitfalls

- **Do not hand-type computed numbers into the HTML.** Build from a script; a stale figure in a table is invisible until the user checks it.
- **An extractor's 403 / "keyless backend" error is the extractor failing, not the site.** Retry the URL with `curl -sL -A "Mozilla/5.0 ... Chrome/122 Safari/537.36"` plus a Python tag-strip before declaring a source unreachable.
- **Do not mix shell heredoc syntax into `execute_code`** — it is Python, not a shell. Use `terminal` for heredocs and `<<'PYEOF'` so nothing expands inside report content.
- **Do not paste the same table twice** in different sections; one canonical table per metric set.
- **Long tool-running builds need visible progress text**, not only silent tool batches — say what is being fetched and what was just confirmed.

## Related skills

- `llm-inference-and-selection` — LLM-specific discovery sources and deployment caveats.
- `excalidraw` / `architecture-diagram` — when the deliverable is a diagram rather than a data report.
