# Case Study: google-labs-code/stitch-skills

Worked example of evaluating an external skill library, rejecting it due to
proprietary lock-in, and extracting portable ideas into existing Hermes skills.

## External repo

- **URL:** https://github.com/google-labs-code/stitch-skills
- **Purpose:** Agent skills for Google Stitch (visual design-to-code tool).
- **Star/fork count at review:** 6.3k stars, 750 forks.

## Why we did not install it

The library is built around the **Stitch MCP server**. Every skill in the repo
lists `allowed-tools: ["stitch*:*"]` and the README explicitly states:

> These skills require the **Stitch MCP** server to be configured and running.

Installing the skills without the server would add dead references. We do not
use Google Stitch, so importing the library would only create lock-in and
broken tool expectations.

## Inventory mapping to our library

| stitch-skill | Our existing skill | Decision |
|---|---|---|
| `design-md` | `design-md` | Already covered. No action. |
| `taste-design` | `ui-ux-pro-max`, `luxury-immersive-web`, `claude-design` | Partially covered; extracted anti-generic checklist + vague→professional map into `ui-ux-pro-max`. |
| `popular-web-designs` | `popular-web-designs` | Already stronger (54 real design systems). Added `examples/prompt-enhancement.md` for before/after briefs. |
| `react-components` / `react-native` | `nextjs-*`, `pentajunior-v2-*` | Project-specific; no generic replacement needed. |
| `code-to-design` | — | Requires Stitch; not portable. Skipped. |
| `generate-design` | — | Requires Stitch; not portable. Skipped. |
| `stitch-loop` | `claude-design` + `generative-widgets` | Covered by existing workflow. |
| `enhance-prompt` | `ui-ux-pro-max` (partially) | Extracted terminology map and checklist. |

## Portable ideas extracted

1. **Prompt Enhancement Pipeline** (`claude-design`)
   - Detect vague terms → ask concise questions → load companion skills →
     translate to professional language → structure final brief.
   - Added as a new workflow step: *Enhance the brief*.

2. **Anti-Generic Design Checklist** (`ui-ux-pro-max`)
   - 10-item checklist to avoid "AI-design slop" even when data gives safe
     defaults. Rule: if >3 unchecked, ask a clarifying question.

3. **Vague → Professional Terminology Map** (`ui-ux-pro-max`)
   - Translation table: modern/clean/premium/make-it-pop → concrete design
     decisions to pass to implementation skills.

4. **Cross-skill integration rule** (`ui-ux-pro-max`)
   - `ui-ux-pro-max` gives *what* (data-driven brief).
   - `claude-design` gives *how* (process, variants, verification).
   - Repo/brand context always wins over generic defaults.

## Conflict checks performed

- Verified `claude-design` workflow items are numbered 1–8 with no duplicates.
- Confirmed `claude-design` owns the enhancement *process* while
  `ui-ux-pro-max` owns the *data hand-off*.
- Ensured repo-context priority is explicit in `ui-ux-pro-max` so data-driven
  defaults don't override existing brand docs.

## References

- stitch-skills README: https://github.com/google-labs-side/stitch-skills
- Updated skills: `claude-design`, `ui-ux-pro-max`, `popular-web-designs`
- Governing umbrella: `hermes-agent-skill-authoring`
