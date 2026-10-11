---
name: html-analysis-reports
description: "Use when the user wants a visual HTML comparison report."
version: 1.0.0
tags: [reporting, comparison, evaluation, html, charts, deliverables, verification]
metadata:
  hermes:
    tags: [reporting, comparison, evaluation, html, charts, deliverables, verification]
    related_skills: [llm-inference-and-selection, code-quality-gates]
---

# HTML Analysis Reports

Produce one self-contained HTML file that lets the user judge N options at a glance. The canonical
request is "сводка в виде html чтобы наглядно всё оценить" — the deliverable is a file in the
workspace that opens offline and prints, not a chat answer with tables in it.

## When to use

- Several options must be compared: models, libraries, vendors, plans, architectures.
- The user asks for something "наглядно", a "сводка", or a table they can scan.
- A previously delivered report must absorb a newly added option.
- A recommendation must be defended with sources the user can check.

## Order of work

1. **Collect evidence, sources first.** Work outside-in from cheap sources, and record the URL
   beside every number. For LLM comparisons the source map is in
   `references/model-comparison-sources.md`.
2. **Run a live head-to-head before writing any verdict.** See below. Aggregates predict badly and
   the test re-ranks options they put level.
3. **Model the cost/impact on the user's real workload** — computed in code, never estimated.
   See below.
4. **Write the report** in the structure below.
5. **Verify, then deliver.** Never hand over a report without rendering it.

## Live head-to-head

Give every candidate the SAME task taken from the user's real work; compare outputs, not scores.
One shot each, timed:

```bash
for m in candidate-a candidate-b; do
  start=$(date +%s)
  timeout 180 <runner> "$m" "$(cat prompt.txt)" > "$m.txt" 2>&1
  echo "$m: $(( $(date +%s) - start ))s"
done
```

Design prompts to **discriminate**, never to flatter:

- A **generation task with a hard constraint** — word limit, "exactly one question", a required
  structure. Format discipline is what breaks at scale (a course is 100+ lessons from one template).
- A **role task with a spoiler ban** — "explain the error, do not give the finished solution".
  Reveals whether the option can hold a role instead of dumping an answer.

Score and tabulate: constraint respected / structure respected / no spoiler / order of steps /
caught the non-obvious detail / volunteered its own uncertainty / latency. Include the
"volunteered uncertainty" column — for teaching, support, or legal work it outranks fluency.

Keep prompts and raw outputs on disk and cite the path in the report's sources; the evidence
trail is what makes the verdict auditable.

## Cost modelling

Compute per message and per month on a realistic workload.

```python
def msg_cost(hit_in, miss_in, out_t, prices):   # prices = (cache_hit, cache_miss, output) per 1M
    ch, cm, o = prices
    ch = cm if ch is None else ch                # provider publishes no cache price
    return (hit_in*ch + miss_in*cm + out_t*o) / 1e6
```

- **Cache hits dominate** recurring work; always model with a hit ratio rather than assuming full price.
- **Respect tiers.** Cheap below a provider's tier boundary, mid-pack above it. Both verdicts are
  true at different prompt sizes — state which tier you applied in a footnote.
- **Show promo and post-promo, peak and off-peak rows** wherever a discount or time-based rate exists.
- Highlight the cheapest cell **per row**, not the cheapest option overall.

## Report structure

One file, inline `<style>` only, no CDN and no external assets, no JS required. Warm/cream
editorial palette suits this user (paper `#fffdf9` on `#faf7f2`, ink `#221e19`, accent `#b5563f`,
sage `#5f7a52`, blue `#4a6b8a`); serif headings, sans body; wide tables inside an
`overflow-x:auto` wrapper.

Section skeleton:

1. **Short verdict list** — one bullet per option, leading with what changed or what matters.
2. **Spec table** — the objective attributes of every option.
3. **Charts** — inline CSS bars, one per dimension worth seeing.
4. **Comparison table with a source column** — labelling each figure's provenance.
5. **Cost/impact table**.
6. **Per-option cards** — strengths, limitations, and one line on what it means for the user's tasks.
7. **Scenario verdicts plus a routing rule** (default choice → explicit escalation conditions),
   not a single global winner.
8. **Risks and conflicts** — contradictory data named out loud.
9. **Sources** — URLs and access date.

## Chart rules

- **Compute bar widths in code** (`width = value/max*100`) and emit the markup from the numbers.
  Hand-typed widths silently drift out of sync the moment a value is edited.
- **Compressed ranges need a truncated axis.** When values cluster (ratings, scores, ELO), scale
  from a stated floor rather than zero and write the truncation into the caption — otherwise every
  bar renders the same length and the chart actively hides the difference it exists to show.
- Put the unit and any caveat in the value label (`0.10 (до 100K)`, `1.20 (промо)`), not in a legend.
- Rebuild a whole chart block when values change; never patch individual widths.

## Honesty rules

- Label every figure: vendor / third-party / which index version. **A dash beats a borrowed
  number** — if a metric was never measured on the same scale, leave it empty and say why.
- Keep a **risks and conflicts** section that names contradicting data, says which source you trust,
  and why.
- State the limits of your own test in the same sentence as the strong claim it supports ("two
  prompts is a signal, not a sample").
- Flag anomalies that are clearly measurement artifacts rather than letting them stand as facts.
- Write in the same informal register the user speaks in ("ты") — never mix "вы" and "ты" in one document.

## Verifying before delivery

Three checks, in order:

1. **Structure** — parse with `html.parser`, assert no unclosed tags and that every table has one
   distinct cell count across its rows. Also assert the prose has no `nan`/`None`/template
   placeholders leaking from f-string maths.
2. **Render** — `google-chrome --headless=new --disable-gpu --no-sandbox --hide-scrollbars
   --window-size=1280,<height> --virtual-time-budget=5000 --screenshot=... file://$PWD/report.html`,
   then confirm the PNG is not blank and has real dimensions.
3. **Look at the render** and check that bars are proportional to the numbers printed beside them.
   A chart whose bars do not discriminate is worse than no chart. To inspect one section at full
   resolution, extract it into a scratch page reusing the same `<style>` instead of squinting at a
   tall full-page capture.

## Editing a delivered report

When a new option arrives after delivery:

1. **Back the file up first** (`cp report.html /tmp/report.backup.html`).
2. **`assert` each anchor string exists before replacing**, so a silent no-op is impossible; a
   failed assert leaving the file untouched is the safe outcome.
3. Regenerate whole blocks (spec table, chart divs, comparison table, cost table, affected
   sections) instead of nudging cells.
4. **Renumber** any sections that shifted, and re-run all three verification checks.
5. The new option must reach **every** table and chart *and* the top-line verdict list — present in
   the deep tables but missing from the summary reads as an oversight.

## Pitfalls

- Delivering the summary in chat and calling the file optional. The file is the deliverable.
- Quoting a single price for a tiered provider; the economics flip between short and long prompts.
- Letting an aggregator's number for one scale stand in for another scale.
- Editing a report without a backup and without an anchor assert, then shipping a half-patched file.
- Assuming the aggregate tables predict the live test. They routinely do not — run the test.

## See also

- `llm-inference-and-selection` — model discovery, Ollama/llama.cpp/vLLM deployment, hardware fit.
  That skill is **user-owned**; propose changes to the user rather than patching it autonomously.
- `references/model-comparison-sources.md` — where to get comparable numbers for LLMs, and the
  index-version trap.
