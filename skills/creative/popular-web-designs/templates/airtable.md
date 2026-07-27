# Design System: Airtable

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `airtable/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/airtable.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `Haas Groot Disp` → **Fallback:** `Inter`
> - **Mono:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Airtable's marketing surfaces are quietly editorial. The base atmosphere is white canvas, dark ink type, generous whitespace, and a near-black pill CTA — nothing is fighting for attention until a section needs to. The brand voltage doesn't come from gradient washes or accent walls; it comes from **full-bleed signature cards** in `{colors.signature-coral}`, `{colors.signature-forest}`, and `{colors.surface-dark}` that punctuate long-scroll explainer pages every two or three screens. Between those signature bands, the page reads like a print magazine: a headline, supporting copy, a small image cluster, then breathing room.

Type voice is Haas Grotesk at modest weights (400 for display, 500 for sub-titles and buttons). Display headlines never go bolder than 500 — emphasis comes from size and color contrast, not from weight. Body copy stays at 14px / 400 throughout. The pricing surface runs its own dialect: **Inter Display** at unusual mid-weights (475 / 575) and **pill-shaped buttons** (`{rounded.pill}`) that don't appear on any other page — a deliberate sub-system signaling "this page is about commercial precision."

**Key Characteristics:**
- Primary CTA is `{colors.primary}` (near-black ink) with white text and a `{rounded.lg}` (12px) corner — it reads as confident and final, never decorative.
- Secondary CTA is a `{colors.canvas}` button with `{colors.ink}` text and a hairline outline. The two together form Airtable's signature button pair.
- Hero is white canvas. There is no atmospheric gradient, no mesh, no background flourish. The brand strength comes from the type and the buttons sitting in clean whitespace.
- Brand voltage lives in **signature surface cards**: `{colors.signature-coral}`, `{colors.signature-forest}`, and `{colors.surface-dark}` carry full-bleed product callouts every few screens.
- Demo-card grids carry product UI fragments on `{colors.signature-peach}`, `{colors.signature-mint}`, `{colors.signature-cream}` and other warm pastel surfaces.
- Section rhythm: white canvas → coral signature card → white body → cream callout band → dark navy CTA → light gray CTA banner → footer. The canvas resets between every signature surface.
- Border radius is hierarchical: `{rounded.lg}` (12px) for primary CTAs and large signature cards, `{rounded.md}` (10px) for content cards and demo grids, `{rounded.sm}` (6px) for inputs, `{rounded.full}` for icon buttons. Pricing buttons jump to `{rounded.pill}` to mark themselves as a separate dialect.
- Vertical rhythm is `{spacing.section}` (96px) between major bands — universal across every page.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#181d26` — near-black
- **Primary Active** (primary-active): `#0d1218` — near-black
- **On Primary** (on-primary): `#ffffff` — pure/near-white
### Surfaces & Backgrounds
- **Canvas** (canvas): `#ffffff` — pure/near-white
- **Surface Soft** (surface-soft): `#f8fafc` — pure/near-white
- **Surface Strong** (surface-strong): `#e0e2e6`
- **Surface Dark** (surface-dark): `#181d26` — near-black
- **Surface Dark Elevated** (surface-dark-elevated): `#1d1f25` — near-black
### Text & Ink
- **Ink** (ink): `#181d26` — near-black
- **Body** (body): `#333840`
- **Muted** (muted): `#41454d`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
- **Link** (link): `#1b61c9` — cool blue tint
- **Link Active** (link-active): `#1a3866` — cool blue tint
- **Pricing Ink** (pricing-ink): `#1d1f25` — near-black
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#dddddd`
- **Border Strong** (border-strong): `#9297a0`
- **Info Border** (info-border): `#458fff` — cool blue tint
- **Success Border** (success-border): `#39bf45` — green tint
### Semantic & Status
- **Info** (info): `#254fad` — cool blue tint
- **Success** (success): `#006400` — green tint
### Accent / Other
- **Signature Coral** (signature-coral): `#aa2d00` — warm red/orange tint
- **Signature Forest** (signature-forest): `#0a2e0e`
- **Signature Cream** (signature-cream): `#f5e9d4`
- **Signature Peach** (signature-peach): `#fcab79` — warm red/orange tint
- **Signature Mint** (signature-mint): `#a8d8c4`
- **Signature Yellow** (signature-yellow): `#f4d35e`
- **Signature Mustard** (signature-mustard): `#d9a441` — warm red/orange tint

## 3. Typography Rules

### Font Family
- **Primary:** `Haas Groot Disp, Haas, sans-serif`

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-xl | Haas Groot Disp, Haas, sans-serif | 48px | 500 | 1.1 | 0 |  |
| display-lg | Haas Groot Disp, Haas, sans-serif | 40px | 400 | 1.2 | 0 |  |
| display-md | Haas Groot Disp, Haas, sans-serif | 32px | 400 | 1.2 | 0 |  |
| title-lg | Haas, sans-serif | 24px | 400 | 1.35 | 0.12px |  |
| title-md | Haas Groot Disp, Haas, sans-serif | 20px | 400 | 1.5 | 0 |  |
| title-sm | Haas, sans-serif | 18px | 500 | 1.4 | 0 |  |
| label-md | Haas, sans-serif | 16px | 500 | 1.4 | 0 |  |
| button | Haas, sans-serif | 16px | 500 | 1.4 | 0 |  |
| body-md | Haas, sans-serif | 14px | 400 | 1.25 | 0 |  |
| caption | Haas, sans-serif | 14px | 500 | 1.35 | 0.16px |  |
| legal | Haas, sans-serif | 13.12px | 600 | 1.2 | 0 |  |
| pricing-display | Inter Display, system-ui, sans-serif | 44.8px | 475 | 1.1 | 0 |  |
| pricing-section | Inter Display, system-ui, sans-serif | 28px | 475 | 1.2 | 0 |  |
| pricing-card-title | Inter Display, system-ui, sans-serif | 20px | 475 | 1.3 | 0 |  |


## 4. Component Stylings

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.lg}
- **padding:** 16px 24px

### button-primary-active

- **backgroundColor:** {colors.primary-active}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.lg}

### button-secondary

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.lg}
- **padding:** 16px 24px

### button-secondary-on-dark

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.lg}
- **padding:** 16px 24px

### button-legal

- **backgroundColor:** {colors.link}
- **textColor:** {colors.on-primary}
- **typography:** {typography.legal}
- **rounded:** {rounded.xs}
- **padding:** 12px 10px

### button-icon-circular

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **rounded:** {rounded.full}
- **size:** 40px

### button-pricing-pill

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.pricing-ink}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 12px 24px

### text-link

- **backgroundColor:** transparent
- **textColor:** {colors.link}
- **typography:** {typography.body-md}

### top-nav

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **height:** 64px

### hero-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.display-lg}
- **padding:** 96px

### signature-coral-card

- **backgroundColor:** {colors.signature-coral}
- **textColor:** {colors.on-primary}
- **typography:** {typography.display-md}
- **rounded:** {rounded.lg}
- **padding:** 48px

### signature-forest-card

- **backgroundColor:** {colors.signature-forest}
- **textColor:** {colors.on-primary}
- **typography:** {typography.display-md}
- **rounded:** {rounded.lg}
- **padding:** 48px

### hero-card-dark

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-md}
- **rounded:** {rounded.lg}
- **padding:** 48px

### feature-card-tabbed

- **backgroundColor:** {colors.surface-soft}
- **textColor:** {colors.ink}
- **typography:** {typography.title-lg}
- **rounded:** {rounded.lg}
- **padding:** 32px

### cream-callout-card

- **backgroundColor:** {colors.signature-cream}
- **textColor:** {colors.ink}
- **typography:** {typography.title-lg}
- **rounded:** {rounded.md}
- **padding:** 24px

### demo-grid-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.label-md}
- **rounded:** {rounded.md}
- **padding:** 16px

### logo-strip

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.muted}
- **typography:** {typography.body-md}
- **padding:** 32px

### article-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.title-sm}
- **rounded:** {rounded.md}
- **padding:** 16px

### topic-filter-rail

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.body}
- **typography:** {typography.body-md}
- **width:** 240px

### text-input

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.sm}
- **padding:** 12px 16px
- **height:** 44px

### text-input-focus

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **rounded:** {rounded.sm}

### pricing-tier-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.pricing-ink}
- **typography:** {typography.pricing-card-title}
- **rounded:** {rounded.md}
- **padding:** 32px

### pricing-tier-card-featured

- **backgroundColor:** {colors.surface-soft}
- **textColor:** {colors.pricing-ink}
- **typography:** {typography.pricing-card-title}
- **rounded:** {rounded.md}
- **padding:** 32px

### pricing-comparison-row

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.body}
- **typography:** {typography.body-md}
- **padding:** 12px

### cta-band-light

- **backgroundColor:** {colors.surface-strong}
- **textColor:** {colors.ink}
- **typography:** {typography.display-md}
- **rounded:** {rounded.lg}
- **padding:** 48px

### footer

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.body}
- **typography:** {typography.body-md}
- **padding:** 64px


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
| `xs` | 2px |
| `sm` | 6px |
| `md` | 10px |
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

- Demo-card grids carry product UI fragments on `{colors.signature-peach}`, `{colors.signature-mint}`, `{colors.signature-cream}` and other warm pastel surfaces.
- Border radius is hierarchical: `{rounded.lg}` (12px) for primary CTAs and large signature cards, `{rounded.md}` (10px) for content cards and demo grids, `{rounded.sm}` (6px) for inputs, `{rounded.full}` for icon buttons. Pricing buttons jump to `{rounded.pill}` to mark themselves as a separate dialect.
- **Forest** (`{colors.signature-forest}` — #0a2e0e): A deep-green signature card used in the homepage demo-grid cluster.
- **Peach** (`{colors.signature-peach}` — #fcab79), **Mint** (`{colors.signature-mint}` — #a8d8c4), **Yellow** (`{colors.signature-yellow}` — #f4d35e), **Mustard** (`{colors.signature-mustard}` — #d9a441): Demo-card surfaces that carry small product UI fragments inside the multi-card grid sections.
- **Card internal padding:** `{spacing.xl}` (32px) for tabbed feature cards and pricing tier cards; `{spacing.xxl}` (48px) inside signature coral / forest / dark cards; `{spacing.lg}` (24px) for cream callouts and demo-grid cards.
- **Gutters:** `{spacing.lg}` (24px) between cards in 3-up grids; `{spacing.md}` (16px) inside denser logo strips and footer column gutters.
- **Max content width:** ~1280px centered, with `{spacing.xxl}` (48px) horizontal breathing room.
- **Editorial body:** Single 8/12-column at large breakpoints, collapsing to single-column on mobile.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Body sections, top nav, footer |
| Soft hairline | 1px `{colors.hairline}` border | Inputs, sub-nav rails, comparison-table dividers, secondary buttons |
| Button rest | Soft drop with subtle blue-tinted glow at low alpha | Primary CTA buttons (the blue tint is a holdover from the link color and reads as a faint accent under the dark button) |
| Button focus | Outer 2px blue ring at higher alpha | Keyboard focus state on primary buttons |
| Card flat | No shadow; relies on color contrast against the surface band | Signature coral / forest / dark cards, cream callouts, demo-grid cards |

The elevation philosophy is **color-block first, shadow second**. Shadows are minimal; depth is delegated to the contrast between white canvas and signature surface cards. There is no soft-glow / atmospheric-shadow / heavy-elevation language anywhere in the marketing system.


## 8. Do's and Don'ts

### Do
- Keep `{component.button-primary}` near-black. The brand's primary CTA is `{colors.primary}`, not the link blue. Mixing them up turns a confident hero into a confused one.
- Reserve `{component.button-primary}` for one primary action per viewport. The system is designed for scarcity at the brand-action layer.
- Use `{component.button-secondary}` (white with hairline outline) as the natural pair with `{component.button-primary}`. The two together form Airtable's signature button row.
- Trust whitespace as the hero atmosphere. Hero bands are intentionally calm — no gradient, no mesh, no atmospheric backdrop. Going against this reads as off-brand.
- Use `{component.signature-coral-card}`, `{component.signature-forest-card}`, and `{component.hero-card-dark}` to break editorial monotony. These are the brand's voltage moments.
- Keep `{component.demo-grid-card}` heights uneven within a grid. Uniform heights feel like a spec sheet.
- Treat the pricing surface as its own dialect: keep `{typography.pricing-display}`, `{typography.pricing-card-title}`, and `{component.button-pricing-pill}` together. Mixing them with Haas Grotesk button type breaks the sub-system's voice.
- Anchor every editorial band with `{spacing.section}` (96px) vertical padding.

### Don't
- Don't make `{colors.link}` (#1b61c9) the primary button color. It is the link color. The primary button is `{colors.primary}` (#181d26, near-black). Treating link-blue as the brand action is the most common mistake when reading Airtable's CSS variables.
- Don't add a gradient backdrop to the hero. Airtable's hero is white, full stop. Mesh, aurora, spotlight gradients all read as "another SaaS template" — not Airtable.
- Don't bold display-weight type. `{typography.display-xl}` and `{typography.display-lg}` are intentionally weight 400 / 500 — going to 700 reads as marketing-page-template.
- Don't use `{rounded.pill}` outside the pricing surface. It's a sub-system signal, not a general radius option.
- Don't repeat the same surface mode in two consecutive bands. The editorial pacing depends on rhythm: white → signature card → white → cream → dark → white. Two whites in a row read as a typography blog.
- Don't add hover state styling beyond what the system already encodes. The system documents Default and Active/Pressed only.
- Don't introduce additional accent colors beyond the documented signature card palette. The system's voltage already uses coral, forest, dark navy, cream, peach, mint, yellow, and mustard.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 768px | Single-column body; top nav collapses to hamburger; demo-grid drops to 1-up; signature cards stay full-bleed; logo strip wraps to 2 rows; footer collapses to single-column |
| Tablet | 768–1024px | 2-up demo-grid; top nav stays horizontal but tightens; cream-callout cards stack 2-up; pricing comparison table becomes horizontally scrollable |
| Desktop | 1024–1440px | 3-up demo-grid (and 4-up for tighter content); full top-nav with all menu items visible; pricing tier cards render 4-across |
| Wide | > 1440px | Same as Desktop with more outer breathing room; max content width caps at ~1280px and the page adds outer margin rather than scaling type up |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#181d26`
- Background / Canvas: `#ffffff`
- Heading / Strong text: `#181d26`
- Body / Secondary text: `#333840`
- Primary Active: `#0d1218`
- Muted: `#41454d`
- Hairline: `#dddddd`
- Border Strong: `#9297a0`
- Surface Soft: `#f8fafc`
- Surface Strong: `#e0e2e6`

### Example Component Prompts

- "Create a hero on the canvas background (`#ffffff`). Headline at 48px using the display font, weight 500, line-height 1.1, color `#181d26` with fallback Google Font. Primary CTA uses `#181d26` background, white text, 10px radius, and comfortable padding."
- "Design a content card: `#ffffff` background, 1px `#dddddd` border, `12px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

