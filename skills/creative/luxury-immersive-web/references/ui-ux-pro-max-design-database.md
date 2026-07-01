# UI/UX Pro Max — Design Intelligence Database (Reference)

Repo: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (88.9k stars, MIT license)

## What It Is
An AI skill (not a library) that provides design intelligence for building professional UI/UX. It consists of CSV databases + Python BM25 search engine. When a user says "build a luxury gallery website", the skill searches its database and returns a complete design system.

## Relevance to Luxury Immersive Web Projects

This is one of the best free design reference resources available. It maps 161 product types to complete design systems (style + colors + fonts + patterns + anti-patterns).

### For VIDVIS-Type Projects (Art Gallery / Luxury)

The database recommends for **Luxury/Premium Brand** and **E-commerce Luxury**:

| Element | Recommendation |
|---|---|
| **Primary Style** | Liquid Glass + Glassmorphism |
| **Secondary** | 3D & Hyperrealism, Aurora UI |
| **Landing Pattern** | Storytelling-Driven + Feature-Rich Showcase |
| **Dashboard** | Sales Intelligence Dashboard (if applicable) |
| **Colors** | Black (#1C1917) + Gold (#FFD700) + White + Minimal accent |
| **Typography** | Cormorant Garamond / Montserrat (already in luxury-immersive-web skill) |
| **Key Effects** | Soft shadows + Smooth transitions (200-300ms) + Gentle hover states |
| **Anti-patterns** | Bright neon colors, harsh animations, dark mode, AI purple/pink gradients |

### For Pentajunior-Type Projects (Corporate/B2B)

| Element | Recommendation |
|---|---|
| **Primary Style** | Trust & Authority + Minimalism |
| **Secondary** | Feature-Rich, Conversion-Optimized |
| **Colors** | Professional blue (#1E3A8A) + neutral grey + trust white |
| **Typography** | Lexend / Source Sans 3 (accessibility-first) |
| **Pattern** | Feature-Rich Showcase + CTA |

### Complete Color Palettes (Ready to Copy)

Each of the 161 product types has a full 16-color design system in `data/colors.csv`:
- Primary, On Primary, Secondary, On Secondary
- Accent, On Accent, Background, Foreground
- Card, Card Foreground, Muted, Muted Foreground
- Border, Destructive, On Destructive, Ring

Example (Luxury):
```
Primary:    #1C1917 (Near Black)
On Primary: #FFFFFF
Secondary:  #44403C (Warm Grey)
Accent:     #A16207 (Gold)
Background: #FAFAF9 (Warm White)
Foreground: #0C0A09
Card:       #FFFFFF
Card Foreground: #0C0A09
Border:     #D6D3D1
```

### Font Pairings with Google Fonts URLs

The database includes 57 curated pairings with:
- Google Fonts share URLs
- CSS `@import` statements
- Tailwind `fontFamily` config snippets

Key pairings for luxury projects:
- **Classic Elegant**: Playfair Display + Inter
- **Luxury Serif**: Cormorant + Montserrat
- **Editorial Classic**: Cormorant Garamond + Libre Baskerville
- **Minimal Swiss**: Inter + Inter (single font system)

### 67 UI Styles

Styles most relevant to luxury immersive web:
| # | Style | Best For |
|---|---|---|
| 3 | Glassmorphism | Modern SaaS, financial dashboards |
| 4 | Brutalism | Design portfolios, artistic projects |
| 5 | 3D & Hyperrealism | Gaming, product showcase, immersive |
| 9 | Claymorphism | Educational apps, children's apps, SaaS |
| 14 | Liquid Glass | Premium SaaS, high-end e-commerce |
| 19 | Soft UI Evolution | Modern enterprise apps, SaaS |
| 24 | Organic Biophilic | Wellness apps, sustainability brands |
| 31 | Parallax Storytelling | Brand storytelling, product launches |
| 33 | HUD / Sci-Fi FUI | Sci-fi games, space tech, cybersecurity |
| 50 | Luxury Minimalist | Bodoni Moda + Jost, high-end fashion |

## How to Use in Hermes Sessions

### Load the Skill
```bash
# The ui-ux-pro-max skill is installed locally with full CSV database
skill_view(name="ui-ux-pro-max")
```

### Option 1: BM25 Search (Fastest)
```bash
cd ~/.hermes/skills/creative/ui-ux-pro-max/scripts
python3 search.py "<query>" --domain <domain> [--max-results N]
```

**Domains:** `product`, `style`, `color`, `typography`, `landing`, `chart`, `ux`, `app-interface`

**Examples:**
```bash
python3 search.py "luxury gallery" --domain product --max-results 3
python3 search.py "glassmorphism" --domain style
python3 search.py "Cormorant" --domain typography
```

### Option 2: Design System Generation (Full Brief)
```bash
python3 search.py "luxury art gallery" --design-system -p "VIDVIS"
# Outputs complete ASCII brief: pattern + style + colors + typography + effects + anti-patterns
```

### Option 3: Direct CSV Lookup (Programmatic)
```python
import csv
from pathlib import Path

DATA_DIR = Path("~/.hermes/skills/creative/ui-ux-pro-max/data").expanduser()

def get_design_system(product_type):
    with open(DATA_DIR / "products.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if product_type.lower() in row["Product Type"].lower():
                return row
    return None

def get_colors(product_type):
    with open(DATA_DIR / "colors.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if product_type in row["Product Type"]:
                return row
    return None
```

## Integration with Luxury Immersive Web Skill

When building a luxury site, cross-reference with this database:
1. Identify the product type (art gallery → "Photography Studio" or "Portfolio/Personal")
2. Get the recommended style, colors, and fonts
3. Apply the luxury-immersive-web patterns (PerspectiveScene, ParallaxDivider, 3D tilt)
4. Use the database's anti-patterns as "avoid" checklist

## Key Files to Reference
- `data/products.csv` — 161 product types with style recommendations
- `data/colors.csv` — Full 16-color design systems
- `data/typography.csv` — 57 font pairings with code snippets
- `data/styles.csv` — 67 UI style descriptions
- `scripts/search.py` — BM25 search engine (Python, no deps)
- `scripts/design_system.py` — Design system generator

## Caution
- **Version drift:** README advertises 67 UI styles, but `styles.csv` contains 84 rows (version 2.0+ added mobile-specific styles). Use `wc -l` or check CSV directly rather than relying on README badge numbers.
- Google Fonts CDN may be blocked in Russia — download fonts locally via `next/font/google` or self-host
- This is a knowledge base, not an npm package — can't `npm install`
- Some documentation is in Chinese
