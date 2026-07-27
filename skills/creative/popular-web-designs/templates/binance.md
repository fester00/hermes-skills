# Design System: Binance

> **Hermes Agent — Implementation Notes**
>
> Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — `binance/DESIGN.md`  
> Use this template with `popular-web-designs` skill. Load via `skill_view(name="popular-web-designs", file_path="templates/binance.md")`.  
> Prefer `next/font/google` or self-hosted fonts; Google Fonts CDN may be blocked in Russia.
> - **Original display/body family:** `BinanceNova` → **Fallback:** `Inter`
> - **Mono:** `JetBrains Mono`
> - **Primary stack (CSS):** `font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;`
> - **Mono stack (CSS):** `font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;`

> ```html
> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via `browser_vision` skill (cloudflared tunnel).  
> Verify visual accuracy with `browser_vision` after generating.

## 1. Visual Theme & Atmosphere

Binance reads like a financial trading platform that wants to feel both authoritative and energetic. The base atmosphere is **deep near-black canvas** (`{colors.canvas-dark}` — #0b0e11) holding white type and a single, ubiquitous accent: **Binance Yellow** (`{colors.primary}` — #FCD535). That yellow does almost all of the brand's heavy lifting — it carries every primary CTA, every value-claim headline ("FUNDS ARE SAFU"), every "Sign Up" pill, every featured tier indicator, and the wordmark itself. There is no secondary brand color. The system trusts the yellow voltage to do the brand work, and it carries it.

Type runs Binance's custom **BinanceNova** (display + body) and **BinancePlex** (numerical / financial display) stack. BinanceNova carries display headlines, section titles, and body copy. BinancePlex appears on price tickers, large stat numbers (transaction volumes, user counts, prize pools) — anywhere a number wants to feel "tabular and reliable." Both run at modest weights — display sizes use weight 600-700 (bolder than typical marketing because trading platforms need numbers to read at a glance), body stays at 400.

The product is **multi-theme**: marketing surfaces (homepage, smart-money, futures arena) default to dark, while transactional surfaces (buy crypto, deposit, withdraw) flip to a light theme. The same yellow CTAs and gray-blue hairlines (`{colors.hairline-on-light}` — #eaecef) thread through both — only canvas, surface, and text tones flip. Trading **green** (`{colors.trading-up}` — #0ecb81) and **red** (`{colors.trading-down}` — #f6465d) signal price direction in tables, charts, and price tickers across both modes.

**Key Characteristics:**
- Single accent color: `{colors.primary}` (#FCD535) does all brand voltage — primary CTAs, hero headlines, brand mark, badges. Used scarcely on dark for emphasis, ubiquitously on transactional dialogs.
- Custom type stack: `BinanceNova` (display + body) and `BinancePlex` (numbers, prices, financial data). Big stat numbers always render in BinancePlex for tabular consistency.
- Multi-theme: marketing pages default dark (`{colors.canvas-dark}`); transactional pages flip light (`{colors.canvas-light}`). Yellow CTAs and trading green/red are shared across both.
- Light footer on dark body: the homepage uses `{colors.surface-soft-light}` (#fafafa) for the footer even when the body above it is dark — a deliberate inversion that visually closes the page.
- Trading semantics: green up / red down (`{colors.trading-up}` / `{colors.trading-down}`) for price changes, applied as text color rather than badge background.
- Card surfaces: `{colors.surface-card-dark}` (#1e2329) for elevated cards on dark; `{colors.canvas-light}` for cards on light. No gradient surfaces, no atmospheric backdrops — flat color blocks throughout.
- Border radius is small to medium: `{rounded.md}` (6px) for primary buttons, `{rounded.lg}` (8px) for inputs and content cards, `{rounded.xl}` (12px) for elevated card containers, `{rounded.pill}` for prominent feature CTAs.
- Spacing follows a 4-multiple scale; major editorial bands sit at `{spacing.section}` (80px) — slightly tighter than typical marketing-only sites because product pages need denser layouts.


## 2. Color Palette & Roles

### Brand & Primary
- **Primary** (primary): `#fcd535`
- **Primary Active** (primary-active): `#f0b90b` — warm red/orange tint
- **Primary Disabled** (primary-disabled): `#3a3a1f`
- **On Primary** (on-primary): `#181a20` — near-black
- **Accent Turquoise** (accent-turquoise): `#2dbdb6`
### Surfaces & Backgrounds
- **Canvas Light** (canvas-light): `#ffffff` — pure/near-white
- **Canvas Dark** (canvas-dark): `#0b0e11` — near-black
- **Surface Card Dark** (surface-card-dark): `#1e2329`
- **Surface Elevated Dark** (surface-elevated-dark): `#2b3139`
- **Surface Soft Light** (surface-soft-light): `#fafafa` — pure/near-white
- **Surface Strong Light** (surface-strong-light): `#f5f5f5` — pure/near-white
### Text & Ink
- **Ink** (ink): `#181a20` — near-black
- **Body** (body): `#eaecef`
- **Body On Light** (body-on-light): `#181a20` — near-black
- **Muted** (muted): `#707a8a`
- **Muted Strong** (muted-strong): `#929aa5`
- **Hairline On Light** (hairline-on-light): `#eaecef`
- **Hairline On Dark** (hairline-on-dark): `#2b3139`
- **On Dark** (on-dark): `#ffffff` — pure/near-white
### Hairlines, Borders & Dividers
- **Border Strong** (border-strong): `#cdd1d6`
### Semantic & Status
- **Info** (info): `#3b82f6` — cool blue tint
- **Info Ring** (info-ring): `#3b82f6` — cool blue tint
### Accent / Other
- **Trading Up** (trading-up): `#0ecb81` — green tint
- **Trading Down** (trading-down): `#f6465d` — warm red/orange tint

## 3. Typography Rules

### Font Family
- **Primary:** `BinanceNova, -apple-system, BlinkMacSystemFont, sans-serif`

### Hierarchy

| Token | Font | Size | Weight | Line Height | Letter Spacing | Features |
|---|---|---|---|---|---|---|
| hero-display | BinanceNova, -apple-system, BlinkMacSystemFont, sans-serif | 64px | 700 | 1.1 | -1px |  |
| display-lg | BinanceNova, sans-serif | 48px | 700 | 1.1 | -0.5px |  |
| display-md | BinanceNova, sans-serif | 40px | 600 | 1.15 | -0.3px |  |
| display-sm | BinanceNova, sans-serif | 32px | 600 | 1.2 | 0 |  |
| title-lg | BinanceNova, sans-serif | 24px | 600 | 1.3 | 0 |  |
| title-md | BinanceNova, sans-serif | 20px | 600 | 1.35 | 0 |  |
| title-sm | BinanceNova, sans-serif | 16px | 600 | 1.4 | 0 |  |
| number-display | BinancePlex, BinanceNova, sans-serif | 40px | 700 | 1.1 | -0.3px |  |
| number-md | BinancePlex, BinanceNova, sans-serif | 16px | 500 | 1.4 | 0 |  |
| number-sm | BinancePlex, BinanceNova, sans-serif | 14px | 500 | 1.4 | 0 |  |
| body-md | BinanceNova, sans-serif | 14px | 400 | 1.5 | 0 |  |
| body-sm | BinanceNova, sans-serif | 13px | 400 | 1.5 | 0 |  |
| caption | BinanceNova, sans-serif | 12px | 500 | 1.4 | 0 |  |
| button | BinanceNova, sans-serif | 14px | 600 | 1 | 0 |  |
| nav-link | BinanceNova, sans-serif | 14px | 500 | 1.4 | 0 |  |


## 4. Component Stylings

### button-primary

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 12px 24px
- **height:** 40px

### button-primary-active

- **backgroundColor:** {colors.primary-active}
- **textColor:** {colors.on-primary}
- **rounded:** {rounded.md}

### button-primary-disabled

- **backgroundColor:** {colors.primary-disabled}
- **textColor:** {colors.muted}
- **rounded:** {rounded.md}

### button-primary-pill

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.pill}
- **padding:** 14px 32px

### button-secondary-on-dark

- **backgroundColor:** {colors.surface-card-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 12px 24px

### button-secondary-on-light

- **backgroundColor:** {colors.canvas-light}
- **textColor:** {colors.ink}
- **typography:** {typography.button}
- **rounded:** {rounded.md}
- **padding:** 12px 24px

### button-tertiary-text

- **backgroundColor:** transparent
- **textColor:** {colors.body}
- **typography:** {typography.button}

### button-trading-up

- **backgroundColor:** {colors.trading-up}
- **textColor:** {colors.on-dark}
- **typography:** {typography.button}
- **rounded:** {rounded.sm}
- **padding:** 8px 20px

### button-trading-down

- **backgroundColor:** {colors.trading-down}
- **textColor:** {colors.on-dark}
- **typography:** {typography.button}
- **rounded:** {rounded.sm}
- **padding:** 8px 20px

### button-subscribe

- **backgroundColor:** {colors.primary}
- **textColor:** {colors.on-primary}
- **typography:** {typography.button}
- **rounded:** {rounded.sm}
- **padding:** 6px 16px
- **height:** 28px

### text-link

- **backgroundColor:** transparent
- **textColor:** {colors.primary}
- **typography:** {typography.body-md}

### top-nav-dark

- **backgroundColor:** {colors.canvas-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.nav-link}
- **height:** 64px

### top-nav-light

- **backgroundColor:** {colors.canvas-light}
- **textColor:** {colors.ink}
- **typography:** {typography.nav-link}
- **height:** 64px

### hero-band-dark

- **backgroundColor:** {colors.canvas-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.hero-display}
- **padding:** 80px

### stat-callout-card

- **backgroundColor:** transparent
- **textColor:** {colors.primary}
- **typography:** {typography.number-display}

### trust-badge

- **backgroundColor:** {colors.surface-card-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-sm}
- **rounded:** {rounded.lg}
- **padding:** 16px 20px

### markets-table-card

- **backgroundColor:** {colors.surface-card-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.body-md}
- **rounded:** {rounded.xl}
- **padding:** 24px

### markets-row

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.number-md}
- **padding:** 12px 0

### price-up-cell

- **backgroundColor:** transparent
- **textColor:** {colors.trading-up}
- **typography:** {typography.number-md}

### price-down-cell

- **backgroundColor:** transparent
- **textColor:** {colors.trading-down}
- **typography:** {typography.number-md}

### search-input-on-dark

- **backgroundColor:** {colors.surface-card-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.body-md}
- **rounded:** {rounded.lg}
- **padding:** 10px 16px
- **height:** 40px

### text-input-on-light

- **backgroundColor:** {colors.canvas-light}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.md}
- **padding:** 10px 16px
- **height:** 40px

### funds-safu-band

- **backgroundColor:** {colors.canvas-dark}
- **textColor:** {colors.primary}
- **typography:** {typography.display-lg}
- **padding:** 80px

### feature-photo-card

- **backgroundColor:** {colors.surface-card-dark}
- **textColor:** {colors.on-dark}
- **rounded:** {rounded.xl}

### qr-promo-card

- **backgroundColor:** {colors.surface-card-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-md}
- **rounded:** {rounded.xl}
- **padding:** 32px

### faq-row

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.title-sm}
- **rounded:** {rounded.md}
- **padding:** 20px 0

### cta-band-dark

- **backgroundColor:** {colors.surface-card-dark}
- **textColor:** {colors.on-dark}
- **typography:** {typography.display-sm}
- **rounded:** {rounded.xl}
- **padding:** 48px

### arena-hero-gradient

- **backgroundColor:** {colors.canvas-dark}
- **textColor:** {colors.primary}
- **typography:** {typography.display-lg}
- **padding:** 80px

### cookie-consent-card

- **backgroundColor:** {colors.canvas-light}
- **textColor:** {colors.ink}
- **typography:** {typography.body-sm}
- **rounded:** {rounded.lg}
- **padding:** 16px

### buy-crypto-amount-card

- **backgroundColor:** {colors.canvas-light}
- **textColor:** {colors.ink}
- **typography:** {typography.number-display}
- **rounded:** {rounded.lg}
- **padding:** 24px

### steps-card

- **backgroundColor:** {colors.canvas-light}
- **textColor:** {colors.ink}
- **typography:** {typography.title-sm}
- **rounded:** {rounded.lg}
- **padding:** 24px

### price-chart-card

- **backgroundColor:** {colors.canvas-light}
- **textColor:** {colors.ink}
- **typography:** {typography.body-md}
- **rounded:** {rounded.lg}
- **padding:** 24px

### conversion-cell

- **backgroundColor:** transparent
- **textColor:** {colors.body-on-light}
- **typography:** {typography.body-md}

### trader-row

- **backgroundColor:** transparent
- **textColor:** {colors.on-dark}
- **typography:** {typography.body-md}
- **padding:** 12px 0

### footer-light

- **backgroundColor:** {colors.surface-soft-light}
- **textColor:** {colors.body-on-light}
- **typography:** {typography.body-md}
- **padding:** 64px


## 5. Spacing & Radii

**Border Radius Scale**

| Token | Value |
|---|---|
| `xs` | 2px |
| `sm` | 4px |
| `md` | 6px |
| `lg` | 8px |
| `xl` | 12px |
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

- Border radius is small to medium: `{rounded.md}` (6px) for primary buttons, `{rounded.lg}` (8px) for inputs and content cards, `{rounded.xl}` (12px) for elevated card containers, `{rounded.pill}` for prominent feature CTAs.
- **Gutters:** `{spacing.lg}` (24px) between cards in 3-up grids; `{spacing.md}` (16px) inside footer column gutters and dense FAQ lists.
- **Max content width:** ~1280px centered on marketing pages; ~1440px on product surfaces (markets, smart-money tables) where horizontal density matters.
- **Editorial body:** Single 12-column grid; product pages often use 8/4 split (main panel + side rail).
- **Markets table:** 5-column header (Pair / Last Price / 24h Change / 24h Volume / Action), with the first column carrying coin icon + symbol pair.
- **Footer:** 6-column link list at desktop, wrapping to 2-up at tablet and 1-up on mobile.


## 7. Depth & Elevation

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Body sections, top nav, hero bands, footer |
| Soft hairline | 1px `{colors.hairline-on-dark}` or `{colors.hairline-on-light}` | Inputs, table dividers, FAQ row separators, secondary buttons |
| Card surface | `{colors.surface-card-dark}` background on dark canvas, `{colors.canvas-light}` on light context — no shadow | All elevated cards (markets-table-card, QR-promo-card, feature-photo-card, trust-badges) |
| Subtle drop shadow | Faint shadow visible only when a card sits over imagery | Used sparingly on the buy-crypto-amount-card on transactional pages |
| Focus ring | `0 0 0 2px {colors.info-ring}` at 50% alpha | Input + button keyboard focus state |

The elevation philosophy is **flat surfaces with color-block separation**. Binance does not use heavy drop shadows or glassmorphism — depth comes from the contrast between `{colors.canvas-dark}` and `{colors.surface-card-dark}` (a 12-step lightness jump that reads as a clear elevation boundary).


## 8. Do's and Don'ts

### Do
- Reserve `{colors.primary}` (Binance Yellow) for primary actions, brand-claim headlines, and the wordmark. Never use it for secondary or decorative purposes — yellow's scarcity is what makes it powerful.
- Keep `{component.button-primary}` (yellow with black text) as the universal primary CTA across both dark and light modes. The same button appears identically on `{colors.canvas-dark}` and `{colors.canvas-light}`.
- Use `{component.button-trading-up}` (green) and `{component.button-trading-down}` (red) only for explicit Buy/Sell or Long/Short actions. Never use them for general "confirm" or "cancel" because they carry semantic price-direction meaning.
- Use BinancePlex for every number. Prices, volumes, percentages, stat counters — all BinancePlex. Mixing BinanceNova into a number ticker breaks the trading-platform character.
- Choose canvas mode by surface intent: dark for marketing / product showcase / trading dashboards; light for transactional dialogs (buy / deposit / withdraw / form submission).
- Anchor every editorial band with `{spacing.section}` (80px). Binance is denser than airy marketing sites — 80px is the right rhythm.

### Don't
- Don't introduce a second brand color. The system has exactly one accent (`{colors.primary}`) and any expansion dilutes the brand identity. The turquoise on Smart Money is a single-product experiment, not a system token.
- Don't use yellow for body text or large surface fills. It is for focal-point CTAs and headlines only.
- Don't use `{colors.trading-up}` / `{colors.trading-down}` as background fills on cards. They are price-direction signals, expressed as text color or small badge fill — never as a card surface.
- Don't soften display weight. `{typography.hero-display}` and `{typography.display-lg}` are intentionally weight 700 — going to 400 reads as design-portfolio, not trading platform.
- Don't add atmospheric gradients to the canvas (mesh, aurora, glow effects). Binance trusts color-block contrast — adding atmospheric depth muddies the trading-platform feel.
- Don't invert `{component.button-primary}`'s text color. Black on yellow is the system's signature — white text on yellow loses contrast and brand recognition.


## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 768px | Top nav collapses to hamburger; hero h1 drops from 64px to ~36px; markets table converts to a horizontally-scrollable card list; demo grids drop to 1-up; footer 6 columns wrap to 2 |
| Tablet | 768–1024px | Top nav stays horizontal but tightens, secondary menu items hide behind a "More" dropdown; markets table 2-up; pricing/feature grids 2-up |
| Desktop | 1024–1440px | Full top-nav with all primary menu items; 5-column markets table; trading dashboards in 8/4 split (chart + side rail) |
| Wide | > 1440px | Same as desktop with more outer breathing room; max content width caps at 1280-1440px depending on surface |


## 10. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Ink: `#fcd535`
- Heading / Strong text: `#181a20`
- Body / Secondary text: `#eaecef`
- Primary Active: `#f0b90b`
- Primary Disabled: `#3a3a1f`
- Body On Light: `#181a20`
- Muted: `#707a8a`
- Muted Strong: `#929aa5`
- Hairline On Light: `#eaecef`

### Example Component Prompts

- "Create a hero on the canvas background (`#ffffff`). Headline at 64px using the display font, weight 700, line-height 1.1, color `#181a20` with fallback Google Font. Primary CTA uses `#fcd535` background, white text, 6px radius, and comfortable padding."
- "Design a content card: `#ffffff` background, 1px `#e5e7eb` border, `8px` radius, padding `24px`. Title in the title font at the token size/weight; body in the body font."

### Iteration Guide

1. Always use the documented primary color for primary CTAs and brand text.
2. Preserve the display/body font split and fallback stack.
3. Keep border radii inside the documented scale.
4. Use the section spacing token as the default vertical rhythm.

