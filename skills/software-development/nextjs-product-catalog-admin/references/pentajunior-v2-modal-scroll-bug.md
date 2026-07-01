# Case study: pentajunior-v2 admin product modal scroll jump

## Symptom

In the admin product edit modal, typing a single character into the
"Особенности (по строке)" textarea (and other `lines`/`textarea` fields)
scrolled the modal body back to the top. The field itself felt like it was
re-rendering.

## Code in play

- `src/app/admin/products/page.tsx` — `ProductsPage` + `ProductForm`
- `src/components/admin/TemplateDataEditor.tsx` — `TemplateDataEditor` + `FieldRow`

## Root cause

`TemplateDataEditor.FieldRow` was already uncontrolled (`defaultValue` + `ref`,
flush on blur/debounce), which was correct at the field level. However,
`ProductForm` was a plain function component. Every keystroke called
`setEditing({ ...product, template_data: ... })` in the parent, producing a new
`editing` object. That re-rendered `ProductForm`, which re-rendered the
scrollable `.modal-body` and reset its scroll position.

## Fix applied (final)

1. Wrapped `ProductForm` with `React.memo(...)`.
2. Replaced the `formRef` callback with a plain `useRef` + `useLayoutEffect` that
   captures `.modal-body.scrollTop` and restores it whenever React resets it to
   `0` after a parent-state update.

```tsx
const ProductForm = memo(function ProductForm({ product, categories, onChange, onCategoryChange }: {
  product: Product; categories: Category[]; onChange: (p: Product) => void; onCategoryChange: (p: Product, id: number) => void;
}) {
  // ... stable useCallback hooks ...

  const scrollRef = useRef<number>(0);
  const formRef = useRef<HTMLDivElement | null>(null);
  useLayoutEffect(() => {
    const modalBody = formRef.current?.closest('.modal-body');
    if (!modalBody) return;
    const el = modalBody as HTMLElement;
    const top = el.scrollTop;
    if (top === 0 && scrollRef.current > 0) {
      el.scrollTop = scrollRef.current;
    }
    scrollRef.current = el.scrollTop;
  });

  return (
    <div className="row g-3" ref={formRef}>
      ...
      <TemplateDataEditor ... />
    </div>
  );
});
```

## Verification

- `npm run build` passed.
- `npx eslint` reported only pre-existing issues (legacy `any` and a `loadData`
  declaration order warning unrelated to the change).
- User confirmed the bug was resolved.
- Commit `4ed8e81`, pushed to `origin/master`.

## Lesson

When a modal form scrolls to top on typing, check three layers:

1. **Field layer:** is the input uncontrolled and memoized?
2. **Parent layer:** is the form component memoized with stable callbacks?
3. **Scroll-preservation layer:** if the parent still re-renders because it creates a new state object on every keystroke, capture and restore `.modal-body.scrollTop` with `useLayoutEffect` so the user does not see the jump.

Fixing only the field or memo layer often leaves the scroll bug because the scrollable container re-renders with the parent.
container re-renders with the parent.
