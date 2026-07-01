# React Fragment keys for admin lists with expandable rows

When an admin table maps over items and each iteration renders more than one top-level element (for example, a main row plus an optional expanded detail row), the shorthand `<>` fragment cannot accept a `key` prop. React then warns:

```
Warning: Each child in a list should have a unique "key" prop.
```

## The fix

Import `Fragment` from `react` and give it a stable key:

```tsx
import { Fragment, useEffect, useState } from 'react';

// inside render:
<tbody>
  {categories.map((c) => {
    const isExpanded = expandedCategory === c.id;
    return (
      <Fragment key={c.id}>
        <tr>
          <td>{c.id}</td>
          <td>{c.title}</td>
          <td>
            <button onClick={() => toggleCategory(c.id)}>
              {isExpanded ? 'Свернуть' : 'Развернуть'}
            </button>
          </td>
        </tr>
        {isExpanded && (
          <tr key={`${c.id}-subs`}>
            <td colSpan={3}>
              {/* nested subcategory table */}
            </td>
          </tr>
        )}
      </Fragment>
    );
  })}
</tbody>
```

## Why not `<>...</>`

The shorthand fragment does not support props, including `key`. The long form does:

```tsx
// ❌ warns
<>
  <tr key={c.id}>...</tr>
  <tr key={`${c.id}-subs`}>...</tr>
</>

// ✅ stable key on the Fragment itself
<Fragment key={c.id}>
  <tr>...</tr>
  <tr key={`${c.id}-subs`}>...</tr>
</Fragment>
```

## Common admin scenarios

- Categories with expandable subcategory tables.
- Orders with expandable line items.
- Users with expandable roles/permissions.
- Products with expandable variants or price history.

## Pitfalls

- Do not move `key` onto the first `<tr>` only and leave the second `<tr>` keyless — React still sees two sibling elements without a shared keyed parent.
- Do not use array index as the Fragment key when the list supports reordering or deletion; use the entity id.
- If the expansion row itself contains another `.map()`, each child inside it still needs its own key (e.g. `<tr key={s.id}>` for subcategory rows).
