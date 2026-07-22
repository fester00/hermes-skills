# Detecting dead CSS in a Next.js / React project

CBM (codebase-memory-mcp) indexes CSS files as `File` nodes only. It does not track class-level usage. Use this recipe instead.

## Tool

[PurgeCSS](https://purgecss.com/) — npm/npx, no project install needed.

## Recipe

```bash
# Run from any writable directory
npx -y purgecss \
  --css /path/to/project/src/app/globals.css \
  --content "/path/to/project/src/**/*.{ts,tsx}" \
  --output /tmp/globals-purged.css

wc -l /tmp/globals-purged.css /path/to/project/src/app/globals.css
```

## Interpretation

- Compare original vs purged line counts / selector counts.
- Selectors present in the original but missing from the purged output are **potentially dead**.
- Cross-check the removed classes in `.ts/.tsx` files with grep:
  ```bash
  grep -R "className.*dead-class-name" /path/to/project/src
  ```

## False positives to expect

- Classes added **dynamically** (`classNames(...)`, template strings, CMS/markdown content).
- Bootstrap utility classes used by third-party components.
- Classes referenced only in `dangerouslySetInnerHTML` or raw HTML strings.

Always verify with a project build (`next build`) before deleting CSS.

## Why not CBM for this?

CBM builds a structural code graph (functions, calls, imports). CSS class usage is not a structural edge it tracks today. Use CBM for architecture, call tracing, and dead *code* detection; use PurgeCSS for dead *styles*.
