# Design System: Clickhouse

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `clickhouse/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/clickhouse.md")`.  
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

ClickHouse's marketing surface is the highest-contrast interface in the database / data-platform category. The base atmosphere is **near-pure black canvas** (`{colors.canvas}` — #0a0a0a) with **electric yellow** (`{colors.primary}` — #faff69) as the singular brand voltage. The yellow handles every primary CTA, every stat-callout number, every "GET STARTED" badge — used scarcely on individual elements but generously on full-bleed yellow CTA cards. White typography in confident weight-700 sans-serif anchors the editorial body.

The yellow + black pairing is what makes ClickHouse instantly recognizable. Where Snowflake uses cool blue gradients and Databricks uses red + slate, ClickHouse leans hard into one electric yellow that does all the brand work. Code blocks, terminal output, and product UI fragments embed directly in dark `{colors.surface-card}` (#1a1a1a) cards across every page.

Type voice runs **Inter** at confident weights — 700 for display headlines (with negative letter-spacing -1 to -2.5px), 600 for sub-titles and buttons, 400 for body. The system has no display-serif counter-voice; everything is one geometric humanist sans, scaled and weighted for hierarchy.

**Key Characteristics:**
- Near-pure black canvas (`{colors.canvas}` — #0a0a0a) with white type. The system has no light-mode marketing surface.
- Electric yellow primary (`{colors.primary}` — #faff69). Used on primary CTAs, large stat-callout numbers ("2.8k+", "74k+"), and full-bleed yellow CTA bands.
- Inter at weight 700 for display, weight 600 for sub-titles + buttons, weight 400 for body. No serif counterpoint.
- Dark surface cards (`{colors.surface-card}` — #1a1a1a) for feature cards, code windows, and product mockups. Cards barely lighter than canvas — color-block contrast is subtle.
- Code blocks render in JetBrains Mono inside `{colors.surface-card}`. SQL syntax-highlighted in muted blues / yellows / grays.
- Stat numbers in yellow + sans-700 + huge size carry the credibility moment ("779+", "2.8k+", "47k+" community / contributor / star counts).
- Border radius is hierarchical: `{rounded.md}` (8px) for buttons, `{rounded.lg}` (12px) for content cards. No pill except in tag badges.
- Section rhythm `{spacing.section}` (96px) between major editorial bands.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#faff69` — green tint
- **Primary Active** (primary-active): `#e6eb52` — green tint
- **Primary Disabled** (primary-disabled): `#3a3a1f`
- **On Primary** (on-primary): `#0a0a0a` — near-black
- **Accent Emerald** (accent-emerald): `#22c55e` — green tint
- **Accent Rose** (accent-rose): `#ef4444` — warm red/orange tint
- **Accent Blue** (accent-blue): `#3b82f6` — cool blue tint
### Surfaces & Backgrounds
- **Canvas** (canvas): `#0a0a0a` — near-black
- **Surface Soft** (surface-soft): `#121212` — near-black
- **Surface Card** (surface-card): `#1a1a1a` — near-black
- **Surface Elevated** (surface-elevated): `#242424` — near-black
- **Surface Yellow Band** (surface-yellow-band): `#faff69` — green tint
### Text & Ink
- **Ink** (ink): `#ffffff` — pure/near-white
- **Body** (body): `#cccccc`
- **Body Strong** (body-strong): `#e6e6e6`
- **Muted** (muted): `#888888`
- **Muted Soft** (muted-soft): `#5a5a5a`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
- **On Yellow** (on-yellow): `#0a0a0a` — near-black
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#2a2a2a`
- **Hairline Strong** (hairline-strong): `#3a3a3a`
### Semantic & Status
- **Success** (success): `#22c55e` — green tint
- **Warning** (warning): `#f59e0b` — warm red/orange tint
- **Error** (error): `#ef4444` — warm red/orange tint

## 3. Typography Rules

### Font Family
- **Primary:** `Inter, sans-serif`
- **Monospace:** used for code/terminal surfaces.

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-xl | Inter, sans-serif | 72px | 700 | 1.05 | -2.5px |  |
| display-lg | Inter, sans-serif | 56px | 700 | 1.1 | -2px |  |
| display-md | Inter, sans-serif | 40px | 700 | 1.15 | -1.5px |  |
| display-sm | Inter, sans-serif | 32px | 700 | 1.2 | -1px |  |
| title-lg | Inter, sans-serif | 24px | 700 | 1.3 | -0.3px |  |
| title-md | Inter, sans-serif | 18px | 600 | 1.4 | 0 |  |
| title-sm | Inter, sans-serif | 16px | 600 | 1.4 | 0 |  |
| stat-display | Inter, sans-serif | 56px | 700 | 1.0 | -1.5px |  |
| body-md | Inter, sans-serif | 16px | 400 | 1.55 | 0 |  |
| body-sm | Inter, sans-serif | 14px | 400 | 1.55 | 0 |  |
| caption | Inter, sans-serif | 13px | 500 | 1.4 | 0 |  |
| caption-uppercase | Inter, sans-serif | 12px | 600 | 1.4 | 1.5px |  |
| code | JetBrains Mono, ui-monospace, monospace | 14px | 400 | 1.55 | 0 |  |
| button | Inter, sans-serif | 14px | 600 | 1 | 0 |  |
| nav-link | Inter, sans-serif | 14px | 500 | 1.4 | 0 |  |


## 4. Component Stylings

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 12px 20px
- **height:** 40px

### button-primary-active

- **backgroundColor:** {colors.primary-active}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.md}

### button-primary-disabled

- **backgroundColor:** {colors.primary-disabled}
- **textColor:** {colors.muted}
- **rounded:** {rounded.md}

### button-secondary

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 12px 20px
- **height:** 40px

### button-text-link

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.button}

### button-icon-circular

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.full}
- **size:** 36px

### text-link

- **backgroundColor:** transparent
- **textColor:** {colors.primary}
- **typography:** {typography.body-md}

### top-nav

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.nav-link}
- **height:** 64px

### hero-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-xl}
- **padding:** 96px

### hero-stat-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.primary}
- **typography:** {typography.stat-display}

### feature-card-yellow

- **backgroundColor:** {colors.surface-yellow-band}
- **textColor:** {colors.on-yellow}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 32px

### feature-card-dark

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 32px

### code-window-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **typography:** {typography.code}
- **rounded:** {rounded.lg}
- **padding:** 24px

### product-mockup-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 24px

### pricing-tier-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-lg}
- **rounded:** {rounded.lg}
- **padding:** 32px

### pricing-tier-card-featured

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.title-lg}
- **rounded:** {rounded.lg}
- **padding:** 32px

### stat-callout

- **backgroundColor:** transparent
- **textColor:** {colors.primary}
- **typography:** {typography.stat-display}

### cta-band-yellow

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.display-md}
- **rounded:** {rounded.lg}
- **padding:** 64px

### text-input

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **typography:** {typography.body-md}
- **rounded:** {rounded.md}
- **padding:** 10px 14px
- **height:** 40px

### text-input-focused

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.md}

### category-tab

- **backgroundColor:** transparent
- **textColor:** {colors.muted}
- **typography:** {typography.nav-link}
- **rounded:** {rounded.md}
- **padding:** 8px 14px

### category-tab-active

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **typography:** {typography.nav-link}
- **rounded:** {rounded.md}

### badge-pill

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **typography:** {typography.caption}
- **rounded:** {rounded.pill}
- **padding:** 4px 12px

### badge-yellow

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.caption-uppercase}
- **rounded:** {rounded.pill}
- **padding:** 4px 12px

### events-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 24px

### customer-logo-strip

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.muted}
- **typography:** {typography.body-md}
- **padding:** 32px

### footer

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.muted}
- **typography:** {typography.body-sm}
- **padding:** 64px


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
| `xs` | 4px |
| `sm` | 6px |
| `md` | 8px |
| `lg` | 12px |
| `pill` | 9999px |
| `full` | 9999px |

**Spacing Scale**

| Token | Value |
|---|---|
| `xxs` | 4px |
| `xs` | 8px |
| `sm` | 12px |
| `md` | 16px |
| `lg` | 24px |
| `xl` | 32px |
| `xxl` | 48px |
| `section` | 96px |


## 6. Layout Principles

- **Section rhythm:** `96px` vertical padding between major bands.

### Grid & Container

- **Max content width:** ~1280px centered.
- **Editorial body:** Single 12-column grid; hero often uses 7/5 split (h1 left, code mockup right).
- **Feature card grids:** 3-up at desktop, 2-up at tablet, 1-up at mobile.
- **Pricing grid:** 3-4 up at desktop, 1-up at mobile.
- Hero 7-5 grid → single-column on mobile.
- Feature card grids reduce columns rather than scaling.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Body sections, top nav, hero |
| Soft hairline | 1px `{colors.hairline}` border | Code-window cards, content cards |
| Surface card | `{colors.surface-card}` background — no shadow | Feature cards, pricing tiers, event cards |
| Yellow band | `{colors.primary}` background — no shadow | Full-bleed yellow CTA cards / bands |

The system uses no drop shadows. Depth comes from the contrast between black canvas and `{colors.surface-card}` (a barely-lighter-than-canvas tone) — the contrast is subtle, more like an "engineering-grade dim panel" than an "elevated card."


## 8. Do's and Don'ts

### Do
- Anchor every page on the black canvas. The yellow + black pairing is the brand voltage.
- Reserve `{colors.primary}` (yellow) for primary CTAs, stat-callout numbers, and full-bleed yellow CTA bands. The yellow's scarcity at the element level + abundance at the band level is what makes it powerful.
- Use Inter at weight 700 for every display headline, with -1 to -2.5px letter-spacing.
- Show actual SQL code blocks inside `{component.code-window-card}` — ClickHouse is a database; show the query, don't paint marketing illustrations of queries.
- Use `{component.stat-callout}` numbers to establish credibility (community size, contributors, performance benchmarks). The yellow stat numbers are signature.
- Anchor every band with `{spacing.section}` (96px) vertical rhythm.

### Don't
- Don't introduce a second brand color. ClickHouse is monochromatic + yellow.
- Don't bold display weight beyond 700 or use weight 500 for headlines. The hierarchy depends on size, not on weight gradation.
- Don't use yellow for body text or large surface fills outside of intentional yellow cards.
- Don't use rounded buttons / pills outside of small badges. The standard button radius is 8px (md).
- Don't repeat the same surface mode in two consecutive bands. Black canvas → dark feature card → yellow CTA card → black canvas → code-window card.
- Don't replace SQL code mockups with abstract illustrations. The code IS the marketing voltage.
- Don't add hover state styling beyond what the system already encodes.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 768px | Hamburger nav; hero h1 72→36px; code-window-card stacks below; feature grids 1-up; pricing 1-up |
| Tablet | 768–1024px | Top nav tightens; feature cards 2-up; pricing 2-up |
| Desktop | 1024–1440px | Full top-nav; 3-up feature cards; 3-4 up pricing tiers |
| Wide | > 1440px | Same as desktop with more breathing room; max content 1280px |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#faff69`
- Background / Canvas: `#0a0a0a`
- Heading / Strong text: `#ffffff`
- Body / Secondary text: `#cccccc`
- Primary Active: `#e6eb52`
- Primary Disabled: `#3a3a1f`
- Body Strong: `#e6e6e6`
- Muted: `#888888`
- Muted Soft: `#5a5a5a`
- Hairline: `#2a2a2a`

### Example Component Prompts

- "Create a hero on the canvas background (`#0a0a0a`). Headline at 72px using the display font, weight 700, line-height 1.05, color `#ffffff` with fallback Google Font. Primary CTA uses `#faff69` background, white text, 8px radius, and comfortable padding."
- "Design a content card: `#1a1a1a` background, 1px `#2a2a2a` border, `12px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

