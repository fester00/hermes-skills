# Mapping v1 `application` JSX blocks into v2 `template_data`

## Context

In the legacy `pentajunior` project (Next.js + hardcoded `products.tsx`) each product has an `application` JSX block that mixes **areas of use**, **application method**, and **important notes**. In `pentajunior-v2` these concepts are split across separate fields in `template_data` because the `UniversalTemplate` renders each as its own section:

- `applications` → "Области применения" section (`ApplicationAreasSection`)
- `application_industrial` → "Области применения → В промышленности"
- `application_domestic` → "Области применения → Бытовое"
- `method` → "Дополнительная информация" / "Способ нанесения"
- `important_note` → highlighted warning paragraph
- `application` → "Применение" section text / free-form markdown
- `surface_prep`, `mixing_steps`, `degassing`, `safety` → instructional subsections inside "Применение"

## Mapping rules

When migrating `application` JSX from v1 to v2:

1. **Read the existing v2 row first.** If `applications`/`method`/`important_note` are already populated, skip that field so you do not overwrite newer content. Only fill missing fields.

2. **Decide whether the v1 block is "areas of use" or "how to use".** This determines which v2 field receives the list:
   - Heading says `**Область применения...**` / `**Промышленное применение**` / `**Специализированное применение**` → the items are areas of use → `applications` / `application_industrial` / `application_domestic`.
   - Heading says `**Способ применения...**` / `**Способы применения...**` / `**Способ нанесения...**` → the items are instructions → `recommendations` (for bullet lists) or `method` (for a prose sentence), plus `important_note` for warnings.
   - Mixed blocks (common in release agents, silicones, waterproofers): split them — areas go to `applications`, instructions go to `method`/`recommendations`/`important_note`.

3. **Identify semantic parts** by bold headings inside the JSX:
   - `**Область применения...**` / `**Промышленное применение**` / `**Специализированное применение**` → list of `<li>` items → `applications` array
   - Distinct "В промышленности" / "Бытовое" subsections → `application_industrial` / `application_domestic`
   - `**Способ нанесения**` / `**Способ применения**` / `**Способы применения**` / text about how to use → `method` or `recommendations`
   - `**Рекомендация:**` / advice paragraph → `method`
   - `**Важно:**` / `**Внимание:**` / warning emoji → `important_note`
   - Numbered instructions (`<ol>`) → `recommendations` or `mixing_steps`

4. **Remove or clear the legacy `application` field** after splitting its content, unless the v1 block genuinely contains only free-form "Применение" text. Otherwise the UniversalTemplate will render both "Применение" and "Области применения" with duplicated content.

5. **Clean `body`/`intro` of trailing application headings.** Legacy v1 descriptions often end with `Область применения {Name}:`, `Способ применения {Name}:`, or `Способы применения {Name}:` followed by nothing or duplicated text. Strip that trailing fragment so it does not appear in the "Описание" section. Regex example:

```python
import re

def clean_body(body: str) -> str:
    body = re.sub(r'\s*Способы? применения [^:]+:.*$', '', body, flags=re.DOTALL).strip()
    body = re.sub(r'\s*Область применения [^:]+:.*$', '', body, flags=re.DOTALL).strip()
    return body
```

## Practical extraction helper (Python)

```python
import re
from html.parser import HTMLParser

class HTMLToMarkdown(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.stack = []
        self.in_skip = False
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in ('script','style'):
            self.in_skip = True
            return
        self.stack.append(tag)
        if tag == 'p': self.result.append('\n\n')
        elif tag == 'br': self.result.append('\n')
        elif tag in ('strong','b'): self.result.append('**')
        elif tag in ('ul','ol'): self.result.append('\n')
        elif tag == 'li': self.result.append('\n- ')
        elif tag == 'h3': self.result.append('\n\n### ')
    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ('script','style'):
            self.in_skip = False
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        if tag in ('strong','b'): self.result.append('**')
        elif tag == 'p': self.result.append('\n')
        elif tag in ('ul','ol'): self.result.append('\n')
    def handle_data(self, data):
        if not self.in_skip:
            self.result.append(data)
    def get_text(self):
        text = ''.join(self.result)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()

def html_to_md(html: str) -> str:
    parser = HTMLToMarkdown()
    parser.feed(html)
    return parser.get_text()

def split_application(md: str):
    """Split a v1 application markdown dump into v2 template_data fields."""
    applications = []
    application_industrial = []
    application_domestic = []
    method = ''
    important_note = ''
    recommendations = []

    # Split by bold headings
    parts = re.split(r'\n\n\*\*([^*]+)\*\*[:：]?\s*', md)
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        content = parts[i+1].strip() if i+1 < len(parts) else ''
        lower = heading.lower()
        items = [re.sub(r'^-\s*', '', l).strip() for l in content.split('\n') if l.strip().startswith('-')]

        if 'в промышленности' in lower or 'промышленное применение' in lower:
            application_industrial.extend(items)
        elif 'бытовое' in lower or 'бытовое применение' in lower:
            application_domestic.extend(items)
        elif any(k in lower for k in ('область', 'применение', 'специализированное', 'электротехническое')):
            applications.extend(items)
        elif any(k in lower for k in ('способ нанесения', 'способ применения')):
            method = ' '.join(items) if items else content
        elif 'важно' in lower or 'примечание' in lower:
            important_note = content.replace('**','').strip()
        elif re.search(r'\n\s*\d+\.', content):
            recommendations = [l.strip() for l in re.split(r'\n\s*\d+\.\s*', content) if l.strip()]

    result = {}
    if application_industrial:
        result['application_industrial'] = application_industrial
    if application_domestic:
        result['application_domestic'] = application_domestic
    if applications:
        # Only keep general applications if they do not duplicate domestic/industrial lists
        if applications != application_industrial and applications != application_domestic:
            result['applications'] = applications
    if method:
        result['method'] = method
    if important_note:
        result['important_note'] = important_note
    if recommendations:
        result['recommendations'] = recommendations
    return result
```

## Examples

For per-category decisions in the `pentajunior-v2` migration (which fields were chosen for each category and why), see `references/pentajunior-v2-category-migration-log.md`.

### Release / smazka category

v1 block:
```jsx
<>
  <p className="news-card-desc  mb-3"><strong>Область применения:</strong></p>
  <ul>
    <li>Формование изделий из резины, полиэтилена, полипропилена</li>
    <li>Стеклопластики на эпоксидных и полиэфирных связующих</li>
  </ul>
  <p className="news-card-desc  mb-3"><strong>Способ нанесения:</strong> распылением или кистью в 2-4 слоя...</p>
  <p className="news-card-desc  mb-3"><strong>⚠️ Важно:</strong> содержит бензин — не наносить на горячий пресс!</p>
</>
```

v2 `template_data`:
```json
{
  "applications": [
    "Формование изделий из резины, полиэтилена, полипропилена",
    "Стеклопластики на эпоксидных и полиэфирных связующих"
  ],
  "method": "распылением или кистью в 2-4 слоя на обезжиренную поверхность. Интервал между слоями 15 мин. После последнего слоя нагреть пресс до 150-200°C на 10-20 мин.",
  "important_note": "содержит бензин — не наносить на горячий пресс!"
}
```

### Silikon category

When every product in a category shares the same instructions, store those as reusable instructional blocks in `template_data`:

```json
{
  "surface_prep": "Перед заливкой убедитесь, что поверхность чистая и сухая...",
  "mixing_steps": [
    "Тщательно перемешайте основу до однородности...",
    "Взвесьте компоненты в соотношении согласно таблице..."
  ],
  "degassing": "Для получения формы без пузырей рекомендуется вакуумирование...",
  "important_note": "Ускорение отверждения нагревом снижает механические свойства...",
  "safety": "Компаунд относится к 4 классу опасности..."
}
```

This fills the "Применение" section via `ApplicationSection` in `UniversalTemplate`.

### TSM / domestic+industrial category

When v1 already splits applications into "В промышленности" and "Бытовое", map directly to the matching fields and omit the general `applications` list:

```json
{
  "application_industrial": [
    "Выпечка и расстойка хлебобулочных и кондитерских изделий",
    "Заморозка полуфабрикатов",
    "Покрытие противней и поддонов конвейерных печей"
  ],
  "application_domestic": [
    "Коврик для духовки (газовой, электрической)",
    "Использование в микроволновой печи (без функции гриль)",
    "Поверхность для замешивания теста"
  ]
}
```

## Pitfalls

- **Store list fields as arrays of plain strings, not Markdown strings.** `UniversalTemplate` renders `applications`, `recommendations`, and `important_note` via `CheckList`, which treats each item as plain text and adds its own icon. If you store a Markdown string such as `"**Область применения:**\n\n- item\n- item"`, users will see literal `**` asterisks and the section heading will be duplicated. Convert the list to `["item", "item"]` and remove the bold heading from the value.
  - Correct: `"applications": ["Обувь из кожи", "Сумки и ремни"]`
  - Incorrect: `"applications": "**Область применения:**\n\n- Обувь из кожи\n- Сумки и ремни"`
  - For `important_note`, use an array when it is a list (`["Алюминий: 2,5–3%", "Сталь: 1,5–2,5%"]`); use a plain string only for a single prose warning.
- **Verify list rendering visually.** Accessibility snapshots may show empty `listitem` nodes when Bootstrap icons are used as list markers. Always confirm with `browser_vision` that text appears next to each marker.
- **Do not store raw HTML** in fields rendered by `MarkdownParagraph`. The `renderMarkdownText` helper treats angle brackets as literal text; the page will show `<p>...` to users.
- **Detecting raw HTML early:** if a migrated page shows literal tags like `<p>` or `<strong>`, the source was HTML, not Markdown. Re-run the extraction with `html_to_md()` and clear the HTML value.
- **Clear the legacy `application` field** after splitting content, or the "Применение" section will duplicate the "Области применения" section.
- **Clean `body` of trailing fragments.** After splitting, run `clean_body()` on `body` (and `intro` if necessary) to remove leftover `Область применения {Name}:` / `Способ применения {Name}:` / `Способы применения {Name}:` text that v1 appended to the description.
- **For category-wide instructions**, add the same instructional blocks to all affected products. Do not create per-product copies unless the instructions genuinely differ.
- **Empty `application` still renders a section** if `ApplicationSection` finds other instructional blocks (`surface_prep`, `mixing_steps`, etc.). Remove those too if the product should not have a "Применение" section at all.
- **Duplicate `surfaces` trap:** if `applications` and `surfaces` end up with identical lists, `DescriptionSection` will render "Применимые поверхности" and `ApplicationAreasSection` will render the same list as "Области применения". Delete `surfaces` (or `applications`) so each fact appears once.
- **Duplicate `application_industrial` trap:** after populating `applications`, check the v2 DB row. If `application_industrial` exists and equals `applications`, delete `application_industrial` so `ApplicationAreasSection` does not render the list twice (once general, once under "В промышленности").
- **Duplicate `application_domestic` / `application_industrial` layout:** `ApplicationAreasSection` renders `applications` first, then `application_industrial`, then `application_domestic`. If the v1 block already contained distinct "В промышленности" and "Бытовое" subsections, map them directly to `application_industrial` and `application_domestic` and do **not** also create a general `applications` array, or the same items will appear three times.
- **Avoid non-atomic DB commits when doing category-wide migrations.** Because the SQLite DB file is committed as a binary blob, multiple category updates between commits can accidentally bundle unrelated categories into one commit. Commit after each category (or write a backup + verify SHA before `git add pentajunior.db`) so the git history stays atomic and reviewable.

## Detecting accidental bundled DB changes

The SQLite DB is a binary blob; `git status --short` only shows `M pentajunior.db`, not which rows changed. Before committing, verify the current DB state matches the intended category:

```bash
# Confirm the working DB contains the expected update
python3 - <<'PY'
import sqlite3, json
conn = sqlite3.connect('pentajunior.db')
cur = conn.cursor()
cur.execute("SELECT id, template_data FROM products WHERE category_id=?", (4,))
for pid, td in cur.fetchall():
    data = json.loads(td or '{}')
    print(pid, 'applications' in data, 'application_industrial' in data)
conn.close()
PY

# Confirm the file SHA differs from HEAD if you expect changes
sha256sum pentajunior.db
git show HEAD:pentajunior.db | sha256sum
```

If the SHA matches HEAD but the script reported updates, the updates were already committed by an earlier command — inspect `git log --oneline` before adding a redundant commit.

## Atomic-commit recipe

```bash
# 1. migrate one category via script
python3 scripts/migrate_category.py --category-id 2
# 2. verify
npx tsc --noEmit && npm run build
# 3. stage and commit only the DB change
git add pentajunior.db
git commit -m "data(products): migrate application blocks for category 2 (release agents)"
git pull --rebase origin master && git push origin master
# 4. restart dev server if needed
pkill -f 'next start --port 3001'
npx next start --port 3001
```

## Restarting the dev server after DB/content changes

`next start` serves the `.next` output that was produced by the most recent `npm run build`. If you update `template_data` in the SQLite DB and rebuild, the running `next start` process will continue to serve the old static HTML until it is killed and restarted. Always:

1. `npm run build` after DB updates.
2. Kill the existing `next start` process (`pkill -f 'next start --port 3001'` or find PID with `ss -tlnp | grep 3001`).
3. Restart `npx next start --port 3001`.
4. Verify with `curl -I http://localhost:3001/production/{slug}/{productId}`.

## Verification

After migration:
- Open `/production/{slug}/{productId}` in the browser.
- Confirm no raw HTML tags are visible.
- Confirm "Описание" does not end with a dangling "Область применения..." fragment.
- Confirm "Области применения" and "Применение" / "Дополнительная информация" each contain distinct content.
- Confirm "Области применения" is not duplicated under "В промышленности" or "Бытовое".
- Run `npm run build` and check that all static pages generate.
- Verify the DB SHA matches what you expect (`sha256sum pentajunior.db && git show HEAD:pentajunior.db | sha256sum`) before declaring a no-change scenario.

## User constraints for this project

For `pentajunior-v2` migrations specifically, the user has requested:
- Migrate content **only where missing**; do not overwrite existing descriptions.
- Do **not** update product images.
- Only backfill `meta_description`/`keywords`/`title` if the v2 field is empty.
- Process categories **one at a time**.
- Run `npx tsc --noEmit` + `npm run build`, then commit/push after each category.
