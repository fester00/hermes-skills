# Web Bundlers Quick Reference

Condensed comparison of JavaScript build tools. Extracted from search session 2026-05-03.

## Bun — All-in-One Toolkit

**Site:** [bun.sh](https://bun.sh)
**Tagline:** "A fast all-in-one JavaScript runtime"

**What it is:** Runtime (replaces Node.js) + bundler + package manager + test runner + transpiler. Written in Zig.

**When to use:**
- Starting a new project from scratch
- Need maximum speed (3–5× faster than Node.js)
- Want one tool instead of npm + webpack + jest + nodemon

**Quick start:**
```bash
curl -fsSL https://bun.sh/install | bash
bun create next-app my-app    # or react, vue, etc.
bun run dev                   # dev server
bun install express           # install packages (20× faster than npm)
bun build ./index.ts --outdir ./dist   # production build
bun test                      # run tests (jest replacement)
```

**Pros:** Speed, built-in bundler, TypeScript out of the box, npm-compatible.
**Cons:** Young (possible bugs), partial Node.js API coverage, smaller ecosystem.

---

## Vite — Frontend Dev Server & Builder

**Site:** [vitejs.dev](https://vitejs.dev)
**Tagline:** "Next Generation Frontend Tooling"

**What it is:** Dev server + production bundler for frontend (React, Vue, Svelte, vanilla). Uses native ES Modules in dev, Rollup for production.

**When to use:**
- Frontend website or SPA
- Need instant dev server start and fast HMR (Hot Module Replacement)
- Development workflow matters

**Quick start:**
```bash
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install
npm run dev          # instant start, HMR in milliseconds
npm run build        # → dist/ optimized for production
```

**Pros:** Instant start, best-in-class HMR, simple config, TypeScript/CSS/assets out of the box.
**Cons:** Frontend-only (not a server runtime), requires modern browser.

---

## esbuild — Ultra-Fast Bundler

**What it is:** Go-written bundler and minifier. Extremely fast. Used under the hood by Vite.

**When to use:**
- Need a bundler in a tool or pipeline
- Vite handles this automatically — rarely needed directly

**Quick start:**
```bash
npx esbuild app.jsx --bundle --outfile=out.js
```

---

## Webpack — Mature Configurable Bundler

**When to use:**
- Legacy project already using Webpack
- Need maximum configurability
- Complex plugin ecosystem required

**Cons:** Slower, verbose config. Modern projects prefer Vite or Bun.

---

## Parcel — Zero-Config Bundler

**When to use:**
- Want zero configuration
- Smaller projects

**Cons:** Less control than Webpack/Vite. Community has shifted to Vite.

---

## Decision Matrix

| Scenario | Tool | Why |
|----------|------|-----|
| New fullstack project | **Bun** | One tool for everything |
| React/Vue frontend | **Vite** | Best dev experience |
| Legacy project | Webpack | Already configured |
| Library bundling | esbuild / Rollup | Speed + control |
| Script/CLI tool | Bun | Runtime + bundler in one |
| Simple static site | Vite | Instant setup |

**Simple rule:**
- Backend / Fullstack / CLI → Bun
- Frontend site / app → Vite
- Can combine: Bun as runtime + Vite as frontend bundler
