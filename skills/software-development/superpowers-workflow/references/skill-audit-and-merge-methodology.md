# Skill Audit and Merge Methodology

Use this reference when the user asks to audit, consolidate, or adopt an external skill library.

## When to run

- User drops a link to an external skill repo (e.g. `obra/superpowers`, Anthropic, Cursor rules, Google Stitch) and asks "should we use this?"
- Local skill library has grown and may contain duplicates or stale references.
- A skill was patched and the patch needs to ripple to related skills.

## Workflow

### 1. Structural audit

```python
import os, json

skills_dir = "/home/natan/.hermes/skills"
all_skills = []
for root, dirs, files in os.walk(skills_dir):
    if "SKILL.md" in files and ".archive" not in root:
        rel = os.path.relpath(root, skills_dir)
        with open(os.path.join(root, "SKILL.md")) as f:
            content = f.read()
        all_skills.append({"path": rel, "name": os.path.basename(root), "size": len(content)})

print(f"Total active: {len(all_skills)}")
```

### 2. Detect stale references

Collect archived skill names, then scan active SKILL.md files for references to them.
Also scan for references to superseded standalone skills such as:

- `hermes-software-development-workflow`
- `orchestrator-mode`
- `subagent-driven-development`
- `writing-plans`
- `test-driven-development`
- `systematic-debugging`
- `requesting-code-review`
- `verification-before-completion`
- `plan`
- `spike`

Replace stale references with the current canonical names:

| Old | Current canonical |
|---|---|
| `hermes-software-development-workflow` | `superpowers-workflow` |
| `orchestrator-mode` | `superpowers-workflow` |
| `subagent-driven-development` | `superpowers-subagent-driven-development` |
| `writing-plans` | `superpowers-writing-plans` |
| `test-driven-development` | `code-quality-gates` (operational gate) or `superpowers-test-driven-development` (deep-dive reference) |
| `systematic-debugging` | `code-quality-gates` (operational gate) or `superpowers-systematic-debugging` (deep-dive reference) |
| `requesting-code-review` | `code-quality-gates` Gate 3 |
| `verification-before-completion` | `code-quality-gates` Gate 4 |
| `plan` | `superpowers-writing-plans` |
| `spike` | `superpowers-workflow` Phase 0 spike |
| `react-vite-tailwind-landing-pages` | `frontend-efficiency-audit` / `frontend-css-maintenance` |
| `expo-tanstack-backend` | archived/deleted |
| `legacy-php-modernization` | archived/deleted |
| `zf1-isp-billing` | archived/deleted |

### 3. Compare external libraries

For each external repo:

1. Read `README.md` and representative `SKILL.md` files.
2. Identify the target runtime (Hermes, Codex, Cursor, Claude Code, Stitch MCP).
3. Check for lock-in: proprietary MCP, hosted service, paid API, harness-only runtime.
4. Map each skill to local skills using `skills_list()` and `skill_view()`.

### 4. Decide per skill

| Situation | Action |
|---|---|
| Requires external service we do not have | Ignore |
| Duplicate of existing local skill | **Ignore** unless materially better |
| Good ideas but wrong runtime/format | **Adapt** ideas into existing local skills |
| Genuinely missing capability and compatible | **Adopt** selectively |

### 5. Adopt / merge rules

- Remove harness-specific language ("Claude Code", "Codex", "Cursor", "Stitch MCP").
- Convert tool names to Hermes equivalents (`delegate_task`, `terminal`, `read_file`, `search_files`, `browser_navigate`, MCP servers).
- Preserve hard gates and red flags.
- Convert tables to bullet lists for Telegram safety when needed.
- Place skills under `~/.hermes/skills/<category>/<name>/`. Do NOT place active skills in `~/.hermes/profiles/<profile>/skills/` — that directory is not scanned by the skill loader.

### 6. Archive or delete

- Duplicate or superseded skills go to `~/.hermes/skills/.archive/<category>/`.
- After archiving, update any active skills that referenced the archived skill.
- Run a final broken-reference check: scan all active skills for `related_skills` pointing to non-existent names.

### 7. Verify

- `skills_list(category="...")` shows expected active skills.
- No duplicate names.
- No broken `related_skills`.
- No active skill references an archived name in a directive context.

## Quality principle

When merging duplicates, compare **method and result on the output**, not just coverage. Choose the skill that gives a clearer, more actionable, more Hermes-native path. Consolidate the best parts into one class-level skill rather than keeping two overlapping entries.