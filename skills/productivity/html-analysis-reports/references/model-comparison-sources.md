# Sources for model comparison numbers

Use with the `html-analysis-reports` skill when the report compares LLMs. The point of this file
is **comparability**: most published numbers are not on the same scale, and quoting two of them
side by side produces a confident, wrong table.

---

## The one-scale source

**Artificial Analysis comparison pages are the only place where multiple models are measured by one
methodology.** Fetch one page per pair:

```bash
curl -sL -A "Mozilla/5.0" "https://artificialanalysis.ai/models/comparisons/<model-a>-vs-<model-b>"
```

A single page returns a side-by-side table for BOTH models: index, per-benchmark scores, price per
1M, cache-hit price, cost per task, tokens per task, output speed, time to first token, context
window, total/active params, license and input modalities. Pull one page per pair against a common
reference model until every candidate is covered.

### The index-version trap

The "Intelligence Index" is versioned, and aggregators re-quote values from different versions —
the same model legitimately appears as 29 on one site and 55 in its launch article.

- Compare values **only within one version**.
- Quote the version beside the number (`v4.3.x`).
- Leave a dash for a model that version never measured. Substituting a number from another scale is
  the single easiest way to make a comparison table wrong while every cell looks sourced.
- Treat an aggregator's "(estimated)" figure as an estimate, not a measurement.
- A very large TTFT (hundreds of seconds) is usually an artefact of a max-effort measurement
  setting, not real latency. Flag it as such or omit the row.

## Language-specific fit

- **`https://arena.ai/leaderboard/text/russian`** (swap the locale for others) ranks the same
  models for that language. For this user, Russian is a first-class selection criterion: a model
  absent from that board has **no crowdsourced evidence at all**, which is different from a bad
  score and must be reported as such.
- `https://openlm.ai/chatbot-arena` — ELO, coding, vision, license, org in one readable table.
- `https://benchlm.ai/models/<slug>` — per-model benchmark ledger with a source column; useful for
  agentic/tool-use rows (MCP Atlas, τ²-bench) that general boards omit.
- A newly released model is absent from a board snapshot simply because of timing. Name the nearest
  prior generation as an explicit **proxy**, never as the model's own score.

## Architecture, license and price

- **Hugging Face model card** (`https://huggingface.co/<org>/<model>/raw/main/README.md`) is the
  authority for total/active params, context, KV-cache design, training data volume and license.
- **Vendor launch post** is the authority for pricing, including tiers and peak/off-peak windows.
- When aggregators disagree on parameter count, one figure is usually the **previous generation's**
  (a successor inherits its predecessor's size in re-quotes). Trust the model card, and report the
  conflict in the report rather than silently choosing.
- Extract these pages with curl plus a tag-stripping script; the keyless web extractor frequently
  returns 403 on vendor and benchmark sites.

## Availability before recommendation

Check what the user can actually run before recommending anything:

```bash
curl -sL -o /dev/null -w '%{http_code}' https://ollama.com/library/<model>   # 404 = no local path
opencode models | grep -i <family>            # gateway models reachable with no vendor key
```

A model available only through a gateway is a real option but a dependent one: no weights, no
offline path, and the capability disappears if the gateway does. Say that in the report instead of
listing the model as simply "available".

## Independent harnesses outrank vendor self-reports

For honesty and instruction-following metrics (hallucination resistance, admission-of-ignorance,
format compliance), search out a third-party evaluation run before quoting the vendor's own number.
Vendor benchmark tables are marketing artefacts measured on the vendor's terms; a neutral harness
with a published method is what justifies a recommendation for teaching, support or legal work.
