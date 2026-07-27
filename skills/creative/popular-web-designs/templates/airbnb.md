# Design System: Airbnb

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `airbnb/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/airbnb.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `Airbnb Cereal VF` → **Fallback:** `Inter`
> - **Mono:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Airbnb is the canonical example of a generous, photography-led consumer marketplace. The base canvas is **pure white** (`{colors.canvas}` — #ffffff) with deep near-black ink (`{colors.ink}` — #222222) for headlines and body, and a single voltage of **Rausch** (`{colors.primary}` — #ff385c) carrying every primary CTA, the search-button orb, the heart save state, and inline brand links. There is no secondary brand color in mainline marketing — the **Luxe purple** (`{colors.luxe}` — #460479) and **Plus magenta** (`{colors.plus}` — #92174d) tokens are sub-brand accents that only appear inside Airbnb Luxe / Plus contexts.

Type runs **Airbnb Cereal VF** (a custom variable font Airbnb licenses), with **Circular** as the historic in-house fallback and a system stack underneath. Cereal sits at modest weights — display headlines render at 22–28px in weight 500–600, not the heavy 700+ weights that financial or enterprise systems lean on. The hero h1 ("Inspiration for future getaways") on the homepage is just 28px / 700, which would feel small on a typical SaaS page; here it works because the layout leans on photography (city collage, property cards) for visual weight rather than typographic muscle.

The shape language is **soft**. Buttons are 8px radius (`{rounded.sm}`), property cards are ~14px (`{rounded.md}`), the search bar is fully pill-shaped (`{rounded.full}`), wishlist hearts and search orbs are circles (`{rounded.full}`), and category strip rounded corners run at 32px (`{rounded.xl}`). There is essentially no hard corner anywhere except the body grid itself — every interactive element is rounded.

**Key Characteristics:**
- Single accent color: `{colors.primary}` (#ff385c — "Rausch") carries every primary CTA, the search orb, the heart save state, and the brand wordmark. Used scarcely — most pages are 90% white + ink with one or two Rausch moments.
- Custom variable type: `Airbnb Cereal VF`. Display weights sit at 500–700, body at 400. Modest weight is intentional — the system trusts photography for visual heft.
- Three-product top nav: Homes, Experiences, Services — each with a hand-illustrated 32px icon and "NEW" badges (`{component.new-tag}`) on the two newer products. Active tab uses an underline rule (`{component.product-tab-active}`).
- Pill-shaped global search bar: white surface, fully rounded (`{rounded.full}`), divided by 1px hairlines into Where / When / Who segments, terminated by a circular Rausch search orb (`{component.search-orb}`).
- Property cards are photo-first: aspect-ratio rectangles with `{rounded.md}` corner clipping, swipeable image carousel, "Guest favorite" floating badge top-left, heart icon top-right, then 4–5 lines of meta beneath.
- Editorial dropdowns (footer, language picker) are clean text columns over the white canvas — no card surface, no shadow.
- The design system caps elevation at one shadow tier (`box-shadow: rgba(0,0,0,0.02) 0 0 0 1px, rgba(0,0,0,0.04) 0 2px 6px, rgba(0,0,0,0.1) 0 4px 8px`) — used on hover-floated cards and search/account dropdowns.
- 8px base spacing system, with major sections at `{spacing.section}` (64px) — generous but not airy enough to feel editorial-magazine; the marketplace density wants more cards per scroll.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#ff385c` — warm red/orange tint
- **Primary Active** (primary-active): `#e00b41` — warm red/orange tint
- **Primary Disabled** (primary-disabled): `#ffd1da` — warm red/orange tint
- **Primary Error Text** (primary-error-text): `#c13515` — warm red/orange tint
- **Primary Error Text Hover** (primary-error-text-hover): `#b32505` — warm red/orange tint
- **On Primary** (on-primary): `#ffffff` — pure/near-white
### Surfaces & Backgrounds
- **Canvas** (canvas): `#ffffff` — pure/near-white
- **Surface Soft** (surface-soft): `#f7f7f7` — pure/near-white
- **Surface Card** (surface-card): `#ffffff` — pure/near-white
- **Surface Strong** (surface-strong): `#f2f2f2` — pure/near-white
### Text & Ink
- **Ink** (ink): `#222222` — near-black
- **Body** (body): `#3f3f3f`
- **Muted** (muted): `#6a6a6a`
- **Muted Soft** (muted-soft): `#929292`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
- **Legal Link** (legal-link): `#428bff` — cool blue tint
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#dddddd`
- **Hairline Soft** (hairline-soft): `#ebebeb`
- **Border Strong** (border-strong): `#c1c1c1`
### Accent / Other
- **Luxe** (luxe): `#460479` — cool blue tint
- **Plus** (plus): `#92174d` — warm red/orange tint
- **Star Rating** (star-rating): `#222222` — near-black
- **Scrim** (scrim): `#000000` — near-black

## 3. Typography Rules

### Font Family
- **Primary:** `'Airbnb Cereal VF', Circular, -apple-system, system-ui, Roboto, 'Helvetica Neue', sans-serif`

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-xl | 'Airbnb Cereal VF', Circular, -apple-system, system-ui, Roboto, 'Helvetica Neue', sans-serif | 28px | 700 | 1.43 | 0 |  |
| display-lg | 'Airbnb Cereal VF', Circular, sans-serif | 22px | 500 | 1.18 | -0.44px |  |
| display-md | 'Airbnb Cereal VF', Circular, sans-serif | 21px | 700 | 1.43 | 0 |  |
| display-sm | 'Airbnb Cereal VF', Circular, sans-serif | 20px | 600 | 1.2 | -0.18px |  |
| title-md | 'Airbnb Cereal VF', Circular, sans-serif | 16px | 600 | 1.25 | 0 |  |
| title-sm | 'Airbnb Cereal VF', Circular, sans-serif | 16px | 500 | 1.25 | 0 |  |
| rating-display | 'Airbnb Cereal VF', Circular, sans-serif | 64px | 700 | 1.1 | -1px |  |
| body-md | 'Airbnb Cereal VF', Circular, sans-serif | 16px | 400 | 1.5 | 0 |  |
| body-sm | 'Airbnb Cereal VF', Circular, sans-serif | 14px | 400 | 1.43 | 0 |  |
| caption | 'Airbnb Cereal VF', Circular, sans-serif | 14px | 500 | 1.29 | 0 |  |
| caption-sm | 'Airbnb Cereal VF', Circular, sans-serif | 13px | 400 | 1.23 | 0 |  |
| badge | 'Airbnb Cereal VF', Circular, sans-serif | 11px | 600 | 1.18 | 0 |  |
| micro-label | 'Airbnb Cereal VF', Circular, sans-serif | 12px | 700 | 1.33 | 0 |  |
| uppercase-tag | 'Airbnb Cereal VF', Circular, sans-serif | 8px | 700 | 1.25 | 0.32px | uppercase |
| button-md | 'Airbnb Cereal VF', Circular, sans-serif | 16px | 500 | 1.25 | 0 |  |
| button-sm | 'Airbnb Cereal VF', Circular, sans-serif | 14px | 500 | 1.29 | 0 |  |
| link | 'Airbnb Cereal VF', Circular, sans-serif | 14px | 400 | 1.43 | 0 |  |
| nav-link | 'Airbnb Cereal VF', Circular, sans-serif | 16px | 600 | 1.25 | 0 |  |


## 4. Component Stylings

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button-md}
- **rounded:** {rounded.sm}
- **padding:** 14px 24px
- **height:** 48px

### button-primary-active

- **backgroundColor:** {colors.primary-active}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.sm}

### button-primary-disabled

- **backgroundColor:** {colors.primary-disabled}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.sm}

### button-secondary

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.button-md}
- **rounded:** {rounded.sm}
- **padding:** 13px 23px
- **height:** 48px

### button-tertiary-text

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.button-md}

### button-pill-rausch

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button-sm}
- **rounded:** {rounded.full}
- **padding:** 10px 20px

### search-orb

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.full}
- **height:** 48px

### icon-button-circle

- **backgroundColor:** {colors.surface-strong}
- **textColor:** {colors.ink}
- **rounded:** {rounded.full}
- **height:** 32px

### icon-button-outline

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **rounded:** {rounded.full}
- **height:** 40px

### top-nav

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.nav-link}
- **height:** 80px

### product-tab-active

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.nav-link}
- **rounded:** {rounded.none}

### product-tab-inactive

- **backgroundColor:** transparent
- **textColor:** {colors.muted}
- **typography:** {typography.nav-link}

### search-bar-pill

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.full}
- **padding:** 14px 24px
- **height:** 64px

### search-field-segment

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.caption}
- **padding:** 8px 24px

### category-strip

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.muted}
- **typography:** {typography.button-sm}

### category-tab-active

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.button-sm}
- **rounded:** {rounded.none}

### property-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.md}

### property-card-photo

- **rounded:** {rounded.md}

### experience-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.md}

### city-link-block

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.title-sm}

### rating-display-card

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.rating-display}

### guest-favorite-badge

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.badge}
- **rounded:** {rounded.full}
- **padding:** 4px 10px

### new-tag

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.uppercase-tag}
- **rounded:** {rounded.full}
- **padding:** 2px 6px

### amenity-row

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **padding:** 12px 0

### reviews-card

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}

### host-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.md}
- **padding:** 24px

### reservation-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.md}
- **padding:** 24px

### date-picker-day

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.full}

### date-picker-day-selected

- **backgroundColor:** {colors.ink}
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.full}

### text-input

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.sm}
- **padding:** 14px 12px
- **height:** 56px

### footer-light

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **padding:** 48px 80px

### footer-link

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}

### legal-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.muted}
- **typography:** {typography.caption-sm}


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
| `none` | 0px |
| `xs` | 4px |
| `sm` | 8px |
| `md` | 14px |
| `lg` | 20px |
| `xl` | 32px |
| `full` | 9999px |

**Spacing Scale**

| Token | Value |
|---|---|
| `xxs` | 2px |
| `xs` | 4px |
| `sm` | 8px |
| `md` | 12px |
| `base` | 16px |
| `lg` | 24px |
| `xl` | 32px |
| `xxl` | 48px |
| `section` | 64px |


## 6. Layout Principles

- **Section rhythm:** `64px` vertical padding between major bands.

### Grid & Container

- **Card internal padding:** `{spacing.lg}` (24px) for `{component.host-card}` and `{component.reservation-card}`; `{spacing.base}` (16px) for property-card meta block; `{spacing.sm}` (8px) for caption / date-row gutters.
- **Gutters:** `{spacing.base}` (16px) between cards in the homepage city grid; `{spacing.lg}` (24px) inside footer column gutters; `{spacing.xs}` (4px) on dense category-strip dividers.
- **Max content width:** ~1280px centered on the homepage and editorial pages. Listing detail pages cap closer to 1080px to keep the photo banner and reservation rail readable.
- **City link grid (homepage footer):** 6-column grid at desktop with each cell housing a city name in `{typography.title-md}` and a category sub-label in `{typography.body-sm}` muted.
- **Listing detail:** 2-column with photo / amenity body on the left (~64% width) and a sticky reservation card (`{component.reservation-card}`) on the right (~32%).
- **Footer:** 3-column link list (Support / Hosting / Airbnb) at desktop, collapsing to 1-column on mobile.
- Property and city-link grids drop column counts cleanly at each breakpoint — never reflow rows; always reduce columns.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow / no border | Page background, inline text |
| Hairline | 1px border tone | Cards, dividers, inputs |
| Elevated | Surface lift or subtle shadow | Featured cards, floating panels |


## 8. Do's and Don'ts

### Do
- Use the documented color tokens and type hierarchy.
- Keep primary CTAs consistent with the brand color and radius.

### Don't
- Don't introduce undocumented colors or weights.
- Don't use radii outside the documented scale for the same component family.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 744px | Top nav collapses to logo + hamburger; product tabs hide behind a sheet; search bar collapses to a single tappable pill; property cards stack 1-up; city grid 1-column; listing detail collapses reservation card to a sticky bottom bar. |
| Tablet | 744–1128px | Top nav keeps product tabs but search bar narrows; property cards 2-up; city grid 2–3 column; reservation card stays sticky right-rail at narrower width. |
| Desktop | 1128–1440px | Full top nav with three product tabs centered; search bar at full pill width with all 3 segments visible; property cards 4-up; city grid 6-column; listing detail 2-column with reservation rail. |
| Wide | > 1440px | Content width caps at 1440px on listing/search pages and ~1280px on editorial; gutters absorb the rest. |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#ff385c`
- Background / Canvas: `#ffffff`
- Heading / Strong text: `#222222`
- Body / Secondary text: `#3f3f3f`
- Primary Active: `#e00b41`
- Primary Disabled: `#ffd1da`
- Primary Error Text: `#c13515`
- Primary Error Text Hover: `#b32505`
- Luxe: `#460479`
- Plus: `#92174d`

### Example Component Prompts

- "Create a hero on the canvas background (`#ffffff`). Headline at 28px using the display font, weight 700, line-height 1.43, color `#222222` with fallback Google Font. Primary CTA uses `#ff385c` background, white text, 14px radius, and comfortable padding."
- "Design a content card: `#ffffff` background, 1px `#dddddd` border, `20px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

