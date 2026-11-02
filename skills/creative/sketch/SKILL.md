---
name: sketch
description: Use when exploring UI directions quickly. Produce 2-3 disposable HTML mockup variants for side-by-side comparison.
version: 1.0.0
author: Hermes Agent (adapted from gsd-build/get-shit-done)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sketch, mockup, design, ui, prototype, html, variants, exploration, wireframe, comparison]
    related_skills: [single-file-web-page, excalidraw]
---

# Sketch

Use this skill when the user wants to **see a design direction before committing** to one — exploring a UI/UX idea as disposable HTML mockups. The point is to generate 2-3 interactive variants so the user can compare visual directions side-by-side, not to produce shippable code.

Load this when the user says things like "sketch this screen", "show me what X could look like", "compare layout A vs B", "give me 2-3 takes on this UI", "let me see some variants", "mockup this before I build".

## When NOT to use this

- User wants a production component — build it properly in the project
- User wants a polished one-off HTML artifact (landing page, deck) — `single-file-web-page`
- User wants a diagram — `excalidraw`, `architecture-diagram`
- The design is already locked — just build it

## If the user has the full GSD system installed

If `gsd-sketch` shows up as a sibling skill (installed via `npx get-shit-done-cc --hermes`), prefer **`gsd-sketch`** for the full workflow: persistent `.planning/sketches/` with MANIFEST, frontier mode analysis, consistency audits across past sketches, and integration with the rest of GSD. This skill is the lightweight standalone version — one-off sketching without the state machinery.

## Core method

```
intake  →  variants  →  head-to-head  →  pick winner (or iterate)
```

### 1. Intake (skip if the user already gave you enough)

Before generating variants, get three things — one question at a time, not all at once:

1. **Feel.** "What should this feel like? Adjectives, emotions, a vibe." — *"calm, editorial, like Linear"* tells you more than *"minimal"*.
2. **References.** "What apps, sites, or products capture the feel you're imagining?" — actual references beat abstract descriptions.
3. **Core action.** "What's the single most important thing a user does on this screen?" — the variants should all serve this well; if they don't, they're just decoration.

Reflect each answer briefly before the next question. If the user already gave you all three upfront, skip straight to variants.

### 2. Variants (2-3, never 1, rarely 4+)

Produce **2-3 variants** in one go. Each variant is a complete, standalone HTML file. Don't describe variants — build them. The point is comparison.

Each variant should take a **different design stance**, not different pixel values. Three good variant axes:

- **Density:** compact / airy / ultra-dense (pick two contrasting poles)
- **Emphasis:** content-first / action-first / tool-first
- **Aesthetic:** editorial / utilitarian / playful
- **Layout:** single-column / sidebar / split-pane
- **Grounding:** card-based / bare-content / document-style

Pick one axis and pull apart from it. Two variants that differ only in accent color are wasted effort — the user can't distinguish them.

**Variant naming:** describe the stance, not the number.

```
sketches/
├── 001-calm-editorial/
│   ├── index.html
│   └── README.md
├── 001-utilitarian-dense/
│   ├── index.html
│   └── README.md
└── 001-playful-split/
    ├── index.html
    └── README.md
```

### 3. Make them real HTML

Each variant is a **single self-contained HTML file**:

- Inline `<style>` — no build step, no external CSS
- System fonts or one Google Font via `<link>`
- Tailwind via CDN (`<script src="https://cdn.tailwindcss.com"></script>`) is fine
- Realistic fake content — actual sentences, actual names, not "Lorem ipsum"
- **Interactive**: links clickable, hovers real, at least one state transition (open/close, filter, toggle). A frozen static image is a worse spike than a sloppy animated one.

Open it in a browser. If it looks broken, fix it before showing the user.

**Verify variants visually — use Hermes' browser tools.** Don't just write HTML and hope it renders; load each variant and look at it:

```
browser_navigate(url="file:///absolute/path/to/sketches/001-calm-editorial/index.html")
browser_vision(question="Does this layout look clean and readable? Any visible bugs (overlapping text, unstyled elements, broken images)?")
```

`browser_vision` returns an AI description of what's actually on the page plus a screenshot path — catches layout bugs that pure source inspection misses (e.g. a font import that silently failed, a flex container that collapsed). Fix and re-navigate until each variant looks right.

**Default CSS reset + system font stack** for fast starts:

```html
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    color: #1a1a1a;
    background: #fafafa;
    line-height: 1.5;
  }
</style>
```

### 4. Variant README

Each variant's `README.md` answers:

```markdown
## Variant: {stance name}

### Design stance
One sentence on the principle driving this variant.

### Key choices
- Layout: ...
- Typography: ...
- Color: ...
- Interaction: ...

### Trade-offs
- Strong at: ...
- Weak at: ...

### Best for
- The kind of user or use case this variant actually serves
```

### 5. Head-to-head

After all variants are built, present them as a comparison. Don't just list — **opinionate**:

```markdown
## Three takes on the home screen

| Dimension | Calm editorial | Utilitarian dense | Playful split |
|-----------|----------------|-------------------|---------------|
| Density   | Low            | High              | Medium        |
| Primary action visibility | Low | High | Medium |
| Scan-ability | High | Medium | Low |
| Feel | Calm, trusted | Sharp, tool-like | Inviting, energetic |

**My take:** Utilitarian dense for power users, calm editorial for content-forward audiences. Playful split is weakest — tries to do both and commits to neither.
```

Let the user pick a winner, or combine two into a hybrid, or ask for another round.

## Redesigning a live site: variants that can actually be shipped

A sketch for an existing production site stops being disposable — it is the candidate the owner will judge the
real site against. Six rules change the method:

1. **Export the real content before drawing anything.** Pull the page's own data (categories, products, prices,
copy, statistics) and its assets out of the source system into one JSON file that every variant reads. Prototypes
built on invented numbers teach the owner nothing, and the mismatch surfaces only after the rebuild starts.
2. **Audit the “before” with numbers first.** Screenshot the live page at desktop and phone widths, measure it,
and write a short audit note: structure, palette, typography, the defects you can actually see (a stray band under
the header, a navigation item breaking into three lines, a muted subtitle on a dark hero). That note is what
makes the variants comparable. **Identify the element behind every oddity before writing it down as a defect:**
the “stray light band” under the header was a real utility strip rendered at near-zero contrast, so the variants
fixed it by giving that strip a proper bar — delete the element without looking and real content goes with it.
3. **System before directions.** Fix the tokens — type scale, vertical rhythm, grid, radii, shadows, motion,
media aspect ratios, and palette *slots* — in one file, then let each direction fill the palette slots with its
own colours. Three variants built on unrelated scales can only be preferred, never compared.
4. **One direction per file, one agent per file, in parallel.** Same content JSON and same invariants in every
brief; what differs is the stance — mood, density, typographic register — not two shades of the same page. Never
let two agents write the same file. Each brief carries the content JSON path, the token file, the boundaries
(which project not to touch), and the measurer command; each agent must **return its own JSON measurement lines
and screenshot paths** — a prose “looks good” is not evidence, and the parent re-measures anyway.
5. **Measure each variant before showing it.** Overflow zero, no console errors, no 404s at 1440 / 768 / 375, and
look at the screenshots yourself (`single-file-web-page` → `scripts/check-page.cjs`). A variant the owner cannot
open is not a variant.
6. **Fact-check the variants against the source page.** Grep each file for claim-bearing text — years (“с 1997 г.”),
statistics, prices, certifications, “собственное производство” — and confirm every one exists in the source HTML
(`curl -s http://localhost:PORT/ | grep -c '<phrase>'`). A variant that invents a fact or a number is a liability
the owner may ship by accident, and the check costs one command.

**Invariants while redesigning a live site:** copy, headings, prices, meta tags and structured data move over
unchanged — a redesign changes arrangement, not the words; photos of mixed origin go into one fixed frame
(`aspect-ratio` + `object-fit: cover`) instead of being resized one by one; long navigation labels and wrong
plurals are defects to fix, not content to preserve.

**After the pick:** the chosen direction becomes the reference pages (catalogue with filters, product card, price
list, contacts, phone widths), and the transfer into the real project happens page by page behind that project's
build gate — never as one wholesale rewrite of its stylesheet.

**Build the reference pages on a frozen kit, not by copy-paste.** Pull what the approved variant already contains —
its stylesheet, its header and footer markup — into a small per-direction layer (`directions/<name>/base.css` plus
`partials/`), then one agent per page group copies the partials in, links the base and adds only page-scoped styles
under a prefix (`.cat-`, `.prd-`). The base is read-only: several agents sharing a stylesheet they may all edit
diverge in the header faster than a single agent produces pages.

**Owners keep what they like: develop every direction they named to the same page set, and park the runner-up
whole.** The page set must be the same and the data identical, or the comparison is not honest, and a direction
that merely stopped being drawn can never be picked up later. Say where it is parked and what finishing it would
cost — a half-built variant is worse than a shelved one.

**Handing the variants over:** the files stay self-contained, but their photos are reached through paths relative
to the project — a copy saved on its own shows broken images, so send the served URL
(`http://localhost:8130/directions/01-*.html`) together with the screenshots. Tall pages photograph badly when
scaled down to a chat preview: send the full-height desktop shot, and slice it (crop the original at full
resolution) when a section has to be judged closely.

## Single-file variant gallery (quick A/B in one scroll)

When the user only needs to **pick a visual direction** and doesn't require separate artifacts, pack 4-6 variants as sections inside **one self-contained HTML file**. This is faster than per-variant directories and lets the user scroll through options in a single browser tab.

### How to build it

- One `<section class="variant v1|v2|...">` per design direction.
- Shared CSS variables at the top for the project's palette; each variant overrides them.
- Reuse the same sample data across all variants so the user compares *style*, not content.
- Label each section with a short stance name (e.g., "Clean cards with top image", "Dark hero cards", "Magazine tiles").

### Example layout

```html
<section class="variant v1">
  <div class="variant-label">Variant 1 — Clean cards with top image</div>
  <div class="cards">...</div>
</section>
<section class="variant v2">
  <div class="variant-label">Variant 2 — Dark hero cards</div>
  <div class="cards">...</div>
</section>
```

### When to use

- The component is narrow (a card, a list item, a form, a blog index).
- The user explicitly asks to "show me a few styles" or "let me choose."
- You already know the project's color palette and want to stay inside it.

### When to avoid

- Full page layouts with heavy navigation/footer repetition — use separate files.
- Variants that need real interaction beyond hover/filter — separate files are easier to wire.

See `references/catalog-card-seo.md` for a worked example of moving from a chosen sketch to production while keeping catalog cards SEO-clean.

## Interactivity bar

A sketch is interactive enough when the user can:

1. **Click a primary action** and something visible happens (state change, modal, toast, navigation feint)
2. **See one meaningful state transition** (filter a list, toggle a mode, open/close a panel)
3. **Hover recognizable affordances** (buttons, rows, tabs)

More than that is over-engineering a throwaway. Less than that is a screenshot.

## Frontier mode (picking what to sketch next)

If sketches already exist and the user says "what should I sketch next?":

- **Consistency gaps** — two winning variants from different sketches made independent choices that haven't been composed together yet
- **Unsketched screens** — referenced but never explored
- **State coverage** — happy path sketched, but not empty / loading / error / 1000-items
- **Responsive gaps** — validated at one viewport; does it hold at mobile / ultrawide?
- **Interaction patterns** — static layouts exist; transitions, drag, scroll behavior don't

Propose 2-4 named candidates. Let the user pick.

## Output

- Create `sketches/` (or `.planning/sketches/` if the user is using GSD conventions) in the repo root
- One subdir per variant: `NNN-stance-name/index.html` + `README.md`
- Tell the user how to open them: `open sketches/001-calm-editorial/index.html` on macOS, `xdg-open` on Linux, `start` on Windows
- Keep variants disposable — a sketch that you felt the need to preserve should be promoted into real project code, not curated as an asset

**Typical tool sequence for one variant:**

```
terminal("mkdir -p sketches/001-calm-editorial")
write_file("sketches/001-calm-editorial/index.html", "<!doctype html>...")
write_file("sketches/001-calm-editorial/README.md", "## Variant: Calm editorial\n...")
browser_navigate(url="file://$(pwd)/sketches/001-calm-editorial/index.html")
browser_vision(question="How does this look? Any obvious layout issues?")
```

Repeat for each variant, then present the comparison table.

## Attribution

Adapted from the GSD (Get Shit Done) project's `/gsd-sketch` workflow — MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)). The full GSD system ships persistent sketch state, theme/variant pattern references, and consistency-audit workflows; install with `npx get-shit-done-cc --hermes --global`.
