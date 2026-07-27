# Design System: Hashicorp

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `hashicorp/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/hashicorp.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `hashicorpSans` → **Fallback:** `Inter`
> - **Mono:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

HashiCorp's marketing canvas is a near-black ground that serves a multi-product portfolio without ever feeling generic. The dominant surface is `{colors.canvas}` (pure black) layered with `{colors.surface-1}` charcoal cards and 1px translucent gray hairlines. The chrome is monochrome — white pill-rounded buttons (`{components.button-primary}`), white type, gray secondary type — but the system is held together by a **palette of per-product accent colors** that signal which HashiCorp tool a given section belongs to: Terraform purple, Vault yellow, Consul red, Waypoint cyan, Vagrant blue, Nomad green, Boundary coral.

Display type is **hashicorpSans** at weights 600/700 with tight line-heights (1.17–1.21); body type is the same family at 500 weight with deliberately relaxed line-heights (1.50–1.71) — the contrast feels editorial, not enterprise-templated. CTAs use small `{rounded.md}` 8px corners rather than pills, which keeps the system reading as developer-facing rather than consumer-y.

The signature device is the **product-card** family — each HashiCorp product gets its own colored card variant on the home and infrastructure pages, lifting Terraform into a violet ground, Vault into yellow, Waypoint into cyan. These aren't decorative gradients — they're identity surfaces. A reader scrolling the page can tell which product a section is about from the corner of their eye.

**Key Characteristics:**
- Black-canvas marketing system: `{colors.canvas}` is the surface for hero, body, pricing, comparison tables, and footer alike.
- **Per-product color identity**: Terraform `{colors.product-terraform}`, Vault `{colors.product-vault}`, Waypoint `{colors.product-waypoint}`, Vagrant `{colors.product-vagrant}`, Consul `{colors.product-consul}`, Nomad `{colors.product-nomad}`, Boundary `{colors.product-boundary}` — each with its own button + card variant.
- Display headlines run hashicorpSans 600/700 with line-height 1.17–1.21 (tight); body runs the same family at 500 with 1.50–1.71 (relaxed) — the proportional gap is the brand's voice.
- CTA shape is `{rounded.md}` 8px — not a pill — keeping the system reading as developer-tool rather than consumer-app.
- Charcoal surface lift (canvas → surface-1 → surface-2) instead of shadow-driven elevation.
- 1px translucent gray hairlines (`rgba(178,182,189,0.1)`) define cards and dividers — the borders are felt more than seen.
- Eyebrow typography (12–13px, 600 weight, 0.6px positive tracking, uppercase) marks every section as a category label.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#000000` — near-black
- **On Primary** (on-primary): `#ffffff` — pure/near-white
- **Accent Blue** (accent-blue): `#2b89ff` — cool blue tint
- **Inverse Canvas** (inverse-canvas): `#ffffff` — pure/near-white
### Surfaces & Backgrounds
- **Canvas** (canvas): `#000000` — near-black
- **Surface 1** (surface-1): `#15181e` — near-black
- **Surface 2** (surface-2): `#1f232b`
- **Surface 3** (surface-3): `#3b3d45`
### Text & Ink
- **Ink** (ink): `#ffffff` — pure/near-white
- **Ink Muted** (ink-muted): `#b2b6bd`
- **Ink Subtle** (ink-subtle): `#656a76`
- **Inverse Ink** (inverse-ink): `#000000` — near-black
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#3b3d45`
- **Hairline Soft** (hairline-soft): `#252830`
### Semantic & Status
- **Semantic Success** (semantic-success): `#00ca8e` — green tint
- **Semantic Warning** (semantic-warning): `#ffcf25` — warm red/orange tint
- **Semantic Error** (semantic-error): `#e62b1e` — warm red/orange tint
- **Semantic Visited** (semantic-visited): `#a737ff` — cool blue tint
### Accent / Other
- **Product Terraform** (product-terraform): `#7b42bc` — cool blue tint
- **Product Terraform Bright** (product-terraform-bright): `#911ced` — cool blue tint
- **Product Vault** (product-vault): `#ffcf25` — warm red/orange tint
- **Product Consul** (product-consul): `#e62b1e` — warm red/orange tint
- **Product Waypoint** (product-waypoint): `#14c6cb`
- **Product Waypoint Deep** (product-waypoint-deep): `#12b6bb`
- **Product Vagrant** (product-vagrant): `#1868f2` — cool blue tint
- **Product Nomad** (product-nomad): `#00ca8e` — green tint
- **Product Boundary** (product-boundary): `#f24c53` — warm red/orange tint
- **Amber 100** (amber-100): `#fbeabf`
- **Amber 200** (amber-200): `#bb5a00` — warm red/orange tint
- **Blue 7** (blue-7): `#101a59` — cool blue tint

## 3. Typography Rules

### Font Family
- **Primary:** `hashicorpSans`

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-xl | hashicorpSans | 80px | 700 | 1.17 | -2.5px |  |
| display-lg | hashicorpSans | 56px | 700 | 1.18 | -1.6px |  |
| display-md | hashicorpSans | 40px | 600 | 1.19 | -1.0px |  |
| headline | hashicorpSans | 28px | 600 | 1.21 | -0.6px |  |
| card-title | hashicorpSans | 22px | 600 | 1.18 | -0.4px |  |
| subhead | hashicorpSans | 20px | 600 | 1.35 | -0.2px |  |
| body-lg | hashicorpSans | 18px | 500 | 1.69 | 0 |  |
| body | hashicorpSans | 16px | 500 | 1.5 | 0 |  |
| body-sm | hashicorpSans | 14px | 500 | 1.71 | 0 |  |
| caption | hashicorpSans | 13px | 500 | 1.38 | 0.2px |  |
| button | hashicorpSans | 14px | 600 | 1.29 | 0 |  |
| eyebrow | hashicorpSans | 12px | 600 | 1.23 | 0.6px |  |


## 4. Component Stylings

### button-primary

- **backgroundColor:** {colors.inverse-canvas}
- **textColor:** {colors.inverse-ink}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 10px 18px

### button-primary-pressed

- **backgroundColor:** {colors.inverse-canvas}
- **textColor:** {colors.inverse-ink}
- **typography:** {typography.button}
- **rounded:** {rounded.md}

### button-secondary

- **backgroundColor:** {colors.surface-2}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 10px 18px

### button-tertiary

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 10px 18px

### button-product-terraform

- **backgroundColor:** {colors.product-terraform}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 10px 18px

### button-product-vault

- **backgroundColor:** {colors.product-vault}
- **textColor:** {colors.inverse-ink}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 10px 18px

### button-product-waypoint

- **backgroundColor:** {colors.product-waypoint}
- **textColor:** {colors.inverse-ink}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 10px 18px

### product-card

- **backgroundColor:** {colors.surface-1}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.lg}
- **padding:** 24px

### product-card-terraform

- **backgroundColor:** {colors.product-terraform}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.lg}
- **padding:** 24px

### product-card-vault

- **backgroundColor:** {colors.product-vault}
- **textColor:** {colors.inverse-ink}
- **typography:** {typography.body}
- **rounded:** {rounded.lg}
- **padding:** 24px

### product-card-waypoint

- **backgroundColor:** {colors.product-waypoint}
- **textColor:** {colors.inverse-ink}
- **typography:** {typography.body}
- **rounded:** {rounded.lg}
- **padding:** 24px

### feature-card

- **backgroundColor:** {colors.surface-1}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.lg}
- **padding:** 24px

### pricing-card

- **backgroundColor:** {colors.surface-1}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.lg}
- **padding:** 32px

### pricing-card-featured

- **backgroundColor:** {colors.surface-2}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.lg}
- **padding:** 32px

### resource-card

- **backgroundColor:** {colors.surface-1}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.lg}
- **padding:** 16px

### text-input

- **backgroundColor:** {colors.surface-1}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.md}
- **padding:** 10px 14px

### text-input-focused

- **backgroundColor:** {colors.surface-1}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.md}
- **padding:** 10px 14px

### product-pill

- **backgroundColor:** {colors.surface-1}
- **textColor:** {colors.ink-muted}
- **typography:** {typography.caption}
- **rounded:** {rounded.pill}
- **padding:** 4px 10px

### top-nav

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.xs}
- **height:** 64px

### comparison-row

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink-muted}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.xs}

### cta-banner

- **backgroundColor:** {colors.surface-1}
- **textColor:** {colors.ink}
- **typography:** {typography.subhead}
- **rounded:** {rounded.xxl}
- **padding:** 48px

### footer

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink-muted}
- **typography:** {typography.caption}
- **rounded:** {rounded.xs}
- **padding:** 64px 32px


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
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

- Max content width sits around 1280px with side gutters scaling from `{spacing.xxl}` on desktop down to `{spacing.lg}` on mobile.
- Product card grids are 3-up on desktop, 2-up at tablet, 1-up on mobile.
- Pricing tier grid is 3-up across desktop; comparison table beneath uses fixed-width left column.
- Resource directory (PDF library) uses 4-up dense thumbnail grid.
- **Product card grid**: 3-up → 2-up at 1024px → 1-up below 768px.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| 0 (flat) | No shadow, no border | Canvas-mounted display type, hero, footer |
| 1 (charcoal lift) | `{colors.surface-1}` background + 1px `rgba(178,182,189,0.1)` border | Default cards, resource tiles, pricing cards |
| 2 (surface-2 lift) | `{colors.surface-2}` background + 1px `{colors.hairline}` border | Featured pricing card, hovered cards, sub-nav |
| 3 (product chromatic) | Per-product accent color background — Terraform purple, Vault yellow, Waypoint cyan | Product showcase cards |

The product chromatic level isn't a "modal lift" — it's an identity device. A Terraform card sits at the same z-plane as a feature-card; the difference is meaning, not depth.


## 8. Do's and Don'ts

### Do

- Reserve `{colors.canvas}` (black) and `{colors.surface-1}` (charcoal) as the system's two anchor surfaces. Every band of the page is one or the other.
- When introducing a section about a specific HashiCorp product, use that product's `{colors.product-*}` token consistently — for the section pill, the CTA button, and (where appropriate) the showcase card background.
- Use `{rounded.md}` 8px on CTA buttons; HashiCorp's brand reads as engineered, not consumer.
- Pair tight display line-heights (1.17–1.21) with relaxed body line-heights (1.50–1.71). The contrast IS the brand voice.
- Use the eyebrow typography (`{typography.eyebrow}`, uppercase, 0.6px tracking) above every meaningful section.
- Use surface lift (canvas → surface-1 → surface-2) to express hierarchy on dark.
- Reserve product-chromatic cards for product identity; keep generic feature cards on `{colors.surface-1}`.

### Don't

- Don't ship a light-mode marketing page. HashiCorp's marketing brand IS dark.
- Don't introduce mid-tone gray text outside the documented `ink` / `ink-muted` / `ink-subtle` set.
- Don't square off CTA corners — use `{rounded.md}` 8px, not 0px.
- Don't use a product accent color for a CTA on a page that isn't about that product. Terraform purple on the Vault page is a brand violation.
- Don't combine multiple product accents in the same viewport — the system says "this section is about THIS tool", and mixing accents breaks that signal.
- Don't add drop shadows on dark; surface lift carries elevation.
- Don't replace `hashicorpSans` with a display-only sans for headlines and a different family for body. The brand is held together by one family across the full hierarchy.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Desktop-XL | 1440px | Default desktop layout |
| Desktop | 1280px | Pricing 3-up grid maintained |
| Tablet | 1024px | Product card grid 3-up → 2-up |
| Mobile-Lg | 768px | Pricing comparison becomes per-tier accordion; nav becomes hamburger |
| Mobile | 480px | Single-column everything; display-xl scales 80px → ~36px |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#000000`
- Background / Canvas: `#000000`
- Heading / Strong text: `#ffffff`
- On Primary: `#ffffff`
- Accent Blue: `#2b89ff`
- Ink Muted: `#b2b6bd`
- Ink Subtle: `#656a76`
- Surface 1: `#15181e`
- Surface 2: `#1f232b`

### Example Component Prompts

- "Create a hero on the canvas background (`#000000`). Headline at 80px using the display font, weight 700, line-height 1.17, color `#ffffff` with fallback Google Font. Primary CTA uses `#000000` background, white text, 8px radius, and comfortable padding."
- "Design a content card: `#000000` background, 1px `#3b3d45` border, `12px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

