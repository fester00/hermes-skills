# Design System: Coinbase

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `coinbase/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/coinbase.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `Coinbase Display` → **Fallback:** `Inter`
> - **Original mono family:** `Coinbase Mono` → **Fallback:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Coinbase reads like an institutional financial brand that happens to trade crypto — the marketing surfaces are quiet, white-canvas, editorially-spaced, and almost monochromatic. The single brand voltage is **Coinbase Blue** (`{colors.primary}` — #0052ff), used scarcely: every primary CTA pill, the brand wordmark, and inline emphasis links. Beyond that one blue, the system is white canvas + ink + soft gray elevation bands + a deep near-black editorial canvas (`{colors.surface-dark}` — #0a0b0d) for full-bleed product-mockup heroes.

Type pairs **CoinbaseDisplay** for hero headlines with **CoinbaseSans** for body, captions, and navigation. Display sits at **weight 400** — not the 700+ typical of trading platforms. The choice signals editorial calm and institutional trust rather than fintech urgency.

The page rhythm rotates three modes: bright white editorial sections, soft-gray elevation bands, and **full-bleed dark editorial heroes** carrying layered product-UI mockup cards. The dark hero with floating dashboard mockups is the single most distinctive component.

**Key Characteristics:**
- Single accent color: `{colors.primary}` (#0052ff Coinbase Blue) carries every primary CTA, wordmark, and inline brand link. Used scarcely.
- Modest display weights — CoinbaseDisplay at weight 400, never 700+.
- Editorial pill geometry: every CTA is `{rounded.pill}` (100px), every asset glyph is `{rounded.full}`, every card is `{rounded.xl}` (24px). Sharp corners absent.
- Full-bleed dark heroes with floating product-UI cards: `{component.hero-band-dark}` plus inline `{component.product-ui-card-dark}` mockups is the brand's strongest signature pattern.
- Trading semantics: `{colors.semantic-up}` (#05b169) and `{colors.semantic-down}` (#cf202f) — text color only, never background fills.
- 96px section rhythm — generous editorial pacing.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#0052ff` — cool blue tint
- **Primary Active** (primary-active): `#003ecc` — cool blue tint
- **Primary Disabled** (primary-disabled): `#a8b8cc`
- **On Primary** (on-primary): `#ffffff` — pure/near-white
- **Accent Yellow** (accent-yellow): `#f4b000` — warm red/orange tint
### Surfaces & Backgrounds
- **Canvas** (canvas): `#ffffff` — pure/near-white
- **Surface Soft** (surface-soft): `#f7f7f7` — pure/near-white
- **Surface Card** (surface-card): `#ffffff` — pure/near-white
- **Surface Strong** (surface-strong): `#eef0f3`
- **Surface Dark** (surface-dark): `#0a0b0d` — near-black
- **Surface Dark Elevated** (surface-dark-elevated): `#16181c` — near-black
### Text & Ink
- **Ink** (ink): `#0a0b0d` — near-black
- **Body** (body): `#5b616e`
- **Body Strong** (body-strong): `#0a0b0d` — near-black
- **Muted** (muted): `#7c828a`
- **Muted Soft** (muted-soft): `#a8acb3`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
- **On Dark Soft** (on-dark-soft): `#a8acb3`
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#dee1e6`
- **Hairline Soft** (hairline-soft): `#eef0f3`
### Accent / Other
- **Semantic Up** (semantic-up): `#05b169` — green tint
- **Semantic Down** (semantic-down): `#cf202f` — warm red/orange tint

## 3. Typography Rules

### Font Family
- **Primary:** `'Coinbase Display', -apple-system, system-ui, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`
- **Monospace:** used for code/terminal surfaces.

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-mega | 'Coinbase Display', -apple-system, system-ui, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif | 80px | 400 | 1.0 | -2px |  |
| display-xl | 'Coinbase Display', sans-serif | 64px | 400 | 1.0 | -1.6px |  |
| display-lg | 'Coinbase Display', sans-serif | 52px | 400 | 1.0 | -1.3px |  |
| display-md | 'Coinbase Display', sans-serif | 44px | 400 | 1.09 | -1px |  |
| display-sm | 'Coinbase Sans', sans-serif | 36px | 400 | 1.11 | -0.5px |  |
| title-lg | 'Coinbase Sans', sans-serif | 32px | 400 | 1.13 | -0.4px |  |
| title-md | 'Coinbase Sans', sans-serif | 18px | 600 | 1.33 | 0 |  |
| title-sm | 'Coinbase Sans', sans-serif | 16px | 600 | 1.25 | 0 |  |
| body-md | 'Coinbase Sans', sans-serif | 16px | 400 | 1.5 | 0 |  |
| body-strong | 'Coinbase Sans', sans-serif | 16px | 700 | 1.5 | 0 |  |
| body-sm | 'Coinbase Sans', sans-serif | 14px | 400 | 1.5 | 0 |  |
| caption | 'Coinbase Sans', sans-serif | 13px | 400 | 1.5 | 0 |  |
| caption-strong | 'Coinbase Sans', sans-serif | 12px | 600 | 1.5 | 0 |  |
| number-display | 'Coinbase Mono', 'Coinbase Sans', monospace | 18px | 500 | 1.4 | 0 |  |
| button | 'Coinbase Sans', sans-serif | 16px | 600 | 1.15 | 0 |  |
| nav-link | 'Coinbase Sans', sans-serif | 14px | 500 | 1.4 | 0 |  |


## 4. Component Stylings

### top-nav-light

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.nav-link}
- **height:** 64px

### top-nav-on-dark

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.nav-link}
- **height:** 64px

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 12px 20px
- **height:** 44px

### button-primary-active

- **backgroundColor:** {colors.primary-active}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.pill}

### button-primary-disabled

- **backgroundColor:** {colors.primary-disabled}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.pill}

### button-secondary-light

- **backgroundColor:** {colors.surface-strong}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 12px 20px
- **height:** 44px

### button-secondary-dark

- **backgroundColor:** {colors.surface-dark-elevated}
- **textColor:** {colors.on-dark}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 12px 20px
- **height:** 44px

### button-outline-on-dark

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 11px 19px
- **height:** 44px

### button-tertiary-text

- **backgroundColor:** transparent
- **textColor:** {colors.primary}
- **typography:** {typography.button}

### button-pill-cta

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 16px 32px
- **height:** 56px

### hero-band-dark

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-mega}
- **padding:** 96px

### hero-band-light

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.display-mega}
- **padding:** 96px

### product-ui-card-dark

- **backgroundColor:** {colors.surface-dark-elevated}
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.xl}
- **padding:** 32px

### product-ui-card-light

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **rounded:** {rounded.xl}
- **padding:** 32px

### feature-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.xl}
- **padding:** 32px

### asset-row

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **padding:** 16px 0

### price-up-cell

- **backgroundColor:** transparent
- **textColor:** {colors.semantic-up}
- **typography:** {typography.number-display}

### price-down-cell

- **backgroundColor:** transparent
- **textColor:** {colors.semantic-down}
- **typography:** {typography.number-display}

### pricing-tier-card

- **backgroundColor:** {colors.canvas}
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

### cta-band-dark

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-lg}
- **padding:** 96px

### text-input

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.md}
- **padding:** 14px 16px
- **height:** 48px

### search-input-pill

- **backgroundColor:** {colors.surface-strong}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.pill}
- **padding:** 12px 20px
- **height:** 44px

### badge-pill

- **backgroundColor:** {colors.surface-strong}
- **textColor:** {colors.ink}
- **typography:** {typography.caption-strong}
- **rounded:** {rounded.pill}
- **padding:** 4px 12px

### asset-icon-circular

- **backgroundColor:** {colors.surface-strong}
- **rounded:** {rounded.full}
- **size:** 32px

### footer-light

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.body}
- **typography:** {typography.body-sm}
- **padding:** 64px 48px

### footer-link

- **backgroundColor:** transparent
- **textColor:** {colors.body}
- **typography:** {typography.body-sm}

### legal-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.muted}
- **typography:** {typography.caption}


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
| `none` | 0px |
| `xs` | 4px |
| `sm` | 8px |
| `md` | 12px |
| `lg` | 16px |
| `xl` | 24px |
| `pill` | 100px |
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

- **Max content width:** ~1200px centered. Hero photography full-bleed.
- **Editorial body:** Single 12-column grid.
- **Feature card grids:** 2-up at desktop for hero splits, 3-up for benefit grids.
- **Footer:** 6-column link list at desktop.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | 80% of surfaces |
| Hairline border | 1px `{colors.hairline}` | Feature card outlines on white |
| Soft drop | `0 4px 12px rgba(0, 0, 0, 0.04)` | Single shadow tier — hovered cards |
| Photographic | Full-bleed product-UI mockups | Hero depth |


## 8. Do's and Don'ts

### Do
- Reserve `{colors.primary}` (Coinbase Blue) for primary CTAs, wordmark, brand-glyph illustrations, inline accent links.
- Set every CTA as `{rounded.pill}` (100px); every asset glyph as `{rounded.full}`.
- Keep CoinbaseDisplay headlines at weight 400.
- Use the dark/light band rotation as page rhythm.
- Render every numerical value in CoinbaseMono via `{typography.number-display}`.
- Pair every dark hero with a layered product-UI mockup card stack.

### Don't
- Don't introduce a secondary brand color. Coinbase Blue is the only action color; trading green/red are semantic-only.
- Don't bold display copy — display sits at weight 400; bolding shifts the brand voice.
- Don't add drop shadow tiers — system has one shadow tier.
- Don't use sharp `{rounded.none}` (0px) on CTAs.
- Don't mix CoinbaseDisplay and CoinbaseSans inside the same headline.
- Don't use trading green/red as a button background.
- Don't extract a CTA color from a third-party widget (cookie consent, OneTrust). The brand's CTA color is what appears on actual product CTAs, not on injected modals.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 640px | Hero h1 80→40px; feature card grid 1-up; asset row stacks; nav collapses to hamburger; layered product-UI cards collapse to single card. |
| Tablet | 640–1024px | Hero h1 64px; feature card grid 2-up; asset rows stay horizontal but compress columns. |
| Desktop | 1024–1280px | Full hero h1 80px; feature card grid 3-up; full asset row layout. |
| Wide | > 1280px | Content caps at 1200px; hero photography full-bleed. |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#0052ff`
- Background / Canvas: `#ffffff`
- Heading / Strong text: `#0a0b0d`
- Body / Secondary text: `#5b616e`
- Primary Active: `#003ecc`
- Primary Disabled: `#a8b8cc`
- Body Strong: `#0a0b0d`
- Muted: `#7c828a`
- Muted Soft: `#a8acb3`
- Hairline: `#dee1e6`

### Example Component Prompts

- "Create a hero on the canvas background (`#ffffff`). Headline at 80px using the display font, weight 400, line-height 1.0, color `#0a0b0d` with fallback Google Font. Primary CTA uses `#0052ff` background, white text, 12px radius, and comfortable padding."
- "Design a content card: `#ffffff` background, 1px `#dee1e6` border, `16px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

