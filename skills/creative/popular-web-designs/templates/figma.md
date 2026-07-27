# Design System: Figma

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `figma/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/figma.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `figmaSans` → **Fallback:** `Inter`
> - **Original mono family:** `figmaMono` → **Fallback:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Figma's marketing canvas is, at the system level, an editor-clean black-and-white frame. The chrome — top nav, body type, footer, primary CTA — is monochrome. Headlines are oversized `{typography.display-xl}` set in `figmaSans` with aggressive negative tracking, body copy hovers around weight 320–340 of the same variable family, and small mono `{typography.eyebrow}` and `{typography.caption}` labels (figmaMono, all-caps, positive tracking) act as section markers. Every CTA is a pill — `{rounded.pill}` — and the primary action across the entire site is the same black `{components.button-primary}` paired with the same white `{components.button-secondary}`.

What makes the design unique is what happens **between** those monochrome bookends: the page repeatedly drops into oversized pastel **color-block sections** — lime, lavender, cream, mint, pink, coral, and a deep navy — that span the full content width with `{rounded.lg}` corners and `{spacing.xxl}` interior padding. These blocks are where the storytelling lives. They aren't accents tucked into a card; they take over a whole viewport's worth of vertical space, like a designer arranging giant sticky notes on a clean wall. FigJam is the most pastel-saturated, the home page rotates through the full set, and the pricing page ends with a lime FAQ panel — same vocabulary, different rhythm per route.

This is a system built on contrast: the monochrome chrome makes the color blocks feel intentional rather than decorative, and the color blocks make the monochrome chrome feel like editorial paper rather than enterprise SaaS. Density is generous, line-heights are tight on display sizes, and the interface never reaches for shadows or gradients to do the work that color blocks and confident typography already do.

**Key Characteristics:**
- Monochrome system core: `{colors.primary}` (black) and `{colors.canvas}` (white) carry every CTA, every body line, every footer link.
- Oversized pastel **color-block sections** (`{colors.block-lime}`, `{colors.block-lilac}`, `{colors.block-cream}`, `{colors.block-mint}`, `{colors.block-pink}`, `{colors.block-coral}`, `{colors.block-navy}`) define the narrative rhythm of every long-form page.
- Pill is the only button shape — `{rounded.pill}` for text CTAs, `{rounded.full}` for icon buttons. No square buttons anywhere.
- `figmaSans` variable typeface used at unusually fine weight increments (320, 330, 340, 450, 480, 540) — the type system reads as a single voice that flexes rather than a multi-weight family.
- Tight negative letter-spacing on display sizes (-1.72px at 86px, -0.96px at 64px) creates a confident editorial cadence.
- `figmaMono` reserved for category labels, eyebrows, and captions — always uppercase, positive tracking — to flag taxonomy without competing with display type.
- Color-block page rhythm (home): white hero → marquee strip → white feature → lime systems block → navy ship-products block → coral developer block → white template grid → white footer.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#000000` — near-black
- **On Primary** (on-primary): `#ffffff` — pure/near-white
- **Inverse Canvas** (inverse-canvas): `#000000` — near-black
- **Accent Magenta** (accent-magenta): `#ff3d8b` — warm red/orange tint
### Surfaces & Backgrounds
- **Canvas** (canvas): `#ffffff` — pure/near-white
- **Surface Soft** (surface-soft): `#f7f7f5` — pure/near-white
### Text & Ink
- **Ink** (ink): `#000000` — near-black
- **Inverse Ink** (inverse-ink): `#ffffff` — pure/near-white
- **On Inverse Soft** (on-inverse-soft): `#ffffff` — pure/near-white
- **Block Pink** (block-pink): `#efd4d4`
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#e6e6e6`
- **Hairline Soft** (hairline-soft): `#f1f1f1` — pure/near-white
### Semantic & Status
- **Semantic Success** (semantic-success): `#1ea64a` — green tint
### Accent / Other
- **Block Lime** (block-lime): `#dceeb1` — green tint
- **Block Lilac** (block-lilac): `#c5b0f4` — cool blue tint
- **Block Cream** (block-cream): `#f4ecd6`
- **Block Mint** (block-mint): `#c8e6cd`
- **Block Coral** (block-coral): `#f3c9b6` — warm red/orange tint
- **Block Navy** (block-navy): `#1f1d3d`
- **Overlay Scrim** (overlay-scrim): `#000000` — near-black

## 3. Typography Rules

### Font Family
- **Primary:** `figmaSans`
- **Monospace:** used for code/terminal surfaces.

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-xl | figmaSans | 86px | 340 | 1.0 | -1.72px | kern |
| display-lg | figmaSans | 64px | 340 | 1.1 | -0.96px | kern |
| headline | figmaSans | 26px | 540 | 1.35 | -0.26px | kern |
| subhead | figmaSans | 26px | 340 | 1.35 | -0.26px | kern |
| card-title | figmaSans | 24px | 700 | 1.45 | 0 | kern |
| body-lg | figmaSans | 20px | 330 | 1.4 | -0.14px | kern |
| body | figmaSans | 18px | 320 | 1.45 | -0.26px | kern |
| body-sm | figmaSans | 16px | 330 | 1.45 | -0.14px | kern |
| link | figmaSans | 20px | 480 | 1.4 | -0.10px | kern |
| button | figmaSans | 20px | 480 | 1.4 | -0.10px | kern |
| eyebrow | figmaMono | 18px | 400 | 1.3 | 0.54px | kern |
| caption | figmaMono | 12px | 400 | 1.0 | 0.60px | kern |


## 4. Component Stylings

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 10px 20px

### button-primary-pressed

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}

### button-secondary

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 8px 18px 10px

### button-tertiary-text

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.link}
- **rounded:** {rounded.full}
- **padding:** 8px 12px

### button-icon-circular

- **backgroundColor:** {colors.surface-soft}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.full}
- **size:** 40px

### button-icon-circular-inverse

- **backgroundColor:** {colors.on-inverse-soft}
- **textColor:** {colors.inverse-ink}
- **typography:** {typography.button}
- **rounded:** {rounded.full}
- **size:** 40px

### button-magenta-promo

- **backgroundColor:** {colors.accent-magenta}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 10px 18px

### pricing-tab-default

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 8px 18px

### pricing-tab-selected

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 8px 18px

### text-input

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.md}
- **padding:** 12px 14px

### text-input-focused

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.md}
- **padding:** 12px 14px

### pricing-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.lg}
- **padding:** 24px

### pricing-card-feature-row

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.xs}

### color-block-section

- **backgroundColor:** {colors.block-lime}
- **textColor:** {colors.ink}
- **typography:** {typography.subhead}
- **rounded:** {rounded.lg}
- **padding:** 48px

### color-block-section-lilac

- **backgroundColor:** {colors.block-lilac}
- **textColor:** {colors.ink}
- **typography:** {typography.subhead}
- **rounded:** {rounded.lg}
- **padding:** 48px

### color-block-section-navy

- **backgroundColor:** {colors.block-navy}
- **textColor:** {colors.inverse-ink}
- **typography:** {typography.subhead}
- **rounded:** {rounded.lg}
- **padding:** 48px

### promo-banner-lilac

- **backgroundColor:** {colors.block-lilac}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.md}
- **padding:** 16px 24px

### template-card

- **backgroundColor:** {colors.surface-soft}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.md}
- **padding:** 16px

### feature-illustration-tile

- **backgroundColor:** {colors.surface-soft}
- **textColor:** {colors.ink}
- **typography:** {typography.eyebrow}
- **rounded:** {rounded.md}
- **padding:** 24px

### top-nav

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.xs}
- **height:** 56px

### marquee-strip

- **backgroundColor:** {colors.inverse-canvas}
- **textColor:** {colors.inverse-ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.xs}
- **height:** 36px

### comparison-checkmark

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.semantic-success}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.full}
- **size:** 16px

### footer

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.caption}
- **rounded:** {rounded.xs}
- **padding:** 64px 32px


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
| `xs` | 2px |
| `sm` | 6px |
| `md` | 8px |
| `lg` | 24px |
| `xl` | 32px |
| `pill` | 50px |
| `full` | 9999px |

**Spacing Scale**

| Token | Value |
|---|---|
| `hair` | 1px |
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

- Color-block page rhythm (home): white hero → marquee strip → white feature → lime systems block → navy ship-products block → coral developer block → white template grid → white footer.
- **Block Cream** ({colors.block-cream}): Soft warm background — FigJam hero strip, template-grid section.
- Max content width sits around 1280px (one of the explicit breakpoints), with side gutters that scale from `{spacing.xxl}` on desktop down to `{spacing.lg}` on mobile.
- Three- and four-column grids on the desktop pricing comparison and FigJam template galleries.
- Color-block sections break the column grid — they span content width with full bleed inside the rounded `{rounded.lg}` corners, then place a single editorial column of headline + body inside.
- Template thumbnails on the home grid sit in `{rounded.md}` tiles with `{spacing.md}` interior padding around the embedded preview.
- Background `{colors.canvas}`, text `{colors.ink}`, type `{typography.caption}` for column headings and small links, padding `{spacing.section}` top/bottom · `{spacing.xl}` sides.
- **Pricing tier grid**: 4-up → 2-up at 960px → 1-up below 768px. The pill toggle stays horizontal and scrolls horizontally if needed below 560px.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| 0 (flat) | No shadow, no border | Default for color-block sections, inverse-canvas footer, hero |
| 1 (hairline) | 1px `{colors.hairline}` border on `{colors.canvas}` | Pricing cards, form inputs, comparison table cells |
| 2 (soft elevation) | Subtle drop shadow approx 0 4px 16px rgba(0,0,0,0.06) | Floating template tiles, dropdown menus |
| 3 (modal) | Stronger shadow + `{colors.overlay-scrim}` behind | Video / image lightbox overlays |

Figma's marketing system is shadow-light by design — the color blocks substitute for traditional elevation. Where most SaaS sites use a shadowed white card to draw attention, Figma uses a saturated background panel. This makes the rare actual shadow (e.g., a floating template card hovering over a cream section) feel like an exception worth noticing.


## 8. Do's and Don'ts

### Do

- Reserve `{colors.primary}` for genuine primary CTAs and selected states (e.g., `pricing-tab-selected`). Don't use it as a decorative accent.
- When introducing a story section, choose **one** color block from the `{colors.block-*}` family and let it span full content width with `{rounded.lg}` corners and `{spacing.xxl}` interior padding.
- Keep type in `figmaSans` at variable weights — pick from 320, 330, 340, 480, 540, 700 to express hierarchy. Avoid intermediate weights outside this set.
- Use `figmaMono` only for eyebrows and captions, always uppercase, with the documented positive letter-spacing.
- Compose every CTA as a pill (`{rounded.pill}`) and every icon button as a circle (`{rounded.full}`).
- Allow the page to **return to white canvas** between every two color blocks so each block reads as deliberate.
- Pair `button-primary` and `button-secondary` whenever a section needs both a primary action and a sales / secondary action — the black-and-white pair is the brand signature.

### Don't

- Don't introduce mid-gray text. Body hierarchy comes from `figmaSans` weight, not from opacity.
- Don't add drop shadows to color-block sections — the color is the depth device.
- Don't introduce new accent colors outside the documented `{colors.block-*}` palette and `{colors.accent-magenta}`. Adding, e.g., a saturated brand orange would break the system.
- Don't combine more than one color block visible inside a single viewport — Figma's pacing always lets the white canvas separate them.
- Don't square off CTAs. Square buttons read as a different brand.
- Don't put `figmaMono` in body copy — it's a taxonomy tool, not a reading typeface.
- Don't replace the `pricing-tab-selected` black fill with a colored tab; the brand pattern is "selected = primary surface".


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| 4k | 1920px | Max content width holds at 1280px; gutters expand |
| Desktop-XL | 1440px | Default desktop layout |
| Desktop | 1400px | Comparison table column widths normalize |
| Desktop-S | 1280px | Pricing 4-up tier grid maintained |
| Tablet | 960px | Pricing collapses 4-up → 2-up; nav becomes hamburger |
| Mobile-L | 768px | Color-block sections become full-bleed (no rounded corners on edges) |
| Mobile | 560px | Display-xl reduces from 86px to ~48px; pill CTAs go full-width |
| Mobile-XS | 559px | Two-column footer collapses to single column |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#000000`
- Background / Canvas: `#ffffff`
- Heading / Strong text: `#000000`
- On Primary: `#ffffff`
- Inverse Canvas: `#000000`
- Inverse Ink: `#ffffff`
- On Inverse Soft: `#ffffff`
- Hairline: `#e6e6e6`
- Hairline Soft: `#f1f1f1`

### Example Component Prompts

- "Create a hero on the canvas background (`#ffffff`). Headline at 86px using the display font, weight 340, line-height 1.0, color `#000000` with fallback Google Font. Primary CTA uses `#000000` background, white text, 8px radius, and comfortable padding."
- "Design a content card: `#ffffff` background, 1px `#e6e6e6` border, `24px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

