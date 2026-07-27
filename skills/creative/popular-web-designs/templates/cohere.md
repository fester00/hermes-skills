# Design System: Cohere

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `cohere/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/cohere.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `CohereText` → **Fallback:** `Inter`
> - **Original mono family:** `CohereMono` → **Fallback:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Cohere's current web presence feels like a sober enterprise AI command center with editorial restraint. The home page opens on a huge typographic declaration over a white canvas, then uses photography, dark product mockups, trust logos, and generous empty space to make AI infrastructure feel controlled rather than speculative. Product pages invert the tone into deep green-black or dark navy bands, while blog and research pages move toward publishing-system clarity: large filters, thin rules, dense lists, and pale technical backgrounds.

What makes the system distinctive is the mix of austere black-and-white UI with bursts of tactile brand imagery. The site avoids decorative chrome in the normal interface; color arrives through photography, abstract 3D media, coral blog taxonomy chips, blue research links, and dark product environments. Cards are rounded but not cute. Type is large, tight, and almost monospaced in spirit, creating a research-lab cadence across marketing, product, and editorial surfaces.

**Key Characteristics:**
- Monumental display headlines with very tight line height and negative tracking.
- White editorial canvases interrupted by deep green, dark navy, and image-led CTA bands.
- Rounded media cards and product cards, usually 8px to 22px.
- Pill CTAs in near-black or white, with most secondary actions rendered as underlined text links.
- Trust-logo strips with monochrome partner marks and very wide vertical spacing.
- Agent-console mockups using dark panels, small status chips, and product integration badges.
- Blog and research surfaces with prominent taxonomy chips, long rule-separated lists, and search fields.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#17171c` — near-black
- **Cohere Black** (cohere-black): `#000000` — near-black
- **On Primary** (on-primary): `#ffffff` — pure/near-white
### Surfaces & Backgrounds
- **Canvas** (canvas): `#ffffff` — pure/near-white
- **Card Border** (card-border): `#f2f2f2` — pure/near-white
### Text & Ink
- **Ink** (ink): `#212121` — near-black
- **Muted** (muted): `#93939f`
- **Body Muted** (body-muted): `#616161`
- **Action Blue** (action-blue): `#1863dc` — cool blue tint
- **On Dark** (on-dark): `#ffffff` — pure/near-white
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#d9d9dd`
- **Border Light** (border-light): `#e5e7eb`
### Semantic & Status
- **Error** (error): `#b30000` — warm red/orange tint
### Accent / Other
- **Deep Green** (deep-green): `#003c33`
- **Dark Navy** (dark-navy): `#071829`
- **Soft Stone** (soft-stone): `#eeece7`
- **Pale Green** (pale-green): `#edfce9`
- **Pale Blue** (pale-blue): `#f1f5ff` — pure/near-white
- **Slate** (slate): `#75758a`
- **Focus Blue** (focus-blue): `#4c6ee6` — cool blue tint
- **Coral** (coral): `#ff7759` — warm red/orange tint
- **Coral Soft** (coral-soft): `#ffad9b` — warm red/orange tint
- **Form Focus** (form-focus): `#9b60aa` — cool blue tint

## 3. Typography Rules

### Font Family
- **Primary:** `CohereText`
- **Monospace:** used for code/terminal surfaces.

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| hero-display | CohereText | 96px | 400 | 1 | -1.92px |  |
| product-display | CohereText | 72px | 400 | 1 | -1.44px |  |
| section-display | Unica77 Cohere Web | 60px | 400 | 1 | -1.2px |  |
| section-heading | Unica77 Cohere Web | 48px | 400 | 1.2 | -0.48px |  |
| card-heading | Unica77 Cohere Web | 32px | 400 | 1.2 | -0.32px |  |
| feature-heading | Unica77 Cohere Web | 24px | 400 | 1.3 | 0 |  |
| body-large | Unica77 Cohere Web | 18px | 400 | 1.4 | 0 |  |
| body | Unica77 Cohere Web | 16px | 400 | 1.5 | 0 |  |
| button | Unica77 Cohere Web | 14px | 500 | 1.71 | 0 |  |
| caption | Unica77 Cohere Web | 14px | 400 | 1.4 | 0 |  |
| mono-label | CohereMono | 14px | 400 | 1.4 | 0.28px |  |
| micro | Unica77 Cohere Web | 12px | 400 | 1.4 | 0 |  |


## 4. Component Stylings

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 12px 24px

### button-secondary

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.xs}
- **padding:** 8px 0

### button-pill-outline

- **backgroundColor:** transparent
- **textColor:** {colors.primary}
- **typography:** {typography.button}
- **rounded:** {rounded.xl}
- **padding:** 6px 12px

### announcement-bar

- **backgroundColor:** {colors.cohere-black}
- **textColor:** {colors.on-dark}
- **typography:** {typography.micro}
- **height:** 36px

### hero-photo-card

- **backgroundColor:** {colors.canvas}
- **rounded:** {rounded.lg}

### agent-console-card

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.sm}
- **padding:** 24px

### trust-logo-strip

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.caption}

### capability-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.xs}
- **padding:** 24px

### dark-feature-band

- **backgroundColor:** {colors.deep-green}
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.lg}
- **padding:** 80px

### product-card

- **backgroundColor:** {colors.soft-stone}
- **textColor:** {colors.ink}
- **rounded:** {rounded.sm}
- **padding:** 32px

### blog-filter-chip

- **backgroundColor:** transparent
- **textColor:** {colors.coral}
- **typography:** {typography.card-heading}
- **rounded:** {rounded.sm}
- **padding:** 8px 14px

### research-table

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-large}

### contact-form-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **rounded:** {rounded.lg}
- **padding:** 32px

### footer-newsletter

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-dark}
- **typography:** {typography.micro}


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
| `xs` | 4px |
| `sm` | 8px |
| `md` | 16px |
| `lg` | 22px |
| `xl` | 30px |
| `pill` | 32px |
| `full` | 9999px |

**Spacing Scale**

| Token | Value |
|---|---|
| `xxs` | 2px |
| `xs` | 6px |
| `sm` | 8px |
| `md` | 12px |
| `lg` | 16px |
| `xl` | 24px |
| `xxl` | 32px |
| `section` | 80px |


## 6. Layout Principles

- **Section rhythm:** `80px` vertical padding between major bands.

### Grid & Container

- Feature sections commonly use 3-column cards on desktop.
- Product pages alternate centered hero blocks, trust-logo strips, large single-feature bands, and 2- or 3-column card grids.
- Research pages use full-width lists with date and chip columns instead of decorative cards.
- Forms use two-column input rows inside a rounded white card on dark or stone section backgrounds.
- Product and capability grids collapse from 3 columns to 2 and then 1.
- Form fields collapse from paired rows to a single column.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, white or dark field | Hero copy, research lists, editorial surfaces |
| Bordered | 1px `#d9d9dd`, `#e5e7eb`, or dark translucent rules | Research rows, forms, pale cards, footer inputs |
| Media Lift | Rounded image or video over contrasting section color | Hero photo cards, product videos, CTA imagery |
| Dark Product Field | Deep green or navy full-width band | Command, North, financial services, security sections |


## 8. Do's and Don'ts

### Do

- Use white canvas as the default surface; introduce dark green or navy as full-width product bands.
- Keep primary CTAs pill-shaped and near-black on light surfaces.
- Use 22px radius on major media cards and placeholders.
- Use coral for editorial taxonomy and small warm accents, not as the main CTA system.
- Use monochrome trust logos with wide spacing.
- Use thin-line geometric illustrations for research and capability icons.
- Let photography and product mockups carry color, while the UI shell stays restrained.

### Don't

- Do not turn coral or blue into broad decorative surface colors.
- Do not add heavy drop shadows to cards.
- Do not make every section card-based; Cohere often uses unframed rows, rules, and open space.
- Do not use rounded cards below 8px for major media.
- Do not replace the display/body type split with one generic sans-serif voice.
- Do not render undocumented interaction variants in documentation or previews.
- Do not use saturated gradients as normal UI backgrounds; keep gradients media-led.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---:|---|
| Small Mobile | <425px | Single-column cards, compact nav, reduced hero headline scale |
| Mobile | 425-640px | Hero media stacks, card grids become one column, form rows stack |
| Large Mobile | 640-768px | Wider one-column layouts with larger media cards |
| Tablet | 768-1024px | Two-column cards begin, nav spacing tightens |
| Desktop | 1024-1440px | Full nav, 3-column card grids, split hero compositions |
| Large Desktop | 1440-2560px | Wide containers and large empty vertical intervals |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#17171c`
- Background / Canvas: `#ffffff`
- Heading / Strong text: `#212121`
- Cohere Black: `#000000`
- Deep Green: `#003c33`
- Dark Navy: `#071829`
- Soft Stone: `#eeece7`
- Pale Green: `#edfce9`
- Pale Blue: `#f1f5ff`

### Example Component Prompts

- "Create a hero on the canvas background (`#ffffff`). Headline at 96px using the display font, weight 400, line-height 1, color `#212121` with fallback Google Font. Primary CTA uses `#17171c` background, white text, 16px radius, and comfortable padding."
- "Design a content card: `#ffffff` background, 1px `#d9d9dd` border, `22px` radius, padding `16px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

