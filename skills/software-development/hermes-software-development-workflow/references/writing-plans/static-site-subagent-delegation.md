# Static Site Subagent Delegation — Field Notes

Umbrella: `writing-plans`  
Session: ts-tutorial-site (10-page static HTML tutorial site)  
Agent: kimi-k2.6:cloud

## What worked

### Sequential batching beats parallel mega-batch

- Batch 1: 2 agents × 2 pages each → 100% success (490s + 354s)
- Batch 2: 3 agents × 2-1 pages → 1 interrupted, 1 skipped → 33% failure
- Batch 3: 3 agents × 1 page each → 100% success (301s + 410s + 368s)

**Lesson:** With ~300-400 lines per page, 2 pages/subagent is reliable; 3 is risky.

### DOM Contract + BRIEF.md = Zero path drift

Every page had identical structure: `data-base-path="../../"`, `../../assets/`, `../../index.html`. Zero 404s.

### Subagent context template

```
PROJECT STRUCTURE:
- Root: ~/PROJECT/
- Assets: ~/PROJECT/assets/{style.css,script.js,search-data.json}
- BRIEF: ~/PROJECT/BRIEF.md

DOM CONTRACT:
- Every page: <body data-base-path="../../">
- Asset refs: ../../assets/style.css, ../../assets/script.js
- Header logo: ../../index.html
- Content: .content-section, .code-block, .tip-box, .warning-box
- Practice: .exercise-card + <details class="solution">

SIDEBAR: full sidebar with ../../ prefix on ALL cross-module links
```

## What failed

- One agent timed out at 255s on 2-page task (mapped + utility types)
- One agent was skipped when user sent new message mid-execution

## Integration checklist (curl-based, no browser needed)

1. `find . -name "*.html" | wc -l` — verify page count
2. Per-page: `grep -c 'class="code-block"'` — content exists
3. Per-page: check title tag
4. Assets: curl HEAD for 200
5. Nested pages: verify `../../` asset paths
6. Search data: JSON syntax + entry count

## Page complexity budget

| Lines/page | Risk | Recommendation |
|---|---|---|
| 200-300 | Low | Safe for 2 pages/agent |
| 300-500 | Medium | Safe for 2 pages/agent; 1 for guaranteed success |
| 500-700 | High | Only 1 page/agent |
| >700 | Critical | Split content into 2 pages or run in main session |
