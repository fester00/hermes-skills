# Dark Terminal Theme Design Tokens

Reference palette for static documentation sites targeting developers. Inherits from GitHub dark mode but adds Russian-language polish.

## CSS Custom Properties

```css
:root{
  --bg:#0d1117;          /* page background */
  --surface:#161b22;     /* cards, sidebar, header */
  --border:#30363d;      /* all borders, dividers */
  --text:#c9d1d9;        /* primary text */
  --muted:#8b949e;        /* secondary, placeholder */
  --accent:#58a6ff;      /* links, active nav, hover */
  --green:#3fb950;       /* success states */
  --red:#f85149;         /* error states */
  --purple:#a371f7;     /* attention, callouts */
  --radius:6px;
  --nav-h:56px;
  --sidebar-w:260px;
}
```

## Syntax Highlight Palette (self-built JS tokenizer)

| Token class | Color | Used for |
|-------------|-------|----------|
| `.tk-keyword` | `#ff7b72` | PHP keywords (echo, if, function, return...) |
| `.tk-string` | `#a5d6ff` | Single/double quoted strings |
| `.tk-comment` | `#8b949e` + italic | `//`, `/* ... */`, `#` |
| `.tk-number` | `#79c0ff` | Integers, floats, hex |
| `.tk-function` | `#d2a8ff` | Identifiers followed by `(` |
| `.tk-variable` | `#ffa657` | `$var` in PHP, regular identifiers |

## Typography

- Body: `system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif`
- Code: `'Fira Code', monospace` (loaded via Google Fonts `@import`)
- Line-height: 1.5 body, 1.55 code blocks
- Tab width: 2 spaces in code examples

## Scrollbar (Firefox + WebKit)

```css
html{
  scrollbar-color: var(--border) var(--surface);
  scrollbar-width: thin;
}
```

## Mobile Breakpoint

- Single breakpoint at `768px`
- Sidebar becomes off-canvas with `#menu-toggle` button
- Cards collapse from 3 → 2 → 1 column
- Search input max-width shrinks to 260px

## Fixed Header Pitfall

`.content` MUST have top padding equal to `var(--nav-h)` + desired spacing. Without this, the first heading is clipped by the fixed navbar.
