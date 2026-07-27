# Design System: Cal.com

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `cal/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/cal.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `Cal Sans` → **Fallback:** `Manrope`
> - **Original mono family:** `JetBrains Mono` → **Fallback:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Manrope', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Cal.com's marketing surface is a clean, friendly modern-SaaS interface — white canvas (`{colors.canvas}` — #ffffff) with black primary CTAs (`{colors.primary}` — #111111), custom **Cal Sans** display typography, and `{colors.surface-card}` (#f5f5f5) light-gray cards holding product UI fragments. The system reads as confidently engineered without trying to impress — every band has clear hierarchy, generous whitespace, and a single primary action.

Type voice splits cleanly into two roles: **Cal Sans** (the brand's custom geometric display face — used for h1, h2, h3, and hero headlines) and **Inter** (used for everything else — body, buttons, nav, captions). Cal Sans uses weight 600 with negative letter-spacing (-0.5px to -2px depending on size) — it feels modern, slightly condensed, distinctly Cal.com.

Component voltage comes from **product UI fragments shown directly inside cards** — calendar widgets, scheduling forms, automation diagrams, integration tiles. Cal.com doesn't paint marketing illustrations of the product; it shows the actual product chrome at small scale embedded in the marketing flow.

The footer flips to `{colors.surface-dark}` (#101010) — a deep near-black that visually closes every long-scroll page. The footer is the only dark surface in the system; everything above stays white-with-light-gray-cards.

**Key Characteristics:**
- White canvas with black primary CTA (`{colors.primary}` — #111111). Buttons are `{rounded.md}` (8px) with confident weight-600 labels. Standard friendly-SaaS button.
- Custom `Cal Sans` display typeface for headlines (substituted with Inter weight 600 here). Negative letter-spacing on display sizes — geometric, precise, slightly condensed.
- Light-gray card surfaces (`{colors.surface-card}` — #f5f5f5) for feature cards, testimonials, and pricing tiers (non-featured). The featured pricing tier flips to `{colors.surface-dark}` (the only dark card on light pages).
- Product UI fragments embedded directly in cards — Cal.com shows real schedule pickers, calendar widgets, integration grids inside its marketing cards. Brand voltage from real product chrome at small scale.
- Nav-pill-group (`{component.nav-pill-group}`) — a small pill-radius wrapper around grouped nav segments (e.g., the sub-nav switcher between product views). The pill wrapper is one of the system's signature interactive components.
- Avatars are circular (`{rounded.full}`), 36px diameter, used in testimonial rows and team-listing surfaces.
- Footer is dark navy (`{colors.surface-dark}` — #101010) with light text (`{colors.on-dark-soft}` — #a1a1aa). The dark footer closes every page even though the body above is white.
- Spacing rhythm is `{spacing.section}` (96px) between major bands — tight enough to feel modern-SaaS but generous enough to breathe.
- Border radius is hierarchical: `{rounded.md}` (8px) for buttons + inputs, `{rounded.lg}` (12px) for content cards, `{rounded.xl}` (16px) for the hero app-mockup container, `{rounded.pill}` for nav-pill-group + badges, `{rounded.full}` for avatars + icon buttons.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#111111` — near-black
- **Primary Active** (primary-active): `#242424` — near-black
- **Primary Disabled** (primary-disabled): `#e5e7eb`
- **On Primary** (on-primary): `#ffffff` — pure/near-white
- **Brand Accent** (brand-accent): `#3b82f6` — cool blue tint
### Surfaces & Backgrounds
- **Canvas** (canvas): `#ffffff` — pure/near-white
- **Surface Soft** (surface-soft): `#f8f9fa` — pure/near-white
- **Surface Card** (surface-card): `#f5f5f5` — pure/near-white
- **Surface Strong** (surface-strong): `#e5e7eb`
- **Surface Dark** (surface-dark): `#101010` — near-black
- **Surface Dark Elevated** (surface-dark-elevated): `#1a1a1a` — near-black
### Text & Ink
- **Ink** (ink): `#111111` — near-black
- **Body** (body): `#374151`
- **Muted** (muted): `#6b7280`
- **Muted Soft** (muted-soft): `#898989`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
- **On Dark Soft** (on-dark-soft): `#a1a1aa`
- **Badge Pink** (badge-pink): `#ec4899` — warm red/orange tint
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#e5e7eb`
- **Hairline Soft** (hairline-soft): `#f3f4f6` — pure/near-white
### Semantic & Status
- **Success** (success): `#10b981` — green tint
- **Warning** (warning): `#f59e0b` — warm red/orange tint
- **Error** (error): `#ef4444` — warm red/orange tint
### Accent / Other
- **Badge Orange** (badge-orange): `#fb923c` — warm red/orange tint
- **Badge Violet** (badge-violet): `#8b5cf6` — cool blue tint
- **Badge Emerald** (badge-emerald): `#34d399` — green tint

## 3. Typography Rules

### Font Family
- **Primary:** `Cal Sans, Inter, sans-serif`
- **Monospace:** used for code/terminal surfaces.

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-xl | Cal Sans, Inter, sans-serif | 64px | 600 | 1.05 | -2px |  |
| display-lg | Cal Sans, Inter, sans-serif | 48px | 600 | 1.1 | -1.5px |  |
| display-md | Cal Sans, Inter, sans-serif | 36px | 600 | 1.15 | -1px |  |
| display-sm | Cal Sans, Inter, sans-serif | 28px | 600 | 1.2 | -0.5px |  |
| title-lg | Inter, sans-serif | 22px | 600 | 1.3 | -0.3px |  |
| title-md | Inter, sans-serif | 18px | 600 | 1.4 | 0 |  |
| title-sm | Inter, sans-serif | 16px | 600 | 1.4 | 0 |  |
| body-md | Inter, sans-serif | 16px | 400 | 1.5 | 0 |  |
| body-sm | Inter, sans-serif | 14px | 400 | 1.5 | 0 |  |
| caption | Inter, sans-serif | 13px | 500 | 1.4 | 0 |  |
| code | JetBrains Mono, ui-monospace, monospace | 14px | 400 | 1.5 | 0 |  |
| button | Inter, sans-serif | 14px | 600 | 1 | 0 |  |
| nav-link | Inter, sans-serif | 14px | 500 | 1.4 | 0 |  |


## 4. Component Stylings

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 12px 20px
- **height:** 40px

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
- **height:** 40px

### button-icon-circular

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **rounded:** {rounded.full}
- **size:** 36px

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

### nav-pill-group

- **backgroundColor:** {colors.surface-soft}
- **textColor:** {colors.ink}
- **typography:** {typography.nav-link}
- **rounded:** {rounded.pill}
- **padding:** 6px

### hero-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.display-xl}
- **padding:** 96px

### hero-app-mockup-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **rounded:** {rounded.xl}

### feature-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 32px

### feature-icon-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.title-sm}
- **rounded:** {rounded.lg}
- **padding:** 24px

### product-mockup-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
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

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-lg}
- **rounded:** {rounded.lg}
- **padding:** 32px

### text-input

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.md}
- **padding:** 10px 14px
- **height:** 40px

### text-input-focused

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **rounded:** {rounded.md}

### category-tab

- **backgroundColor:** transparent
- **textColor:** {colors.muted}
- **typography:** {typography.nav-link}
- **padding:** 8px 14px
- **rounded:** {rounded.md}

### category-tab-active

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.nav-link}
- **rounded:** {rounded.md}

### avatar-circle

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **rounded:** {rounded.full}
- **size:** 36px

### badge-pill

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.caption}
- **rounded:** {rounded.pill}
- **padding:** 4px 12px

### rating-stars

- **backgroundColor:** transparent
- **textColor:** {colors.badge-orange}
- **typography:** {typography.caption}

### cta-band-light

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.display-sm}
- **rounded:** {rounded.lg}
- **padding:** 48px

### footer

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark-soft}
- **typography:** {typography.body-sm}
- **padding:** 64px


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
| `xs` | 4px |
| `sm` | 6px |
| `md` | 8px |
| `lg` | 12px |
| `xl` | 16px |
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

- Product UI fragments embedded directly in cards — Cal.com shows real schedule pickers, calendar widgets, integration grids inside its marketing cards. Brand voltage from real product chrome at small scale.
- Border radius is hierarchical: `{rounded.md}` (8px) for buttons + inputs, `{rounded.lg}` (12px) for content cards, `{rounded.xl}` (16px) for the hero app-mockup container, `{rounded.pill}` for nav-pill-group + badges, `{rounded.full}` for avatars + icon buttons.
- **Gutters:** `{spacing.lg}` (24px) between cards in 3-up grids; `{spacing.md}` (16px) inside footer columns.
- **Max content width:** ~1200px centered on marketing pages.
- **Editorial body:** Single 12-column grid; hero band often uses 7/5 split (h1 left, app mockup card right).
- **Feature card grids:** 3-up at desktop, 2-up at tablet, 1-up at mobile.
- **Pricing grid:** 4-up at desktop, 2-up at tablet, 1-up at mobile.
- **Footer:** 4-column link list at desktop, wrapping to 2-up at tablet, 1-up at mobile.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Body sections, top nav, hero bands |
| Soft hairline | 1px `{colors.hairline}` border | Inputs, table dividers, occasionally on cards |
| Card surface | `{colors.surface-card}` background — no shadow | Feature cards, testimonials |
| Subtle drop shadow | Faint shadow at low alpha | Pricing tier cards, hover-elevated states (the system uses `0 1px 2px rgba(0,0,0,0.05)` and `0 4px 12px rgba(0,0,0,0.08)`) |
| Featured tier | `{colors.surface-dark}` background, no shadow needed | The featured pricing tier inverts to dark surface — color contrast does the elevation work |

The elevation philosophy is **soft and modern** — small drop shadows on elevated cards, color-block contrast for emphasis. No heavy shadows, no neumorphism, no glassmorphism.


## 8. Do's and Don'ts

### Do
- Reserve `{colors.primary}` (#111111) for primary CTAs and h1/h2 type. Cal.com's button is near-black, not blue.
- Use Cal Sans for every display headline. Pair with Inter body. Never blur the boundary.
- Apply negative letter-spacing on display sizes (-0.5 to -2px). Cal Sans without it reads as off-brand.
- Use `{component.feature-card}` (light gray) and `{component.product-mockup-card}` (white with chrome) deliberately — the gray cards signal "abstract feature claim", white cards signal "look at the actual product".
- Embed real product UI fragments inside marketing cards. Don't paint marketing illustrations of the product when you can show the product itself.
- Keep avatar circles at 36px, perfect circles, sometimes with pastel fills. Avatars are the only place where badge pastels appear.
- Use `{component.nav-pill-group}` for grouped sub-nav segments. The pill-in-pill treatment is signature.
- End every page with the dark footer. The light-to-dark transition is part of the editorial rhythm.

### Don't
- Don't use accent colors (`{colors.brand-accent}`, badge pastels) on primary CTAs. The system is monochrome at the action layer.
- Don't bold display weight beyond 600. Cal Sans at 700 reads as bombastic.
- Don't use rounded radius beyond `{rounded.xl}` (16px) on cards. Larger radii read as consumer-app, not professional booking software.
- Don't put dark surface cards anywhere except the footer and the featured pricing tier. The dark surface is a deliberate, scarce signal.
- Don't repeat the same surface mode in two consecutive bands. Cal.com's pacing alternates white → light-gray → white → product-mockup-card → white → dark-footer.
- Don't add hover state styling beyond what the system already encodes — primary darkens on press; nothing else changes.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 768px | Hamburger nav; hero h1 64→32px; hero-app-mockup-card stacks below content; feature grids 1-up; pricing 1-up; footer 4 cols → 1 |
| Tablet | 768–1024px | Top nav stays horizontal but tightens; nav-pill-group wraps; feature cards 2-up; pricing 2-up |
| Desktop | 1024–1440px | Full top-nav with all menu items; 3-up feature cards; 4-up pricing tiers |
| Wide | > 1440px | Same as desktop with more outer breathing room; max content width caps at 1200px |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#111111`
- Background / Canvas: `#ffffff`
- Heading / Strong text: `#111111`
- Body / Secondary text: `#374151`
- Primary Active: `#242424`
- Primary Disabled: `#e5e7eb`
- Muted: `#6b7280`
- Muted Soft: `#898989`
- Hairline: `#e5e7eb`
- Hairline Soft: `#f3f4f6`

### Example Component Prompts

- "Create a hero on the canvas background (`#ffffff`). Headline at 64px using the display font, weight 600, line-height 1.05, color `#111111` with fallback Google Font. Primary CTA uses `#111111` background, white text, 8px radius, and comfortable padding."
- "Design a content card: `#f5f5f5` background, 1px `#e5e7eb` border, `12px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

