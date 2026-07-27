# Design System: Ferrari

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `ferrari/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/ferrari.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `FerrariSans` → **Fallback:** `Inter`
> - **Mono:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Ferrari's marketing site reads as cinematic editorial — closer to a luxury-magazine spread than a typical car-OEM site. The base canvas is **near-black** (`{colors.canvas}` — #181818) holding pure white display type; white-canvas bands appear only inside specific editorial contexts (preowned listings, pricing tables, dealer surfaces). The single brand voltage is **Rosso Corsa** (`{colors.primary}` — #da291c), the iconic Ferrari racing red, used scarcely on primary CTAs, the Cavallino mark, and Formula 1 race-position highlights.

Type runs **FerrariSans** as the single sans family at modest weights — display 500, body 400. CTA labels render in uppercase with generous tracking (1.1-1.4px). The brand never uses bold display copy.

The brand's strongest visual signature is the **full-bleed cinematic hero photograph** — top-of-page imagery shows car photography, model details, or trackside livery without any chrome competing with it. Headlines float over the bottom of the photo or sit in a tight band beneath. Spacing follows the explicit 8px token ladder: `xxxs` 4 / `xxs` 8 / `xs` 16 / `sm` 24 / `md` 32 / `lg` 48 / `xl` 64 / `xxl` 96 / `super` 128.

**Key Characteristics:**
- Single accent: `{colors.primary}` (Rosso Corsa #da291c) for primary CTAs, the Cavallino, F1 race-position highlights. Used scarcely.
- Near-black canvas (#181818) — never pure black. White-canvas bands only inside editorial contexts.
- Single sans family: FerrariSans across every text role.
- Display weight stays at 500 — never bold.
- CTA labels render uppercase with 1.4px tracking.
- Sharp `{rounded.none}` (0px) corners on every CTA, card, and band — luxury-automotive precision.
- Full-bleed cinematic hero photography is the page chrome.
- Explicit 8px spacing token ladder with named scale (xxxs through super).
- Hairlines + photographic depth — no drop shadow tiers.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#da291c` — warm red/orange tint
- **Primary Active** (primary-active): `#b01e0a` — warm red/orange tint
- **Primary Hover** (primary-hover): `#9d2211` — warm red/orange tint
- **On Primary** (on-primary): `#ffffff` — pure/near-white
- **Accent Yellow Hypersail** (accent-yellow-hypersail): `#fff200`
- **Accent Yellow** (accent-yellow): `#f6e500`
### Surfaces & Backgrounds
- **Canvas** (canvas): `#181818` — near-black
- **Canvas Elevated** (canvas-elevated): `#303030`
- **Canvas Light** (canvas-light): `#ffffff` — pure/near-white
- **Surface Card** (surface-card): `#303030`
- **Surface Soft Light** (surface-soft-light): `#f7f7f7` — pure/near-white
- **Surface Strong Light** (surface-strong-light): `#ebebeb`
### Text & Ink
- **Ink** (ink): `#ffffff` — pure/near-white
- **Body** (body): `#969696`
- **Body Strong** (body-strong): `#ffffff` — pure/near-white
- **Body On Light** (body-on-light): `#181818` — near-black
- **Muted** (muted): `#666666`
- **Muted Soft** (muted-soft): `#8f8f8f`
- **Hairline On Light** (hairline-on-light): `#d2d2d2`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
- **On Light** (on-light): `#181818` — near-black
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#303030`
- **Hairline Soft** (hairline-soft): `#ebebeb`
### Semantic & Status
- **Semantic Info** (semantic-info): `#4c98b9`
- **Semantic Success** (semantic-success): `#03904a` — green tint
- **Semantic Warning** (semantic-warning): `#f13a2c` — warm red/orange tint

## 3. Typography Rules

### Font Family
- **Primary:** `'FerrariSans', -apple-system, system-ui, sans-serif`

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-mega | 'FerrariSans', -apple-system, system-ui, sans-serif | 80px | 500 | 1.05 | -1.6px |  |
| display-xl | 'FerrariSans', sans-serif | 56px | 500 | 1.1 | -1.12px |  |
| display-lg | 'FerrariSans', sans-serif | 36px | 500 | 1.2 | -0.36px |  |
| display-md | 'FerrariSans', sans-serif | 26px | 500 | 1.5 | 0.195px |  |
| title-md | 'FerrariSans', sans-serif | 18px | 700 | 1.2 | 0 |  |
| title-sm | 'FerrariSans', sans-serif | 16px | 500 | 1.4 | 0.08px |  |
| body-md | 'FerrariSans', sans-serif | 14px | 400 | 1.5 | 0 |  |
| body-sm | 'FerrariSans', sans-serif | 13px | 400 | 1.5 | 0 |  |
| caption | 'FerrariSans', sans-serif | 12px | 400 | 1.4 | 0 |  |
| caption-uppercase | 'FerrariSans', sans-serif | 11px | 600 | 1.4 | 1.1px | uppercase |
| button | 'FerrariSans', sans-serif | 14px | 700 | 1.0 | 1.4px | uppercase |
| nav-link | 'FerrariSans', sans-serif | 13px | 600 | 1.4 | 0.65px | uppercase |
| number-display | 'FerrariSans', sans-serif | 80px | 700 | 1.0 | -1.6px |  |


## 4. Component Stylings

### top-nav-on-dark

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.nav-link}
- **height:** 64px

### top-nav-on-light

- **backgroundColor:** {colors.canvas-light}
- **textColor:** {colors.body-on-light}
- **typography:** {typography.nav-link}
- **height:** 64px

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.none}
- **padding:** 14px 32px
- **height:** 48px

### button-primary-active

- **backgroundColor:** {colors.primary-active}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.none}

### button-outline-on-dark

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.none}
- **padding:** 13px 31px
- **height:** 48px

### button-outline-on-light

- **backgroundColor:** transparent
- **textColor:** {colors.body-on-light}
- **typography:** {typography.button}
- **rounded:** {rounded.none}
- **padding:** 13px 31px
- **height:** 48px

### button-tertiary-text

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.button}

### hero-band-cinema

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.display-mega}
- **padding:** 0

### hero-band-light

- **backgroundColor:** {colors.canvas-light}
- **textColor:** {colors.body-on-light}
- **typography:** {typography.display-xl}
- **padding:** 96px

### feature-card-photo

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.none}
- **padding:** 0

### feature-card-light

- **backgroundColor:** {colors.canvas-light}
- **textColor:** {colors.body-on-light}
- **typography:** {typography.title-md}
- **rounded:** {rounded.none}
- **padding:** 32px

### livery-band

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.ink}
- **typography:** {typography.display-lg}
- **padding:** 96px

### preowned-listing-card

- **backgroundColor:** {colors.canvas-light}
- **textColor:** {colors.body-on-light}
- **typography:** {typography.body-md}
- **rounded:** {rounded.none}
- **padding:** 24px

### spec-cell

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.number-display}
- **padding:** 24px 0

### race-position-cell

- **backgroundColor:** transparent
- **textColor:** {colors.primary}
- **typography:** {typography.number-display}

### race-calendar-row

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **padding:** 16px 0

### driver-card

- **backgroundColor:** {colors.canvas-elevated}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.none}
- **padding:** 24px

### text-input-on-dark

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.sm}
- **padding:** 14px 16px
- **height:** 48px

### text-input-on-light

- **backgroundColor:** {colors.canvas-light}
- **textColor:** {colors.body-on-light}
- **typography:** {typography.body-md}
- **rounded:** {rounded.sm}
- **padding:** 14px 16px
- **height:** 48px

### badge-pill

- **backgroundColor:** {colors.canvas-elevated}
- **textColor:** {colors.ink}
- **typography:** {typography.caption-uppercase}
- **rounded:** {rounded.full}
- **padding:** 4px 12px

### cta-band-dark

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.display-lg}
- **padding:** 96px

### newsletter-input-band

- **backgroundColor:** {colors.canvas-elevated}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.sm}
- **padding:** 32px

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
| `xs` | 2px |
| `sm` | 4px |
| `md` | 6px |
| `lg` | 8px |
| `xl` | 12px |
| `full` | 9999px |

**Spacing Scale**

| Token | Value |
|---|---|
| `xxxs` | 4px |
| `xxs` | 8px |
| `xs` | 16px |
| `sm` | 24px |
| `md` | 32px |
| `lg` | 48px |
| `xl` | 64px |
| `xxl` | 96px |
| `super` | 128px |


## 6. Layout Principles


### Grid & Container

- Max content width: ~1280px on editorial bands. Hero photography goes full-bleed.
- Editorial body: 12-column grid.
- Feature card grids: 2-up at desktop for hero splits, 3-up for benefit grids, 4-up for preowned listing tiles.
- Footer: 5-column at desktop.
- Feature card grid: 4-up → 3-up → 2-up → 1-up.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat (canvas) | `{colors.canvas}` (#181818) | Body bands, footer |
| Card | `{colors.canvas-elevated}` (#303030) | Driver cards, livery plates |
| Light band | `{colors.canvas-light}` (#ffffff) | Preowned listings, pricing |
| Hairline border | 1px `{colors.hairline}` or `{colors.hairline-on-light}` | Card outlines, dividers |
| Soft drop | `0 4px 8px rgba(0,0,0,0.1)` | Hovered cards (single shadow tier) |
| Photographic | Full-bleed cinema imagery | Hero band, livery photographs |


## 8. Do's and Don'ts

### Do
- Reserve `{colors.primary}` (Rosso Corsa) for primary CTAs, the Cavallino mark, and F1 race-position highlights.
- Set every CTA at `{rounded.none}` (0px sharp corners) — the brand's signature precision.
- Render CTA labels in uppercase with 1.4px tracking via `{typography.button}`.
- Pair every hero with a full-bleed cinematic photograph — the photograph IS the depth.
- Use the explicit 8px spacing ladder (`xxxs` through `super`) rather than ad-hoc px values.
- Keep display weight at 500 — never bold.

### Don't
- Don't introduce a saturated brand color other than Rosso Corsa.
- Don't use rounded or pill CTAs — sharp 0px corners are the brand button.
- Don't bold display copy. The cinematic photography does the visual heavy-lifting.
- Don't use Hypersail yellow outside the Hypersail sailing program context.
- Don't use pure black canvas. The brand canvas is `{colors.canvas}` (#181818) — slightly warm.
- Don't add drop shadow tiers. Photography + brightness-step elevation carry the depth.
- Don't extract a CTA color from a third-party widget (cookie consent, OneTrust). The brand's CTA color is what appears on actual product CTAs, not on injected modals.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 640px | Hero photograph crops vertically; hero h1 80→32px; feature card grid 1-up; nav hamburger; preowned listing 1-up. |
| Tablet | 640–1024px | Hero h1 56px; feature card grid 2-up; preowned listing 2-up. |
| Desktop | 1024–1280px | Full hero h1 80px; feature card grid 3-up; preowned listing 4-up. |
| Wide | > 1280px | Editorial body content caps at 1280px; hero photography continues full-bleed. |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#da291c`
- Background / Canvas: `#181818`
- Heading / Strong text: `#ffffff`
- Body / Secondary text: `#969696`
- Primary Active: `#b01e0a`
- Primary Hover: `#9d2211`
- Body Strong: `#ffffff`
- Body On Light: `#181818`
- Muted: `#666666`
- Muted Soft: `#8f8f8f`

### Example Component Prompts

- "Create a hero on the canvas background (`#181818`). Headline at 80px using the display font, weight 500, line-height 1.05, color `#ffffff` with fallback Google Font. Primary CTA uses `#da291c` background, white text, 6px radius, and comfortable padding."
- "Design a content card: `#303030` background, 1px `#303030` border, `8px` radius, padding `48px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

