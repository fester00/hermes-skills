# PurgeCSS Dead-Code Recipe for `globals.css`

Use this recipe to remove unused CSS rules from a large global stylesheet in a Next.js / React project.

## When to use

- `globals.css` has grown large and you suspect dead component styles.
- You want a fast, semi-automated cleanup with easy rollback.
- You are willing to verify visually after the cleanup (PurgeCSS can make mistakes with dynamic classes).

## Requirements

- Node.js + npm (`npx` available)
- Project uses `className="..."` or explicit class strings in `.ts` / `.tsx` files.

## Recipe

### 1. Create a backup

```bash
cp src/app/globals.css /tmp/globals.css.backup
```

### 2. Run PurgeCSS

```bash
npx -y purgecss \
  --css src/app/globals.css \
  --content "src/**/*.{ts,tsx}" \
  --output /tmp/globals-purged.css
```

### 3. Compare size and selector counts

```bash
wc -l src/app/globals.css /tmp/globals-purged.css
du -h src/app/globals.css /tmp/globals-purged.css
```

### 4. Review the diff before applying

```bash
diff -u src/app/globals.css /tmp/globals-purged.css | less
```

Pay special attention to classes that might be used dynamically:
- `classNames('foo', condition && 'bar')`
- `className={\`product-card \${variant}\`}`
- classes rendered from markdown/JSON

### 5. Apply the cleaned file

```bash
cp /tmp/globals-purged.css src/app/globals.css
```

### 6. Build and verify

```bash
npx tsc --noEmit && npm run build
```

Then visually check key pages: home, category, product, contacts, admin.

### 7. Commit and push

```bash
git add src/app/globals.css
git commit -m "refactor(css): remove unused styles from globals.css via PurgeCSS"
git push origin master
```

## Rollback

If anything breaks:

```bash
cp /tmp/globals.css.backup src/app/globals.css
# OR
git revert HEAD
git push origin master
```

## Real-world example

On `pentajunior-v2` this recipe removed **380 lines** from `src/app/globals.css` (536 → 469 selectors, 84K → 72K) with no visual regressions.

## Caveats

- PurgeCSS scans explicit content files only. Classes injected by runtime JS, markdown, or external libraries may be flagged falsely.
- Always cross-check removed classes with `grep -R "className.*<class>" src/` or similar.
- Never apply PurgeCSS output blindly in production without a build + visual check.
