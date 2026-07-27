---
name: react-vite-tailwind-landing-pages
description: |
  Build and polish single-page React + Vite + Tailwind CSS landing pages with
  smooth animations, product catalogs, modal details, validated forms, and
  SEO-ready structure. Covers Russian-language projects, image placeholders,
  scroll-lock modals, and data sourcing from local SQLite.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [software-development, frontend, react, vite, tailwind, landing-page, animations, modals, seo]
    related_skills: [hermes-software-development-workflow, frontend-css-maintenance, code-quality-gates, popular-web-designs, ui-ux-pro-max, claude-design]
---

# React + Vite + Tailwind Landing Pages

## Overview

This skill governs the construction and polish of single-page product landing
sites built on **React 19 + Vite + Tailwind CSS + TypeScript**. It supports two
motion strategies:

1. **CSS-only / native APIs** — preferred when the user explicitly wants to avoid
   `framer-motion`, `GSAP`, or `Lenis` ("без фреймворка", "плавность без
   фреймворка"). Uses CSS animations, transitions, and `IntersectionObserver`
   for reveals.
2. **Animation libraries** — `framer-motion` + `GSAP` + `Lenis` for richer motion
   when the user wants maximum polish and does not object to the dependencies.

Use it when the user asks for a marketing-style landing page, product showcase,
or one-page catalog with sections like Hero, Features/Applications, Product
Catalog, Gallery, Stats, and Contact.

**Core principle:** Polish is not optional. The user expects harmonious design,
smooth animations, clean typography, and bug-free interactions. Iterate until
the result looks and feels finished.

---

## Trigger Conditions

- User wants a landing page or one-page site on React + Vite
- Tech stack includes Tailwind CSS, TypeScript, and optionally animation libraries
- User explicitly asks to avoid `framer-motion`, `GSAP`, or `Lenis` (e.g. "без
  фреймворка", "plain CSS animations", "no animation libraries")
- Sections include Hero, product grid/catalog, modal details, contact form
- Need to adapt an existing Vite starter into a product showcase
- Russian-language or other localized UI required

---

## Phase 1: Confirm Stack and Project Location

1. Read `package.json` to confirm: React version, Vite version, Tailwind version,
   animation libraries (framer-motion, gsap, lenis), icon library.
2. List `src/` structure and `public/` assets.
3. Confirm project path with the user if ambiguous.

---

### Phase 3: Choose Animation Strategy

Before writing components, decide whether to use animation libraries or go
CSS-only. This choice affects dependencies, bundle size, and scroll-lock
complexity.

| Criterion | Use CSS-only | Use framer-motion + GSAP + Lenis |
|-----------|--------------|-----------------------------------|
| User says "без фреймворка" / "CSS only" | ✅ default | ❌ violates request |
| Bundle-size sensitive | ✅ smaller bundle | ~+200-400 KB JS |
| Complex scroll-linked parallax | limited | ✅ easier with GSAP ScrollTrigger |
| Scroll-lock reliability | ✅ simpler | needs Lenis coordination |
| Rapid hand-crafted motion | more manual | ✅ faster for rich sequences |

**When going CSS-only:**
- Remove `framer-motion`, `gsap`, `lenis`, `tailwindcss-animate`.
- Use `IntersectionObserver` for scroll reveals.
- Use CSS `@keyframes` for loading screen, marquee, hero entrances.
- Use native `scroll-behavior: smooth` instead of Lenis.
- See `references/no-framework-css-animations-for-react-landing.md` for the
  full replacement recipe.

**When using libraries:**
- Confirm versions in `package.json`.
- Use a single `gsap` registration module (`src/lib/gsap.ts`) instead of
  `gsap.registerPlugin(ScrollTrigger)` in every file.
- Coordinate Lenis with `scroll-locked` class via `MutationObserver`.

After choosing the strategy, continue with the design contract and component
patterns below.

## Phase 4: Design Contract (Before Code)

Before editing components, establish:

- **Section inventory**: Hero, Products/Featured, Catalog, Gallery, Applications,
  Stats, Contact/Footer
- **Color system**: dark/light theme tokens, accent color, surface elevations
- **Typography**: display font (serif/italic for headlines), body font
- **Animation language**: entrance easing, hover transitions, scroll reveals
- **Interaction model**: product click → modal vs link? order button → form?
- **SEO requirements**: title, meta description, keywords, Open Graph, JSON-LD,
  canonical URL

Write these down or present them to the user for approval on non-trivial jobs.

---

## Phase 5: Data Layer

### Product Data

Keep product data in a single source-of-truth file, e.g. `src/data/site.ts`.

```typescript
export interface Product {
  id: string;
  name: string;
  title: string;
  description: string;
  price: string;
  unit: string;
  currency: string;
  image: string;
  features: string[];
  applications: string[];
  pack?: string;
}

export interface ProductGroup {
  id: string;
  name: string;
  title: string;
  description: string;
  image: string;
  products: Product[];
}
```

### Sourcing from an Existing Database

If the user has an existing catalog (e.g. pentajunior-v2 with SQLite), query it
directly for real prices, names, and image paths, then copy needed images into
`public/images/`.

```bash
sqlite3 /home/natan/pentajunior-v2/pentajunior.db \
  "SELECT p.id, p.name, p.title, p.price, p.unit, pi.path \
   FROM products p LEFT JOIN product_images pi ON pi.product_id = p.id;"
```

### Placeholder Images

When real product photos are missing, generate consistent placeholder cards
programmatically so no UI element stays empty.

See `references/placeholder-image-generator.py` for a ready-to-use script.

---

## Phase 6: Component Patterns

### Hero Section

- Full viewport height
- Background video or image with dark gradient overlay
- Large display title (localized)
- Rotating roles / value proposition
- Two CTAs: primary (to products) and secondary (to contact)
- Scroll indicator at bottom

### Product Catalog

- Group products logically (aerosols, RTV-2 group, polyurethane)
- Each item: image, name, short title, price, feature tags
- Click opens modal with full description
- Order button opens pre-filled contact form
- No external links on product cards

### Product Modal

Must be:
- Centered on screen (flexbox wrapper)
- Scrollable internally
- Body scroll locked while open
- Scroll events blocked at the document level so the page doesn't scroll
  when wheeling over the backdrop, at modal boundaries, or via keyboard
- Closeable by the X button, backdrop click, and `Escape`
- Focus trapped while open for accessibility

Implementation: see `references/modal-scroll-lock-pattern.md`.

#### Scroll-lock that still lets the modal scroll

The classic pitfall is blocking **all** wheel/touch/keyboard events while the
modal is open. That locks the page correctly, but it also prevents the user
from scrolling the modal content itself — a critical bug on mobile and for tall
modals. Use a smart `useScrollLock` that inspects the event target and only
prevents the event when it would scroll the page, not when it would scroll an
element inside the modal.

See `references/modal-scroll-lock-with-inside-scrolling.md` for a tested,
production-ready hook plus Playwright verification snippets.

When using a third-party smooth-scroll library (e.g. Lenis), do not rely on
this hook alone — coordinate the lock through a `scroll-locked` class or by
pausing the Lenis instance while the modal is open.

### Contact / Order Form

Fields: Name, Phone, Email, Message — all required with validation.
Validation rules:
- Name: ≥ 2 chars
- Phone: `+?[\d\s\-()]{7,20}`
- Email: standard format
- Message: ≥ 10 chars

Submission: `mailto:` link with prefilled subject/body to the requested address.
Show success state after opening the mail client.

### Mobile Navigation

- Collapsible menu
- Smooth scroll to anchors
- Close menu after navigation

---

## Phase 7: Animation and Polish

### 7A — CSS-only animation stack

Use this when the user wants no animation frameworks.

1. **Scroll reveals** — `useInView` hook + `InView` wrapper + `.reveal` / `.reveal.in-view` CSS.
2. **Hero entrance** — CSS `@keyframes` for label, title, subtitle, description, CTAs.
3. **Loading screen** — CSS `@keyframes` for word enter/exit; React state drives index.
4. **Marquee** — CSS `@keyframes marquee` with duplicated content.
5. **Hover states** — Tailwind transitions + custom CSS for card lift, image zoom.
6. **Mobile menu / accordion** — CSS transitions on `max-height`, `opacity`, `transform`.
7. **Modal** — CSS transitions on `.modal-backdrop` / `.modal-content` classes.

See `references/no-framework-css-animations-for-react-landing.md` for exact code.

### 7B — Library animation stack

Use when `framer-motion`, `GSAP`, and `Lenis` are allowed.

1. **Consistent motion easing** — prefer `[0.16, 1, 0.3, 1]` for entrances.
2. **Scroll-triggered reveals** — `whileInView` with `viewport={{ once: true }}`.
3. **Hover states** — `whileHover`, `whileTap`.
4. **Loading screen** — `AnimatePresence` with `motion.span`.
5. **Smooth scroll** — Lenis with anchor-link handling.


---

## Phase 6: Localization

- Every UI string must be in the target language (e.g. Russian).
- Meta tags, loading screen, buttons, labels, placeholders, error messages.
- Keep a short glossary: Catalog → Каталог, Contact → Контакты, Order → Заказать.

---

## Phase 7: SEO and HTML Structure

- `html lang="ru"`
- Unique `<title>` with brand and keywords
- `<meta name="description">` and `keywords`
- Open Graph + Twitter Card tags
- `canonical` link
- JSON-LD `Organization` or `Product` schema
- Proper heading hierarchy: one `h1` in Hero, `h2` per section, `h3` in cards
- `robots.txt` and `sitemap.xml` in `public/` so they are copied to `dist/`
  for crawlers
- Prerendered `index.html` body content for non-JS crawlers (see
  `references/ssr-prerender-for-vite-spa.md`)

---

## Phase 8: Verification Gates

Before claiming completion, run:

```bash
npm run build      # TypeScript + Vite build + prerender passes
npx oxlint         # 0 warnings, 0 errors
```

Also verify interactively:
- All product images load
- Product modals open and close
- Modals scroll without scrolling background
- Order form validates and prefills product
- Mobile menu works
- All text is localized
- No broken external links on product elements
- **Icon containers look clean, not clipped or artifacted** — especially non-square icons (`MapPin`, `Phone`) in small circular wells; verify at 2× scale and after reveal animations finish

Add Playwright tests for critical interactions:
- modal open/close by button, Escape, and backdrop click;
- modal internal scroll without leaking to page;
- form validation and prefilled message;
- mobile navigation.

This catches regressions that manual dev-server checks miss and documents
expected behavior for the next developer.

### Visual artifact isolation checklist

When a user reports broken backgrounds, clipping, or "glitchy" icons:

1. Screenshot the area at 2× scale with Playwright `clip` to the element.
2. Check computed styles: `background`, `border`, `border-radius`, `overflow`, `box-shadow`, `filter`, `transform`, plus `::before`/`::after` content.
3. Hide the background layer (video/image/gradient) in DevTools to separate icon issues from background issues.
4. If the icon still looks wrong, inspect the SVG `viewBox` and path — the icon shape may not fit the chosen container (e.g. `MapPin` in a small circle).
5. Prefer a larger wrapper or a rounded-square shape (`rounded-xl`/`rounded-2xl`) over forcing non-square icons into tiny circles.

See `frontend-css-maintenance/references/diagnosing-broken-icon-backgrounds.md` for the full recipe.
expected behavior for the next developer.

### Visual artifact isolation checklist

When a user reports broken backgrounds, clipping, or "glitchy" icons:

1. Screenshot the area at 2× scale with Playwright `clip` to the element.
2. Check computed styles: `background`, `border`, `border-radius`, `overflow`, `box-shadow`, `filter`, `transform`, plus `::before`/`::after` content.
3. Hide the background layer (video/image/gradient) in DevTools to separate icon issues from background issues.
4. If the icon still looks wrong, inspect the SVG `viewBox` and path — the icon shape may not fit the chosen container (e.g. `MapPin` in a small circle).
5. Prefer a larger wrapper or a rounded-square shape (`rounded-xl`/`rounded-2xl`) over forcing non-square icons into tiny circles.

See `frontend-css-maintenance/references/diagnosing-broken-icon-backgrounds.md` for the full recipe.

## Task Framing for Design Polish + Bugfix Work

When the user wants to refine an existing landing page ("проработай дизайн", "убери баги", "сделай плавный скролл", "поправь мобильную версию"), they should not need to negotiate the workflow each time. Use this template as a default. It matches the user's preferred order: audit → design contract → plan → execute → verify → finish.

### Default prompt template to return to the user

```
Проект: <project-name>
Путь: <absolute-path>

Задача:
1. Проработать существующий дизайн — привести к полированному, целостному виду.
2. Исправить баги в UI/UX и взаимодействиях.
3. Сделать скроллинг плавным (CSS scroll-behavior: smooth, и при необходимости Lenis/GSAP).
4. Использовать все подходящие навыки: frontend, design, code-quality-gates.

Что нужно сделать:
- Провести аудит текущего состояния (структура, стили, анимации, баги).
- Определить конкретные баги (hover, модалки, формы, мобильное меню, скролл).
- Предложить и согласовать правки по дизайну.
- Реализовать правки.
- Прогнать build + lint.
- Проверить визуально (скриншоты / браузер).
- Написать / обновить Playwright-тесты на критичные взаимодействия.

Контрольные точки:
- После аудита — отчёт.
- После дизайн-правок — показать результат.
- После багфикса — список исправленных багов.
- Финал — build проходит, тесты проходят.

Ограничения:
- Не менять стек без согласования.
- Сохранить текущую визуальную идентичность, улучшить полировку.
- Все изменения в отдельной ветке / worktree.
```

### How the agent should respond

1. Load relevant skills immediately (this skill, `frontend-css-maintenance`, `frontend-efficiency-audit`, `code-quality-gates`, plus design skills such as `ui-ux-pro-max` or `popular-web-designs` when visual polish is requested).
2. Run a quick baseline: `tsc -b && npx oxlint && npm run build` if it is fast.
3. Inspect project structure, package.json, tailwind.config, index.css, and the main sections/components.
4. Present a short audit with concrete findings: bugs, typography issues, mobile risks, scroll behavior.
5. Propose a design contract: what will change and what will not.
6. After user approval, write an implementation plan with verification commands per step.
7. Execute in small commits/gates; do not batch unrelated visual and structural changes.
8. Finish only after fresh build, lint, and Playwright (or manual browser) verification evidence.

### Pitfall: accepting "make it beautiful" without constraints

Vague requests invite rework. Always surface the concrete dimensions: typography, spacing, color, motion, mobile, accessibility. If the user does not specify the scroll strategy (CSS vs Lenis), default to CSS-only smooth scroll and ask for confirmation before adding dependencies.

---

## Task Framing for Design Polish + Bugfix Work

When the user wants to refine an existing landing page ("проработай дизайн",
"убери баги", "сделай плавный скролл", "поправь мобильную версию"), they should
not need to negotiate the workflow each time. Use this template as a default.
It matches the user's preferred order: **audit → design contract → plan →
execute → verify → finish**.

### Default prompt template to return to the user

```
Проект: <project-name>
Путь: <absolute-path>

Задача:
1. Проработать существующий дизайн — привести к полированному, целостному виду.
2. Исправить баги в UI/UX и взаимодействиях.
3. Сделать скроллинг плавным (CSS scroll-behavior: smooth, и при необходимости Lenis/GSAP).
4. Использовать все подходящие навыки: frontend, design, code-quality-gates.

Что нужно сделать:
- Провести аудит текущего состояния (структура, стили, анимации, баги).
- Определить конкретные баги (hover, модалки, формы, мобильное меню, скролл).
- Предложить и согласовать правки по дизайну.
- Реализовать правки.
- Прогнать build + lint.
- Проверить визуально (скриншоты / браузер).
- Написать / обновить Playwright-тесты на критичные взаимодействия.

Контрольные точки:
- После аудита — отчёт.
- После дизайн-правок — показать результат.
- После багфикса — список исправленных багов.
- Финал — build проходит, тесты проходят.

Ограничения:
- Не менять стек без согласования.
- Сохранить текущую визуальную идентичность, улучшить полировку.
- Все изменения в отдельной ветке / worktree.
```

### How the agent should respond

1. Load relevant skills immediately (this skill, `frontend-css-maintenance`,
   `frontend-efficiency-audit`, `code-quality-gates`, plus design skills such as
   `ui-ux-pro-max` or `popular-web-designs` when visual polish is requested).
2. Run a quick baseline: `tsc -b && npx oxlint && npm run build` if it is fast.
3. Inspect project structure, package.json, tailwind.config, index.css, and the
   main sections/components.
4. Present a short audit with concrete findings: bugs, typography issues, mobile
   risks, scroll behavior.
5. Propose a design contract: what will change and what will not.
6. After user approval, write an implementation plan with verification commands
   per step.
7. Execute in small commits/gates; do not batch unrelated visual and structural
   changes.
8. Finish only after fresh build, lint, and Playwright (or manual browser)
   verification evidence.

### Pitfall: accepting "make it beautiful" without constraints

Vague requests invite rework. Always surface the concrete dimensions:
typography, spacing, color, motion, mobile, accessibility. If the user does not
specify the scroll strategy (CSS vs Lenis), default to CSS-only smooth scroll
and ask for confirmation before adding dependencies.

---

## Common Pitfalls

- **Skipping design contract** — results in mismatched sections and rework
- **Product cards linking externally** — user wants inline modal behavior
- **Empty image slots** — always fill placeholders, even if generated
- **Modals not centered** — use flex wrapper, not absolute positioning alone
- **Background scroll leaking through modal** — implement body scroll lock + wheel trap
- **Lenis overriding the scroll lock** — freeze body with `position: fixed` and stop Lenis via a `scroll-locked` class
- **Stale `read_file` cache after rapid edits** — verify with `terminal` or Python
- **English strings left in UI** — scan all `.tsx` files before finishing
- **Missing SEO meta tags** — add them to `index.html` and/or an SEO component
- **Not running build/lint** — always verify before declaring done
- **Manual-only verification** — write Playwright tests for modal and form behavior
- **Vague design/bugfix requests** — always translate into concrete audit + design contract + plan before coding
- **Forcing non-square icons into tiny circles** — `MapPin`, `Phone`, and similar silhouettes look broken inside small `rounded-full` wells. Use a larger wrapper or `rounded-xl`/`rounded-2xl` instead. See `frontend-css-maintenance/references/diagnosing-broken-icon-backgrounds.md`.
- **Forcing non-square icons into tiny circles** — `MapPin`, `Phone`, and similar silhouettes look broken inside small `rounded-full` wells. Use a larger wrapper or `rounded-xl`/`rounded-2xl` instead. See `frontend-css-maintenance/references/diagnosing-broken-icon-backgrounds.md`.

---

## References

- `references/modal-scroll-lock-pattern.md` — body scroll lock + wheel event trap for accessible modals, including Lenis coordination
- `references/modal-scroll-lock-with-inside-scrolling.md` — body scroll lock that still allows the modal content itself to scroll (tested hook + Playwright snippets)
- `references/modal-centering-flexbox.md` — center modals vertically and horizontally without absolute positioning bugs
- `references/vite-seo-template.md` — SEO meta and JSON-LD template for Vite index.html
- `references/russian-landing-glossary.md` — common UI labels in Russian for landing pages
- `references/ssr-prerender-for-vite-spa.md` — prerender a Vite SPA with Playwright so search bots see rendered content
- `templates/playwright-modal-test.spec.ts` — starter Playwright spec for modal open/close, Escape, backdrop click, and scroll isolation

