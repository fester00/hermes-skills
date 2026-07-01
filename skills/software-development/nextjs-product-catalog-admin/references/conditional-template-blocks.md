# Conditional hardcoded blocks in product templates

Product templates often contain shared instructional content that is correct for one sub-type of product but misleading for another within the same category. For example, a "silikon" template may render fixed blocks for surface preparation, mixing, degassing, and safety — but those steps do not apply to a non-compound product such as a luminescent pigment additive.

This reference describes how to make fixed instructional blocks conditional while keeping the same template and category mapping.

## When to use

- A single category template serves heterogeneous products.
- Some products have technical compound parameters (`ratio`, `pot_life`, `cure_time`, `viscosity`, `hardness`, etc.); others do not.
- You want to avoid creating a separate template for edge-case products.

## Rule

Render the fixed instructional block only when at least one compound-specific parameter is present in `template_data`.

```tsx
const hasUsageInstructions = [
  'ratio',
  'pot_life',
  'cure_time',
  'viscosity',
  'hardness',
  'shrinkage',
  'catalyst_type',
].some((key) => templateData[key as keyof typeof templateData]);
```

If the product lacks those parameters, the block is suppressed entirely. The surrounding section renders only if there is editable content (`application`, `usage`, `recommendations`) or the fixed block.

```tsx
{(templateData.application || templateData.usage || templateData.recommendations || hasUsageInstructions) && (
  <section aria-labelledby="application-heading">
    <h2 id="application-heading">Применение</h2>
    <hr />

    {templateData.application && <MarkdownParagraph>{templateData.application}</MarkdownParagraph>}

    {templateData.usage && (
      <>
        <h3 className="h4">Как использовать</h3>
        <MarkdownParagraph>{templateData.usage}</MarkdownParagraph>
      </>
    )}

    {templateData.recommendations && templateData.recommendations.length > 0 && (
      <>
        <h3 className="h4">Рекомендации</h3>
        <ul className="list-unstyled">
          {templateData.recommendations.map((item, i) => (
            <li key={i}><i className="bi bi-check-circle-fill text-success me-2" />{item}</li>
          ))}
        </ul>
      </>
    )}

    {hasUsageInstructions && (
      <>
        <h3 className="h4">Подготовка поверхности</h3>
        ...
      </>
    )}
  </section>
)}
```

## Adding flexible sub-fields for non-compound products

For products that do not fit the compound workflow, add template fields such as:

- `usage` — how to mix/use the product
- `recommendations` — bullet list of tips

Add them to the admin editor fallback for the template type as well, so they appear in `TemplateDataEditor` even if the category's `category_templates` row has not been updated yet.

```tsx
{ key: 'usage', label: 'Как использовать', type: 'textarea', rows: 3 },
{ key: 'recommendations', label: 'Рекомендации (по строке)', type: 'lines', rows: 4 },
```

## Admin UX: preserving manual template_type on category change

If the admin panel auto-selects a template based on category, changing the category must not overwrite a deliberately chosen template.

```tsx
const handleCategoryChange = (product, categoryId) => {
  const suggested = getSuggestedTemplate(categories, categoryId);
  const previousSuggested = getSuggestedTemplate(categories, product.category_id);
  const nextTemplate =
    product.template_type === previousSuggested || product.template_type === 'default'
      ? suggested
      : product.template_type;
  setEditing({ ...product, category_id: categoryId, template_type: nextTemplate });
};
```

This keeps explicit user choices while still helping during initial product creation.

## Development-time pitfall: stale SSG / module cache

When `better-sqlite3` is loaded at module level and pages use `generateStaticParams`, the dev server may serve a stale rendered page even after DB updates. Symptoms: DB contains the new data, but the browser still shows the old layout or missing sections.

Fixes:

1. Add `export const dynamic = 'force-dynamic';` to the product page if real-time DB updates are required during development and the catalog size permits SSR.
2. If SSG must remain, delete `.next` and restart the dev server after DB migrations.
3. Verify with a raw `curl` of the page HTML rather than relying on browser snapshots alone.

## Verification

- [ ] Compound product page still shows all fixed blocks.
- [ ] Non-compound product page suppresses fixed blocks and shows only relevant fields.
- [ ] `tsc --noEmit` passes.
- [ ] Admin category change respects manual `template_type` selection.