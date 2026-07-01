# Product template text formatting + syncing template_data from old project

This reference covers three common follow-up tasks after migrating a Next.js + SQLite catalog to category-specific product templates:

1. Let content managers mark words/phrases as bold inside admin textareas.
2. Render that markup safely on public pages as semantic `<strong>` (SEO-friendly).
3. Bulk-import or re-sync `template_data` from a legacy hardcoded `products.tsx` source.

## 1. Markdown formatting in template fields

### Goal

Admins can select text in a textarea and click a **B** button; the stored value wraps the selection in `**...**`. On the public page the template renders it as `<strong>`.

### Why this shape

- Avoids WYSIWYG editors and their dependency weight.
- Avoids storing raw HTML in the database (`dangerouslySetInnerHTML`).
- Produces clean, predictable HTML that search engines see as `<strong>`.
- The same markdown syntax can be typed by hand when the toolbar is not available.

### Minimal safe renderer

Create `src/lib/markdown.tsx`:

```tsx
import { Fragment, ReactNode } from 'react';

export function renderMarkdownText(text: string | undefined | null): ReactNode {
  if (text == null) return null;
  const str = String(text);
  if (str === '') return null;

  const lines = str.split('\n');
  const nodes: ReactNode[] = [];

  lines.forEach((line, lineIndex) => {
    if (lineIndex > 0) nodes.push(<br key={`br-${lineIndex}`} />);

    const parts: ReactNode[] = [];
    let remaining = line;
    let partIndex = 0;

    while (remaining.length > 0) {
      const open = remaining.indexOf('**');
      if (open === -1) {
        parts.push(<span key={`plain-${lineIndex}-${partIndex++}`}>{remaining}</span>);
        break;
      }
      const afterOpen = remaining.slice(open + 2);
      const close = afterOpen.indexOf('**');
      if (close === -1) {
        parts.push(<span key={`plain-${lineIndex}-${partIndex++}`}>{remaining}</span>);
        break;
      }
      if (open > 0) {
        parts.push(<span key={`plain-${lineIndex}-${partIndex++}`}>{remaining.slice(0, open)}</span>);
      }
      const boldContent = remaining.slice(open + 2, open + 2 + close);
      parts.push(<strong key={`bold-${lineIndex}-${partIndex++}`}>{boldContent || '\u00A0'}</strong>);
      remaining = remaining.slice(open + 2 + close + 2);
    }

    nodes.push(<Fragment key={`line-${lineIndex}`}>{parts}</Fragment>);
  });

  return <>{nodes}</>;
}

export function MarkdownParagraph({ children, className }: { children: string | undefined | null; className?: string }) {
  if (!children) return null;
  return <p className={className}>{renderMarkdownText(children)}</p>;
}
```

Rules implemented:
- `**text**` → `<strong>text</strong>`.
- Newlines become `<br />`.
- No `dangerouslySetInnerHTML`; no arbitrary HTML parsing.
- Unmatched `**` is left as plain text.

### Template usage

In any product template (`ReleaseTemplate.tsx`, `OilTemplate.tsx`, etc.):

```tsx
import { renderMarkdownText } from '@/lib/markdown';

<p className="news-card-desc mb-3">
  {renderMarkdownText(templateData.intro)}
</p>
```

Apply it consistently to all free-text template fields: `intro`, `body`, `composition`, `application`, `usage`, `viscosity_note`, `method`, etc.

### Admin toolbar

In the template-data editor component (`TemplateDataEditor.tsx` or similar), add a small toolbar above each `textarea` and `lines` field:

```tsx
const textareaRefs = useRef<Record<string, HTMLTextAreaElement | null>>({});

const supportsFormatting = (field) => field.type === 'textarea' || field.type === 'lines';

const toggleBold = useCallback((key: string) => {
  const textarea = textareaRefs.current[key];
  if (!textarea) return;
  const start = textarea.selectionStart ?? 0;
  const end = textarea.selectionEnd ?? 0;
  if (start === end) return;

  const raw = getValue(key);
  const before = raw.slice(0, start);
  const selected = raw.slice(start, end);
  const after = raw.slice(end);
  const marker = '**';

  const isWrapped =
    raw.slice(start - marker.length, start) === marker &&
    raw.slice(end, end + marker.length) === marker;

  let nextValue: string;
  let nextStart: number;
  let nextEnd: number;

  if (isWrapped) {
    nextValue = before.slice(0, start - marker.length) + selected + after.slice(marker.length);
    nextStart = start - marker.length;
    nextEnd = nextStart + selected.length;
  } else {
    nextValue = before + marker + selected + marker + after;
    nextStart = start + marker.length;
    nextEnd = nextStart + selected.length;
  }

  setValue(key, nextValue, fieldType);
  requestAnimationFrame(() => {
    textarea.focus();
    textarea.setSelectionRange(nextStart, nextEnd);
  });
}, [fields, getValue, setValue]);
```

UX notes:
- Only show the button for `textarea` / `lines` fields, not for one-line `text` inputs.
- Add a hint: `Поддерживается **жирный текст**`.
- Make the button toggle: selected already-wrapped text becomes plain again.

## 2. Syncing template_data from a legacy hardcoded source

### Scenario

The old project has product data in `src/data/products.tsx` as hardcoded TSX arrays with JSX descriptions. The new project stores the same content as JSON in `products.template_data`. After the initial migration, you need to re-populate or enrich fields for an entire category to match the latest admin panel fields.

### High-level strategy

1. Parse the legacy TSX block for each product in the category.
2. Convert JSX tags to plain text + markdown bold (`<strong>` → `**...**`).
3. Split content into template fields: `intro`, `composition`, `body`, `bullets`, `method`, `temp_range`, `shelf_life`, `tu`, `application_industrial`, `application_domestic`.
4. Back up the new SQLite database.
5. Update `template_data` per product, preserving any already-good manual overrides.
6. Run `tsc --noEmit` and the production build.

### Parsing recipe

For each product block in `products.tsx`:

```python
import re, html

def clean_text(text: str) -> str:
    # 1. preserve <strong> as markdown bold
    text = re.sub(r'<strong[^>]*>(.*?)</strong>', lambda m: f'**{m.group(1)}**', text, flags=re.I | re.S)
    # 2. strip remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()

def extract_li_strings(ul_html: str) -> list[str]:
    parts = re.split(r'<li[^>]*>', ul_html, flags=re.I)[1:]
    out = []
    for part in parts:
        m = re.search(r'</li>', part, flags=re.I)
        item = part[:m.start()] if m else part
        ct = clean_text(item)
        if ct:
            out.append(ct)
    return out
```

### Field mapping from legacy JSX

| Legacy fragment | `template_data` field | Notes |
|---|---|---|
| First `<p className="news-card-desc">…</p>` | `intro` | Usually starts with `<strong>Name</strong> — description` |
| Paragraph containing `<strong>Состав:</strong>` | `composition` | Text after the label |
| Remaining description paragraphs | `body` | Skip intro, composition, and method paragraphs to avoid duplication |
| Description `<ul>/<ol>` items | `bullets` | Filter out lines that are really `shelf_life`, `tu`, `temp_range` |
| Application `<ul>/<ol>` items | `application_industrial` | First list under application block |
| Paragraph with `<strong>Бытовое применение:</strong>` | `application_domestic` | String, not a list |
| Paragraph with `<strong>Способ нанесения:</strong>` | `method` | Or "Способ применения" |
| List item matching `Срок годности: …` | `shelf_life` | Move out of `bullets` |
| List item matching `^ТУ …` | `tu` | Move out of `bullets` |
| Temperature mentions in text | `temp_range` | `до +250°C`, `от −60 до +300°C`, etc. |
| Technical parameter rows from spec tables | `ratio`, `viscosity`, `hardness`, `elongation`, `tear_resistance`, `pot_life`, `cure_time`, `shrinkage`, `color`, `certificates` | Use when the category template explicitly renders these scalars (e.g., silikon compounds). Do **not** duplicate the entire comparison table here — that stays in `spec_tables`. |

For the silikon-compound category, an expanded field set is used: `intro`, `body`, `bullets`, `application`, `temp_range`, `shelf_life`, `tu`, `color`, `ratio`, `viscosity`, `hardness`, `tensile_strength`, `elongation`, `tear_resistance`, `pot_life`, `cure_time`, `shrinkage`, `catalyst_type`, `certificates`. The template renders the free-text sections first, then a property grid for technical parameters, and finally the shared application instructions. See `references/spec-comparison-tables-admin.md` for the comparison-table side.

### Merge policy

When the database already contains hand-edited data:

- Prefer the freshly parsed legacy data for structured arrays (`bullets`, `application_industrial`, `application_domestic`) because legacy source is usually canonical.
- For scalar fields (`temp_range`, `method`, `composition`, `body`), prefer the freshly parsed value only if the current DB value is empty, a placeholder (`"Не указан"`), or clearly worse.
- Keep manual overrides that add value (e.g., `surfaces`, `properties` fields the legacy source never had).

### Binary SQLite DB conflicts during git merge

Because `pentajunior.db` is a binary file tracked in git, a remote push can produce:

```
Auto-merging pentajunior.db
CONFLICT (content): Merge conflict in pentajunior.db
```

Blindly choosing `--ours` or `--theirs` risks discarding legitimate manual edits from one side. Use a **smart merge** instead.

#### Smart-merge path

1. Abort the automatic merge: `git merge --abort`.
2. Export both versions of the DB from git:
   ```bash
   git show HEAD:pentajunior.db > pentajunior.db.LOCAL
   git show origin/master:pentajunior.db > pentajunior.db.REMOTE
   ```
3. Run the sync script against `LOCAL` as the base to ensure it is canonical (no placeholders, all fields from legacy source).
4. Compare `LOCAL` and `REMOTE` field-by-field for each product. Layer in from `REMOTE` only fields that are:
   - non-empty,
   - not placeholders (`"Не указан"`, `"Не указана"`, `""`),
   - and missing or worse in `LOCAL`.
5. Remove placeholder strings (`"Не указан"`, `"Не указана"`) from the merged result.
6. Overwrite `pentajunior.db` with the merged result.
7. `git add pentajunior.db`, commit, then pull with `-s recursive -X ours` to keep the local binary and apply remote text-file changes.
8. Push.

#### Smart-merge helper script (Python)

```python
import json, sqlite3

def load_template_data(db_path: str) -> dict[str, dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id, template_data FROM products").fetchall()
    conn.close()
    return {r['id']: json.loads(r['template_data'] or '{}') for r in rows}

PLACES = {"Не указан", "Не указана", "", "N/A"}

def better(a, b):
    if b in PLACES:
        return False
    if a in PLACES:
        return True
    return False  # keep local when both are real values

local = load_template_data('pentajunior.db.LOCAL')
remote = load_template_data('pentajunior.db.REMOTE')

merged = {}
for pid in set(local) | set(remote):
    merged[pid] = dict(local.get(pid, {}))
    r = remote.get(pid, {})
    for key, val in r.items():
        if better(merged[pid].get(key), val):
            merged[pid][key] = val

conn = sqlite3.connect('pentajunior.db')
for pid, data in merged.items():
    conn.execute(
        "UPDATE products SET template_data = ? WHERE id = ?",
        (json.dumps(data, ensure_ascii=False), pid)
    )
conn.commit()
conn.close()
```

Use this script as a starting point. Adjust `better()` logic per category (some fields may legitimately be short strings).

### Verification

After any bulk sync:

- [ ] Open admin panel → edit each product → all template fields populated, no `"Не указан"`.
- [ ] Public pages render bold phrases as `<strong>`.
- [ ] `tsc --noEmit` passes.
- [ ] `npm run build` / `pnpm build` succeeds and generates all static pages.
- [ ] No `dangerouslySetInnerHTML` introduced in template rendering.

## SEO note

Search engines see the final rendered HTML. `**текст**` rendered as `<strong>текст</strong>` is semantically identical to writing `<strong>` by hand. The markup itself does not affect ranking; the benefit is cleaner editing and safer storage.