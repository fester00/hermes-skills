# Converting DESIGN.md Teardowns into Narrative Templates

A DESIGN.md file is usually either:

1. **YAML + narrative** — YAML front matter with tokens, followed by Markdown sections.
2. **Pure narrative** — Markdown headings and tables only, no front matter.

When the user asks to convert a batch of these into narrative templates (e.g. for the
`popular-web-designs` skill library), follow this workflow.

## Target template shape

```md
# Design System: <Display Name>

> **Hermes Agent — Implementation Notes**
>
> The original site uses proprietary fonts. <one-line substitute note>.
> For self-contained HTML output, use these CDN substitutes:
> - **Primary:** `<Google Font>` | **Mono:** `<Google Mono>`
> - **Font stack (CSS):** `font-family: '<Google Font>', system-ui, ...`
> - **Mono stack (CSS):** `font-family: '<Mono>', ui-monospace, ...`
> ```html
> <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
> ```
> Use `write_file` to create HTML, serve via a local HTTP server or static preview, and verify visual accuracy with `browser_vision`.
> Verify visual accuracy with `browser_vision` after generating.

## <Token Summary / Overview>

<Narrative from upstream DESIGN.md>
```

## Conversion steps

1. **List source files** directly with `terminal` and `read_file`; do not rely
   on `search_files` with glob-style patterns like `*.md` — `search_files` uses
   regex and patterns such as `^.*\.md$` can return zero matches depending on
   implementation. Prefer `ls /path/to/design-md/`.
2. **Read each `DESIGN.md`** with `read_file`. Large files may truncate at 500
   lines; use `offset=` parameters to read remaining sections.
3. **Parse front matter** with Python + `yaml`:
   - Extract `colors`, `typography`, `rounded`, `spacing`, `components`.
   - If the file has no front matter, skip the token summary block and preserve
     the narrative sections as-is.
4. **Determine the display font** from `typography.*.fontFamily`. Strip generic
   fallbacks (`system-ui`, `-apple-system`, `Inter`, `Arial`, etc.) and pick the
   proprietary/custom face. Suggest a Google Fonts substitute based on character:
   - Geometric display → `Inter`, `DM Sans`, `Space Grotesk`
   - Heavy condensed display → `Oswald`, `Anton`, `Bebas Neue`
   - High-contrast serif → `Playfair Display`, `Source Serif Pro`
   - Monospace labels → `Space Mono`, `JetBrains Mono`, `Inconsolata`
5. **Emit a token summary** only when YAML data exists:
   - Colors as bullet list with hex values.
   - Typography as a compact table: token, font, size, weight, line-height,
     letter-spacing.
   - Radius / spacing as token/value tables.
   - Components as a flat list of key/value pairs (skip `ex-*` illustrative
     entries unless the user wants them).
6. **Append the upstream narrative** verbatim, removing any duplicate leading
   title. Ensure the first narrative heading is `## Overview` or matches the
   original section hierarchy.
7. **Save** to `~/.hermes/skills/creative/popular-web-designs/templates/<site>.md`.
8. **Verify** all target files exist with a shell loop and spot-read headers.

## Font substitution notes for common brands

| Proprietary Font | Recommended Substitute | Why |
|---|---|---|
| sohne-var (Stripe) | Source Sans 3 | Light weight elegance |
| LamboType | Oswald / Anton | Ultra-condensed uppercase display |
| MarkForMC | Sofia Sans | Documented Mastercard fallback |
| Manuka | Anton / Oswald / Bebas Neue | Brutalist display |
| WiredDisplay | Playfair Display | High-contrast editorial serif |
| NeueHaasGrotesk Display | Inter 300 | Thin display weight |
| Salesforce Avant Garde / Sans | Inter | Humanist sans |
| Universal Sans | Inter | Geometric, normal tracking |
| Vodafone custom display | Inter 800 | Heavy uppercase display |
| WF Visual Sans | Inter | Clean geometric sans |
| Wise Sans | Inter 900 / Manrope 800 | Heavy geometric display |
| SoDoSans | Inter | Friendly, confident |
| Lander Tall | Source Serif Pro | Warm editorial serif |
| Kalam | Kalam | Handwritten cup-name script |

## Pitfalls

- **Do not assume `search_files` finds markdown files.** Use `terminal` listing
  or direct paths.
- **Large DESIGN.md files truncate at 500 lines by default.** Continue with
  `offset=501` (or the hint provided by `read_file`).
- **Preserve narrative sections verbatim** — they carry the brand rationale
  and component examples that token tables alone lose.
- **Avoid claiming proprietary fonts are available.** Always map to an open
  substitute in the implementation notes.
- **Verify outputs with a shell loop** rather than trusting the file count from
  a single directory read.
