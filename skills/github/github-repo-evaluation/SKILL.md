---
name: github-repo-evaluation
description: |
  Evaluate a GitHub repository for adoption fit — deep-dive methodology to answer
  "should we use this?" Assesses architecture, activity signals, dependencies,
  license, red flags, and maps findings to the user's specific projects and needs.
version: 1.0.0
author: Master Ugwai
metadata:
  hermes:
    tags: [github, evaluation, open-source, assessment, repository, adoption]
    related_skills: [github-workflows, github-repo-management, systematic-debugging]
---

# GitHub Repo Evaluation

Evaluate any GitHub repository to answer the user's question: **"Does this fit us?"**

## Trigger

User sends a GitHub URL and asks:
- «Подойдёт ли он нам?» / «Will this work for us?»
- «Should we use this?»
- «What do you think about this project?»
- «Analyze this repo»

## Evaluation Flow

### Step 1 — Surface Signals (30 seconds)

Navigate to the repo page. Read:
- **Stars / forks** — popularity indicator and community size
- **Last commit date** — project health (months stale = red flag)
- **Commit count** — maturity vs. abandonware
- **Open issues / PRs ratio** — maintenance burden
- **License** — MIT/Apache = good; GPL/AGPL = check compatibility
- **README completeness** — does it explain WHAT and WHY clearly?

### Step 2 — Deep Clone & Structure (1 minute)

```bash
cd /tmp && git clone <url> repo-eval && cd repo-eval
ls -la
find . -maxdepth 3 -type f | sort | head -50
```

Look for:
- `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod` — tech stack
- `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md` — project health
- `docs/` — documentation quality
- `tests/`, `*.test.*` — testing culture
- `.github/workflows/` — CI/CD presence
- Monorepo structure (`packages/`, `apps/`, `libs/`)

### Step 3 — Read Core Metadata

Read these files in order:
1. `README.md` — understand the project's purpose and claims
2. `package.json` / build config — dependencies, scripts, engines
3. Any `PROJECT_SUMMARY.md`, `CLAUDE.md`, or roadmap docs
4. `CHANGELOG.md` — see if claims match reality
5. Key source files (entry points, main generator/parser logic)

### Step 4 — Red Flag Checklist

| Flag | Severity | What it means |
|---|---|---|
| **>6 months no commits** | 🔴 High | Likely abandoned |
| **0 stars, 0 forks, no issues** | 🔴 High | No community, no feedback |
| **Hard dependency on specific cloud** (GCP, AWS-only) | 🟡 Medium | Vendor lock-in risk |
| **Created by AI, no human maintenance** | 🟡 Medium | May be brilliant but brittle |
| **No tests, no CI** | 🟡 Medium | Quality unknown |
| **Outdated dependencies** | 🟡 Medium | Security/compat risk |
| **Documentation promises > code delivers** | 🟡 Medium | Hype gap |
| **No license file** | 🔴 High | Cannot legally use |
| **GPL/AGPL** | 🟡 Medium | Check if user's project is proprietary |

### Step 5 — Map to User's Context

Compare against user's **active projects** and **preferences** (from memory + Obsidian):

| User Need | What to Check |
|---|---|
| **Next.js / React** | Is it JS/TS? Can it integrate? |
| **Rust learning** | Any Rust code to study? Patterns to adopt? |
| **CakePHP backend** | Any PHP relevance? |
| **Luxury web design** | Any design resources, UI libraries, references? |
| **Russian market** | Google Fonts blocked? CDN dependencies? |
| **Ozon/WB/Yandex** | Any e-commerce/marketplace integrations? |
| **CPU-conscious** | Heavy build? Local LLM dependencies? |

### Step 6 — Verdict Format

Deliver a structured answer:

```
## What is [Project]
2-sentence elevator pitch.

## Strong sides ✓
- Bullet list of genuine strengths

## Red flags ✗
- Bullet list of concerns

## Does it fit us?
Depends on goal:
- If X → Yes/No/Conditional with reasoning
- If Y → Maybe, with adaptation needed

## Recommendation
Concrete next step: try / fork / avoid / use as reference.
```

## Pitfalls

- **Don't stop at README.** Many projects have polished READMEs but rotten internals. Always clone and read source.
- **Check for AI-generated code.** Projects with "Made with Claude Code" in README may lack human judgment on edge cases.
- **Verify claims against code.** If README says "99/100 security score", find the scanner and see if it's real.
- **Assess dependency weight.** A project with 50 npm dependencies is heavier than one with 3.
- **Watch for platform lock-in.** "Requires Google Cloud Vertex AI" means it won't run without GCP.

## Related Skills

- `github-workflows` — for managing your own repos
- `github-repo-management` — clone, fork, create repos
- `systematic-debugging` — if evaluating reveals bugs to investigate

## References

- `references/session-magic-mcp.md` — example evaluation of a young MCP generator (Magic-MCP)
- `references/session-ui-ux-pro-max.md` — example evaluation of a popular design intelligence database (UI/UX Pro Max)
