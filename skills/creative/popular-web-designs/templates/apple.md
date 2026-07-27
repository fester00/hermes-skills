# Design System: Apple

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `apple/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/apple.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Primary:** `Inter`
> - **Mono:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Apple's web presence is a masterclass in **reverent product photography framed by near-invisible UI**. Every page is a stack of edge-to-edge product "tiles" — alternating light and dark canvases, each centered on a hero headline, a one-line tagline, two tiny blue pill CTAs, and an impossibly crisp product render. Nothing competes with the product. Typography is confident but quiet; color is either pure white, an off-white parchment, or a near-black tile; interactive elements are a single, quiet blue.

Density is unusually low even by contemporary SaaS standards. Each tile occupies roughly one viewport, and there is no decorative chrome — no borders, no gradients, no decorative frames, no shadows on headlines. Elevation appears only when a product image rests on a surface (a single soft `rgba(0, 0, 0, 0.22) 3px 5px 30px` drop for visual weight). The result is a catalog that feels more like a museum gallery: the wall disappears and the artifact takes over.

Store and shop surfaces retain the same chassis but switch modes. The product configurator (iPhone 17 Pro, accessories grid) introduces a tight grid of white utility cards at `{rounded.lg}` (18px) radius with a thin border, paired with a persistent thin sub-nav strip. The environment page leans darker and more editorial. Across all five surfaces the typographic system, spacing rhythm, and the single blue accent are consistent — this is one design language expressed at different volumes.

**Key Characteristics:**
- Photography-first presentation; UI recedes so the product can speak.
- Alternating full-bleed tile sections: white/parchment ↔ near-black, with the color change itself acting as the section divider.
- Single blue accent (`{colors.primary}` — #0066cc) carries every interactive element. No second brand color exists.
- Two button grammars: tiny blue pill CTAs (`{rounded.pill}`) and compact utility rects (`{rounded.sm}`).
- SF Pro Display + SF Pro Text — negative letter-spacing at display sizes for the signature "Apple tight" headline feel.
- Whisper-soft elevation used only when a product image needs to breathe — exactly one drop-shadow in the entire system.
- Tight two-row nav: slim `{component.global-nav}` + product-specific `{component.sub-nav-frosted}` with persistent right-aligned primary CTA.
- Section rhythm across multiple pages: light hero → dark product tile → light utility tile → dark tile → parchment footer — a predictable pulse.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#0066cc` — cool blue tint
- **Primary Focus** (primary-focus): `#0071e3` — cool blue tint
- **Primary On Dark** (primary-on-dark): `#2997ff` — cool blue tint
- **On Primary** (on-primary): `#ffffff` — pure/near-white
### Surfaces & Backgrounds
- **Canvas** (canvas): `#ffffff` — pure/near-white
- **Canvas Parchment** (canvas-parchment): `#f5f5f7` — pure/near-white
- **Surface Pearl** (surface-pearl): `#fafafc` — pure/near-white
- **Surface Tile 1** (surface-tile-1): `#272729`
- **Surface Tile 2** (surface-tile-2): `#2a2a2c`
- **Surface Tile 3** (surface-tile-3): `#252527` — near-black
- **Surface Black** (surface-black): `#000000` — near-black
- **Surface Chip Translucent** (surface-chip-translucent): `#d2d2d7`
### Text & Ink
- **Ink** (ink): `#1d1d1f` — near-black
- **Body** (body): `#1d1d1f` — near-black
- **Body On Dark** (body-on-dark): `#ffffff` — pure/near-white
- **Body Muted** (body-muted): `#cccccc`
- **Ink Muted 80** (ink-muted-80): `#333333`
- **Ink Muted 48** (ink-muted-48): `#7a7a7a`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
### Hairlines, Borders & Dividers
- **Divider Soft** (divider-soft): `#f0f0f0`
- **Hairline** (hairline): `#e0e0e0`

## 3. Typography Rules

### Font Family
- **Primary:** `SF Pro Display, system-ui, -apple-system, sans-serif`

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| hero-display | SF Pro Display, system-ui, -apple-system, sans-serif | 56px | 600 | 1.07 | -0.28px |  |
| display-lg | SF Pro Display, system-ui, -apple-system, sans-serif | 40px | 600 | 1.1 | 0 |  |
| display-md | SF Pro Text, system-ui, -apple-system, sans-serif | 34px | 600 | 1.47 | -0.374px |  |
| lead | SF Pro Display, system-ui, -apple-system, sans-serif | 28px | 400 | 1.14 | 0.196px |  |
| lead-airy | SF Pro Text, system-ui, -apple-system, sans-serif | 24px | 300 | 1.5 | 0 |  |
| tagline | SF Pro Display, system-ui, -apple-system, sans-serif | 21px | 600 | 1.19 | 0.231px |  |
| body-strong | SF Pro Text, system-ui, -apple-system, sans-serif | 17px | 600 | 1.24 | -0.374px |  |
| body | SF Pro Text, system-ui, -apple-system, sans-serif | 17px | 400 | 1.47 | -0.374px |  |
| dense-link | SF Pro Text, system-ui, -apple-system, sans-serif | 17px | 400 | 2.41 | 0 |  |
| caption | SF Pro Text, system-ui, -apple-system, sans-serif | 14px | 400 | 1.43 | -0.224px |  |
| caption-strong | SF Pro Text, system-ui, -apple-system, sans-serif | 14px | 600 | 1.29 | -0.224px |  |
| button-large | SF Pro Text, system-ui, -apple-system, sans-serif | 18px | 300 | 1.0 | 0 |  |
| button-utility | SF Pro Text, system-ui, -apple-system, sans-serif | 14px | 400 | 1.29 | -0.224px |  |
| fine-print | SF Pro Text, system-ui, -apple-system, sans-serif | 12px | 400 | 1.0 | -0.12px |  |
| micro-legal | SF Pro Text, system-ui, -apple-system, sans-serif | 10px | 400 | 1.3 | -0.08px |  |
| nav-link | SF Pro Text, system-ui, -apple-system, sans-serif | 12px | 400 | 1.0 | -0.12px |  |


## 4. Component Stylings

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.body}
- **rounded:** {rounded.pill}
- **padding:** 11px 22px

### button-primary-focus

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.pill}

### button-primary-active

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.pill}

### button-secondary-pill

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.primary}
- **typography:** {typography.body}
- **rounded:** {rounded.pill}
- **padding:** 11px 22px

### button-dark-utility

- **backgroundColor:** {colors.ink}
- **textColor:** {colors.on-dark}
- **typography:** {typography.button-utility}
- **rounded:** {rounded.sm}
- **padding:** 8px 15px

### button-pearl-capsule

- **backgroundColor:** {colors.surface-pearl}
- **textColor:** {colors.ink-muted-80}
- **typography:** {typography.caption}
- **rounded:** {rounded.md}
- **padding:** 8px 14px

### button-store-hero

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button-large}
- **rounded:** {rounded.pill}
- **padding:** 14px 28px

### button-icon-circular

- **backgroundColor:** {colors.surface-chip-translucent}
- **textColor:** {colors.ink}
- **rounded:** {rounded.full}
- **size:** 44px

### text-link

- **backgroundColor:** transparent
- **textColor:** {colors.primary}
- **typography:** {typography.body}

### text-link-on-dark

- **backgroundColor:** transparent
- **textColor:** {colors.primary-on-dark}
- **typography:** {typography.body}

### global-nav

- **backgroundColor:** {colors.surface-black}
- **textColor:** {colors.on-dark}
- **typography:** {typography.nav-link}
- **height:** 44px

### sub-nav-frosted

- **backgroundColor:** {colors.canvas-parchment}
- **textColor:** {colors.ink}
- **typography:** {typography.tagline}
- **height:** 52px

### product-tile-light

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.display-lg}
- **rounded:** {rounded.none}
- **padding:** 80px

### product-tile-parchment

- **backgroundColor:** {colors.canvas-parchment}
- **textColor:** {colors.ink}
- **typography:** {typography.display-lg}
- **rounded:** {rounded.none}
- **padding:** 80px

### product-tile-dark

- **backgroundColor:** {colors.surface-tile-1}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-lg}
- **rounded:** {rounded.none}
- **padding:** 80px

### product-tile-dark-2

- **backgroundColor:** {colors.surface-tile-2}
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.none}

### product-tile-dark-3

- **backgroundColor:** {colors.surface-tile-3}
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.none}

### store-utility-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-strong}
- **rounded:** {rounded.lg}
- **padding:** 24px

### configurator-option-chip

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.caption}
- **rounded:** {rounded.pill}
- **padding:** 12px 16px

### configurator-option-chip-selected

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **rounded:** {rounded.pill}

### search-input

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.pill}
- **padding:** 12px 20px
- **height:** 44px

### floating-sticky-bar

- **backgroundColor:** {colors.canvas-parchment}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **height:** 64px
- **padding:** 12px 32px

### environment-quote-card

- **backgroundColor:** {colors.surface-tile-1}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-lg}
- **rounded:** {rounded.none}
- **padding:** 80px

### footer

- **backgroundColor:** {colors.canvas-parchment}
- **textColor:** {colors.ink-muted-80}
- **typography:** {typography.fine-print}
- **padding:** 64px


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
| `none` | 0px |
| `xs` | 5px |
| `sm` | 8px |
| `md` | 11px |
| `lg` | 18px |
| `pill` | 9999px |
| `full` | 9999px |

**Spacing Scale**

| Token | Value |
|---|---|
| `xxs` | 4px |
| `xs` | 8px |
| `sm` | 12px |
| `md` | 17px |
| `lg` | 24px |
| `xl` | 32px |
| `xxl` | 48px |
| `section` | 80px |


## 6. Layout Principles

- **Section rhythm:** `80px` vertical padding between major bands.

### Grid & Container

- **Pure White** (`{colors.canvas}` — #ffffff): The dominant canvas. Content, utility cards, store tiles, configurator grids.
- **Near-Black Tile 1** (`{colors.surface-tile-1}` — #272729): The primary dark-tile surface on the homepage product grid.
- **Card padding:** `{spacing.lg}` (24px) inside utility grid cards.
- **Max content width:** ~980px on text-heavy sections (environment), ~1440px on product grids (store, accessories), full-bleed for product tiles (homepage).
- **Column patterns:** 3 to 5 column utility card grid on store/accessories; 2-column side-by-side tiles on homepage occasional sections; single-column centered stack on product tile heroes.
- **Gutters:** 20–24px between cards in a utility grid.
- **Accessory grid**: square 1:1 crops at `{rounded.lg}` (18px) radius, light neutral backgrounds, product centered with 20–40px internal padding.
- **Product tiles**: stack from 2-column to 1-column at 834px; vertical padding tightens from 80px → 48px at small-phone.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Full-bleed tiles, global nav, footer, body sections |
| Soft hairline | 1px `rgba(0, 0, 0, 0.08)` border | Utility cards, sub-nav frosted-glass separator |
| Backdrop blur | `backdrop-filter: blur(N)` on Parchment 80% | Sub-nav and the iPhone buy floating sticky bar |
| Product shadow | `rgba(0, 0, 0, 0.22) 3px 5px 30px 0` | Product renders resting on a surface (the only true "shadow" in the system) |

**Shadow philosophy.** Apple uses **exactly one** drop-shadow, and it is applied to photographic product imagery — never to cards, never to buttons, never to text. Elevation in the UI comes from (a) surface-color change (light tile ↔ dark tile) and (b) backdrop-blur on sticky bars. The single shadow is about giving the product weight, not about UI hierarchy.


## 8. Do's and Don'ts

### Do
- Use `{colors.primary}` (Action Blue #0066cc) for every interactive element — links, pill CTAs, focus signals — and nothing else. The single accent is non-negotiable.
- Set headlines in `{typography.hero-display}` or `{typography.display-lg}` with negative letter-spacing (`-0.28 → -0.374px`) to get the signature "Apple tight" cadence.
- Run body copy at `{typography.body}` (17px / 400 / 1.47 / -0.374px) — not 16px. The extra pixel defines the brand's reading pace.
- Alternate `{component.product-tile-light}` (or parchment) and `{component.product-tile-dark}` for full-bleed section rhythm. The color change IS the divider.
- Reserve `{rounded.pill}` for the primary blue CTA and any other element that should read as an "action" (configurator chips, search input, sticky bar CTA).
- Apply the single product-shadow (`rgba(0, 0, 0, 0.22) 3px 5px 30px`) only to product renders resting on a surface — never on cards, buttons, or text.
- Use `transform: scale(0.95)` as the active/press state on every button — it's the system-wide micro-interaction.
- Keep the global nav `{colors.surface-black}` (true black) — it's the only place pure black appears on most pages.

### Don't
- Don't introduce a second accent color; every "click me" signal is `{colors.primary}` (Action Blue).
- Don't add shadows to cards, buttons, or text — shadow is reserved for product imagery.
- Don't use gradients as decorative backgrounds; atmosphere comes from photography.
- Don't set body copy at weight 500 — Apple's ladder is 300 / 400 / 600 / 700, with 500 deliberately absent. Body is always 400; strong inline is 600; display is 600.
- Don't round full-bleed tiles — tiles are rectangular and edge-to-edge; the color change is the divider.
- Don't tighten line-height below 1.47 for body copy — the editorial leading is part of the brand.
- Don't mix radii grammars — use `{rounded.sm}` for compact utility, `{rounded.lg}` for utility cards, `{rounded.pill}` for pills, and nothing in between (except the rare `{rounded.md}` Pearl Button).
- Don't use `{colors.primary-on-dark}` (Sky Link Blue) on light surfaces — it's the dark-tile-only variant. Action Blue is for light surfaces.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Small phone | ≤ 419px | Single-column tiles; sub-nav collapses to category name + primary CTA only; hero typography drops to 28px |
| Phone | 420–640px | Single-column stack; product renders scale to 80% of tile width; hero h1 drops to 34px |
| Large phone | 641–735px | Tiles transition to tighter padding (48px vertical vs 80px); fine-print wraps |
| Tablet portrait | 736–833px | Global nav collapses to hamburger; sub-nav hides category chips, keeps primary CTA |
| Tablet landscape | 834–1023px | Global nav returns fully expanded; 3-column utility grids become 2-column |
| Small desktop | 1024–1068px | Product tiles use 2/3 width with margin gutters; hero h1 stays at 40px |
| Desktop | 1069–1440px | Full layout; 4–5 column store grids; 1440px content max |
| Wide desktop | ≥ 1441px | Content locks at 1440px, margins absorb extra width |

The structural breakpoints that matter for agents: 1440px (content lock), 1068px (small-desktop), 833px (tablet landscape switch), 734px (tablet portrait), 640px (phone), 480px (small phone).


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#0066cc`
- Background / Canvas: `#ffffff`
- Heading / Strong text: `#1d1d1f`
- Body / Secondary text: `#1d1d1f`
- Primary Focus: `#0071e3`
- Primary On Dark: `#2997ff`
- Body On Dark: `#ffffff`
- Body Muted: `#cccccc`
- Ink Muted 80: `#333333`
- Ink Muted 48: `#7a7a7a`

### Example Component Prompts

- "Create a hero on the canvas background (`#ffffff`). Headline at 56px using the display font, weight 600, line-height 1.07, color `#1d1d1f` with fallback Google Font. Primary CTA uses `#0066cc` background, white text, 11px radius, and comfortable padding."
- "Design a content card: `#ffffff` background, 1px `#e0e0e0` border, `18px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

