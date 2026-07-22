---
name: writing-plans
description: "Write implementation plans: bite-sized tasks, paths, code."
version: 1.2.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, design, implementation, workflow, documentation]
    related_skills: [superpowers-workflow, subagent-driven-development, test-driven-development, requesting-code-review]
---

# Writing Implementation Plans

## Overview

Write comprehensive implementation plans assuming the implementer has zero context for the codebase and questionable taste. Document everything they need: which files to touch, complete code, testing commands, docs to check, how to verify. Give them bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume the implementer is a skilled developer but knows almost nothing about the toolset or problem domain. Assume they don't know good test design very well.

**Core principle:** A good plan makes implementation obvious. If someone has to guess, the plan is incomplete.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

## When to Use

**Always use before:**
- Implementing multi-step features
- Breaking down complex requirements
- Delegating to subagents via subagent-driven-development

**Trigger threshold:**
Use a plan whenever a task requires creating or modifying **2+ files** or has **2+ logical stages**. This covers almost all real feature/refactor/extension work.

**Don't skip when:**
- Feature seems simple (assumptions cause bugs)
- You plan to implement it yourself (future you needs guidance)
- Working alone (documentation matters)

## Bite-Sized Task Granularity

**Each task = one action (2-5 minutes).**

- "Write the failing test" — step
- "Run it to make sure it fails" — step
- "Implement the minimal code to make the test pass" — step
- "Run the tests and make sure they pass" — step
- "Commit" — step

**Too big:**
```markdown
### Task 1: Build authentication system
[50 lines of code across 5 files]
```

**Right size:**
```markdown
### Task 1: Create User model with email field
### Task 2: Add password hash field to User
### Task 3: Create password hashing utility
```

## Plan Document Structure

### Header (Required)

```markdown
# [Feature Name] Implementation Plan

> **For Hermes:** Use `superpowers-workflow` → `subagent-driven-development` to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

## Global Constraints

[Project-wide requirements — version floors, dependency limits, naming rules, platform requirements — one line each, copied verbatim from the spec. Every task implicitly includes this section.]

---
```

### Task Structure

````markdown
### Task N: [Descriptive Name]

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67`
- Test: `tests/path/to/test_file.py`

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter and return types]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: FAIL — "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## No Placeholders

Every step must contain the actual content an engineer needs. These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may read tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for.

- Design units with clear boundaries and well-defined interfaces.
- Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together.
- In existing codebases, follow established patterns. If a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

## Writing Process

1. **Understand requirements** — read specs, acceptance criteria, constraints.
2. **Load right skills first** — call `skills_list()`, then `skill_view(name)` for the most specific skills.
3. **Explore codebase** — project structure, similar features, existing tests.
4. **Design approach** — architecture, file organization, dependencies, testing strategy.
5. **Run a deletion/simplification scan** — check for dead code, duplication, or stdlib/native replacements before adding files.
6. **Write tasks** — setup → core functionality (TDD each) → edge cases → integration → cleanup.
7. **Add complete details** — exact paths, complete code, exact commands, verification steps.
8. **Self-review the plan** — check for placeholders, contradictions, ambiguity, scope gaps.
9. **Save the plan** — `docs/plans/YYYY-MM-DD-feature-name.md` or `.hermes/plans/YYYY-MM-DD_HHMMSS-feature-name.md`.

## Self-Review Checklist

After writing the plan:

- [ ] **Spec coverage:** Can you point to a task for each requirement? List any gaps.
- [ ] **Placeholder scan:** Search for red-flag patterns from the "No Placeholders" section.
- [ ] **Assumption scan:** Karpathy principle — are assumptions stated and interpretations surfaced?
- [ ] **Type consistency:** Do signatures and names match across tasks?
- [ ] **Task sizing:** Is every task 2–5 minutes and independently testable?
- [ ] **Verification:** Does every task end with a concrete command and expected output?

If you find issues, fix them inline.

## Execution Handoff

After saving the plan, offer:

> "Plan complete and saved to `docs/plans/<filename>.md`. Two execution options:
>
> 1. **Subagent-Driven (recommended)** — fresh subagent per task, two-stage review.
> 2. **Inline Execution** — execute in this session using `superpowers-workflow` → `executing-plans`.
>
> Which approach?"

## Principles

### DRY
**Bad:** Copy-paste validation in 3 places
**Good:** Extract validation function, use everywhere

### YAGNI
**Bad:** Add flexibility for future requirements
**Good:** Implement only what's needed now

### Lazy first (Ponytail lens)

Before writing new code in any task, run the ladder in this order and stop at the
first rung that holds:

1. **Does this need to exist at all?** (YAGNI) — speculative need → skip and say so.
2. **Does it already exist in this codebase?** — reuse the helper, util, type, or pattern that's already here.
3. **Does the standard library cover it?** — use stdlib.
4. **Does a native platform feature cover it?** — browser APIs, DB constraints, OS features, CSS before JS.
5. **Does an already-installed dependency cover it?** — use what's in `package.json` / `requirements.txt` / `Cargo.toml`.
6. **Can it be one line?** — make it one line.
7. **Only then:** write the minimum code that works.

The ladder runs **after** you understand the problem: trace the real flow end-to-end
before picking a rung. A small diff in the wrong place is a second bug, not laziness.

When touching an existing file, scan nearby code for:
- Duplication that can be merged
- Dead code that can be deleted
- Old helpers that can be generalized or removed
- Hand-rolled logic replaceable by stdlib or native platform features

If a deliberate simplification leaves a known ceiling (global lock, O(n²) scan,
naive heuristic), mark it with a `ponytail:` comment naming the ceiling and upgrade
path:

```python
# ponytail: global lock; per-account locks if throughput matters
```

The `ponytail:` comment format is:

```
# ponytail: <current ceiling>, <upgrade trigger>
```

Examples:
- `# ponytail: global lock; per-account locks if throughput matters`
- `# ponytail: O(n²) scan; optimize if n > 10_000`
- `# ponytail: naive heuristic; replace with ML model if precision < 90%`

Only mark real shortcuts. Trivial one-liners do not need a `ponytail:` comment.

**Boundary:** the lazy lens never cuts input validation at trust boundaries, error
handling that prevents data loss, security, accessibility, or anything explicitly
requested by the user. It also never replaces TDD with a single assert.

### When content comes from an existing project

If the new landing/feature reuses data from another project (products, categories, contacts, media), the plan must include a **data discovery task** before design:

- Query the source project's database/API/files for exact items to reuse.
- List the IDs/names/paths of content to copy.
- Include a verification step that confirms the copied assets exist in `public/`.

Example for pentajunior-v2 SQLite:

```bash
cd /home/natan/pentajunior-v2
python3 -c "
import sqlite3
c = sqlite3.connect('pentajunior.db').cursor()
c.execute('SELECT id, name, title, price, price_unit, price_currency, image, features FROM products WHERE id IN (?, ?, ?)', ('si-m-aero','vs-m-aero','ks-m-aero'))
for r in c.fetchall(): print(r)
"
```

Do not guess product names or prices from memory; query the source of truth.

### TDD
Every task that produces code should include the full TDD cycle. See `test-driven-development`.

### Frequent Commits
Commit after every task.

## Common Mistakes

- **Vague tasks:** "Add authentication" → "Create User model with email field"
- **Incomplete code:** "Add validation function" without the function
- **Missing verification:** "Test it works" without exact command
- **Missing file paths:** "Create the model file" → "Create: `src/models/user.py`"

## Remember

```
Bite-sized tasks (2-5 min each)
Exact file paths
Complete code (copy-pasteable)
Exact commands with expected output
Verification steps
DRY, YAGNI, TDD
Frequent commits
No placeholders
```

**A good plan makes implementation obvious.**
