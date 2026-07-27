---
name: code-quality-gates
description: |
  Quality gates for software development: test-driven development, systematic
  debugging, pre-commit verification, and runtime debugging for Python, Node.js,
  and Hermes internal components. Use before, during, and after writing code.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [quality, testing, debugging, tdd, review, verification, code-review]
    related_skills: [hermes-software-development-workflow, github-workflows]
---

# Code Quality Gates

A collection of guardrails and practices to ensure code is correct, secure, and maintainable — from the first test through production debugging.

## Gate 1: Test-Driven Development (TDD)

**Core principle:** Write the test first. Watch it fail. Write minimal code to pass.

**When to use:** New features, bug fixes, refactoring, behavior changes.

### The Iron Law
```
No production code without a failing test first.
```

### The RED-GREEN-REFACTOR Cycle
| Phase | Action | Verification |
|-------|--------|--------------|
| **RED** | Write a test that fails | `pytest -k test_name` → must fail |
| **GREEN** | Write the simplest code to pass | `pytest -k test_name` → must pass |
| **REFACTOR** | Clean the code while keeping tests green | Full suite → all pass |

### Anti-Patterns to Catch
- "I'll write the test after" → test never gets written
- "This is too simple to test" → bugs hide in "simple" code
- Testing implementation details instead of behavior
- Asserting on private state
- Not watching the test fail first

**See `references/test-driven-development.md` for full rationalization tables, exceptions checklist, and verification steps.**

### TDD Regression Discovery
A passing test suite can still hide implementation bugs. When extracting legacy
helpers into shared `lib/*.ts` files, write unit tests for the real input shapes
seen in production before trusting the existing behavior. Example: the
`extractPrice` helper used a loose regex (`/[\d.]+/`) that matched a lone dot
and returned `"0"` for formatted prices like `"1 250,50 ₽"`. Tests written after
extraction immediately exposed the bug; the corrected regex (`/\d+(?:\.\d+)?/`)
passed all cases. See `references/extracted-helper-tdd-regression-discovery.md`
for the full pattern, decision tree, and verification steps.

---

## Gate 2: Systematic Debugging

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

### The Iron Law
```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

### 4-Phase Debugging Process
| Phase | Name | Purpose |
|-------|------|---------|
| **1** | **Root Cause Investigation** | Gather evidence, reproduce, trace data flow |
| **2** | **Pattern Analysis** | Compare working vs broken, identify exact change point |
| **3** | **Hypothesis & Testing** | Single hypothesis, minimal change, isolate variables |
| **4** | **Implementation** | Failing test first → fix → verify |

### When to Stop and Ask
- You can't reproduce the issue
- The fix requires a significant architectural change
- You've been debugging >30 min without progress
- Multiple hypotheses rejected — need fresh eyes

**See `references/systematic-debugging.md` for full red-flags table, common rationalizations, and escalation paths.**

### CSS/UI Animation Bugs
When a UI element animates unexpectedly during state changes (filtering, sorting, re-rendering), suspect `transition: all` on grid children. See `references/css-layout-transition-pitfall.md` for the exact pattern and fix.

---

## Gate 3: Pre-Commit Verification

**Core principle:** No agent should verify its own work. Fresh context finds what you miss.

### Pipeline
1. **Get the diff** (`git diff --cached`)
2. **Static security scan** (secrets, shell injection, eval, pickle, SQL injection)
3. **Baseline-aware tests + lint**
4. **Self-review checklist**
5. **Independent reviewer subagent** (2-stage: spec compliance, then code quality)
6. **Auto-fix loop** (max 2 cycles)
7. **Commit with `[verified]` prefix**

### Language-Specific Auto-Detection
| Language | Test Command | Lint Command |
|----------|-------------|--------------|
| Python | `pytest` / `python -m unittest` | `ruff check .` / `flake8` |
| TypeScript | `npm test` / `vitest` | `eslint .` / `tsc --noEmit` |
| JavaScript | `npm test` / `jest` | `eslint .` |
| Go | `go test ./...` | `gofmt -d .` / `golangci-lint` |
| Rust | `cargo test` | `cargo clippy` |

### Security Scan Patterns
```bash
# Hardcoded secrets
git diff --cached | grep "^+" | grep -iE "(api_key|secret|password|token|passwd)\s*=\s*['\"][^'\"]{6,}['\"]"

# Shell injection
git diff --cached | grep "^+" | grep -E "os\.system\(|subprocess.*shell=True"

# Dangerous eval/exec
git diff --cached | grep "^+" | grep -E "eval\(|exec\(|compile\(|__import__\(|pickle\.loads"

# SQL injection
git diff --cached | grep "^+" | grep -E "(cursor\.execute|f\".*SELECT|f\".*INSERT|f\".*UPDATE)"
```

**See `references/requesting-code-review.md` for full checklist, reviewer subagent prompt templates, and result evaluation criteria.**

### ESLint + Next.js Hook Rule Pitfall
`eslint-config-next` can emit `react-hooks/set-state-in-effect` errors for
legitimate controlled state resets in client components (admin auth checks,
form reset on record change). Don't blindly refactor working code; either
derive state with `useMemo`/React `key`, or disable the over-strict rule while
keeping `react-hooks/exhaustive-deps` as a warning. See
`references/eslint-nextjs-hook-rules.md` for the decision tree and exact config.

### React/TypeScript Animation Quality Review
When reviewing a React/TypeScript frontend that uses GSAP, Framer Motion, Lenis,
or custom DOM-driven animations, run the dedicated checklist to catch lifecycle
leaks, stringly-typed animation ids, copy-paste tilt logic, redundant state,
and accessibility gaps. See
`references/react-typescript-animation-quality-review.md` for the full checklist
and verification commands, including Vite/React SPA smooth-scroll integration
and single-page landing ScrollTrigger scoping.

---

## Gate 4: Runtime Debugging

When logs and tests aren't enough, attach a debugger.

### 4.1 — Python Debugging (`pdb` + `debugpy`)

| Tool | When |
|------|------|
| `breakpoint()` + `pdb` | Local, interactive, simplest. Add `breakpoint()` in source, run normally, REPL at that line. |
| `python -m pdb script.py` | Launch under pdb with no source edits. |
| `debugpy` | Remote / headless / attach to running process. DAP protocol, works for long-lived processes (gateway, daemon). |

**Pdb commands:** `n` (next), `s` (step in), `c` (continue), `l` (list), `p expr` (print), `q` (quit)

**See `references/python-debugpy.md` for remote attach recipes, post-mortem debugging, and VSCode launch.json configs.**

### 4.2 — Node.js Debugging (`node --inspect` + CDP)

| Tool | When |
|------|------|
| `node inspect script.js` | Built-in CLI REPL. Always available. |
| `ndb` / `chrome-remote-interface` | Scriptable from Node/Python. Automate breakpoints, collect state. |

**Commands:** `cont`, `next`, `step`, `out`, `bt` (backtrace), `watch(expr)`, `setBreakpoint(filename, line)`

**See `references/node-inspect-debugger.md` for heap snapshots, CPU profiles, and non-interactive CDP automation.**

### 4.3 — Hermes TUI Slash Command Debugging

Hermes slash commands span three layers. When a command misbehaves:

```
Python backend (hermes_cli/commands.py)     ← canonical COMMAND_REGISTRY
       │
       ▼
TUI gateway (tui_gateway/server.py)         ← slash.exec / command.dispatch
       │
       ▼
TUI frontend (ui-tui/src/app/slash/)        ← local handlers + fallthrough
```

**Investigation steps:**
1. Check if command exists in frontend: `search_files --pattern "/commandname" --file_glob "*.ts" --path ui-tui/`
2. Check Python backend: `search_files --pattern "'commandname'" --file_glob "*.py" --path hermes_cli/`
3. Verify COMMAND_REGISTRY entry has correct handler, description, arguments
4. Check gateway whitelist/routing mapping

**See `references/debugging-hermes-tui-commands.md` for full 3-layer sync checklist and common mismatch patterns.**

### TDD Regression Discovery
A passing test suite can still hide implementation bugs. In one refactor, the
`extractPrice` helper used a loose regex (`/[\d.]+/`) that matched a lone dot and
returned `"0"` for formatted prices like `"1 250,50 ₽"`. Unit tests written
*after* the function was extracted immediately caught the bug. The corrected
regex (`/\d+(?:\.\d+)?/`) passed all tests. Lesson: when extracting legacy
helpers, write tests for the real input shapes before trusting the existing
behavior.

---

## Quick Decision Tree

| Situation | Use this gate |
|-----------|---------------|
| About to write a feature | **Gate 1: TDD** |
| Test fails / bug reported | **Gate 2: Systematic Debugging** |
| Code ready, about to commit | **Gate 3: Pre-Commit Verification** |
| Can't see why a value is wrong at runtime | **Gate 4: Runtime Debugging** |
| Slash command missing from TUI | **Gate 4.3: Hermes TUI Debugging** |
| React/TS frontend animation review | **React/TypeScript Animation Quality Review** (Pre-Commit gate add-on) |