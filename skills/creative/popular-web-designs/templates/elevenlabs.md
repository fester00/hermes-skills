# Design System: Elevenlabs

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `elevenlabs/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/elevenlabs.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `Waldenburg` → **Fallback:** `EB Garamond`
> - **Mono:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'EB Garamond', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

ElevenLabs reads like a quietly editorial print magazine that happens to be a voice-AI product. The base canvas is off-white `{colors.canvas}` (#f5f5f5) holding warm near-black ink `{colors.ink}` (#0c0a09). The brand voltage is **photographic, not chromatic**: soft pastel atmospheric gradient orbs (mint, peach, lavender, sky, rose) drift through the page as the only "color" moments. There is no neon accent, no saturated CTA color, no dark-canvas dev-tools atmosphere.

Type pairs **Waldenburg Light** (custom serif at weight 300) for display with **Inter** for body, navigation, captions. The display weight at 300 is the editorial signature — never bold, never heavy.

CTAs are subtle: a near-black ink pill (`{component.button-primary}`) is the primary, a transparent outline (`{component.button-outline}`) is the secondary. The brand trusts atmospheric photography and modest type weights to carry brand work.

**Key Characteristics:**
- Off-white canvas, warm near-black ink. No saturated CTA color.
- Single primary action: ink pill at `{rounded.pill}`. Atmospheric gradients carry visual brand voltage.
- Display runs Waldenburg Light at weight 300 — editorial magazine voice.
- Body runs Inter at 400 with subtle letter-spacing (+0.15-0.18px).
- Pastel gradient orbs (5 tokens: mint, peach, lavender, sky, rose) used as atmospheric brand decoration only.
- Soft pill geometry (`{rounded.pill}` for CTAs, `{rounded.xl}` for cards).
- 96px section rhythm.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#292524`
- **Primary Active** (primary-active): `#0c0a09` — near-black
- **On Primary** (on-primary): `#ffffff` — pure/near-white
### Surfaces & Backgrounds
- **Canvas** (canvas): `#f5f5f5` — pure/near-white
- **Canvas Soft** (canvas-soft): `#fafafa` — pure/near-white
- **Canvas Deep** (canvas-deep): `#0c0a09` — near-black
- **Surface Card** (surface-card): `#ffffff` — pure/near-white
- **Surface Strong** (surface-strong): `#f0efed`
- **Surface Dark** (surface-dark): `#0c0a09` — near-black
- **Surface Dark Elevated** (surface-dark-elevated): `#1c1917` — near-black
### Text & Ink
- **Ink** (ink): `#0c0a09` — near-black
- **Body** (body): `#4e4e4e`
- **Body Strong** (body-strong): `#292524`
- **Muted** (muted): `#777169`
- **Muted Soft** (muted-soft): `#a8a29e`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
- **On Dark Soft** (on-dark-soft): `#a8a29e`
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#e7e5e4`
- **Hairline Soft** (hairline-soft): `#f0efed`
- **Hairline Strong** (hairline-strong): `#d6d3d1`
### Semantic & Status
- **Semantic Error** (semantic-error): `#dc2626` — warm red/orange tint
- **Semantic Success** (semantic-success): `#16a34a` — green tint
### Accent / Other
- **Gradient Mint** (gradient-mint): `#a7e5d3`
- **Gradient Peach** (gradient-peach): `#f4c5a8` — warm red/orange tint
- **Gradient Lavender** (gradient-lavender): `#c8b8e0`
- **Gradient Sky** (gradient-sky): `#a8c8e8`
- **Gradient Rose** (gradient-rose): `#e8b8c4` — warm red/orange tint

## 3. Typography Rules

### Font Family
- **Primary:** `'Waldenburg', 'Times New Roman', serif`

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-mega | 'Waldenburg', 'Times New Roman', serif | 64px | 300 | 1.05 | -1.92px |  |
| display-xl | 'Waldenburg', serif | 48px | 300 | 1.08 | -0.96px |  |
| display-lg | 'Waldenburg', serif | 36px | 300 | 1.17 | -0.36px |  |
| display-md | 'Waldenburg', serif | 32px | 300 | 1.13 | -0.32px |  |
| display-sm | 'Waldenburg', serif | 24px | 300 | 1.2 | 0 |  |
| title-md | 'Inter', sans-serif | 20px | 500 | 1.35 | 0 |  |
| title-sm | 'Inter', sans-serif | 18px | 500 | 1.44 | 0.18px |  |
| body-md | 'Inter', sans-serif | 16px | 400 | 1.5 | 0.16px |  |
| body-strong | 'Inter', sans-serif | 16px | 500 | 1.5 | 0.16px |  |
| body-sm | 'Inter', sans-serif | 15px | 400 | 1.47 | 0.15px |  |
| caption | 'Inter', sans-serif | 14px | 400 | 1.5 | 0 |  |
| caption-uppercase | 'Inter', sans-serif | 12px | 600 | 1.4 | 0.96px | uppercase |
| button | 'Inter', sans-serif | 15px | 500 | 1.0 | 0 |  |
| nav-link | 'Inter', sans-serif | 15px | 500 | 1.4 | 0 |  |


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
- **rounded:** {rounded.pill}
- **padding:** 10px 20px
- **height:** 40px

### button-primary-active

- **backgroundColor:** {colors.primary-active}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.pill}

### button-outline

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 9px 19px
- **height:** 40px

### button-tertiary-text

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.button}

### hero-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.display-mega}
- **padding:** 96px

### gradient-orb-card

- **backgroundColor:** {colors.canvas-soft}
- **textColor:** {colors.ink}
- **rounded:** {rounded.xxl}
- **padding:** 32px

### feature-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.xl}
- **padding:** 24px

### product-card-stack

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.xl}
- **padding:** 0

### voice-row

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **padding:** 12px 0

### voice-icon-circular

- **backgroundColor:** {colors.surface-strong}
- **rounded:** {rounded.full}
- **size:** 32px

### pricing-tier-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.xl}
- **padding:** 32px

### pricing-tier-featured

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.body-md}
- **rounded:** {rounded.xl}
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
- **rounded:** {rounded.xl}
- **padding:** 32px

### audio-waveform-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **rounded:** {rounded.xl}
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
| `xxl` | 24px |
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

- Max content width: ~1200px.
- Editorial body: 12-column grid.
- Feature card grids: 2-up at desktop for hero splits, 3-up for benefit grids.
- Footer: 5-column at desktop.
- Feature grid: 3-up → 2-up → 1-up.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat (canvas) | `{colors.canvas}` (#f5f5f5) | Body bands, footer |
| Card | `{colors.surface-card}` (#ffffff) | Content cards |
| Hairline border | 1px `{colors.hairline}` | Card outlines |
| Soft drop | `0 4px 16px rgba(0, 0, 0, 0.04)` | Hovered cards (single shadow tier) |
| Gradient orb | Radial gradient with one of `{colors.gradient-*}` | Atmospheric depth — never a card surface |


## 8. Do's and Don'ts

### Do
- Reserve `{colors.primary}` (ink pill) for primary CTAs.
- Use Waldenburg Light at weight 300 for every display headline. Never bold.
- Use Inter at +0.15-0.18px tracking for body — the editorial dialect.
- Use atmospheric gradient orbs (mint/peach/lavender/sky/rose) as decoration only.
- Use the pill shape for every CTA and badge.

### Don't
- Don't introduce a saturated brand action color. Ink pill is the only CTA color.
- Don't bold display copy. Display sits at weight 300 — bolding shifts the brand voice from editorial to consumer-marketing.
- Don't use gradient orbs as button fills, text colors, or component backgrounds. They are pure atmosphere.
- Don't use sharp `{rounded.none}` (0px) on CTAs. Pill geometry is the brand button.
- Don't drop body Inter to weight 300 to match Waldenburg — body stays at 400/500 for legibility.
- Don't extract a CTA color from a third-party widget (cookie consent, OneTrust). The brand's CTA color is what appears on actual product CTAs.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 640px | Hero h1 64→32px; feature cards 1-up; nav hamburger; gradient orbs shrink. |
| Tablet | 640–1024px | Hero h1 48px; feature cards 2-up. |
| Desktop | 1024–1280px | Full hero h1 64px; feature cards 3-up. |
| Wide | > 1280px | Content caps at 1200px. |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#292524`
- Background / Canvas: `#f5f5f5`
- Heading / Strong text: `#0c0a09`
- Body / Secondary text: `#4e4e4e`
- Primary Active: `#0c0a09`
- Body Strong: `#292524`
- Muted: `#777169`
- Muted Soft: `#a8a29e`
- Hairline: `#e7e5e4`
- Hairline Soft: `#f0efed`

### Example Component Prompts

- "Create a hero on the canvas background (`#f5f5f5`). Headline at 64px using the display font, weight 300, line-height 1.05, color `#0c0a09` with fallback Google Font. Primary CTA uses `#292524` background, white text, 8px radius, and comfortable padding."
- "Design a content card: `#ffffff` background, 1px `#e7e5e4` border, `12px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

