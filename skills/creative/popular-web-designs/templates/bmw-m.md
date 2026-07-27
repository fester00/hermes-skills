# Design System: BMW M

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `bmw-m/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/bmw-m.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `BMWTypeNextLatin` → **Fallback:** `Inter`
> - **Mono:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

BMW M's marketing surface is a near-pure black canvas (`{colors.canvas}` — #000) holding white BMW Type Next Latin headlines in **confident UPPERCASE**. The system has no decorative voltage of its own; brand energy comes from **full-bleed automotive photography** — cars cornering at speed, carbon-fiber wheel detail, driver cockpit shots, motorsport pit lanes — placed as edge-to-edge content that fills entire bands. UI chrome around the photography stays minimal: thin sans-serif copy, dividers as 1px hairlines (`{colors.hairline}`), all-caps button labels with no fill until hovered.

The **M tricolor stripe** — `{colors.m-blue-light}` (#0066b1) → `{colors.m-blue-dark}` (#1c69d4) → `{colors.m-red}` (#e22718) — appears sparingly as the brand's signature accent, used on the M wordmark, motorsport chrome, vehicle-tech callouts, and model badges. It is never a CTA color and never used as a background fill — the tricolor is exclusively a brand-identity marker.

Type voice runs **BMW Type Next Latin** in two cuts: regular for display + nav labels and Light for body + secondary copy. Display sizes use weight 700 (BMW's signature heavy-but-tight setting), while body type drops to weight 300 (Light). The contrast between heavy display and light body is the system's editorial signature.

**Key Characteristics:**
- Near-pure black canvas (`{colors.canvas}` — #000) with white type. The system inverts almost nothing — there is no light-mode marketing surface.
- Display headlines in UPPERCASE BMW Type Next Latin at weight 700. Sub-heads stay sentence-case at lighter weight.
- M tricolor (`{colors.m-blue-light}` / `{colors.m-blue-dark}` / `{colors.m-red}`) used as 4px brand-stripe dividers, M-wordmark accents, and motorsport chrome — never as buttons or fills.
- Photography fills entire bands edge-to-edge. Cars are always the visual subject; UI chrome backs off to small white labels overlaid on photography.
- Buttons are flat with `{rounded.none}` (0px) corners and uppercase letterspaced labels. The "industrial precision" rectangular silhouette IS the brand.
- Border radius is mostly zero across the system. The few exceptions: `{rounded.full}` on circular icon buttons (carousel arrows, chatbot launcher) and `{rounded.sm}` on a handful of small toggle pills.
- Spacing is generous and grid-aligned: `{spacing.section}` (96px) between major bands; `{spacing.xxl}` (64px) inside hero photo bands; `{spacing.xl}` (40px) inside content cards.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#ffffff` — pure/near-white
- **On Primary** (on-primary): `#000000` — near-black
### Surfaces & Backgrounds
- **Canvas** (canvas): `#000000` — near-black
- **Surface Card** (surface-card): `#1a1a1a` — near-black
- **Surface Elevated** (surface-elevated): `#262626` — near-black
- **Surface Soft** (surface-soft): `#0d0d0d` — near-black
### Text & Ink
- **Ink** (ink): `#ffffff` — pure/near-white
- **Body** (body): `#bbbbbb`
- **Body Strong** (body-strong): `#e6e6e6`
- **Muted** (muted): `#7e7e7e`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
- **Carbon Gray** (carbon-gray): `#2b2b2b`
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#3c3c3c`
- **Hairline Strong** (hairline-strong): `#262626` — near-black
### Semantic & Status
- **Warning** (warning): `#f4b400` — warm red/orange tint
- **Success** (success): `#0fa336` — green tint
### Accent / Other
- **M Blue Light** (m-blue-light): `#0066b1` — cool blue tint
- **M Blue Dark** (m-blue-dark): `#1c69d4` — cool blue tint
- **M Red** (m-red): `#e22718` — warm red/orange tint
- **Bmw Blue** (bmw-blue): `#1c69d4` — cool blue tint
- **Electric Blue** (electric-blue): `#0653b6` — cool blue tint

## 3. Typography Rules

### Font Family
- **Primary:** `BMWTypeNextLatin, sans-serif`

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-xl | BMWTypeNextLatin, sans-serif | 80px | 700 | 1 | 0 |  |
| display-lg | BMWTypeNextLatin, sans-serif | 56px | 700 | 1.05 | 0 |  |
| display-md | BMWTypeNextLatin, sans-serif | 40px | 700 | 1.1 | 0 |  |
| display-sm | BMWTypeNextLatin, sans-serif | 32px | 700 | 1.15 | 0 |  |
| title-lg | BMWTypeNextLatin, sans-serif | 24px | 700 | 1.3 | 0 |  |
| title-md | BMWTypeNextLatin, sans-serif | 20px | 400 | 1.4 | 0 |  |
| title-sm | BMWTypeNextLatin, sans-serif | 18px | 400 | 1.4 | 0 |  |
| label-uppercase | BMWTypeNextLatin, sans-serif | 14px | 700 | 1.3 | 1.5px |  |
| body-md | BMWTypeNextLatin Light, BMWTypeNextLatin, sans-serif | 16px | 300 | 1.5 | 0 |  |
| body-sm | BMWTypeNextLatin Light, sans-serif | 14px | 300 | 1.5 | 0 |  |
| caption | BMWTypeNextLatin, sans-serif | 12px | 400 | 1.4 | 0.5px |  |
| button | BMWTypeNextLatin, sans-serif | 14px | 700 | 1 | 1.5px |  |
| nav-link | BMWTypeNextLatin, sans-serif | 14px | 400 | 1.4 | 0.5px |  |


## 4. Component Stylings

### button-primary

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.button}
- **rounded:** {rounded.none}
- **padding:** 16px 32px
- **height:** 48px

### button-primary-outline

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.button}
- **rounded:** {rounded.none}
- **padding:** 16px 32px
- **height:** 48px

### button-on-light

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.button}
- **rounded:** {rounded.none}
- **padding:** 16px 32px

### button-icon

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.full}
- **size:** 48px

### text-link

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.label-uppercase}

### top-nav

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.nav-link}
- **height:** 64px

### hero-photo-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-xl}
- **padding:** 96px

### m-stripe-divider

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **height:** 4px

### feature-photo-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **rounded:** {rounded.none}
- **padding:** 24px

### model-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-lg}
- **rounded:** {rounded.none}
- **padding:** 24px

### magazine-article-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **rounded:** {rounded.none}
- **padding:** 24px

### spec-cell

- **backgroundColor:** {colors.surface-soft}
- **textColor:** {colors.on-dark}
- **typography:** {typography.body-md}
- **rounded:** {rounded.none}
- **padding:** 24px

### cookie-consent-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.none}
- **padding:** 24px

### category-tab

- **backgroundColor:** transparent
- **textColor:** {colors.body}
- **typography:** {typography.label-uppercase}
- **padding:** 12px 0

### category-tab-active

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.label-uppercase}
- **padding:** 12px 0

### text-input

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **typography:** {typography.body-md}
- **rounded:** {rounded.none}
- **padding:** 12px 16px
- **height:** 48px

### chatbot-launcher

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **rounded:** {rounded.none}
- **padding:** 24px

### cta-band-photo

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-md}
- **padding:** 80px

### motorsport-photo-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **rounded:** {rounded.none}

### carousel-arrow

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.full}
- **size:** 48px

### footer

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.body}
- **typography:** {typography.body-sm}
- **padding:** 64px


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
| `none` | 0px |
| `xs` | 2px |
| `sm` | 4px |
| `md` | 6px |
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
| `section` | 96px |


## 6. Layout Principles

- **Section rhythm:** `96px` vertical padding between major bands.

### Grid & Container

- Spacing is generous and grid-aligned: `{spacing.section}` (96px) between major bands; `{spacing.xxl}` (64px) inside hero photo bands; `{spacing.xl}` (40px) inside content cards.
- **Gutters:** `{spacing.lg}` (24px) between cards in 3-up grids; `{spacing.md}` (16px) inside footer columns.
- **Editorial body:** Single 12-column grid; photo bands bleed full-bleed (no max-width).
- **Card grids:** 3-up at desktop, 2-up at tablet, 1-up at mobile.
- **Footer:** 4-column link list at desktop, 2-up at tablet, 1-up at mobile.
- Use `{spacing.section}` (96px) between major editorial bands for grid-aligned vertical rhythm.
- Don't repeat the same surface mode in two consecutive bands. Rhythm: photo band → spec table → photo band → magazine grid → photo band. Two text-only bands in a row read as a corporate site.
- Card grids reduce columns rather than scaling cards down; photography retains its native aspect ratio.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Body sections, top nav, footer, photo bands |
| Soft hairline | 1px `{colors.hairline}` border | Section dividers, card outlines, table rows |
| Card surface | `{colors.surface-card}` background over canvas — no shadow | Feature photo cards, magazine cards, chatbot launcher |
| Photographic depth | Full-bleed photography with edge-to-edge crop | Hero bands, motorsport features — depth via subject matter, not chrome |

The system uses no drop shadows and no layered chrome. Depth comes entirely from photography (subject + lens + lighting) and the contrast between black canvas and slightly-elevated `{colors.surface-card}`.


## 8. Do's and Don'ts

### Do
- Anchor every page with full-bleed automotive photography. The cars are the brand voltage; chrome backs off.
- Use UPPERCASE display headlines in `{typography.display-xl}` or `{typography.display-lg}`. Sentence-case display reads as off-brand.
- Pair heavy display (700) with light body (300). The weight contrast is the editorial signature.
- Reserve the M tricolor stripe for brand-identity moments — wordmark accents, motorsport chrome, model badges. Never as a button fill or surface.
- Use `{rounded.none}` (0px) by default. Reserve `{rounded.full}` for circular icon buttons only.
- Letter-space all-caps labels at 1.5px. The "machined" feel is non-negotiable.
- Use `{spacing.section}` (96px) between major editorial bands for grid-aligned vertical rhythm.

### Don't
- Don't introduce a brand color outside the M tricolor (`{colors.m-blue-light}` / `{colors.m-blue-dark}` / `{colors.m-red}`) and the heritage `{colors.bmw-blue}`.
- Don't bold body type. Body stays at 300 (Light) — bumping to 400 or 500 makes the page feel marketing-bombastic instead of European-engineered.
- Don't use rounded buttons. The rectangular silhouette IS the brand. Rounded corners read as consumer-tech, not motorsport.
- Don't put gradient backdrops behind hero type. The hero IS the photography — the page floor stays pure black, and the photo provides the depth.
- Don't repeat the same surface mode in two consecutive bands. Rhythm: photo band → spec table → photo band → magazine grid → photo band. Two text-only bands in a row read as a corporate site.
- Don't use the M stripe as a button fill. The stripe is a divider / accent — never an action surface.
- Don't bold uppercase tracking under 1.5px on button labels — the spacing is what makes them feel "machined."


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 768px | Hamburger nav; hero h1 scales 80→48px; demo grid 1-up; photo cards stack full-width; footer 4 cols → 1 |
| Tablet | 768–1024px | Top nav stays horizontal but tightens; 2-up card grids; spec tables 2-up |
| Desktop | 1024–1440px | Full top-nav; 3-up card grids; spec tables 4-up |
| Wide | > 1440px | Same as desktop with more breathing room; max content 1440px |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#ffffff`
- Background / Canvas: `#000000`
- Heading / Strong text: `#ffffff`
- Body / Secondary text: `#bbbbbb`
- Body Strong: `#e6e6e6`
- Muted: `#7e7e7e`
- Hairline: `#3c3c3c`
- Hairline Strong: `#262626`
- Surface Card: `#1a1a1a`
- Surface Elevated: `#262626`

### Example Component Prompts

- "Create a hero on the canvas background (`#000000`). Headline at 80px using the display font, weight 700, line-height 1, color `#ffffff` with fallback Google Font. Primary CTA uses `#ffffff` background, white text, 6px radius, and comfortable padding."
- "Design a content card: `#1a1a1a` background, 1px `#3c3c3c` border, `12px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

