# Design System: Expo

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `expo/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/expo.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `Inter` → **Fallback:** `Inter`
> - **Original mono family:** `JetBrains Mono` → **Fallback:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Expo's marketing site reads like a quietly-confident React-Native developer platform. The base canvas is **pure white** (`{colors.canvas}` — #ffffff) with a soft **sky-blue gradient atmospheric wash** behind the hero band. Near-black ink `{colors.ink}` (#171717) carries body and display alike. The single brand voltage is **pure black** (`{colors.primary}` — #000000) for primary CTAs — minimal and editorial-feeling. A small blue text-link accent (`{colors.text-link}` — #0d74ce) is reserved for inline body links, never as a CTA.

Type runs **Inter** as the single sans family at modest weights (display 600, body 400). JetBrains Mono carries every code surface. No custom typeface — the brand trusts Inter's editorial neutrality.

The brand's strongest visual signature is the **device-mockup hero** — a centered MacBook + iPhone composite showing real Expo dev surfaces (Expo Studio, EAS Build dashboard, the Expo Go simulator) — over a sky-blue gradient atmospheric wash. The composite is the page's chrome instead of an illustration.

**Key Characteristics:**
- Pure white canvas with sky-blue gradient atmospheric backdrop in hero only.
- Single primary CTA: pure black pill at `{rounded.md}` (8px) — compact developer-tool dialect.
- Text-link blue (`{colors.text-link}`) for inline links only — never on a CTA.
- Inter as the single sans family — no custom display typeface.
- JetBrains Mono on every code surface.
- Device-mockup hero with real Expo product surfaces is the brand chrome.
- Hairline + soft drop depth; no atmospheric brand decoration outside the hero.
- 96px section rhythm.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#000000` — near-black
- **Primary Active** (primary-active): `#1a1a1a` — near-black
- **Text Link Secondary** (text-link-secondary): `#476cff` — cool blue tint
- **On Primary** (on-primary): `#ffffff` — pure/near-white
- **Accent Warning** (accent-warning): `#ab6400` — warm red/orange tint
- **Accent Preview** (accent-preview): `#8145b5` — cool blue tint
- **Accent Link Bright** (accent-link-bright): `#47c2ff` — cool blue tint
### Surfaces & Backgrounds
- **Canvas** (canvas): `#ffffff` — pure/near-white
- **Canvas Soft** (canvas-soft): `#fafafa` — pure/near-white
- **Surface Card** (surface-card): `#ffffff` — pure/near-white
- **Surface Strong** (surface-strong): `#f0f0f3`
- **Surface Dark** (surface-dark): `#171717` — near-black
- **Surface Dark Elevated** (surface-dark-elevated): `#1a1a1a` — near-black
### Text & Ink
- **Text Link** (text-link): `#0d74ce` — cool blue tint
- **Ink** (ink): `#171717` — near-black
- **Body** (body): `#60646c`
- **Body Strong** (body-strong): `#171717` — near-black
- **Muted** (muted): `#999999`
- **Muted Soft** (muted-soft): `#cccccc`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
- **On Dark Soft** (on-dark-soft): `#b0b4ba`
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#f0f0f3`
- **Hairline Soft** (hairline-soft): `#f5f5f7` — pure/near-white
- **Hairline Strong** (hairline-strong): `#dcdee0`
### Semantic & Status
- **Semantic Error** (semantic-error): `#eb8e90` — warm red/orange tint
- **Semantic Success** (semantic-success): `#16a34a` — green tint
### Accent / Other
- **Gradient Sky Light** (gradient-sky-light): `#cfe7ff`
- **Gradient Sky Mid** (gradient-sky-mid): `#a8c8e8`

## 3. Typography Rules

### Font Family
- **Primary:** `'Inter', -apple-system, system-ui, sans-serif`
- **Monospace:** used for code/terminal surfaces.

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-mega | 'Inter', -apple-system, system-ui, sans-serif | 64px | 600 | 1.05 | -1.92px |  |
| display-xl | 'Inter', sans-serif | 48px | 600 | 1.1 | -1.44px |  |
| display-lg | 'Inter', sans-serif | 36px | 600 | 1.15 | -1.08px |  |
| display-md | 'Inter', sans-serif | 28px | 600 | 1.2 | -0.84px |  |
| display-sm | 'Inter', sans-serif | 22px | 600 | 1.25 | -0.5px |  |
| title-md | 'Inter', sans-serif | 18px | 600 | 1.4 | 0 |  |
| title-sm | 'Inter', sans-serif | 16px | 600 | 1.4 | 0 |  |
| body-md | 'Inter', sans-serif | 16px | 400 | 1.5 | 0 |  |
| body-sm | 'Inter', sans-serif | 14px | 400 | 1.5 | 0 |  |
| caption | 'Inter', sans-serif | 13px | 400 | 1.4 | 0 |  |
| caption-uppercase | 'Inter', sans-serif | 11px | 600 | 1.4 | 0.88px | uppercase |
| code | 'JetBrains Mono', 'Fira Code', monospace | 13px | 400 | 1.5 | 0 |  |
| button | 'Inter', sans-serif | 14px | 500 | 1.0 | 0 |  |
| nav-link | 'Inter', sans-serif | 14px | 500 | 1.4 | 0 |  |


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
- **textColor:** {colors.text-link}
- **typography:** {typography.button}

### hero-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.display-mega}
- **padding:** 96px

### device-mockup-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **rounded:** {rounded.xl}
- **padding:** 0

### feature-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 24px

### feature-card-dark

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 24px

### workflow-step-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.body}
- **typography:** {typography.body-md}
- **rounded:** {rounded.lg}
- **padding:** 20px

### workflow-step-icon

- **backgroundColor:** {colors.surface-strong}
- **rounded:** {rounded.md}
- **size:** 32px

### code-block

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.code}
- **rounded:** {rounded.lg}
- **padding:** 20px

### ide-mockup-card

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.lg}
- **padding:** 0

### pricing-tier-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.lg}
- **padding:** 32px

### pricing-tier-featured

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
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

### ecosystem-tile

- **backgroundColor:** {colors.surface-card}
- **rounded:** {rounded.md}
- **size:** 64px

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

### footer-light

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
- Ecosystem tile grid: 8-up at desktop.
- Footer: 5-column at desktop.
- Feature grid: 3-up → 2-up → 1-up.
- Ecosystem tile grid: 8-up → 4-up → 3-up → 2-up.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat (canvas) | `{colors.canvas}` (#ffffff) | Body bands, footer |
| Card | `{colors.surface-card}` (#ffffff) | Content cards |
| Hairline border | 1px `{colors.hairline}` | Card outlines |
| Soft drop | `0 4px 12px rgba(0, 0, 0, 0.04)` | Hovered cards (single shadow tier) |
| Atmospheric gradient | Sky-blue radial wash | Hero backdrop only |
| Dark inversion | `{colors.surface-dark}` (#171717) | Dark feature cards, code blocks, featured pricing |


## 8. Do's and Don'ts

### Do
- Reserve `{colors.primary}` (black) for primary CTAs.
- Use `{colors.text-link}` (blue) for inline body links only — never on CTAs or buttons.
- Set every CTA at `{rounded.md}` (8px) — developer dialect.
- Use Inter at weight 600 for display, 400 for body.
- Render every code surface in JetBrains Mono.
- Pair the hero with the device-mockup composite — it's the page chrome.

### Don't
- Don't introduce a saturated brand action color. Black is the only CTA fill.
- Don't use blue (`{colors.text-link}`) on a CTA. Inline links only.
- Don't drop display below weight 600 or above 700.
- Don't use full pills on CTAs — pills are for badges only.
- Don't replicate the sky-blue gradient backdrop outside the hero.
- Don't extract a CTA color from a third-party widget (cookie consent, OneTrust). The brand's CTA is what appears on actual page CTAs.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 640px | Hero h1 64→32px; device mockup → single iPhone screen; feature grid 1-up; nav hamburger. |
| Tablet | 640–1024px | Hero h1 48px; device mockup compresses; feature grid 2-up. |
| Desktop | 1024–1280px | Full hero h1 64px; full MacBook + iPhone composite; feature grid 3-up. |
| Wide | > 1280px | Content caps at 1200px. |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#000000`
- Background / Canvas: `#ffffff`
- Heading / Strong text: `#171717`
- Body / Secondary text: `#60646c`
- Primary Active: `#1a1a1a`
- Text Link: `#0d74ce`
- Text Link Secondary: `#476cff`
- Body Strong: `#171717`
- Muted: `#999999`
- Muted Soft: `#cccccc`

### Example Component Prompts

- "Create a hero on the canvas background (`#ffffff`). Headline at 64px using the display font, weight 600, line-height 1.05, color `#171717` with fallback Google Font. Primary CTA uses `#000000` background, white text, 8px radius, and comfortable padding."
- "Design a content card: `#ffffff` background, 1px `#f0f0f3` border, `12px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

