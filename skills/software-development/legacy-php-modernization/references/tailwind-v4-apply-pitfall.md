# Tailwind CSS v4 + Vite — `Unknown at rule: @apply`

## Error
```
[lightningcss minify] Unknown at rule: @apply
body {
  @apply bg-background text-foreground;
       ^
```

## Cause
Tailwind CSS v4 uses LightningCSS for minification and does NOT support `@apply` inside `@layer base` blocks in the CSS-first configuration mode (no `tailwind.config.js`).

## Fix — Replace with CSS variables

❌ Broken:
```css
@layer base {
  body {
    @apply bg-background text-foreground;
    font-family: system-ui, sans-serif;
  }
}
```

✅ Working:
```css
@layer base {
  body {
    background-color: var(--color-background);
    color: var(--color-foreground);
    font-family: system-ui, sans-serif;
  }
}
```

## Verification
After fix, `vite build` succeeds without minification errors. File `dist/assets/index-*css` is generated correctly.

## Environment
- Tailwind CSS v4.3.0
- Vite 6.0.1
- Node.js 24.13.1
