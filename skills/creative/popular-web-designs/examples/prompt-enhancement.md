# Prompt Enhancement Examples for Popular Web Designs

This directory contains before/after examples of how to translate a vague user
request into a concrete design brief for a specific template.

Use these as a reference when loading `popular-web-designs` alongside
`claude-design`. Run the user's request through `claude-design`'s Prompt
Enhancement Pipeline, then pick the closest template and adapt its tokens.

---

## Example 1 — Stripe-style landing page

**User request (vague):**
> "Make a nice landing page for my SaaS billing product. Something clean and professional."

**Enhanced brief:**

- **Purpose:** Explain a SaaS billing product and drive a primary trial/sign-up action.
- **Audience:** Finance/ops decision-makers at other SaaS companies.
- **Format:** Single self-contained HTML file, desktop-first with responsive breakpoints.
- **Visual posture:** Light mode, generous whitespace, weight-300 hero type, one purple accent gradient, precise 4px/8px/16px radius system.
- **Reference template:** `stripe.md` — use its exact palette, typography, and CTA treatment.
- **Key decisions:**
  - Hero: one headline, one subhead, primary CTA + subtle secondary link.
  - Below-the-fold: 3 proof points, not 6 feature cards.
  - Use Stripe's signature purple gradient only on the primary button.
- **What to avoid:** Generic SaaS cards, fake metrics, rainbow gradients, stock-photo hero.

---

## Example 2 — Linear-style dashboard concept

**User request (vague):**
> "Design a dark dashboard for a task tracker. Modern, minimal."

**Enhanced brief:**

- **Purpose:** Present a task-tracking dashboard that prioritizes speed of comprehension.
- **Audience:** Engineering/product teams.
- **Format:** Self-contained HTML prototype or component board.
- **Visual posture:** Dark mode, ultra-minimal, subtle purple accent, precise type scale, low-density list UI.
- **Reference template:** `linear.app.md` — use its exact dark surfaces, accent usage, and list treatments.
- **Key decisions:**
  - Sidebar + main list layout.
  - Use color only for status/priority, not decoration.
  - Keyboard-friendly hover/focus states.
  - Empty state, loading state, and error state included.
- **What to avoid:** Data slop, neon accents, rounded cards everywhere, fake charts.

---

## Example 3 — Vercel-style developer landing

**User request (vague):**
> "I need a landing page for my dev tool. Make it look like Vercel."

**Enhanced brief:**

- **Purpose:** Position a developer tool as fast, precise, and reliable.
- **Audience:** Frontend developers and platform engineers.
- **Format:** Single self-contained HTML file.
- **Visual posture:** Black-and-white precision, Geist font system, geometric layout, no decorative gradients.
- **Reference template:** `vercel.md` — use its exact type scale, spacing, and component treatment.
- **Key decisions:**
  - Stark headline + concise subhead + primary dark CTA.
  - Code-forward visuals only if real code snippets are available; otherwise use clean typography.
  - One accent color max.
- **What to avoid:** Generic feature grid, decorative illustrations pretending to be product imagery, long body copy.

---

## Example 4 — Notion-style content site

**User request (vague):**
> "Build a clean documentation-style site. Friendly but professional."

**Enhanced brief:**

- **Purpose:** Present documentation or long-form product content with strong readability.
- **Audience:** General users who need to learn or reference information.
- **Format:** Single HTML page or multi-page structure if scope is larger.
- **Visual posture:** Warm minimalism, soft surfaces, serif headings for editorial feel, generous line height.
- **Reference template:** `notion.md` — use its warm neutrals, typography pairing, and card treatments.
- **Key decisions:**
  - Reading-optimized layout: max line length, clear hierarchy, generous whitespace.
  - Navigation: simple, not hamburger-first.
  - Use real content; mark placeholders clearly if final copy is unavailable.
- **What to avoid:** Cluttered sidebars, cool blue-grays without reason, tiny body text.

---

## How to use these examples

1. Load `popular-web-designs`.
2. Identify the user's vague terms and map them to a template from the catalog.
3. Run the brief through `claude-design`'s Prompt Enhancement Pipeline.
4. Pull exact colors, typography, and component values from the chosen template.
5. Generate the HTML with `write_file`, verify with `browser_vision`.
