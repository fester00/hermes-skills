# Template Data Population: Extracting Rich Product Fields from Legacy JSX into SQLite

## Context
When migrating from v1 (hardcoded TSX product arrays with `React.ReactNode` `description`/`application` blocks) to v2 (SQLite + template components + `template_data` JSON), the textual content inside JSX must be extracted, normalized, and stored as JSON in the `template_data` column.

## Extraction Pipeline

### Step 1: Identify template fields per category
From the legacy `description` and `application` JSX blocks, identify these semantic fields. Map legacy JSX keys to the `UniversalTemplateData` interface used by `UniversalTemplate`:

| Legacy JSX field | `template_data` key | Type | Notes |
|---|---|---|---|
| `description` paragraphs / bullets | `intro`, `body`, `bullets` | string / string[] | Split first `<p>` → `intro`, remaining paragraphs → `body`, `<li>` → `bullets`. |
| `application` paragraph | `application` | string | Plain-text application summary. |
| `application` instructional block | `surface_prep` | string | Title controlled by `surface_prep_title` (default "Подготовка поверхности"). |
| `application` numbered steps | `mixing_steps` | string[] | Title controlled by `mixing_title` (default "Приготовление смеси"). |
| `application` degassing paragraph | `degassing` | string | Title controlled by `degassing_title` (default "Дегазация и заливка"). |
| `application` safety paragraph | `safety` | string | Title controlled by `safety_title` (default "Меры безопасности"). |
| `application` warning / note | `important_note` | string | Rendered as a bold "Важно:" paragraph. |
| Composition / ingredients | `<p><strong>Состав:</strong> ...</p>` | `composition` | string |
| Temperature range | Inline text like "до +250°C" | `temp_range` | string |
| Application method | Paragraph after bullets | `method` | string |
| Supported surfaces | Inline text | `surfaces` | string |
| Usage notes | Inline text | `usage` | string |
| Shelf life | Inline text like "Срок годности: 2 года" | `shelf_life` | string |
| Technical standard | Inline text like "ТУ 2257-..." | `tu` | string |
| Industrial applications | `<ul><li>...</li></ul>` inside `application` | `application_industrial` | string[] |
| Domestic applications | Text paragraph in `application` | `application_domestic` | string |

### Step 2: Regex extraction from TSX source

Parse legacy `src/data/products.tsx` carefully because `description` and `application` may be arbitrary JSX fragments. The safest approach is to use **balanced parentheses** to capture each field value, not simple regexes.

```python
import re

with open('src/data/products.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

def extract_product_blocks(src: str) -> list[str]:
    """Split a TSX product array into top-level { ... } blocks using brace counting."""
    blocks = []
    i = 0
    n = len(src)
    while i < n:
        m = re.search(r"\{\s*id:\s*'", src[i:])
        if not m:
            break
        start = i + m.start()
        brace = 1
        j = start + 1
        while j < n and brace > 0:
            if src[j] == '{': brace += 1
            elif src[j] == '}': brace -= 1
            j += 1
        blocks.append(src[start:j])
        i = j
    return blocks

def extract_field(block: str, key: str) -> str:
    """Capture value assigned as `key: ( ... ),` using balanced parens."""
    pat = re.compile(re.escape(key) + r":\s*\(", re.DOTALL)
    mm = pat.search(block)
    if not mm:
        return ''
    pos = mm.end()
    depth = 1
    k = pos
    while k < len(block) and depth > 0:
        if block[k] == '(': depth += 1
        elif block[k] == ')': depth -= 1
        k += 1
    return block[pos:k-1].strip()

# For a single product block:
description_jsx = extract_field(block, 'description')
application_jsx = extract_field(block, 'application')
```

**Important:** Legacy `description` and `application` blocks often share the same `<ul><li>` pattern. Distinguish them by structural position — bullets inside `description` are product properties, bullets inside `application` are industrial use cases.

### Step 2a: JSX → plain text / HTML normalizer

Store only text and minimal markup in `template_data`. Remove React fragment markers, convert `className` to `class`, and strip empty classes.

```python
def jsx_to_text(js: str) -> str:
    if not js:
        return ''
    s = js.replace('\u003c\u003e', '').replace('\u003c/\u003e', '')
    s = re.sub(r'className="([^"]*)"', r'class="\1"', s)
    s = re.sub(r'\s+class=""', '', s)
    s = re.sub(r"\n\s*\n", "\n", s).strip()
    return s
```

Then parse the normalized HTML to split paragraphs and list items:

```python
intro = ''
body_paragraphs = []
bullets = []
desc_html = jsx_to_text(description_jsx)
p_tags = re.findall(r"\u003cp[^\u003e]*\u003e(.*?)\u003c/p\u003e", desc_html, re.DOTALL)
if p_tags:
    intro = p_tags[0]
    body_paragraphs = p_tags[1:]
li_tags = re.findall(r"\u003cli\u003e(.*?)\u003c/li\u003e", desc_html, re.DOTALL)
if li_tags:
    bullets = [re.sub(r"\u003c[^\u003e]+\u003e", "", li).strip() for li in li_tags]

application = re.sub(r"\u003c[^\u003e]+\u003e", "", jsx_to_text(application_jsx)).strip()
```

### Step 3: Normalize and deduplicate

- Strip leading/trailing whitespace
- Remove duplicate entries (e.g. "Срок годности" appearing both as a bullet and as `shelf_life` field)
- Convert HTML entities (`&mdash;`, `&nbsp;`) to plain text equivalents
- **Only fill missing fields.** If v2 already contains an `intro`, `body`, `application`, or `bullets`, leave it untouched to avoid overwriting manual edits.

### Step 4: Build JSON and UPDATE SQLite

```python
import sqlite3, json

db = sqlite3.connect('pentajunior.db')
cur = db.cursor()
cur.execute("SELECT id, template_data FROM products WHERE category_id = ?", (category_id,))
updates = []
for pid, template_data in cur.fetchall():
    data = json.loads(template_data or '{}')
    extracted = extract_for_product(pid)  # your per-product extraction

    # Only write fields that are missing or very short in v2
    for key, value in extracted.items():
        existing = data.get(key)
        if not existing or (isinstance(existing, str) and len(existing.strip()) < 20):
            data[key] = value

    # Strip empty / null values before JSON serialization
    clean = {k: v for k, v in data.items() if v and (not isinstance(v, list) or len(v) > 0)}
    updates.append((json.dumps(clean, ensure_ascii=False), pid))

cur.executemany("UPDATE products SET template_data = ? WHERE id = ?", updates)
db.commit()
```

**Pitfall:** Do not store `null` or empty-string keys in `template_data`. The template component uses conditional rendering (`&&`) — empty strings would still render as empty paragraphs. Filter them out before `JSON.stringify`.

**Pitfall:** Do not overwrite existing, substantive content. The user may have already migrated or refined some sections; the goal is to backfill only what is absent.

### Step 5: Verify via SELECT

```sql
SELECT id,
       json_extract(template_data, '$.intro') as intro,
       json_array_length(template_data, '$.bullets') as bullet_count,
       json_extract(template_data, '$.application') as app,
       json_array_length(template_data, '$.mixing_steps') as mixing_count,
       json_extract(template_data, '$.surface_prep') as prep
FROM products
WHERE category_id = 1;
```

Then open a product page in the browser and confirm that each section renders without empty headings.

## Backfilling generic instructional blocks

When the legacy site renders a shared instruction section for a whole product family (e.g. `SectionUnisilApplication` for all `unisil-9xxx`), but v2 `UniversalTemplate` expects per-product fields like `surface_prep`, `mixing_steps`, `degassing`, `safety`, `important_note`, inject those blocks as `template_data` for every product in the family that already has an `application` paragraph but lacks instructions.

```python
instructional = {
    'surface_prep_title': 'Подготовка поверхности',
    'surface_prep': 'Перед заливкой убедитесь, что поверхность модели чистая и сухая...',
    'mixing_title': 'Приготовление смеси',
    'mixing_steps': ['...', '...'],
    'degassing_title': 'Дегазация и заливка',
    'degassing': '...',
    'important_note': '...',
    'safety_title': 'Меры безопасности',
    'safety': '...',
}

for pid, data in products.items():
    if data.get('application') and not data.get('surface_prep'):
        data.update(instructional)
```

Always keep the titles overridable via `*_title` fields so the admin editor can customize them later.

## Admin Editor Integration

The `template_data` must be editable in the admin panel. The `TemplateDataEditor` component should:

1. Accept `templateType` prop to determine which fields to render
2. Maintain field definitions in a `TEMPLATE_FIELDS` constant keyed by template type
3. Support field types: `text`, `textarea`, `lines` (array of strings)
4. Strip empty values before emitting JSON back to the parent form
5. Auto-switch field set when category (and thus `template_type`) changes

See `references/admin-template-editor-integration.md` for full component pattern.
