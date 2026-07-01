# From sketch to production: page redesign workflow

Worked example from `/contacts` redesign in pentajunior-v2.

## Scenario

User asked for several design variants for an existing page (`/contacts`), provided a specific color palette (#212529, #8fb34f, #160b0d, #6bdb85, #d1c5c6), and requested:
- keep the current light background
- keep interactive Yandex.Maps
- produce 5 design variants in one HTML file for comparison
- later pick one variant and implement it

## Approach

1. **Read the existing page** (`src/app/contacts/page.tsx`) to understand data, maps, forms, and current structure.
2. **Build 5 variants in one disposable HTML file** under `~/workspace/` (not inside the repo) using Bootstrap + the provided palette. Each variant is a separate `<section>` with shared CSS variables. This makes comparison easy and keeps the repo clean.
3. **User picks variant 1** (classic/corporate with olive accents).
4. **Implement the chosen variant** in the real page:
   - Replace old layout with new semantic structure and CSS classes.
   - Add CSS to `src/app/globals.css` under a dedicated namespace (`.contacts-page`, `.contacts-info-card`, `.partner-card`, etc.).
   - Keep all existing data: address, phones, email, hours, bank details, partners, maps, form.
5. **Apply content edits requested alongside the redesign**:
   - Rename section heading "Партнёры в регионах" → "Наши партнёры".
   - Add a new partner entry (ООО "Силагерм") with both office address and a warehouse note.
6. **Run build gate** (`tsc --noEmit && npm run build`) and push.

## Key decisions

- **Light background preserved.** Used `--color-bg: #f8f9fa` / `#fafafa` and card surfaces `#ffffff`.
- **Maps preserved.** Both Yandex iframe maps kept with `loading="lazy"`.
- **Color palette applied through CSS variables** and specific utility classes (`.text-olive`, `.btn-primary-custom`) without changing global Bootstrap primary colors.
- **Partner note support.** Added an optional `note?: string` to the `Partner` interface so additional info (e.g. a separate warehouse address/phone) can be rendered as a dashed sub-block without polluting the main address field.
- **Variants kept outside the repo.** The comparison file and CSS draft live in `~/workspace/`; only the chosen implementation is committed.

## Production CSS pattern

```css
.contacts-page .contacts-info-card {
  background: #ffffff;
  border: 1px solid rgba(143, 179, 79, 0.15);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-md);
  transition: transform var(--transition-base), box-shadow var(--transition-base);
}

.contacts-page .contacts-info-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(143, 179, 79, 0.12);
  color: var(--color-primary);
  border-radius: var(--radius-md);
}

.contacts-page .partner-card {
  background: #ffffff;
  border: 1px solid rgba(143, 179, 79, 0.12);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  height: 100%;
  transition: all var(--transition-base);
}

.contacts-page .partner-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 6px 20px rgba(143, 179, 79, 0.12);
}
```

## Things to remember

- Always run the build gate after a page redesign; layout changes can expose TypeScript or rendering issues.
- If the remote `master` has moved, `git pull --rebase` before pushing.
- Keep the comparison HTML and draft CSS in `~/workspace/` for reference, but don't commit them.
- When adding a new partner, ensure the `Partner` type supports all fields you need; add optional fields rather than concatenating everything into `address`.
- **Recovery from a broken redesign:** if the merged/refactored page or CSS breaks layout, identify the last known-good commit, reset `master` to it, force-push origin, and re-apply the good parts incrementally rather than repeating the same big-bang change.
