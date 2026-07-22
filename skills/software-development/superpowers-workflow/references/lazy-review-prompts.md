---

# Lazy review prompts

Internal prompt bank for applying Ponytail-style minimalism inside the
`superpowers-workflow` / `writing-plans` / `hermes-software-development-workflow`
without adding a second persona.

Use these as self-check prompts or subagent review prompts.

## Before adding code

Ask in this order:

1. Does this need to exist at all? (YAGNI)
2. Does it already exist in this codebase?
3. Does stdlib / native platform cover it?
4. Does an already-installed dependency cover it?
5. Can it be one line?
6. Only then: minimum code that works.

## When modifying a file

- Look at the surrounding code for duplication.
- Check whether an old helper can be deleted or generalized.
- Prefer updating existing code over adding parallel code.
- If you add a new abstraction, there must be at least two call sites now, not "later".
- Mark deliberate simplifications with a known ceiling using a `ponytail:` comment:
  `# ponytail: global lock; per-account locks if throughput matters`.

## Review tags (for reports)

- `delete:` — dead code, unused flexibility, speculative feature.
- `stdlib:` — hand-rolled thing the standard library ships.
- `native:` — dependency or code doing what the platform already does.
- `yagni:` — abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` — same logic, fewer lines.
- `merge:` — two similar things should be one.

## Safe guards (never simplify away)

- Input validation at trust boundaries.
- Error handling that prevents data loss.
- Security.
- Accessibility basics.
- Explicitly requested behavior.
- Calibration knobs for real hardware / real world.

## Output format

One line per finding:

```
<file>:L<line>: <tag> <what>. <replacement>.
```

Example:

```
src/lib/validation.ts:L12-38: stdlib 27-line email validator. Use "@" check + 1 line; real validation is the confirmation mail.
```

End with: `net: -<N> lines possible.`

If nothing to cut: `Lean already. Ship.`
