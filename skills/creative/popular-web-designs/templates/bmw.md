# Design System: BMW

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `bmw/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/bmw.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `BMW Type Next Latin` → **Fallback:** `Inter`
> - **Mono:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

BMW's corporate site carries a far more **measured, corporate-automotive** interface than its motorsport-bombastic cousin BMW M. The atmosphere is light: `{colors.canvas}` (#ffffff) is the base surface, `{colors.surface-card}` (#fafafa) carries the soft-grey card plates, and dark navy `{colors.surface-dark}` (#1a2129) appears only inside hero bands — one per page, framing the lead model render.

Type runs BMW's licensed **BMW Type Next Latin** at two weights: heavy 700 (display + button + nav) and Light 300 (body + secondary copy). That contrast — heavy display next to thin paragraph — is the editorial signature, channeling the brand's "European-engineered" voice. Weight 500 is deliberately absent; weight 400 only appears on caption and nav-link in neutral utility contexts.

The brand action color, **BMW corporate blue** (`{colors.primary}` — #1c69d4), works alone across every primary CTA — buttons are **rectangular, 0px corner**, with white type. The site rotates a blue-button + dark-navy-hero combination across page rhythm. The M tricolor stripe (`{colors.m-blue-light}` → `{colors.m-blue-dark}` → `{colors.m-red}`) only appears in motorsport contexts and as M-model badges/dividers — never in the corporate site's main language.

The configuration and reservation flows add a dealer-side inventory UI on top of the same system — filter chips, model cards, price tables — but typography and color stay identical; only density goes up.

**Key Characteristics:**
- Light `{colors.canvas}` is the base surface; dark navy `{colors.surface-dark}` appears only inside hero bands — page rhythm relies on contrast.
- BMW corporate blue (`{colors.primary}` — #1c69d4) acts as the single primary action color.
- BMW Type Next Latin: weight 700 display against weight 300 body is the signature.
- Buttons are **rectangular, 0px radius** — corporate dialect, distinct from M's sportier radii.
- Model cards run as 4-up or 5-up grids with no hairline border or only minimal border — just white plate + photo + title.
- Photography (model renders) sits in environment, no shadow — depth comes entirely from color-block contrast.
- M tricolor stripe appears only in M-model contexts — not part of the corporate language.
- Section rhythm holds at `{spacing.section}` (80px) for every major band.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#1c69d4` — cool blue tint
- **Primary Active** (primary-active): `#0653b6` — cool blue tint
- **Primary Disabled** (primary-disabled): `#d6d6d6`
- **On Primary** (on-primary): `#ffffff` — pure/near-white
### Surfaces & Backgrounds
- **Canvas** (canvas): `#ffffff` — pure/near-white
- **Surface Soft** (surface-soft): `#f7f7f7` — pure/near-white
- **Surface Card** (surface-card): `#fafafa` — pure/near-white
- **Surface Strong** (surface-strong): `#ebebeb`
- **Surface Dark** (surface-dark): `#1a2129`
- **Surface Dark Elevated** (surface-dark-elevated): `#262e38`
### Text & Ink
- **Ink** (ink): `#262626` — near-black
- **Body** (body): `#3c3c3c`
- **Body Strong** (body-strong): `#1a1a1a` — near-black
- **Muted** (muted): `#6b6b6b`
- **Muted Soft** (muted-soft): `#9a9a9a`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
- **On Dark Soft** (on-dark-soft): `#bbbbbb`
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#e6e6e6`
- **Hairline Strong** (hairline-strong): `#cccccc`
### Semantic & Status
- **Success** (success): `#22c55e` — green tint
- **Warning** (warning): `#f59e0b` — warm red/orange tint
- **Error** (error): `#dc2626` — warm red/orange tint
### Accent / Other
- **M Blue Light** (m-blue-light): `#0066b1` — cool blue tint
- **M Blue Dark** (m-blue-dark): `#1c69d4` — cool blue tint
- **M Red** (m-red): `#e22718` — warm red/orange tint

## 3. Typography Rules

### Font Family
- **Primary:** `'BMW Type Next Latin', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-xl | 'BMW Type Next Latin', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif | 64px | 700 | 1.05 | 0 |  |
| display-lg | 'BMW Type Next Latin', sans-serif | 48px | 700 | 1.1 | 0 |  |
| display-md | 'BMW Type Next Latin', sans-serif | 32px | 700 | 1.15 | 0 |  |
| display-sm | 'BMW Type Next Latin', sans-serif | 24px | 700 | 1.25 | 0 |  |
| title-lg | 'BMW Type Next Latin', sans-serif | 20px | 700 | 1.3 | 0 |  |
| title-md | 'BMW Type Next Latin', sans-serif | 18px | 700 | 1.4 | 0 |  |
| title-sm | 'BMW Type Next Latin', sans-serif | 16px | 700 | 1.4 | 0 |  |
| body-md | 'BMW Type Next Latin', sans-serif | 16px | 300 | 1.55 | 0 |  |
| body-sm | 'BMW Type Next Latin', sans-serif | 14px | 300 | 1.55 | 0 |  |
| caption | 'BMW Type Next Latin', sans-serif | 12px | 400 | 1.4 | 0.5px |  |
| label-uppercase | 'BMW Type Next Latin', sans-serif | 13px | 700 | 1.3 | 1.5px | uppercase |
| button | 'BMW Type Next Latin', sans-serif | 14px | 700 | 1.0 | 0.5px |  |
| nav-link | 'BMW Type Next Latin', sans-serif | 14px | 400 | 1.4 | 0.3px |  |


## 4. Component Stylings

### top-nav

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.nav-link}
- **height:** 64px

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.none}
- **padding:** 14px 32px
- **height:** 48px

### button-primary-active

- **backgroundColor:** {colors.primary-active}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.none}

### button-primary-disabled

- **backgroundColor:** {colors.primary-disabled}
- **textColor:** {colors.muted}
- **rounded:** {rounded.none}

### button-secondary

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.none}
- **padding:** 13px 31px
- **height:** 48px

### button-secondary-on-dark

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.button}
- **rounded:** {rounded.none}
- **padding:** 13px 31px

### button-text-link

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.label-uppercase}

### text-link

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}

### hero-band-dark

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-xl}
- **padding:** 80px

### hero-photo-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.display-lg}
- **padding:** 80px

### model-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.none}
- **padding:** 24px

### model-card-photo

- **backgroundColor:** {colors.surface-card}
- **rounded:** {rounded.none}

### feature-photo-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.none}
- **padding:** 24px

### spec-cell

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.display-sm}
- **rounded:** {rounded.none}
- **padding:** 24px

### inventory-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.title-sm}
- **rounded:** {rounded.none}
- **padding:** 16px

### filter-chip

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.caption}
- **rounded:** {rounded.none}
- **padding:** 8px 14px

### filter-chip-active

- **backgroundColor:** {colors.ink}
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.none}

### configurator-option-tile

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.none}
- **padding:** 16px 24px

### configurator-option-tile-selected

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **rounded:** {rounded.none}
- **padding:** 15px 23px

### text-input

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.none}
- **padding:** 14px 16px
- **height:** 48px

### cookie-consent-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.body}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.none}
- **padding:** 24px

### category-tab

- **backgroundColor:** transparent
- **textColor:** {colors.muted}
- **typography:** {typography.label-uppercase}
- **rounded:** {rounded.none}

### category-tab-active

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.label-uppercase}
- **rounded:** {rounded.none}

### m-stripe-divider

- **backgroundColor:** transparent
- **rounded:** {rounded.none}

### cta-band-photo

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-md}
- **padding:** 80px

### footer

- **backgroundColor:** {colors.surface-soft}
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
| `section` | 80px |


## 6. Layout Principles

- **Section rhythm:** `80px` vertical padding between major bands.

### Grid & Container

- Model cards run as 4-up or 5-up grids with no hairline border or only minimal border — just white plate + photo + title.
- **Max content width:** ~1440px center-aligned.
- **Editorial body:** A single 12-column grid.
- **Model card grids:** 4-up or 5-up at desktop, 2-up at tablet, 1-up on mobile.
- **Configurator inventory grids:** 3-up filter row + 4-up vehicle cards, dense layout.
- The hero band's internal layout drops to a single column.
- Model card grid 4-up/5-up → 2-up → 1-up.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Body, top nav, footer, hero bands |
| Soft hairline | 1px `{colors.hairline}` border | Configurator option tile, table divider |
| Card surface | `{colors.surface-card}` background — no shadow | Model card photo plate |
| Photographic | Edge-to-edge photography | Hero band, model renders |

The system never uses a drop shadow. Depth comes entirely from (a) color-block contrast (light canvas vs dark hero) and (b) photographic subject + lighting.


## 8. Do's and Don'ts

### Do
- Sit every page on `{colors.canvas}` (pure white); reserve `{colors.surface-dark}` for hero bands only.
- Pair primary CTAs with `{colors.primary}` (BMW Blue) + `{colors.on-primary}` white text + `{rounded.none}` 0px corners — the corporate signature.
- Set display headlines in BMW Type Next Latin 700 and body in Light 300. The contrast is non-negotiable.
- Use UPPERCASE letter-spaced links like "LEARN MORE" as inline CTAs.
- Place the model card photo on `{colors.surface-card}` with the title beneath — the standard BMW corporate pattern.
- Hold section rhythm at `{spacing.section}` (80px) — tighter than BMW M's 96px.
- Reserve the M tricolor stripe for M-model contexts and motorsport dividers.

### Don't
- Don't add a brand color other than blue — BMW Blue is the only primary action color.
- Don't use pill or rounded buttons — `{rounded.none}` (0px) rectangular IS the brand button.
- Don't drop display weight to 500 — the system uses 700 / 400 / 300; 500 is absent.
- Don't bold body type — Light 300 is the BMW corporate editorial voice.
- Don't add drop shadows to cards — depth comes from photo + color-block contrast.
- Don't repeat the same surface mode across two consecutive bands — light → dark hero → light → light feature → dark CTA → light footer rotation is required.
- Don't use the M tricolor stripe as a CTA fill — divider/accent role only.
- Don't mix languages in a single page — UI language must stay consistent.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 768px | Hamburger nav; hero h1 64→40px; model card grid 1-up; configurator filter chips 2-up; footer 4 col → 1 col |
| Tablet | 768–1024px | Top nav narrows, secondary menu hides under "More"; model card 2-up; inventory 2-up |
| Desktop | 1024–1440px | Full top-nav; 4-up or 5-up model card grid; inventory 3-up; full configurator UI |
| Wide | > 1440px | Same as desktop, content fixed at 1440px; gutters absorb the rest |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#1c69d4`
- Background / Canvas: `#ffffff`
- Heading / Strong text: `#262626`
- Body / Secondary text: `#3c3c3c`
- Primary Active: `#0653b6`
- Primary Disabled: `#d6d6d6`
- Body Strong: `#1a1a1a`
- Muted: `#6b6b6b`
- Muted Soft: `#9a9a9a`
- Hairline: `#e6e6e6`

### Example Component Prompts

- "Create a hero on the canvas background (`#ffffff`). Headline at 64px using the display font, weight 700, line-height 1.05, color `#262626` with fallback Google Font. Primary CTA uses `#1c69d4` background, white text, 8px radius, and comfortable padding."
- "Design a content card: `#fafafa` background, 1px `#e6e6e6` border, `12px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

