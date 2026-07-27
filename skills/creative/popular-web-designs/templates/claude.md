# Design System: Claude

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `claude/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/claude.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `Copernicus` → **Fallback:** `Cormorant Garamond`
> - **Original mono family:** `JetBrains Mono` → **Fallback:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Cormorant Garamond', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Claude.com is the warmest, most editorial interface in the AI-product category. The base atmosphere is a **tinted cream canvas** (`{colors.canvas}` — #faf9f5) — distinctly warm, deliberately not the cool gray-white that every other AI brand uses. Headlines run a **slab-serif display** ("Copernicus" / Tiempos Headline) at weight 400 with negative letter-spacing, paired with **StyreneB / Inter** body sans. The combination feels like a literary publication, not a SaaS marketing page.

Brand voltage comes from the **cream + coral pairing** — coral (`{colors.primary}` — #cc785c) is the signature Anthropic accent, used on every primary CTA, on the brand wordmark, and on full-bleed callout cards. The coral is warm, slightly muted, never cyan/blue — a deliberate counter-positioning against OpenAI's cool slate, Google's saturated blue, and Microsoft's corporate cyan.

The system has three surface modes that alternate page-by-page:
1. **Cream canvas** (`{colors.canvas}`) — default body floor
2. **Light cream cards** (`{colors.surface-card}`) — feature card backgrounds
3. **Dark navy product surfaces** (`{colors.surface-dark}`) — code editor mockups, model showcase cards, pre-footer CTAs, footer itself

The dark surfaces are where Claude shows its product chrome — code blocks, terminal output, model comparison tables, agentic-flow diagrams. The cream-to-dark contrast is the page's pacing rhythm.

**Key Characteristics:**
- Warm cream canvas (`{colors.canvas}` — #faf9f5) with dark warm-ink text (`{colors.ink}` — #141413). The brand's defining color choice.
- Coral primary CTA (`{colors.primary}` — #cc785c). Used scarcely on individual buttons, generously on full-bleed coral callout cards.
- Slab-serif display headlines via Copernicus / Tiempos Headline at weight 400 with negative letter-spacing. Pairs with humanist sans body for a literary editorial voice.
- Dark navy product mockup cards (`{colors.surface-dark}` — #181715) carrying code blocks, terminal panels, model comparison data — the brand shows the product chrome at scale rather than abstract marketing illustrations.
- Light cream feature cards (`{colors.surface-card}` — #efe9de) — slightly darker than canvas, used for content-driven feature explanations.
- Anthropic radial-spike mark — a small black asterisk-like glyph (4-spoke radial) — appears as the brand wordmark prefix and as a content marker.
- Border radius is hierarchical: `{rounded.md}` (8px) for buttons + inputs, `{rounded.lg}` (12px) for content + product cards, `{rounded.xl}` (16px) for the hero illustration container, `{rounded.pill}` for badges.
- Section rhythm `{spacing.section}` (96px) — modern-SaaS standard. Internal card padding stays generous at `{spacing.xl}` (32px).


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#cc785c` — warm red/orange tint
- **Primary Active** (primary-active): `#a9583e` — warm red/orange tint
- **Primary Disabled** (primary-disabled): `#e6dfd8`
- **On Primary** (on-primary): `#ffffff` — pure/near-white
- **Accent Teal** (accent-teal): `#5db8a6`
- **Accent Amber** (accent-amber): `#e8a55a` — warm red/orange tint
### Surfaces & Backgrounds
- **Canvas** (canvas): `#faf9f5` — pure/near-white
- **Surface Soft** (surface-soft): `#f5f0e8`
- **Surface Card** (surface-card): `#efe9de`
- **Surface Cream Strong** (surface-cream-strong): `#e8e0d2`
- **Surface Dark** (surface-dark): `#181715` — near-black
- **Surface Dark Elevated** (surface-dark-elevated): `#252320` — near-black
- **Surface Dark Soft** (surface-dark-soft): `#1f1e1b` — near-black
### Text & Ink
- **Ink** (ink): `#141413` — near-black
- **Body** (body): `#3d3d3a`
- **Body Strong** (body-strong): `#252523` — near-black
- **Muted** (muted): `#6c6a64`
- **Muted Soft** (muted-soft): `#8e8b82`
- **On Dark** (on-dark): `#faf9f5` — pure/near-white
- **On Dark Soft** (on-dark-soft): `#a09d96`
### Hairlines, Borders & Dividers
- **Hairline** (hairline): `#e6dfd8`
- **Hairline Soft** (hairline-soft): `#ebe6df`
### Semantic & Status
- **Success** (success): `#5db872` — green tint
- **Warning** (warning): `#d4a017` — warm red/orange tint
- **Error** (error): `#c64545` — warm red/orange tint

## 3. Typography Rules

### Font Family
- **Primary:** `Copernicus, Tiempos Headline, serif`
- **Monospace:** used for code/terminal surfaces.

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| display-xl | Copernicus, Tiempos Headline, serif | 64px | 400 | 1.05 | -1.5px |  |
| display-lg | Copernicus, Tiempos Headline, serif | 48px | 400 | 1.1 | -1px |  |
| display-md | Copernicus, Tiempos Headline, serif | 36px | 400 | 1.15 | -0.5px |  |
| display-sm | Copernicus, Tiempos Headline, serif | 28px | 400 | 1.2 | -0.3px |  |
| title-lg | StyreneB, Inter, sans-serif | 22px | 500 | 1.3 | 0 |  |
| title-md | StyreneB, Inter, sans-serif | 18px | 500 | 1.4 | 0 |  |
| title-sm | StyreneB, Inter, sans-serif | 16px | 500 | 1.4 | 0 |  |
| body-md | StyreneB, Inter, sans-serif | 16px | 400 | 1.55 | 0 |  |
| body-sm | StyreneB, Inter, sans-serif | 14px | 400 | 1.55 | 0 |  |
| caption | StyreneB, Inter, sans-serif | 13px | 500 | 1.4 | 0 |  |
| caption-uppercase | StyreneB, Inter, sans-serif | 12px | 500 | 1.4 | 1.5px |  |
| code | JetBrains Mono, ui-monospace, monospace | 14px | 400 | 1.6 | 0 |  |
| button | StyreneB, Inter, sans-serif | 14px | 500 | 1 | 0 |  |
| nav-link | StyreneB, Inter, sans-serif | 14px | 500 | 1.4 | 0 |  |


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

### button-secondary-on-dark

- **backgroundColor:** {colors.surface-dark-elevated}
- **textColor:** {colors.on-dark}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 12px 20px

### button-text-link

- **backgroundColor:** transparent
- **textColor:** {colors.ink}
- **typography:** {typography.button}

### button-icon-circular

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **rounded:** {rounded.full}
- **size:** 36px

### text-link

- **backgroundColor:** transparent
- **textColor:** {colors.primary}
- **typography:** {typography.body-md}

### top-nav

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.nav-link}
- **height:** 64px

### hero-band

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.display-xl}
- **padding:** 96px

### hero-illustration-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **rounded:** {rounded.xl}

### feature-card

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 32px

### product-mockup-card-dark

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 32px

### code-window-card

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.code}
- **rounded:** {rounded.lg}
- **padding:** 24px

### model-comparison-card

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 32px

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

### callout-card-coral

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.title-md}
- **rounded:** {rounded.lg}
- **padding:** 32px

### connector-tile

- **backgroundColor:** {colors.canvas}
- **textColor:** {colors.ink}
- **typography:** {typography.title-sm}
- **rounded:** {rounded.lg}
- **padding:** 20px

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

### cookie-consent-card

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.lg}
- **padding:** 24px

### category-tab

- **backgroundColor:** transparent
- **textColor:** {colors.muted}
- **typography:** {typography.nav-link}
- **padding:** 8px 14px
- **rounded:** {rounded.md}

### category-tab-active

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.nav-link}
- **rounded:** {rounded.md}

### badge-pill

- **backgroundColor:** {colors.surface-card}
- **textColor:** {colors.ink}
- **typography:** {typography.caption}
- **rounded:** {rounded.pill}
- **padding:** 4px 12px

### badge-coral

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.caption-uppercase}
- **rounded:** {rounded.pill}
- **padding:** 4px 12px

### cta-band-coral

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.display-sm}
- **rounded:** {rounded.lg}
- **padding:** 64px

### cta-band-dark

- **backgroundColor:** {colors.surface-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-sm}
- **rounded:** {rounded.lg}
- **padding:** 64px

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

- Border radius is hierarchical: `{rounded.md}` (8px) for buttons + inputs, `{rounded.lg}` (12px) for content + product cards, `{rounded.xl}` (16px) for the hero illustration container, `{rounded.pill}` for badges.
- **Max content width:** ~1200px centered.
- **Editorial body:** Single 12-column grid; hero often uses 6/6 split (h1 left, illustration right).
- **Feature card grids:** 3-up at desktop, 2-up at tablet, 1-up at mobile.
- **Connector tile grids:** 4-up or 6-up at desktop, 2-up at tablet, 1-up at mobile.
- **Pricing grid:** 3-up at desktop (Free / Pro / Team / Enterprise often), 1-up at mobile.
- Hero band's 6-6 grid collapses to single-column on mobile — h1 + sub-head + buttons first, then the illustration / mockup card below.
- Feature grids reduce columns rather than scaling cards down.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Body sections, top nav, hero bands |
| Soft hairline | 1px `{colors.hairline}` border | Inputs, sub-nav, occasionally on cards |
| Cream card | `{colors.surface-card}` background — no shadow | Feature cards, content cards |
| Dark surface card | `{colors.surface-dark}` background — no shadow | Code editor mockups, model showcase cards |
| Subtle drop shadow | Faint shadow at low alpha | Hover-elevated states (the system uses `0 1px 3px rgba(20,20,19,0.08)` rarely) |

The elevation philosophy is **color-block first, shadow rare**. Most depth comes from the cream-vs-dark surface contrast. Shadows are minimal. The dark surface mockups have their own internal product chrome (code editor scrollbars, line numbers, syntax highlighting) which adds detail without needing external shadows.


## 8. Do's and Don'ts

### Do
- Anchor every page on the cream canvas. Pure white reads as "any other AI tool"; the warm tint is the brand differentiator.
- Use Copernicus serif for every display headline. Pair with StyreneB sans body. Negative letter-spacing on display sizes is non-negotiable.
- Reserve `{colors.primary}` (coral) for primary CTAs and full-bleed `{component.callout-card-coral}` moments. Don't paint accent moments coral elsewhere.
- Use `{component.product-mockup-card-dark}` and `{component.code-window-card}` to show actual Claude product chrome. Don't paint marketing illustrations of code when you can show real code.
- Pair `{component.feature-card}` (cream) with `{component.product-mockup-card-dark}` (navy) in alternating bands. The cream-to-dark rhythm is the brand's pacing mechanism.
- Use the Anthropic spike-mark glyph as the brand wordmark prefix. Never invert the mark to white-on-dark within the wordmark itself.
- Apply `{spacing.section}` (96px) between major bands.

### Don't
- Don't use cool grays or pure white for canvas. Cream is the brand.
- Don't bold serif display weight. Copernicus at 700 reads as bombastic; the system stays at 400.
- Don't use cool blue or saturated cyan as a brand accent. The coral is the brand voltage.
- Don't put coral everywhere. The coral is scarce on individual elements and generous only on full-bleed coral callout cards.
- Don't use Inter for display headlines. The serif character is the brand voice.
- Don't repeat the same surface mode in two consecutive bands. The pacing alternates: cream → cream-card → dark-mockup → cream → coral-callout → dark-footer.
- Don't add hover state styling beyond what the system already encodes — primary darkens on press; nothing else changes.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 768px | Hamburger nav; hero h1 64→32px; hero-illustration-card stacks below content; feature grids 1-up; connector tiles 2-up; pricing 1-up; footer 4 cols → 1 |
| Tablet | 768–1024px | Top nav stays horizontal but tightens; feature cards 2-up; connector tiles 3-up; pricing 2-up |
| Desktop | 1024–1440px | Full top-nav with all menu items; 3-up feature cards; 4-up or 6-up connector tiles; 3-up pricing tiers |
| Wide | > 1440px | Same as desktop with more outer breathing room; max content width caps at 1200px |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#cc785c`
- Background / Canvas: `#faf9f5`
- Heading / Strong text: `#141413`
- Body / Secondary text: `#3d3d3a`
- Primary Active: `#a9583e`
- Primary Disabled: `#e6dfd8`
- Body Strong: `#252523`
- Muted: `#6c6a64`
- Muted Soft: `#8e8b82`
- Hairline: `#e6dfd8`

### Example Component Prompts

- "Create a hero on the canvas background (`#faf9f5`). Headline at 64px using the display font, weight 400, line-height 1.05, color `#141413` with fallback Google Font. Primary CTA uses `#cc785c` background, white text, 8px radius, and comfortable padding."
- "Design a content card: `#efe9de` background, 1px `#e6dfd8` border, `12px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

