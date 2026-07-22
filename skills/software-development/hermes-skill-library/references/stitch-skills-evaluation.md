# Case Study — Evaluating google-labs-code/stitch-skills

**Date:** 2026-07-01
**External repo:** https://github.com/google-labs-code/stitch-skills
**Decision:** Do not adopt as a dependency; adapt selected ideas into existing local skills.

## What the repo offers

A library of Agent Skills for the Google Stitch MCP server:

- `stitch-design` — design workflows (generate-design, code-to-design, etc.)
- `stitch-build` — code generation from Stitch designs (React, React Native, Remotion, shadcn-ui)
- `stitch-utilities` — DESIGN.md, prompt enhancement, stitch-loop, taste-design

## Critical dependency

All skills require the **Stitch MCP server** to be configured and running.
Without it, every skill is dead weight.

## Local overlap

| stitch-skill | Local equivalent | Coverage |
|---|---|---|
| `design-md` | `design-md` | Same Google spec, plus lint/export/diff |
| `taste-design` | `ui-ux-pro-max`, `luxury-immersive-web`, `claude-design` | Already covered with data-driven + process + premium |
| `popular-web-designs` | `popular-web-designs` | 54 real systems with exact tokens |
| `react-components` / `react-native` | project-specific skills | More precise for active repos |
| `stitch-loop` | `claude-design` + `generative-widgets` | Multi-page from prompt already possible |
| `enhance-prompt` | partial in `ui-ux-pro-max` | Could be strengthened |

## What we adapted

1. **Prompt Enhancement Pipeline** from `stitch::generate-design` → added to
   `claude-design` as a non-replacing workflow step.
2. **Anti-generic / taste-design standards** → added Anti-Generic Design
   Checklist and Vague→Professional Terminology Map to `ui-ux-pro-max`.
3. **Skill `examples/` directory** → added
   `popular-web-designs/examples/prompt-enhancement.md` with before/after
   briefs for Stripe, Linear, Vercel, Notion.

## What we ignored

- Direct installation of `stitch-skills` plugins.
- Any skill that calls Stitch MCP tools (`stitch*:*`).

## Lesson

When an external skill repo is locked to a service we do not use, treat it as
a source of ideas, not as a dependency. Extract the portable technique, patch
the relevant local umbrella skill, and keep the local library dependency-free.
