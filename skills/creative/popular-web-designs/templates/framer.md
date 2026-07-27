# Design System: Framer

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `framer/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/framer.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `GT Walsheim Framer Medium` → **Fallback:** `Mona Sans`
> - **Mono:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Mona Sans', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Mona+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Framer's marketing canvas is a near-pure black artboard. The dominant surface is `{colors.canvas}` — almost pure black with a faint warmth — and on top of it sits oversized white display type set in **GT Walsheim Medium** with letter-spacing pulled to extreme negative values (-5.5px on the 110px display, -4.25px on the 85px hero). The page reads like a poster: one assertive statement per band, generous breathing room above and below.

The single accent is `{colors.accent-blue}` — used scarcely, mostly for hyperlinks, selection halos, and a subtle blue-tinted shadow ring on focused inputs. The brand chrome itself is monochrome: white pill buttons, charcoal cards, gray secondary text. What makes Framer distinctive is the rhythm break — every few sections the page drops in a **vibrant gradient atmosphere card**: a magenta-violet spotlight, a sunset-orange wash, a coral-pink panel. These aren't section backgrounds; they're individual cards arranged in a card grid, each one a small living poster that shows what Framer can produce.

Body type is **Inter Variable**, with Framer leaning hard into Inter's character variants (`cv01`, `cv05`, `cv09`, `cv11`, `ss03`, `ss07`, `dlig`) — the result is a body voice that feels custom-tuned, with single-storey "a", straight-leg "l", and tabular figures. There's no light mode on the marketing site; the brand IS dark.

**Key Characteristics:**
- Black-canvas marketing system: `{colors.canvas}` is the surface for hero, body, pricing, FAQ, and footer alike — no light interludes.
- Massive negative letter-spacing on display sizes (-5.5px / -4.25px / -3.1px) creates a poster-grade headline cadence.
- White pill (`{components.button-primary}`) is the only primary CTA shape across the site; secondary actions live as charcoal pills (`{components.button-secondary}`) or text links.
- Oversized **gradient spotlight cards** (violet, magenta, orange, coral) act as showcase tiles inside the dark grid; they are individual cards, not section backgrounds.
- Inter Variable with bespoke OpenType character variants (`cv01/05/09/11`, `ss03/ss07`, `dlig`) used everywhere body type appears — the typographic voice is unmistakable.
- Border radius scale runs from 4px utility chips up to 100px pills and full circles, with 15–20px the default for cards and 30px for atmospheric gradient cards.
- A single chromatic accent `{colors.accent-blue}` reserved for hyperlinks, focus, and selection — never decorative.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#ffffff` — pure/near-white
- **On Primary** (on-primary): `#000000` — near-black
- **Accent Blue** (accent-blue): `#0099ff` — cool blue tint
- **Inverse Canvas** (inverse-canvas): `#ffffff` — pure/near-white
### Surfaces & Backgrounds
- **Canvas** (canvas): `#090909` — near-black
- **Surface 1** (surface-1): `#141414` — near-black
- **Surface 2** (surface-2): `#1c1c1c` — near-black
### Text & Ink
- **Ink** (ink): `#ffffff` — pure/near-white
- **Ink Muted** (ink-muted): `#999999`
- **Inverse Ink** (inverse-ink): `#000000` — near-black
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#262626` — near-black
- **Hairline Soft** (hairline-soft): `#1a1a1a` — near-black
### Semantic & Status
- **Semantic Success** (semantic-success): `#22c55e` — green tint
### Accent / Other
- **Gradient Magenta** (gradient-magenta): `#d44df0` — cool blue tint
- **Gradient Violet** (gradient-violet): `#6a4cf5` — cool blue tint
- **Gradient Orange** (gradient-orange): `#ff7a3d` — warm red/orange tint
- **Gradient Coral** (gradient-coral): `#ff5577` — warm red/orange tint

## 3. Typography Rules

### Font Family
- **Primary:** `GT Walsheim Framer Medium`

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-xxl | GT Walsheim Framer Medium | 110px | 500 | 0.85 | -5.5px |  |
| display-xl | GT Walsheim Medium | 85px | 500 | 0.95 | -4.25px | ss02 |
| display-lg | GT Walsheim Medium | 62px | 500 | 1.0 | -3.1px | ss02 |
| display-md | GT Walsheim Medium | 32px | 500 | 1.13 | -1.0px |  |
| headline | Inter | 22px | 700 | 1.2 | -0.8px | cv05 |
| subhead | Inter Variable | 24px | 400 | 1.3 | -0.01px | cv11 |
| body-lg | Inter Variable | 18px | 400 | 1.3 | -0.18px | cv11 |
| body | Inter Variable | 15px | 400 | 1.3 | -0.15px | cv11 |
| body-sm | Inter Variable | 14px | 500 | 1.4 | -0.14px | cv11 |
| caption | Inter Variable | 13px | 500 | 1.2 | -0.13px | cv11 |
| micro | Inter Variable | 12px | 400 | 1.2 | -0.12px | cv11 |
| button | Inter Variable | 14px | 500 | 1.0 | -0.14px | cv11 |


## 4. Component Stylings

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 10px 15px

### button-primary-pressed

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}

### button-secondary

- **backgroundColor:** {colors.surface-1}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 10px 15px

### button-translucent

- **backgroundColor:** {colors.surface-2}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.xxl}
- **padding:** 8px 14px

### button-icon-circular

- **backgroundColor:** {colors.surface-1}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.full}
- **size:** 40px

### pricing-tab-default

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink-muted}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 8px 14px

### pricing-tab-selected

- **backgroundColor:** {colors.surface-2}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 8px 14px

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

### pricing-card

- **backgroundColor:** {colors.surface-1}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.xl}
- **padding:** 24px

### pricing-card-featured

- **backgroundColor:** {colors.surface-2}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.xl}
- **padding:** 24px

### template-card

- **backgroundColor:** {colors.surface-1}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.lg}
- **padding:** 12px

### gradient-spotlight-card

- **backgroundColor:** {colors.gradient-violet}
- **textColor:** {colors.ink}
- **typography:** {typography.subhead}
- **rounded:** {rounded.xl}
- **padding:** 32px

### gradient-spotlight-card-magenta

- **backgroundColor:** {colors.gradient-magenta}
- **textColor:** {colors.ink}
- **typography:** {typography.subhead}
- **rounded:** {rounded.xl}
- **padding:** 32px

### gradient-spotlight-card-orange

- **backgroundColor:** {colors.gradient-orange}
- **textColor:** {colors.ink}
- **typography:** {typography.subhead}
- **rounded:** {rounded.xl}
- **padding:** 32px

### product-mockup-tile

- **backgroundColor:** {colors.surface-1}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.xl}
- **padding:** 16px

### feature-row

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.xs}

### comparison-row

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink-muted}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.xs}

### top-nav

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.xs}
- **height:** 56px

### faq-row

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body}
- **rounded:** {rounded.md}
- **padding:** 24px

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
| `md` | 10px |
| `lg` | 15px |
| `xl` | 20px |
| `xxl` | 30px |
| `pill` | 100px |
| `full` | 9999px |

**Spacing Scale**

| Token | Value |
|---|---|
| `hair` | 1px |
| `xxs` | 4px |
| `xs` | 8px |
| `sm` | 12px |
| `md` | 15px |
| `lg` | 20px |
| `xl` | 30px |
| `xxl` | 40px |
| `section` | 96px |


## 6. Layout Principles

- **Section rhythm:** `96px` vertical padding between major bands.

### Grid & Container

- Oversized **gradient spotlight cards** (violet, magenta, orange, coral) act as showcase tiles inside the dark grid; they are individual cards, not section backgrounds.
- **Inverse Canvas** ({colors.inverse-canvas}): Pure white — used as the surface of light-on-dark pill CTAs and a small set of light-mode template thumbnails embedded in the showcase grid.
- Max content width sits around the 1199px breakpoint, with side gutters that scale toward `{spacing.xl}` on desktop.
- Card grids on the home gallery use 2-up at desktop, collapsing to 1-up below 810px.
- Pricing tier grid is 4-up across the documented breakpoints; comparison table beneath it uses fixed-width left column with horizontally scrolling tier columns at narrow widths.
- Drop one or two `gradient-spotlight-card` variants into a card grid; they are the brand's atmosphere device. Don't overdo it — three or more in the same viewport reads as a moodboard, not a system.
- **Card grids**: the gallery and template-card grids go 2-up on desktop → 1-up on mobile. Gradient spotlight cards retain `{rounded.xxl}` corners at every viewport — they don't bleed.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| 0 (flat) | No shadow, no border | Default for canvas-mounted display type, FAQ rows, footer |
| 1 (charcoal) | `{colors.surface-1}` lift on canvas | Pricing cards, mockup tiles, secondary buttons |
| 2 (light-edge) | `rgba(255,255,255,0.10)` 0.5px top edge + `rgba(0,0,0,0.25)` 0px 10px 30px drop | Floating product cards, modal cards |
| 3 (selected) | `rgba(0,153,255,0.15)` 0px 0px 0px 1px ring | Focused inputs, selected option |

Four shadow signatures recur across the homepage: a 1px subtle drop, a translucent blue ring, a thick near-black 2px outline (used as the active-element marker on sub-nav), and the layered light-edge + drop-shadow used for floating cards.


## 8. Do's and Don'ts

### Do

- Reserve `{colors.primary}` (white) and `{colors.canvas}` (near-black) as the system's two anchor surfaces. Every band of the page chooses one or the other.
- Push display-size letter-spacing aggressively negative — `{typography.display-xxl}` at -5.5px is the brand signature, not a stylistic accident.
- Use `{colors.accent-blue}` only for hyperlinks, focus rings, and selected indicators. Never as a background or button fill.
- Drop one or two `gradient-spotlight-card` variants into a card grid; they are the brand's atmosphere device. Don't overdo it — three or more in the same viewport reads as a moodboard, not a system.
- Compose every CTA as a pill (`{rounded.pill}`); secondary actions live as charcoal pills, never as bordered ghost buttons.
- Keep body type Inter Variable with character variants `cv01`, `cv05`, `cv09`, `cv11`, `ss03`, `ss07` enabled — the brand voice depends on them.
- Use surface lift (canvas → surface-1 → surface-2) to mark hierarchy on dark, not opacity changes on white type.

### Don't

- Don't ship a light-mode marketing page. Framer's identity is dark.
- Don't introduce mid-tone gray text outside `{colors.ink-muted}`. The hierarchy is binary: `ink` or `ink-muted`.
- Don't use `{colors.accent-blue}` as a brand fill (e.g., a blue CTA pill). The blue is a signal color, not a surface.
- Don't square off CTAs. Pill (`{rounded.pill}`) or full circle is the brand vocabulary.
- Don't reduce the negative letter-spacing on display sizes "for accessibility". The compression is intrinsic to the brand voice; reduce the SIZE if needed, but keep the percentage.
- Don't apply gradient backgrounds to whole sections. Gradients are CARDS, not section grounds.
- Don't combine more than one chromatic accent. The palette is monochrome plus one blue plus the gradient family — not "blue, green, and red".


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Desktop | 1199px | Default desktop layout |
| Tablet | 810px | Card grids collapse 4-up → 2-up; nav becomes hamburger |
| Mobile-Lg | 809px | Pricing comparison table becomes per-tier accordion |
| Mobile-XS | 98px | Smallest documented breakpoint — single-column everything |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#ffffff`
- Background / Canvas: `#090909`
- Heading / Strong text: `#ffffff`
- On Primary: `#000000`
- Accent Blue: `#0099ff`
- Ink Muted: `#999999`
- Surface 1: `#141414`
- Surface 2: `#1c1c1c`
- Hairline: `#262626`

### Example Component Prompts

- "Create a hero on the canvas background (`#090909`). Headline at 110px using the display font, weight 500, line-height 0.85, color `#ffffff` with fallback Google Font. Primary CTA uses `#ffffff` background, white text, 10px radius, and comfortable padding."
- "Design a content card: `#090909` background, 1px `#262626` border, `15px` radius, padding `20px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

