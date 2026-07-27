# Design System: Clay

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `clay/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/clay.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `Plain Black` → **Fallback:** `Saira`
> - **Mono:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Saira', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Saira:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Clay.com is the most playful B2B SaaS interface in the GTM-data category. The base atmosphere is **cream-tinted white canvas** (`{colors.canvas}` — #fffaf0) holding dark-navy ink type and **3D-rendered claymation illustrations** (mountains, mascot characters, peach/ochre/lavender landscapes) as the dominant brand voltage. Where most data-platform brands play it cool with grids and gradients, Clay leans hard into hand-crafted-looking 3D illustrations and saturated single-color feature cards.

Type voice runs **Plain Black** (or substituted with Inter weight 500-600) — a custom rounded display face used at very large sizes (72px hero) with negative letter-spacing. Body type uses Inter at standard weights. The display weight stays at 500, never bolder — the rounded character of the typeface gives it warmth without needing weight.

Component voltage comes from **saturated single-color feature cards** in a 6-color palette: hot pink, deep teal, lavender, peach, ochre, and cream-card. Each card shows product UI fragments at small scale — Claygent agent runs, sequencer flows, CRM enrichment outputs. The colored card IS the primary visual element on every long-scroll page.

**Key Characteristics:**
- Cream-tinted white canvas (`{colors.canvas}` — #fffaf0). The warmth differentiates Clay from cool-gray competitor sites.
- Dark navy/black primary CTAs (`{colors.primary}` — #0a0a0a). Buttons rounded `{rounded.md}` (12px) — friendly modern but not pill.
- 6-color saturated feature card palette: `{colors.brand-pink}`, `{colors.brand-teal}`, `{colors.brand-lavender}`, `{colors.brand-peach}`, `{colors.brand-ochre}`, `{colors.surface-card}` (cream).
- 3D claymation illustrations (mountains, characters, abstract shapes) as full-bleed hero artifacts — the brand's most-recognized visual element.
- Custom rounded Plain Black display typeface at 500 weight with -1 to -2.5px letter-spacing on display sizes.
- Border radius is generous: `{rounded.md}` (12px) for buttons + inputs, `{rounded.lg}` (16px) for content cards, `{rounded.xl}` (24px) for feature cards. The bigger radius matches the rounded display type's character.
- Product UI fragments embedded inside colored cards at small scale — agent run logs, sequencer flows, enrichment results.
- Section rhythm `{spacing.section}` (96px) between major bands.
- Footer is cream-tinted (`{colors.surface-soft}`) — Clay does NOT use a dark footer. Even the closing band stays warm-light.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#0a0a0a` — near-black
- **Primary Active** (primary-active): `#1f1f1f` — near-black
- **Primary Disabled** (primary-disabled): `#e5e5e5`
- **On Primary** (on-primary): `#ffffff` — pure/near-white
- **Brand Pink** (brand-pink): `#ff4d8b` — warm red/orange tint
- **Brand Teal** (brand-teal): `#1a3a3a`
- **Brand Lavender** (brand-lavender): `#b8a4ed` — cool blue tint
- **Brand Peach** (brand-peach): `#ffb084` — warm red/orange tint
- **Brand Ochre** (brand-ochre): `#e8b94a` — warm red/orange tint
- **Brand Mint** (brand-mint): `#a4d4c5`
- **Brand Coral** (brand-coral): `#ff6b5a` — warm red/orange tint
### Surfaces & Backgrounds
- **Canvas** (canvas): `#fffaf0`
- **Surface Soft** (surface-soft): `#faf5e8`
- **Surface Card** (surface-card): `#f5f0e0`
- **Surface Strong** (surface-strong): `#ebe6d6`
- **Surface Dark** (surface-dark): `#0a1a1a` — near-black
- **Surface Dark Elevated** (surface-dark-elevated): `#1a2a2a`
### Text & Ink
- **Ink** (ink): `#0a0a0a` — near-black
- **Body** (body): `#3a3a3a`
- **Body Strong** (body-strong): `#1a1a1a` — near-black
- **Muted** (muted): `#6a6a6a`
- **Muted Soft** (muted-soft): `#9a9a9a`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
- **On Dark Soft** (on-dark-soft): `#a0a0a0`
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#e5e5e5`
- **Hairline Soft** (hairline-soft): `#f0f0f0`
### Semantic & Status
- **Success** (success): `#22c55e` — green tint
- **Warning** (warning): `#f59e0b` — warm red/orange tint
- **Error** (error): `#ef4444` — warm red/orange tint

## 3. Typography Rules

### Font Family
- **Primary:** `Plain Black, Inter, sans-serif`

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-xl | Plain Black, Inter, sans-serif | 72px | 500 | 1 | -2.5px |  |
| display-lg | Plain Black, Inter, sans-serif | 56px | 500 | 1.05 | -2px |  |
| display-md | Plain Black, Inter, sans-serif | 40px | 500 | 1.1 | -1px |  |
| display-sm | Plain Black, Inter, sans-serif | 32px | 500 | 1.15 | -0.5px |  |
| title-lg | Inter, sans-serif | 24px | 600 | 1.3 | -0.3px |  |
| title-md | Inter, sans-serif | 18px | 600 | 1.4 | 0 |  |
| title-sm | Inter, sans-serif | 16px | 600 | 1.4 | 0 |  |
| body-md | Inter, sans-serif | 16px | 400 | 1.55 | 0 |  |
| body-sm | Inter, sans-serif | 14px | 400 | 1.55 | 0 |  |
| caption | Inter, sans-serif | 13px | 500 | 1.4 | 0 |  |
| caption-uppercase | Inter, sans-serif | 12px | 600 | 1.4 | 1.5px |  |
| button | Inter, sans-serif | 14px | 600 | 1 | 0 |  |
| nav-link | Inter, sans-serif | 14px | 500 | 1.4 | 0 |  |


## 4. Component Stylings

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 12px 20px
- **height:** 44px

### button-primary-active

- **backgroundColor:** {colors.primary-active}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.md}

### button-primary-disabled

- **backgroundColor:** {colors.primary-disabled}
- **textColor:** {colors.muted}
- **rounded:** {rounded.md}

### button-secondary

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 12px 20px
- **height:** 44px

### button-on-color

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 12px 20px
- **height:** 44px

### button-text-link

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.button}

### text-link

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}

### top-nav

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.nav-link}
- **height:** 64px

### hero-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.display-xl}
- **padding:** 96px

### hero-illustration-card

- **backgroundColor:** {colors.surface-soft}
- **textColor:** {colors.ink}
- **rounded:** {rounded.xl}

### feature-card-pink

- **backgroundColor:** {colors.brand-pink}
- **textColor:** {colors.on-primary}
- **typography:** {typography.title-md}
- **rounded:** {rounded.xl}
- **padding:** 32px

### feature-card-teal

- **backgroundColor:** {colors.brand-teal}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **rounded:** {rounded.xl}
- **padding:** 32px

### feature-card-lavender

- **backgroundColor:** {colors.brand-lavender}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.xl}
- **padding:** 32px

### feature-card-peach

- **backgroundColor:** {colors.brand-peach}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.xl}
- **padding:** 32px

### feature-card-ochre

- **backgroundColor:** {colors.brand-ochre}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.xl}
- **padding:** 32px

### feature-card-cream

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.xl}
- **padding:** 32px

### product-mockup-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 24px

### testimonial-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.lg}
- **padding:** 24px

### pricing-tier-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.title-lg}
- **rounded:** {rounded.lg}
- **padding:** 32px

### pricing-tier-card-featured

- **backgroundColor:** {colors.brand-teal}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-lg}
- **rounded:** {rounded.lg}
- **padding:** 32px

### text-input

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.md}
- **padding:** 12px 16px
- **height:** 44px

### text-input-focused

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **rounded:** {rounded.md}

### category-tab

- **backgroundColor:** transparent
- **textColor:** {colors.muted}
- **typography:** {typography.nav-link}
- **rounded:** {rounded.pill}
- **padding:** 8px 16px

### category-tab-active

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.nav-link}
- **rounded:** {rounded.pill}

### badge-pill

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.caption}
- **rounded:** {rounded.pill}
- **padding:** 4px 12px

### expert-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 24px

### cta-band-illustrated

- **backgroundColor:** {colors.surface-soft}
- **textColor:** {colors.ink}
- **typography:** {typography.display-md}
- **rounded:** {rounded.xl}
- **padding:** 80px

### footer

- **backgroundColor:** {colors.surface-soft}
- **textColor:** {colors.body}
- **typography:** {typography.body-sm}
- **padding:** 80px


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
| `xs` | 6px |
| `sm` | 8px |
| `md` | 12px |
| `lg` | 16px |
| `xl` | 24px |
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
- **Editorial body:** Single 12-column grid; hero often uses 7/5 split (h1 left, illustration right).
- **Feature card grids:** 3-up at desktop, 2-up at tablet, 1-up at mobile.
- **Pricing grid:** 3-4 up at desktop, 1-up at mobile.
- Hero 7-5 grid → single-column on mobile.
- Feature card grids reduce columns rather than scaling.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Body sections, top nav, hero |
| Soft hairline | 1px `{colors.hairline}` border | Inputs, small content cards |
| Saturated card | Brand pink/teal/lavender/peach/ochre fill — no shadow | Feature cards |
| Cream card | `{colors.surface-card}` background — no shadow | Testimonial, secondary cards |
| Subtle drop shadow | Faint shadow at low alpha | Hover-elevated states (rare) |

The system uses no heavy shadows. Depth comes from the saturated color contrast between cream canvas and bright feature cards.


## 8. Do's and Don'ts

### Do
- Anchor every page on the cream canvas (`{colors.canvas}` — #fffaf0). The warm tint differentiates Clay from cool-gray data sites.
- Use 3D claymation illustrations as hero artifacts. Hand-crafted 3D characters and mountains ARE the brand.
- Cycle saturated feature cards across the page — pink → teal → lavender → peach → ochre → cream. Repeating the same color twice in a row reads as off-rhythm.
- Use Plain Black at weight 500 with negative letter-spacing on every display headline.
- Show product UI fragments inside saturated feature cards. The brand voltage is product-driven, not abstract.
- Use cream footer (NOT dark). Clay deliberately closes pages with warm cream rather than the standard dark-footer SaaS template.
- Anchor every band with `{spacing.section}` (96px) vertical rhythm.

### Don't
- Don't use cool grays for canvas. The cream tint is non-negotiable.
- Don't use a 7th brand-color card. The 6-color palette is saturated enough.
- Don't bold display weight beyond 500. Plain Black at 700 reads as bombastic.
- Don't repeat the same brand-color card twice in a row.
- Don't replace claymation illustrations with flat vector art. The hand-crafted 3D character IS the brand voice.
- Don't use a dark footer. The cream footer is part of the system's warm-throughout pacing.
- Don't add hover state styling beyond what the system already encodes.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 768px | Hamburger nav; hero h1 72→36px; hero-illustration-card stacks below; feature grids 1-up; pricing 1-up |
| Tablet | 768–1024px | Top nav tightens; feature cards 2-up; pricing 2-up |
| Desktop | 1024–1440px | Full top-nav; 3-up feature cards; 3-up pricing tiers |
| Wide | > 1440px | Same as desktop with more breathing room; max content 1280px |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#0a0a0a`
- Background / Canvas: `#fffaf0`
- Heading / Strong text: `#0a0a0a`
- Body / Secondary text: `#3a3a3a`
- Primary Active: `#1f1f1f`
- Primary Disabled: `#e5e5e5`
- Body Strong: `#1a1a1a`
- Muted: `#6a6a6a`
- Muted Soft: `#9a9a9a`
- Hairline: `#e5e5e5`

### Example Component Prompts

- "Create a hero on the canvas background (`#fffaf0`). Headline at 72px using the display font, weight 500, line-height 1, color `#0a0a0a` with fallback Google Font. Primary CTA uses `#0a0a0a` background, white text, 12px radius, and comfortable padding."
- "Design a content card: `#f5f0e0` background, 1px `#e5e5e5` border, `16px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

