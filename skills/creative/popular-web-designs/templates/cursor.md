# Design System: Cursor

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `cursor/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/cursor.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `CursorGothic` → **Fallback:** `Inter`
> - **Original mono family:** `JetBrains Mono` → **Fallback:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Cursor's marketing site reads as a quietly-confident developer brand that believes in editorial calm over IDE-darkness. The base canvas is **warm cream** (`{colors.canvas}` — #f7f7f4) holding warm near-black ink (`{colors.ink}` — #26251e) for body and display alike. The single brand voltage is **Cursor Orange** (`{colors.primary}` — #f54e00) reserved for primary CTAs and the wordmark — used scarcely.

Type runs **CursorGothic** as the single sans family. Display sits at weight 400 with negative letter-spacing — a magazine-editorial voice rather than tech-bombastic. JetBrains Mono carries every code surface (and code surfaces are roughly half the page).

The brand's strongest visual signature is the **AI-timeline pill palette**: five pastel pills (peach `{colors.timeline-thinking}`, mint `{colors.timeline-grep}`, blue `{colors.timeline-read}`, lavender `{colors.timeline-edit}`, gold `{colors.timeline-done}`) marking AI-action stages inside in-product timeline visualizations. Used only in product UI — never as system action colors.

**Key Characteristics:**
- Warm cream canvas, not white. Ink is warm (#26251e), not pure black.
- Single CTA color: `{colors.primary}` (Cursor Orange #f54e00). Used scarcely.
- Display weight stays at 400 — never bold. Magazine voice.
- AI timeline pastels: 5 dedicated tokens for in-product agent action stages.
- Compact 8px CTA radius — developer dialect.
- Hairline-only depth; no drop shadows.
- 80px section rhythm.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#f54e00` — warm red/orange tint
- **Primary Active** (primary-active): `#d04200` — warm red/orange tint
- **On Primary** (on-primary): `#ffffff` — pure/near-white
### Surfaces & Backgrounds
- **Canvas** (canvas): `#f7f7f4` — pure/near-white
- **Canvas Soft** (canvas-soft): `#fafaf7` — pure/near-white
- **Surface Card** (surface-card): `#ffffff` — pure/near-white
- **Surface Strong** (surface-strong): `#e6e5e0`
### Text & Ink
- **Ink** (ink): `#26251e` — near-black
- **Body** (body): `#5a5852`
- **Body Strong** (body-strong): `#26251e` — near-black
- **Muted** (muted): `#807d72`
- **Muted Soft** (muted-soft): `#a09c92`
- **Timeline Thinking** (timeline-thinking): `#dfa88f` — warm red/orange tint
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#e6e5e0`
- **Hairline Soft** (hairline-soft): `#efeee8`
- **Hairline Strong** (hairline-strong): `#cfcdc4`
### Semantic & Status
- **Semantic Error** (semantic-error): `#cf2d56` — warm red/orange tint
- **Semantic Success** (semantic-success): `#1f8a65`
### Accent / Other
- **Timeline Grep** (timeline-grep): `#9fc9a2`
- **Timeline Read** (timeline-read): `#9fbbe0`
- **Timeline Edit** (timeline-edit): `#c0a8dd` — cool blue tint
- **Timeline Done** (timeline-done): `#c08532` — warm red/orange tint

## 3. Typography Rules

### Font Family
- **Primary:** `'CursorGothic', system-ui, 'Helvetica Neue', Helvetica, Arial, sans-serif`
- **Monospace:** used for code/terminal surfaces.

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-mega | 'CursorGothic', system-ui, 'Helvetica Neue', Helvetica, Arial, sans-serif | 72px | 400 | 1.1 | -2.16px |  |
| display-lg | 'CursorGothic', sans-serif | 36px | 400 | 1.2 | -0.72px |  |
| display-md | 'CursorGothic', sans-serif | 26px | 400 | 1.25 | -0.325px |  |
| display-sm | 'CursorGothic', sans-serif | 22px | 400 | 1.3 | -0.11px |  |
| title-md | 'CursorGothic', sans-serif | 18px | 600 | 1.4 | 0 |  |
| title-sm | 'CursorGothic', sans-serif | 16px | 600 | 1.4 | 0 |  |
| body-md | 'CursorGothic', sans-serif | 16px | 400 | 1.5 | 0 |  |
| body-tracked | 'CursorGothic', sans-serif | 16px | 400 | 1.5 | 0.08px |  |
| body-sm | 'CursorGothic', sans-serif | 14px | 400 | 1.5 | 0 |  |
| caption | 'CursorGothic', sans-serif | 13px | 400 | 1.4 | 0 |  |
| caption-uppercase | 'CursorGothic', sans-serif | 11px | 600 | 1.4 | 0.88px | uppercase |
| code | 'JetBrains Mono', 'Fira Code', monospace | 13px | 400 | 1.5 | 0 |  |
| button | 'CursorGothic', sans-serif | 14px | 500 | 1.0 | 0 |  |
| nav-link | 'CursorGothic', sans-serif | 14px | 500 | 1.4 | 0 |  |


## 4. Component Stylings

### top-nav

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.nav-link}
- **height:** 64px

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 10px 18px
- **height:** 40px

### button-primary-active

- **backgroundColor:** {colors.primary-active}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.md}

### button-secondary

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 9px 17px
- **height:** 40px

### button-tertiary-text

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.button}

### button-download

- **backgroundColor:** {colors.ink}
- **textColor:** {colors.canvas}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 12px 20px
- **height:** 44px

### hero-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.display-mega}
- **padding:** 80px

### ide-mockup-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **rounded:** {rounded.lg}
- **padding:** 0

### ide-pane

- **backgroundColor:** {colors.canvas-soft}
- **textColor:** {colors.body}
- **typography:** {typography.code}
- **rounded:** {rounded.md}
- **padding:** 16px

### feature-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 24px

### comparison-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.lg}
- **padding:** 24px

### timeline-pill-thinking

- **backgroundColor:** {colors.timeline-thinking}
- **textColor:** {colors.ink}
- **typography:** {typography.caption-uppercase}
- **rounded:** {rounded.pill}
- **padding:** 4px 10px

### timeline-pill-grep

- **backgroundColor:** {colors.timeline-grep}
- **textColor:** {colors.ink}
- **typography:** {typography.caption-uppercase}
- **rounded:** {rounded.pill}
- **padding:** 4px 10px

### timeline-pill-read

- **backgroundColor:** {colors.timeline-read}
- **textColor:** {colors.ink}
- **typography:** {typography.caption-uppercase}
- **rounded:** {rounded.pill}
- **padding:** 4px 10px

### timeline-pill-edit

- **backgroundColor:** {colors.timeline-edit}
- **textColor:** {colors.ink}
- **typography:** {typography.caption-uppercase}
- **rounded:** {rounded.pill}
- **padding:** 4px 10px

### timeline-pill-done

- **backgroundColor:** {colors.timeline-done}
- **textColor:** {colors.on-primary}
- **typography:** {typography.caption-uppercase}
- **rounded:** {rounded.pill}
- **padding:** 4px 10px

### code-block

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.code}
- **rounded:** {rounded.lg}
- **padding:** 20px

### pricing-tier-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.lg}
- **padding:** 32px

### pricing-tier-featured

- **backgroundColor:** {colors.ink}
- **textColor:** {colors.canvas}
- **typography:** {typography.body-md}
- **rounded:** {rounded.lg}
- **padding:** 32px

### text-input

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.md}
- **padding:** 12px 16px
- **height:** 44px

### badge-pill

- **backgroundColor:** {colors.surface-strong}
- **textColor:** {colors.ink}
- **typography:** {typography.caption-uppercase}
- **rounded:** {rounded.pill}
- **padding:** 4px 10px

### cta-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.display-lg}
- **padding:** 96px

### testimonial-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.body}
- **typography:** {typography.body-md}
- **rounded:** {rounded.lg}
- **padding:** 24px

### footer

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.body}
- **typography:** {typography.body-sm}
- **padding:** 64px 48px

### footer-link

- **backgroundColor:** transparent
- **textColor:** {colors.body}
- **typography:** {typography.body-sm}


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
| `none` | 0px |
| `xs` | 4px |
| `sm` | 6px |
| `md` | 8px |
| `lg` | 12px |
| `xl` | 16px |
| `pill` | 9999px |
| `full` | 9999px |

**Spacing Scale**

| Token | Value |
|---|---|
| `xxs` | 4px |
| `xs` | 8px |
| `sm` | 12px |
| `base` | 16px |
| `md` | 20px |
| `lg` | 24px |
| `xl` | 32px |
| `xxl` | 48px |
| `section` | 80px |


## 6. Layout Principles

- **Section rhythm:** `80px` vertical padding between major bands.

### Grid & Container

- Max content width: ~1200px.
- Editorial body: 12-column grid.
- Feature card grids: 2-up at desktop for splits, 3-up for benefits.
- Footer: 5-column at desktop.
- Feature grid: 3-up → 2-up → 1-up.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat (canvas) | `{colors.canvas}` (#f7f7f4) | Body bands, footer |
| Card | `{colors.surface-card}` (#ffffff) | Content cards |
| Hairline border | 1px `{colors.hairline}` | Card outlines, dividers |
| IDE pane | `{colors.canvas-soft}` (#fafaf7) | Inside IDE mockup cards |


## 8. Do's and Don'ts

### Do
- Reserve `{colors.primary}` (Cursor Orange) for primary CTAs and brand wordmark.
- Keep display weight at 400. The editorial voice depends on this.
- Use the cream `{colors.canvas}` page floor — never pure white.
- Render every code surface (inline, blocks, IDE panes) in JetBrains Mono.
- Use timeline pastels only inside in-product agent visualizations — never as system action colors.

### Don't
- Don't introduce a secondary brand action color. Cursor Orange is the only one.
- Don't drop display to bold weights (700+). Magazine voice depends on 400.
- Don't add drop shadows. Hairlines + ink-on-cream contrast carry the depth.
- Don't use timeline pastels on non-timeline UI. They're scoped to the agent timeline only.
- Don't extract a CTA color from a third-party widget (cookie consent, OneTrust). The brand's CTA is what appears on actual product CTAs.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 640px | Hero h1 72→32px; IDE mockup collapses to single pane preview; feature grid 1-up; nav hamburger. |
| Tablet | 640–1024px | Hero h1 56px; IDE mockup compresses; feature grid 2-up. |
| Desktop | 1024–1280px | Full hero h1 72px; full multi-pane IDE mockup; feature grid 3-up. |
| Wide | > 1280px | Content caps at 1200px. |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#f54e00`
- Background / Canvas: `#f7f7f4`
- Heading / Strong text: `#26251e`
- Body / Secondary text: `#5a5852`
- Primary Active: `#d04200`
- Body Strong: `#26251e`
- Muted: `#807d72`
- Muted Soft: `#a09c92`
- Hairline: `#e6e5e0`
- Hairline Soft: `#efeee8`

### Example Component Prompts

- "Create a hero on the canvas background (`#f7f7f4`). Headline at 72px using the display font, weight 400, line-height 1.1, color `#26251e` with fallback Google Font. Primary CTA uses `#f54e00` background, white text, 8px radius, and comfortable padding."
- "Design a content card: `#ffffff` background, 1px `#e6e5e0` border, `12px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

