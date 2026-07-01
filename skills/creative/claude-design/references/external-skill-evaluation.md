# Evaluating External Skill Libraries

Session: 2026-07-01  
Topic: Google `stitch-skills` repository analysis and decision.

## Why this matters

Users will occasionally drop a link to an external agent-skill library (Nerd Fonts, Stitch Skills, Agent Skills marketplace, etc.) and ask "should we use this?". This note records a reusable evaluation pattern.

## Case study: google-labs-code/stitch-skills

Repository: https://github.com/google-labs-code/stitch-skills  
Pitch: library of Agent Skills for Google Stitch, compatible with Codex, Gemini CLI, Claude Code, Cursor.

### What it actually requires

- **Stitch MCP server** must be configured and running. Without it, every skill is a dead dependency.
- Each skill is tightly coupled to Stitch APIs (`stitch*:*` tools).

### What it offers

| Plugin | Skills | Purpose |
|---|---|---|
| stitch-design | generate-design, code-to-design, manage-design-system, extract-design-md, extract-static-html, upload-to-stitch | design inside Stitch |
| stitch-build | react-components, react-native, remotion, shadcn-ui | code generation from Stitch designs |
| stitch-utilities | design-md, enhance-prompt, stitch-loop, taste-design | prompts + DESIGN.md |

### Overlap with our skills

| stitch-skill | Our equivalent | Coverage |
|---|---|---|
| design-md | `design-md` | Same Google spec, plus lint/export/WCAG |
| taste-design | `ui-ux-pro-max`, `luxury-immersive-web`, `claude-design` | Better, no external service |
| popular-web-designs | `popular-web-designs` | 54 exact systems vs generic taste |
| react-components / react-native | `nextjs-luxury-landing-to-catalog`, `pentajunior-v2-*` | Project-specific |
| enhance-prompt | partially in `claude-design` Prompt Enhancement Pipeline | Covered |
| stitch-loop | `claude-design` + `generative-widgets` | Covered |
| code-to-design / generate-design | — | Requires Stitch; do not adopt without Stitch access |

### Decision template

Use this checklist for future external skill libraries:

1. **Hard dependency check** — does the skill require an external service/MCP/account?
2. **Overlap check** — do we already have skills covering the same territory without the dependency?
3. **Lock-in risk** — will adopting it make us dependent on a single vendor/standard?
4. **Idea harvest** — can we extract useful techniques (prompt enhancement, validation pipeline, example structure) without adopting the dependency?

### Verdict for stitch-skills

**Do not install.** Instead, harvest the ideas:

- Prompt enhancement pipeline → added to `claude-design`.
- Anti-generic UI standards → added to `ui-ux-pro-max`.
- `examples/` directory per skill → added to `popular-web-designs`.

This gives 80 % of the value with 0 % of the Stitch lock-in.

## Related

- [[../SKILL.md|claude-design SKILL.md]] — Prompt Enhancement Pipeline
- `~/.hermes/skills/creative/ui-ux-pro-max/SKILL.md` — Anti-Generic Checklist
- `~/.hermes/skills/creative/popular-web-designs/examples/prompt-enhancement.md` — example briefs
