# Design System: Composio

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `composio/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/composio.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `abcDiatype` → **Fallback:** `Inter`
> - **Original mono family:** `JetBrains Mono` → **Fallback:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Composio's marketing site reads like a serious developer-infrastructure brand — closer to Vercel or Stripe Docs in atmosphere than to a typical AI-tools startup. The base canvas is a near-black `{colors.canvas}` (#0f0f0f) holding white type and a single voltage of **deep electric blue** (`{colors.primary}` — #0007cd) carrying every primary CTA, brand wordmark, and atmospheric spotlight glow that backs the homepage hero.

Type runs **abcDiatype** as the single sans family across display, body, navigation, and captions. Display sits at weight 500 — confident but not bombastic. Code blocks and terminal mockups switch to JetBrains Mono.

The page rhythm is monolithic: dark canvas top to bottom with subtle elevation steps via card surfaces. The brand's strongest visual signature is a **four-pane terminal-style mockup** — a 2×2 grid of dark code/output panels with a central blue spotlight glow behind them.

**Key Characteristics:**
- Single accent: `{colors.primary}` (#0007cd) for primary CTAs, wordmark, spotlight glows.
- Single sans family: abcDiatype carries everything except code (JetBrains Mono).
- Dark monolithic canvas: `{colors.canvas}` runs top to bottom; depth from `{colors.surface-card}` and `{colors.surface-card-elevated}` brightness steps.
- Terminal-mockup hero: 2×2 grid of code/output panes is the brand signature.
- Compact pill geometry: CTAs sit at `{rounded.md}` (8px), not full pills — developer-tool dialect.
- Spotlight-glow atmospheric backdrop: a radial blue glow centered behind hero content.
- 96px section rhythm.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#0007cd` — cool blue tint
- **Primary Active** (primary-active): `#0005a3` — cool blue tint
- **Primary Glow** (primary-glow): `#1a26ff` — cool blue tint
- **On Primary** (on-primary): `#ffffff` — pure/near-white
- **Accent Cyan** (accent-cyan): `#00d4ff` — cool blue tint
- **Accent Violet** (accent-violet): `#7b3aed` — cool blue tint
### Surfaces & Backgrounds
- **Canvas** (canvas): `#0f0f0f` — near-black
- **Canvas Deep** (canvas-deep): `#000000` — near-black
- **Surface Card** (surface-card): `#181818` — near-black
- **Surface Card Elevated** (surface-card-elevated): `#222222` — near-black
- **Surface Strong** (surface-strong): `#2a2a2a`
### Text & Ink
- **Ink** (ink): `#ffffff` — pure/near-white
- **Body** (body): `#a8a8a8`
- **Body Strong** (body-strong): `#ffffff` — pure/near-white
- **Muted** (muted): `#888888`
- **Muted Soft** (muted-soft): `#666666`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#222222` — near-black
- **Hairline Soft** (hairline-soft): `#1a1a1a` — near-black
- **Hairline Strong** (hairline-strong): `#333333`
### Semantic & Status
- **Semantic Error** (semantic-error): `#ff4d4d` — warm red/orange tint
- **Semantic Success** (semantic-success): `#33d17a` — green tint

## 3. Typography Rules

### Font Family
- **Primary:** `'abcDiatype', ui-sans-serif, system-ui, sans-serif`
- **Monospace:** used for code/terminal surfaces.

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-mega | 'abcDiatype', ui-sans-serif, system-ui, sans-serif | 72px | 500 | 1.05 | -2.16px |  |
| display-xl | 'abcDiatype', ui-sans-serif, system-ui, sans-serif | 56px | 500 | 1.05 | -1.68px |  |
| display-lg | 'abcDiatype', ui-sans-serif, system-ui, sans-serif | 44px | 500 | 1.1 | -1.32px |  |
| display-md | 'abcDiatype', ui-sans-serif, system-ui, sans-serif | 32px | 500 | 1.15 | -0.96px |  |
| display-sm | 'abcDiatype', ui-sans-serif, system-ui, sans-serif | 24px | 500 | 1.25 | -0.5px |  |
| title-md | 'abcDiatype', ui-sans-serif, system-ui, sans-serif | 18px | 600 | 1.4 | 0 |  |
| title-sm | 'abcDiatype', ui-sans-serif, system-ui, sans-serif | 16px | 600 | 1.4 | 0 |  |
| body-md | 'abcDiatype', ui-sans-serif, system-ui, sans-serif | 16px | 400 | 1.5 | 0 |  |
| body-sm | 'abcDiatype', ui-sans-serif, system-ui, sans-serif | 14px | 400 | 1.5 | 0 |  |
| caption | 'abcDiatype', ui-sans-serif, system-ui, sans-serif | 13px | 400 | 1.4 | 0 |  |
| caption-uppercase | 'abcDiatype', ui-sans-serif, system-ui, sans-serif | 11px | 600 | 1.4 | 0.88px | uppercase |
| code | 'JetBrains Mono', 'Fira Code', monospace | 13px | 400 | 1.5 | 0 |  |
| button | 'abcDiatype', ui-sans-serif, system-ui, sans-serif | 14px | 500 | 1.0 | 0 |  |
| nav-link | 'abcDiatype', ui-sans-serif, system-ui, sans-serif | 14px | 500 | 1.4 | 0 |  |


## 4. Component Stylings

### top-nav-dark

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.body-strong}
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

### button-secondary-dark

- **backgroundColor:** {colors.surface-card-elevated}
- **textColor:** {colors.body-strong}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 10px 18px
- **height:** 40px

### button-outline

- **backgroundColor:** transparent
- **textColor:** {colors.body-strong}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 9px 17px
- **height:** 40px

### button-tertiary-text

- **backgroundColor:** transparent
- **textColor:** {colors.body}
- **typography:** {typography.button}

### hero-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.body-strong}
- **typography:** {typography.display-mega}
- **padding:** 96px

### terminal-mockup-grid

- **backgroundColor:** {colors.canvas-deep}
- **textColor:** {colors.body-strong}
- **typography:** {typography.code}
- **rounded:** {rounded.xl}
- **padding:** 32px

### terminal-pane

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.body}
- **typography:** {typography.code}
- **rounded:** {rounded.lg}
- **padding:** 20px

### feature-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.body}
- **typography:** {typography.title-md}
- **rounded:** {rounded.xl}
- **padding:** 28px

### toolkit-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.body-strong}
- **typography:** {typography.title-sm}
- **rounded:** {rounded.lg}
- **padding:** 20px

### toolkit-icon

- **backgroundColor:** {colors.surface-card-elevated}
- **rounded:** {rounded.md}
- **size:** 40px

### spotlight-glow-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.body-strong}
- **typography:** {typography.display-md}
- **rounded:** {rounded.xl}
- **padding:** 48px

### code-block

- **backgroundColor:** {colors.canvas-deep}
- **textColor:** {colors.body}
- **typography:** {typography.code}
- **rounded:** {rounded.lg}
- **padding:** 20px

### badge-pill

- **backgroundColor:** {colors.surface-card-elevated}
- **textColor:** {colors.body-strong}
- **typography:** {typography.caption-uppercase}
- **rounded:** {rounded.pill}
- **padding:** 4px 10px

### text-input

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.body-strong}
- **typography:** {typography.body-md}
- **rounded:** {rounded.md}
- **padding:** 12px 16px
- **height:** 44px

### search-input

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.body-strong}
- **typography:** {typography.body-md}
- **rounded:** {rounded.md}
- **padding:** 10px 16px
- **height:** 40px

### cta-band-spotlight

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.body-strong}
- **typography:** {typography.display-lg}
- **padding:** 96px

### testimonial-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.body}
- **typography:** {typography.body-md}
- **rounded:** {rounded.lg}
- **padding:** 24px

### footer-dark

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
| `section` | 96px |


## 6. Layout Principles

- **Section rhythm:** `96px` vertical padding between major bands.

### Grid & Container

- Terminal-mockup hero: 2×2 grid of code/output panes is the brand signature.
- **Canvas Deep** (`{colors.canvas-deep}` — #000000): Pure black for terminal mockup grids and code blocks.
- Max content width: ~1200px.
- Editorial body: 12-column grid.
- Terminal mockup grid: 2×2 equal-size panes.
- Toolkit grid: 4-up at desktop, 2-up tablet, 1-up mobile.
- Footer: 5-column at desktop.
- Use the 2×2 terminal-mockup grid as the homepage hero anchor.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat (canvas) | `{colors.canvas}` (#0f0f0f) | Body bands, footer |
| Recessed | `{colors.canvas-deep}` (#000000) | Terminal mockup grid background, code blocks |
| Card | `{colors.surface-card}` (#181818) | Default content cards |
| Card elevated | `{colors.surface-card-elevated}` (#222222) | Terminal panes, secondary buttons |
| Atmospheric glow | Radial gradient using `{colors.primary-glow}` | Hero spotlight backdrop |


## 8. Do's and Don'ts

### Do
- Reserve `{colors.primary}` for primary CTAs, wordmark, and spotlight glows.
- Use `{rounded.md}` (8px) for every CTA — not full pills.
- Use brightness-step ladder for elevation; avoid drop shadows.
- Pair every hero with a centered radial blue spotlight glow.
- Render code, CLI commands in JetBrains Mono via `{typography.code}`.
- Use the 2×2 terminal-mockup grid as the homepage hero anchor.

### Don't
- Don't introduce a secondary brand color. Cyan and violet are illustrative-only.
- Don't use full pills on CTAs.
- Don't drop display weight to 400.
- Don't add drop shadow tiers.
- Don't use canvas-deep (#000000) outside terminal/code surfaces.
- Don't extract a CTA color from a third-party widget (cookie consent, OneTrust). The brand's CTA color is what appears on actual page CTAs.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 640px | Hero h1 72→36px; terminal mockup grid collapses to single pane; toolkit grid 1-up; nav hamburger. |
| Tablet | 640–1024px | Hero h1 56px; terminal mockup grid stays 2×2; toolkit grid 2-up. |
| Desktop | 1024–1280px | Full hero h1 72px; full 2×2 terminal mockup; toolkit grid 4-up. |
| Wide | > 1280px | Content caps at 1200px. |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#0007cd`
- Background / Canvas: `#0f0f0f`
- Heading / Strong text: `#ffffff`
- Body / Secondary text: `#a8a8a8`
- Primary Active: `#0005a3`
- Primary Glow: `#1a26ff`
- Body Strong: `#ffffff`
- Muted: `#888888`
- Muted Soft: `#666666`
- Hairline: `#222222`

### Example Component Prompts

- "Create a hero on the canvas background (`#0f0f0f`). Headline at 72px using the display font, weight 500, line-height 1.05, color `#ffffff` with fallback Google Font. Primary CTA uses `#0007cd` background, white text, 8px radius, and comfortable padding."
- "Design a content card: `#181818` background, 1px `#222222` border, `12px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

