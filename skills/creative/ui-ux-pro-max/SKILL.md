---
name: ui-ux-pro-max
description: |
  AI-powered design intelligence database with 161 product-type design systems,
  67 UI styles, 161 color palettes, 57 font pairings, 99 UX guidelines, and
  25 chart types. Provides industry-specific design recommendations via Python
  BM25 search or direct CSV lookup.
version: 2.0.0
author: NextLevelBuilder (integrated by Hermes)
license: MIT
metadata:
  hermes:
    tags: [design, ui, ux, design-system, color-palette, typography, style-guide, ai-skill]
    related_skills: [luxury-immersive-web, claude-design, popular-web-designs, design-md]
---

# UI/UX Pro Max — Design Intelligence

Integrated knowledge base from the open-source UI/UX Pro Max project
(github.com/nextlevelbuilder/ui-ux-pro-max-skill, 88.9k stars, MIT license).

Provides searchable design systems for any product type: colors, fonts,
styles, landing patterns, anti-patterns, and UX guidelines.

## When To Use

Load this skill when the user starts ANY web design task — landing page,
dashboard, corporate site, app UI. It provides the *design brief* before
coding begins.

**Trigger phrases:**
- "сделай сайт для..."
- "design a ... landing page"
- "какой стиль выбрать"
- "какие цвета подходят"
- "какие шрифты для luxury"
- "help me design a ..."

## How It Works

1. User describes their project ("luxury art gallery", "corporate CRM", etc.)
2. Skill searches the database → returns industry-matched design system
3. Recommendations feed into `luxury-immersive-web` or `claude-design` for implementation

## Database Contents

| Domain | File | Count | What it contains |
|--------|------|-------|------------------|
| Products | `data/products.csv` | 161 | Product type → recommended style, pattern, colors |
| Styles | `data/styles.csv` | 67 | UI style descriptions, CSS keywords, AI prompts |
| Colors | `data/colors.csv` | 161 | Full 16-color design systems (primary/accent/bg/etc) |
| Typography | `data/typography.csv` | 57 | Font pairings with Google Fonts URLs + Tailwind config |
| UX Guidelines | `data/ux-guidelines.csv` | 99 | Best practices, anti-patterns, accessibility rules |
| Charts | `data/charts.csv` | 25 | Chart types + library recommendations |
| Landing | `data/landing.csv` | 24 | Landing page patterns and CTA strategies |
| Icons | `data/icons.csv` | — | Icon library recommendations |
| App Interface | `data/app-interface.csv` | — | Mobile app UI patterns |
| Stacks | `data/stacks/*.csv` | 15 | Framework-specific guidelines (Next.js, React, Vue, etc) |

## Search Methods

### Method 1: BM25 Search (Recommended)

```bash
cd ~/.hermes/skills/creative/ui-ux-pro-max/scripts
python3 search.py "<query>" --domain <domain> [--max-results N]
```

**Domains:** `product`, `style`, `color`, `typography`, `landing`, `chart`, `ux`, `app-interface`

**Examples:**
```bash
# Find design system for a luxury gallery
python3 search.py "luxury gallery" --domain product --max-results 3

# Get glassmorphism technical details
python3 search.py "glassmorphism" --domain style

# Find font pairings
python3 search.py "Cormorant" --domain typography

# Get complete design system (all domains combined)
python3 search.py "luxury art gallery" --design-system -p "ProjectName"
```

### Method 2: Direct CSV Lookup

For exact lookups, read CSV files directly:

```python
import csv
from pathlib import Path

DATA_DIR = Path("~/.hermes/skills/creative/ui-ux-pro-max/data").expanduser()

def find_product_type(keyword):
    with open(DATA_DIR / "products.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if keyword.lower() in row["Product Type"].lower():
                return row
    return None

def get_color_palette(product_type):
    with open(DATA_DIR / "colors.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if product_type in row["Product Type"]:
                return row
    return None
```

### Method 3: Design System Generation (Full Brief)

```bash
python3 search.py "<project description>" --design-system -p "<ProjectName>"
```

Outputs a complete design system:
- Landing page pattern
- Recommended UI style
- Full color palette (16 colors)
- Typography pairing
- Key effects and animations
- Anti-patterns to avoid
- Pre-delivery checklist

## Integration with Other Skills

### With `luxury-immersive-web`

1. Use ui-ux-pro-max to get the design brief
2. Apply luxury-immersive-web patterns for implementation

Example workflow:
```
User: "Сделай сайт для VIDVIS — luxury art gallery"
↓
Search: "luxury art gallery" --design-system
↓
Result: Liquid Glass + Glassmorphism, Black+Gold, Cormorant/Montserrat
↓
Apply: PerspectiveScene, ParallaxDivider, 3D tilt cards, grain overlay
```

### With `claude-design`

Use ui-ux-pro-max for the *what* (design brief),
claude-design for the *how* (process, variants, verification).

When both skills are loaded:

1. Run ui-ux-pro-max first to get the data-driven brief (colors, typography,
   style, anti-patterns).
2. Pass the brief through `claude-design`'s Prompt Enhancement Pipeline to
   translate any remaining vague terms into concrete design language.
3. Use the enhanced brief to drive artifact creation.

Do not let ui-ux-pro-max's safe defaults override `claude-design`'s context
from an existing repo or brand doc; repo context always wins.

### With `popular-web-designs`

ui-ux-pro-max gives industry-specific style direction.
popular-web-designs gives exact CSS values from real brands.

### With external reference libraries (Refero, Mobbin, etc.)

Use ui-ux-pro-max first for strategy, then use external screenshot libraries
for concrete page/flow examples. See `references/external-design-references.md`
for a curated catalog and usage rules.

## Key Product Types for Active Projects

| Project | Product Type | CSV Row |
|---------|-------------|---------|
| VIDVIS (luxury gallery) | "Photography Studio" or "Portfolio/Personal" or "E-commerce Luxury" | ~53, ~11, ~4 |
| Pentajunior (corporate) | "B2B Service" or "SaaS (General)" | ~5, ~1 |
| htdata (CRM/dashboard) | "Financial Dashboard" or "Analytics Dashboard" | ~6, ~7 |

## Color Token Format

Each product type has a complete design system:

```
Primary:        #1C1917    (brand color)
On Primary:     #FFFFFF    (text on primary)
Secondary:      #44403C    (secondary actions)
Accent/CTA:     #A16207    (buttons, highlights)
Background:     #FAFAF9    (page background)
Foreground:     #0C0A09    (main text)
Card:           #FFFFFF    (card surfaces)
Muted:          #E8ECF0    (disabled/inactive)
Border:         #D6D3D1    (dividers)
Destructive:    #DC2626    (errors)
Ring:           #A16207    (focus indicators)
```

## Typography Format

Each pairing includes:
- **Heading font** — display/hero
- **Body font** — paragraphs
- **Mood keywords** — e.g. "elegant, luxury, sophisticated"
- **Best for** — use cases
- **Google Fonts URL** — ready to import
- **CSS @import** — copy-paste ready
- **Tailwind config** — `fontFamily` block

## Anti-Patterns (What NOT To Do)

The database includes industry-specific anti-patterns:

| Industry | Don't Use |
|----------|-----------|
| Banking | Neon colors, playful fonts, AI purple gradients |
| Healthcare | Dark mode primary, aggressive animations |
| Luxury | Bright neon, harsh animations, stock-photo hero |
| SaaS | Too many colors, cluttered dashboard |
| Children | Small text, sharp corners, scary dark themes |

## Anti-Generic Design Checklist

When using this skill to brief another design skill, run every recommendation
through this checklist. The goal is to avoid generic "AI-design slop" even
when the data gives a safe default.

Before finalizing the brief:

- [ ] The palette has **one clear primary** and no more than two accents
- [ ] Every color has a named functional role, not just "accent 1 / accent 2"
- [ ] Typography is chosen for the product's **mood**, not because it is popular
- [ ] The hero/landing structure says **one thing first**, not ten things at once
- [ ] No generic section names ("Features", "Solutions", "About Us") without content
- [ ] Motion is justified by a state change or transition, not decoration
- [ ] The design has a deliberate **density** — sparse, medium, or dense — and a reason
- [ ] Buttons and CTAs use action language, not vague labels like "Learn More" unless necessary
- [ ] Empty states, error states, and loading states are considered, not just the happy path
- [ ] Mobile layout is addressed explicitly, not assumed to "just scale down"

If more than three items are unchecked, ask the user a concise clarifying
question before generating code.

## Vague → Professional Terminology Map

Use this map when handing a brief from this skill to `claude-design`,
`luxury-immersive-web`, or `popular-web-designs`. Translate vague aspiration
words into concrete design decisions.

| User says | Means concretely | What to specify |
|---|---|---|
| "modern" | Minimal chrome, precise type, generous whitespace | type scale, grid, surface treatment |
| "clean" | High contrast, clear hierarchy, reduced noise | color count, spacing scale, content order |
| "premium" | Restrained palette, elevated type, subtle motion | font pairing, accent usage, animation posture |
| "friendly" | Rounded shapes, warm neutrals, approachable type | radius values, palette temperature, weight |
| "technical" | Mono accents, dense data, keyboard affordances | mono font, table density, focus states |
| "futuristic" | Dark surfaces, geometric layout, glow/gradients sparingly | color mode, shape language, motion style |
| "organic" | Warm palette, editorial serif, soft shapes | serif choice, earth tones, border radius |
| "make it pop" | One high-contrast accent on the primary action only | CTA color, placement, size |
| "simple" | One primary action per surface | CTA count, navigation depth |
| "professional" | Consistent components, accessible contrast | component primitives, WCAG checks |

Pass these concrete terms to the implementation skill rather than the
original vague words.

## Google Fonts & Russia

⚠️ **Note:** Google Fonts CDN may be blocked in Russia.

**Alternatives:**
- Use `next/font/google` — Next.js self-hosts fonts automatically
- Download via `curl` and serve from `/public/fonts/`
- Use `fontsource` npm packages (self-hosted)

## File Locations

| Path | Content |
|------|---------|
| `~/.hermes/skills/creative/ui-ux-pro-max/data/*.csv` | All databases |
| `~/.hermes/skills/creative/ui-ux-pro-max/scripts/search.py` | BM25 search CLI |
| `~/.hermes/skills/creative/ui-ux-pro-max/scripts/design_system.py` | Design system generator |
| `~/.hermes/skills/creative/ui-ux-pro-max/scripts/core.py` | Search engine core |
| `~/obsidian-memory/Design/UI-UX Pro Max/` | Obsidian reference notes |

## Obsidian Integration

Cross-reference notes in Obsidian vault for quick manual lookup:
- `Design/UI-UX Pro Max/Product Types.md` — all 161 types
- `Design/UI-UX Pro Max/VIDVIS Reference.md` — VIDVIS-specific brief
- `Design/UI-UX Pro Max/Pentajunior Reference.md` — corporate brief
- `Design/UI-UX Pro Max/htdata Reference.md` — dashboard brief
- `Design/UI-UX Pro Max/Style Catalog.md` — 67 UI styles
- `Design/UI-UX Pro Max/Color Palettes.md` — key palettes
- `Design/UI-UX Pro Max/Typography.md` — 57 font pairings

## Verification

Before using in a session:
```bash
# Test search works
python3 ~/.hermes/skills/creative/ui-ux-pro-max/scripts/search.py \
  "luxury" --domain product --max-results 1

# Check CSV files exist
ls ~/.hermes/skills/creative/ui-ux-pro-max/data/*.csv
```

## License

MIT (original project by NextLevelBuilder).
This skill integrates the open-source database for Hermes Agent use.
