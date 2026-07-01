# Session: Evaluating UI/UX Pro Max (2026-06-08)

Repo: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
User question: «Подойдёт ли он нам?»

## Surface Signals
- 88.9k stars, 9.2k forks
- 134 commits, active community
- MIT license
- Created by NextLevelBuilder (mrgoonie)

## What It Is
AI-powered "design intelligence skill" — not code, but a knowledge base that plugs into Claude/Cursor/Windsurf. When user says "build a spa website", the skill searches its database and returns:
- Recommended style (Soft UI Evolution)
- Color palette (Soft Pink #E8B4B8 + Sage Green #A8D5BA + Gold #D4AF37)
- Font pairing (Cormorant Garamond / Montserrat)
- Landing page pattern (Hero-Centric + Social Proof)
- Anti-patterns to avoid (no AI purple gradients, no neon)

## The Database
| Resource | Count |
|---|---|
| Product types | 161 |
| UI styles | 67 |
| Color palettes | 161 |
| Font pairings | 57 |
| Chart types | 25 |
| UX guidelines | 99 |
| Tech stacks | 15 |

## Strong Sides
- MIT license — free to use
- Massive community (88.9k stars)
- Complete design systems per industry
- All Google Fonts URLs with CSS imports and Tailwind configs
- BM25 search engine (Python, no dependencies)
- Supports 15+ AI platforms

## Red Flags
- **Not a library** — can't `npm install`. It's a knowledge base + Python scripts.
- **Google Fonts CDN** — may be blocked in Russia; need local hosting.
- **Partly Chinese docs** — some files in Chinese.
- **Not directly runnable** — needs Claude/Cursor integration or manual use as reference.

## Mapping to User's Projects
| Project | What the database recommends |
|---|---|
| **VIDVIS** (luxury gallery) | Liquid Glass + Glassmorphism, Cormorant/Montserrat, Premium Black + Gold (#FFD700), Parallax Storytelling |
| **Pentajunior** (corp site) | B2B Service, Trust & Authority, Professional Blue + Grey, Flat Design + Minimalism |
| **htdata** (CRM/dashboard) | Data-Dense Dashboard, Financial Dashboard, Dark Mode OLED, Fira Code + Fira Sans |

User's preferences (from memory) map perfectly:
- Oranienbaum, Cormorant → both in top pairings for luxury
- Parallax, wow-effect → Parallax Storytelling, Kinetic Typography, Motion-Driven in database
- moooi.com vibes → Soft UI Evolution, Liquid Glass, 3D Hyperrealism
- FullHD nature backgrounds → Organic Biophilic style

## How to Use
1. **As reference** — Extract CSV data and save to Obsidian as design reference
2. **As AI skill** — `npx uipro-cli init --ai claude` for Claude Code integration
3. **In Hermes sessions** — Parse CSV on-the-fly to give design recommendations

## Recommendation
**One of the best free design reference resources available.** 161 industry profiles with complete color+font+style specs. Definitely worth adopting as reference library.

## Key Files in Repo
- `src/ui-ux-pro-max/data/products.csv` — 161 product types with style recommendations
- `src/ui-ux-pro-max/data/colors.csv` — Full design system colors per product
- `src/ui-ux-pro-max/data/styles.csv` — 67 UI styles with descriptions
- `src/ui-ux-pro-max/data/typography.csv` — 57 font pairings with Google Fonts URLs
- `src/ui-ux-pro-max/scripts/search.py` — BM25 search engine
- `src/ui-ux-pro-max/scripts/design_system.py` — Design system generator
