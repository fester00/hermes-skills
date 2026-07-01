# Case study: pentajunior-v2 admin product modal — local draft fix

## Symptom (second recurrence)

After the initial `useLayoutEffect` scroll-preservation fix, the user reported
that typing any character still caused the modal to feel like it was
re-rendering. Visual inspection with a scroll spy confirmed the modal body
scrollTop briefly jumped ~850 px and then returned.

## Why the first fix was insufficient

The scroll-preservation `useLayoutEffect` restored the position *after* React
committed the DOM, but the browser had already reflowed and temporarily
scrolled. The real issue was structural: `ProductsPage` held `editing` in
`useState` and `setEditing` created a new `product` object on every keystroke.
`ProductForm` therefore received a new `product` prop identity, so `memo` could
not prevent re-render, and the entire scrollable `.modal-body` re-rendered.

## Correct fix: local draft state inside the form

Instead of passing `product` and an `onChange` that updates parent state per
keystroke, `ProductForm` now keeps its own `draft` in `useState`, initialized
from `initialProduct`. All fields update `draft` locally. The parent only
receives the final object when the user clicks **Сохранить**.

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

  // ... fields read draft and call update() ...

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

Key points:

- `draft` is local, so typing does not touch parent state.
- `prevIdRef` guard ensures `setDraft` runs only when the edited product changes,
  avoiding render-loop/setState-during-render issues.
- `onSave(draft)` is called from a stable closure over the latest `draft`.
- No scroll-preservation hack is needed because the scrollable container no
  longer re-renders on keystroke.

## Pitfall: parent state still needs `editing`, but only for modal open/close

The parent `ProductsPage` still holds `editing: Product | null` to decide
whether the modal is open and which product is being edited. That is fine.
The mistake was making `editing` the **live form state**. After the refactor:

- `editing` is set when the user clicks **Редактировать** and cleared on
  **Сохранить** / **Отмена** / modal close.
- The `ProductForm` receives `initialProduct={editing}` and never calls
  `setEditing` during typing.

This separation is what stops the modal body re-render.

## Verification

- `npm run build` passed.
- Browser scroll spy: `modalBody.scrollTop` stayed constant across typed
  characters (e.g., 1768 → 1768).
- The "Особенности" textarea retained focus and its caret position.
- Cancel/Save buttons remained visible and functional.

## Lesson

Scroll-preservation is a band-aid. The durable fix for a long modal form that
re-renders on every keystroke is to **stop lifting every keystroke into parent
state**. Keep a local draft in the form component and only commit it on save.
This also eliminates the need for `memo`/scrollRef workarounds in most cases.
