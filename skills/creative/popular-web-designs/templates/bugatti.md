# Design System: Bugatti

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `bugatti/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/bugatti.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `Bugatti Display` → **Fallback:** `Inter`
> - **Original mono family:** `Bugatti Monospace` → **Fallback:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Bugatti's marketing surface is the most austere interface in luxury automotive: a near-pure black canvas (`{colors.canvas}` — #000000) holding white uppercase **letterspaced** display type and full-bleed automotive photography. The system has no accent color, no surface card decoration, no shadows, no gradients, no chrome — only **photography, typography, and the brand wordmark**. Every other luxury auto site in this category (BMW M, Aston Martin, Lamborghini) uses some form of accent color or signature element; Bugatti uses nothing. The empty space, the photograph, and the precisely-tracked Bugatti Display headline ARE the brand.

The system runs **three custom Bugatti typefaces**: **Bugatti Display** (display headlines, the "BUGATTI" wordmark, all caps with wide tracking), **Bugatti Text Regular** (body paragraphs, a serif text face), and **Bugatti Monospace** (button labels, navigation, captions, dates — anywhere precision and machined feel matters). The split is deliberate and unbreakable: never use Bugatti Text in a button, never use Bugatti Monospace in a paragraph.

Display sizes use weight 400 (regular) — never bold. Visual emphasis comes from **size and tracking**, not weight. Letter-spacing on the wordmark is 6px; on display headlines 2-4px; on uppercase labels 2-2.5px. Tight tracking is a brand violation. The wide spacing creates the "engineered precision" feel that no other luxury maker matches.

**Key Characteristics:**
- Pure black canvas (`{colors.canvas}` — #000000) with white type. The system does not have a light mode.
- Three custom Bugatti typefaces: **Display** (uppercase headlines + wordmark), **Text Regular** (body serif), **Monospace** (buttons, captions, nav).
- All display headlines are UPPERCASE with wide letter-spacing (2-4px). Body copy stays sentence-case at standard tracking.
- No accent color. The only non-monochrome color anywhere on the site is `{colors.link}` (#c3d9f3) — a desaturated ice-blue used on inline anchor links, and even that appears rarely.
- Buttons are pill-shaped (`{rounded.pill}`) with **transparent background** and a 1px white outline. Bugatti is the only luxury-auto brand whose primary CTA is fully transparent.
- Photography is the only depth element. No drop shadows. No gradients. No card surfaces. Surface cards are `{colors.surface-card}` (#141414) at most — a barely-different-from-black tone.
- Section rhythm is generous — `{spacing.section}` (120px) between major bands, longer than most marketing sites because Bugatti's pages are mostly photography with minimal text density.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#ffffff` — pure/near-white
- **On Primary** (on-primary): `#000000` — near-black
### Surfaces & Backgrounds
- **Canvas** (canvas): `#000000` — near-black
- **Surface Soft** (surface-soft): `#0d0d0d` — near-black
- **Surface Card** (surface-card): `#141414` — near-black
- **Surface Elevated** (surface-elevated): `#1f1f1f` — near-black
### Text & Ink
- **Ink** (ink): `#ffffff` — pure/near-white
- **Body** (body): `#cccccc`
- **Body Strong** (body-strong): `#e6e6e6`
- **Muted** (muted): `#999999`
- **Muted Soft** (muted-soft): `#666666`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
- **On Photo** (on-photo): `#ffffff` — pure/near-white
- **Link** (link): `#c3d9f3`
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#262626` — near-black
- **Hairline Strong** (hairline-strong): `#3a3a3a`
### Semantic & Status
- **Warning** (warning): `#d4a017` — warm red/orange tint
- **Success** (success): `#5fa657` — green tint

## 3. Typography Rules

### Font Family
- **Primary:** `Bugatti Display, sans-serif`
- **Monospace:** used for code/terminal surfaces.

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-xl | Bugatti Display, sans-serif | 64px | 400 | 1.1 | 4px |  |
| display-lg | Bugatti Display, sans-serif | 48px | 400 | 1.15 | 3px |  |
| display-md | Bugatti Display, sans-serif | 32px | 400 | 1.2 | 2px |  |
| display-sm | Bugatti Display, sans-serif | 24px | 400 | 1.3 | 1.5px |  |
| wordmark | Bugatti Display, serif | 14px | 400 | 1 | 6px |  |
| title-md | Bugatti Display, sans-serif | 20px | 400 | 1.3 | 1px |  |
| title-sm | Bugatti Display, sans-serif | 16px | 400 | 1.3 | 1.5px |  |
| caption-uppercase | Bugatti Monospace, ui-monospace, monospace | 11px | 400 | 1.4 | 2px |  |
| body-md | Bugatti Text Regular, serif | 16px | 400 | 1.5 | 0 |  |
| body-sm | Bugatti Text Regular, serif | 14px | 400 | 1.5 | 0 |  |
| button | Bugatti Monospace, ui-monospace, monospace | 14px | 400 | 1 | 2.5px |  |
| nav-link | Bugatti Monospace, ui-monospace, monospace | 12px | 400 | 1.4 | 2px |  |


## 4. Component Stylings

### button-primary

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 14px 32px
- **height:** 44px

### button-icon

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.full}
- **size:** 40px

### text-link

- **backgroundColor:** transparent
- **textColor:** {colors.link}
- **typography:** {typography.button}

### top-nav

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.nav-link}
- **height:** 56px

### wordmark-display

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.wordmark}

### hero-photo-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-xl}
- **padding:** 96px

### caption-overlay

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.caption-uppercase}

### career-callout-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.none}
- **padding:** 16px
- **width:** 320px

### model-photo-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-md}
- **rounded:** {rounded.none}

### newsroom-article-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **rounded:** {rounded.none}
- **padding:** 24px

### career-listing-row

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **padding:** 24px 0

### text-input

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.body-md}
- **rounded:** {rounded.none}
- **padding:** 12px 0
- **height:** 44px

### spec-cell

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **padding:** 24px 0

### date-pill

- **backgroundColor:** transparent
- **textColor:** {colors.muted}
- **typography:** {typography.caption-uppercase}

### category-tag

- **backgroundColor:** transparent
- **textColor:** {colors.muted}
- **typography:** {typography.caption-uppercase}

### cta-band-photo

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-md}
- **padding:** 80px

### footer

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.muted}
- **typography:** {typography.body-sm}
- **padding:** 64px


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
| `none` | 0px |
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
| `xl` | 40px |
| `xxl` | 64px |
| `section` | 120px |


## 6. Layout Principles

- **Section rhythm:** `120px` vertical padding between major bands.

### Grid & Container

- **Gutters:** `{spacing.xl}` (40px) between cards in 2-up grids — wider than typical because Bugatti's grids are sparse.
- **Max content width:** ~1280px centered. Hero photo bands bleed full-width with no max.
- **Editorial body:** Single 12-column grid; photo bands are full-bleed.
- **Newsroom layout:** 2-up article grid at desktop, 1-up at tablet+mobile.
- **Career listings:** Single column with 80px row spacing.
- 2-up newsroom grid collapses to 1-up at < 768px.
- Spec cells reflow from 4-up to 2-up to 1-up; values stay at the same display size regardless of column count.
- The configurator surface (vehicle build pages with custom paint / interior pickers) was not in the analyzed URL set; its swatch grid, customization controls, and price-summary card are not documented here.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Body, top nav, footer, photo bands |
| Soft hairline | 1px `{colors.hairline}` border | Section dividers, table rows |
| Card surface | `{colors.surface-card}` background — no shadow | Career callout, newsroom article container |
| Photographic depth | Full-bleed photography with edge-to-edge crop | Hero bands, model showcases — depth via subject + lens, not chrome |

The system uses no shadows, no glassmorphism, no gradients. Depth comes entirely from photography (lighting, lens, subject framing) and from the contrast between black canvas and minimally-elevated `{colors.surface-card}`.


## 8. Do's and Don'ts

### Do
- Anchor every page with full-bleed automotive photography. The cars are the brand voltage; chrome backs off entirely.
- Keep all display headlines in UPPERCASE Bugatti Display with 2-4px letter-spacing. The wordmark gets 6px.
- Use Bugatti Display for headlines, Bugatti Text Regular (serif!) for body, Bugatti Monospace for buttons + captions + nav. The trinity is unbreakable.
- Keep `{component.button-primary}` transparent with a 1px white outline. The transparent pill IS the brand button.
- Use weight 400 everywhere. Bold breaks the brand voice — the system has no bold weight role.
- Use `{spacing.section}` (120px) between major editorial bands. The whitespace is part of the brand.
- Reserve `{colors.link}` (#c3d9f3) for inline anchor links only. It's the system's only non-monochrome color.

### Don't
- Don't introduce any accent color outside `{colors.link}`. Bugatti's brand discipline is total monochrome + photography. Adding a brand-blue or brand-red breaks the contract.
- Don't bold any type. The system has no bold weight — every typeface stays at 400.
- Don't fill primary buttons. Transparent + outline only. A solid white button reads as off-brand.
- Don't compress whitespace between sections. The 120px rhythm is part of the editorial pacing.
- Don't use rounded corners outside buttons. Cards, photos, inputs all stay at 0px. Rounded cards read as consumer-tech, not luxury-engineered.
- Don't tighten letter-spacing on display headlines. 2-4px tracking on Bugatti Display is non-negotiable.
- Don't use Bugatti Display in a button (use Bugatti Monospace) or Bugatti Monospace in a paragraph (use Bugatti Text Regular). The trinity split is the brand voice.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 768px | Hamburger nav; hero h1 64→32px; career callout card hides; photo bands stay full-bleed; footer 4 cols → 1 |
| Tablet | 768–1024px | Top nav stays minimal (MENU + wordmark + STORE); 2-up newsroom grid; career rows full-width |
| Desktop | 1024–1440px | Full minimal top-nav; 2-up newsroom grid; spec tables 4-up |
| Wide | > 1440px | Same as desktop with more breathing room; max content 1280px |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#ffffff`
- Background / Canvas: `#000000`
- Heading / Strong text: `#ffffff`
- Body / Secondary text: `#cccccc`
- Body Strong: `#e6e6e6`
- Muted: `#999999`
- Muted Soft: `#666666`
- Hairline: `#262626`
- Hairline Strong: `#3a3a3a`
- Surface Soft: `#0d0d0d`

### Example Component Prompts

- "Create a hero on the canvas background (`#000000`). Headline at 64px using the display font, weight 400, line-height 1.1, color `#ffffff` with fallback Google Font. Primary CTA uses `#ffffff` background, white text, 8px radius, and comfortable padding."
- "Design a content card: `#141414` background, 1px `#262626` border, `12px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

