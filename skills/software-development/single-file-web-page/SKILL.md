---
name: single-file-web-page
description: Use when a page must be one self-contained HTML file.
category: software-development
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [html, css, landing, parallax, single-file, visual-verification, progressive-enhancement, scroll-animation]
    related_skills: [ui-ux-pro-max, code-quality-gates, sketch]
---

# Single-file web page

A designed page in one HTML file, opened straight from disk: no build step, no bundler, no external
scripts. The deliverable is the file itself, sent to the user.

## When to use

- «сделай сайт / лендинг / страницу одним файлом», "one HTML file", "no dependencies".
- Decorative and promo pages: parallax depth, scroll storytelling, hero-centered landing, effect-driven
  visuals.
- A demo the user opens locally or shows to somebody — not a project they will maintain.

Not for: multi-page sites, anything with a backend, or a page a team will edit — use that project's stack.

## Procedure

1. **Brief before markup.** Load `ui-ux-pro-max`, search its database for the product type and style, and
   read the matching vault note under `Design/UI-UX Pro Max/` (e.g. `Styles/49 — Parallax Storytelling.md`).
   Fix the brief first: one primary colour role, at most two accents, a display + body font pairing, a
   deliberate density, and the anti-generic checklist passing. Only then write code.
2. **Write one file** — tokens first, content second, effect layers last (see Build rules).
3. **Make content independent of JavaScript** before adding any reveal animation (see Pitfalls).
4. **Verify with real runs** — assertions from inside the page plus a screenshot you actually look at:
   `references/headless-visual-verification.md`.
5. **Deliver** the absolute path with `MEDIA:`, plus one preview screenshot, and report what was measured
   rather than what was intended.

## Build rules

- Design tokens in `:root` — surfaces, one accent, muted, line, panel — each colour carrying a named role,
  plus `--serif` / `--sans` variables. No unnamed "accent-2".
- **Parallax depth**: one fixed layer per plane, speeds ≈ 0.10 / 0.26 / 0.52 from far to near. A single
  `requestAnimationFrame` loop writes CSS custom properties (`--sy`, `--mx`, `--my`, `--p`) and CSS does the
  arithmetic: `transform: translate3d(0, calc(var(--syl) * var(--f) * -1px), 0)`. Never lay out elements one by
  one in JS — it fights the compositor and stutters on scroll. **Bound the travel**: drive the layers from
  `--syl = min(scrollY, TRAVEL)` (≈700 px, ≈600 on phones) while the progress bar keeps the raw `--sy`.
  Unbounded offsets push every plane off screen and the end of the page turns into flat emptiness. Put a
  **static base layer** (`--f:0`, the same night gradient) under the moving planes so a gap can never show.
- Ambient particles (fireflies, dust, snow) are created once by JS into a container inside the matching
  layer with staggered `animation-delay`; they never enter the layout flow.
- Decorative layers: `aria-hidden="true"` on the stage, `pointer-events:none`, `will-change:transform`,
  slightly negative `inset` so movement never exposes an edge.
- `@media (prefers-reduced-motion: reduce)`: disable layer transforms and ambient animation with
  `!important`, and reveal all scroll-gated content.
- Fonts: Google Fonts only as progressive enhancement, always with a system fallback stack
  (`Georgia, "Times New Roman", serif`). The CDN is unreliable from Russia — the page must look deliberate
  without it.
- Scroll-gated reveal: the hidden state lives behind a `js` class added inline in `<head>`, plus a ~1.5 s
  timer that reveals everything if the observer never fires.
- Mobile: in one `@media (max-width: 640px)` block soften the plane speeds (≈0.06 / 0.15 / 0.28), scale the
  decorative layers, trim section padding, drop `backdrop-filter` (expensive on phone GPUs) and shrink the
  wide-tracked small caps. Use `min-height:100dvh` after a `100vh` fallback so the mobile URL bar cannot
  swallow the hero, and add the `-webkit-backdrop-filter` prefix for Safari. Check the hero at 390 px before
  shipping.
- Semantics for a reading page: real `<h1>`/`<h2>`, `lang`, decoration marked decorative, body copy at
  ≥16 px with contrast that survives on the dark surface.

## Pitfalls

- **Never make readability depend on JavaScript.** A panel that starts at `opacity:0` and waits for
  `IntersectionObserver` renders as an empty page in every state where the observer does not fire — a
  headless dump, an anchor jump, a blocked or failed script. Gate the hidden state behind the inline `js`
  class and keep a timer fallback, then verify both states (script working / class removed).
- **CSS that looks correct is not evidence that CSS is running.** After a programmatic scroll, read the
  *computed* transform of every layer and confirm the planes differ in the designed ratio; "it should
  translate" is not proof.
- **A DOM assertion is not visual proof.** `querySelector` happily finds text that is invisible on screen.
  Load the screenshot with vision and confirm the intended content is really rendered before calling the page
  done.
- **Check the END of the page, not just the hero.** Unbounded parallax travel empties the bottom third: the
  planes have flown off and the reader scrolls through flat background. Assert per layer at maximum scroll that
  the artwork still covers the viewport (`getBoundingClientRect()`), and do it on a phone-width viewport too —
  a taller document scrolls further and fails sooner.
- Keep the page network-independent — external font CSS may hang rather than fail; the fallback stack
  must carry the design on its own.
- Do not bolt on scroll-jacking, custom cursors or hidden navigation to look "premium": they break keyboard
  and mobile use, and the user did not ask for them.
- Keep decoration out of the reading order: content sections scroll, decor layers do not participate in
  layout.

## Deliverable checklist

- One file, no external `<script src>`, no build step, opens from `file://`.
- Content visible with scripts disabled; motion reduced when the OS asks for it.
- Measured evidence in the reply: layer offsets per plane, JS error count, screenshot checked by eye.
- File path sent as `MEDIA:` with one preview image.
