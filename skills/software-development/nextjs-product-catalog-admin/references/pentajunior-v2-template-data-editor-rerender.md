# Case study: pentajunior-v2 admin product modal — TemplateDataEditor "перерендер" on keystroke

Session: 2026-06-18. Project `/home/natan/pentajunior-v2` (Next.js 16.2.1, React 19.2.3, Bootstrap admin UI).

## User-reported symptom

In the admin product edit modal, typing a single character into the "Особенности (по строке)" field caused the modal to jump to the top, giving the impression that the whole form was re-rendering.

## Components in play

- `src/app/admin/products/page.tsx` — parent `ProductsPage` and `ProductForm`.
- `src/components/admin/TemplateDataEditor.tsx` — `TemplateDataEditor` and `FieldRow`. Its fields were already uncontrolled (`defaultValue` + ref, flush on blur/debounce), so the re-render was not coming from inside it.

## Initial attempts and why they failed

1. **Wrapped `ProductForm` in `React.memo` and set `.modal-body { scroll-behavior: auto }`.**
   - Did not fix the jump because the parent created a new `product` object on every keystroke via `setEditing({ ...product, ... })`, so `memo` saw a new prop identity and re-rendered the whole form.

2. **Added `useRef` + `useLayoutEffect` to capture and restore `.modal-body.scrollTop` across parent re-renders.**
   - Masked the symptom but did not cure it. Browser console scroll spy showed `scrollTop` briefly jumping (e.g., 1630 → 2480 → 1630) before the effect restored it. The user still felt a flicker/"перерендер".

## Root cause

`ProductsPage` stored the live form values in the `editing` state. On every keystroke `setEditing` produced a new `product` object, which re-rendered `ProductForm` and the scrollable `.modal-body` even though `TemplateDataEditor.FieldRow` was uncontrolled.

The re-render originated **above** the field row, not inside it.

## Definitive fix

Refactored `ProductForm` to hold its own local `draft` state via `useState`, initialized from `initialProduct`. The parent only receives the final object via `onSave(draft)`. Typing no longer touches parent state, so the modal body does not re-render.

```tsx
const ProductForm = memo(function ProductForm({ initialProduct, categories, onSave, onCancel }: {
  initialProduct: Product;
  categories: Category[];
  onSave: (p: Product) => void;
  onCancel: () => void;
}) {
  const [draft, setDraft] = useState<Product>(initialProduct);
  const prevIdRef = useRef(initialProduct.id);
  if (initialProduct.id !== prevIdRef.current) {
    prevIdRef.current = initialProduct.id;
    setDraft(initialProduct);
  }

  const update = useCallback(<K extends keyof Product>(field: K, value: Product[K]) => {
    setDraft((prev) => ({ ...prev, [field]: value }));
  }, []);

  // ... all fields read draft and call update(field, value) ...

  return (
    <div className="row g-3">
      ...
      <TemplateDataEditor
        templateData={draft.template_data || {}}
        onChange={(data) => update('template_data', data)}
        specTableId={draft.spec_table_id}
        onSpecTableChange={(id) => update('spec_table_id', id)}
      />
      ...
      <div className="col-12 d-flex justify-content-end gap-2">
        <button className="btn btn-secondary" onClick={onCancel}>Отмена</button>
        <button className="btn btn-primary" onClick={() => onSave(draft)}>Сохранить</button>
      </div>
    </div>
  );
});
```

Key design choices:

- `draft` is local, so keystrokes do not propagate upward.
- `prevIdRef` guard syncs `draft` only when the edited product identity changes.
- Parent `editing` state is still used for "which product is open / modal open", but never as live form state.
- `onCancel` prop preserved the "Отмена" button behavior.

## Verification

- `npm run build` passed.
- Browser scroll spy confirmed `modalBody.scrollTop` stayed constant across typed characters (e.g., 1768 → 1768, 1804 → 1804) for Cyrillic characters "о", "ф", "ы", "а", "в", "г".
- The "Особенности (по строке)" textarea retained focus and caret position.
- Cancel/Save buttons remained visible and functional.
- Commit `d8d8915` pushed to `origin/master`.

## Lesson

For a long modal form that feels like it re-renders on every keystroke, do not stop at memoizing the form or adding scroll-preservation. Trace where the new state object is created. If the parent is lifting every keystroke into its own state, isolate a local draft inside the form component and only commit on save. That is the durable fix.
