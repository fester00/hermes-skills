---
name: ponytail-review
description: |
  Code review focused on over-engineering. Finds what to delete, replace with
  stdlib/native, or shrink. One line per finding.
category: software-development
related_skills:
  - ponytail
  - superpowers-workflow
  - simplify-code
  - code-quality-gates
---

# Ponytail Review

Review diffs for unnecessary complexity. The diff's best outcome is getting shorter.

## When to use

- After implementation, before merge.
- When user says: "review for over-engineering", "what can we delete", "is this over-engineered", "simplify review".
- As an optional pass in Phase 6 of `superpowers-workflow`, alongside `code-quality-gates`.

## Tags

Use one tag per finding:

- `delete:` — dead code, unused flexibility, speculative feature. Replacement: nothing.
- `stdlib:` — hand-rolled thing the standard library ships. Name the function.
- `native:` — dependency or code doing what the platform already does. Name the feature.
- `yagni:` — abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` — same logic, fewer lines. Show the shorter form.

## Format

```
<file>:L<line>: <tag> <what>. <replacement>.
```

End with the only metric that matters:

```
net: -<N> lines possible.
```

If there is nothing to cut: `Lean already. Ship.`

## Scope

Over-engineering and complexity only. Correctness bugs, security holes, and
performance are out of scope — route them to `code-quality-gates` or `code-quality-gates`.

Does not apply fixes; only lists findings.
