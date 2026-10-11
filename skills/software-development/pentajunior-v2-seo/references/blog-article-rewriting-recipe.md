# Blog Article Rewriting Recipe (pentajunior-v2)

Antisèche pattern for rewriting an existing blog article in `src/data/blog/article-XX.ts` with SEO + humanizer polish, without losing rankings or breaking brand conventions.

## When to use

- User asks to rewrite a blog article (often phrased as "сделай рерайт", "humanize", "по seo").
- User wants the article kept in its current shape (no meta changes); only the body polishes.
- One-article-at-a-time iterative workflow ("будем делать по одной статье").

Distinct from `references/blog-article-format-and-publishing-recipe.md`, which is for **adding new** articles. This recipe is for **rewriting existing** ones.

## Workflow (10 steps)

### 1. Read the article and the type

```
read_file('src/data/blog/article-XX.ts')
read_file('src/data/blog/types.ts')
```

`BlogArticle` interface confirms which fields are meta (NOT touched) vs structural (rewritten).

### 2. Build a "ДНК-паспорт"

Enumerate what MUST stay:

- **Meta fields** (forbidden to touch unless user explicitly asks):
  `id`, `title`, `metaTitle`, `metaDescription`, `keywords`, `category`, `relatedProducts`, `relatedCategories`, `publishDate`, `readTime`, `published`.
- **Markers** (must stay on same positions): `{product:ID}`, `{category:ID}`.
- **Factual numbers and units**: Шор А, вязкость, температура, усадка, %, плотность. Same cells, same values.
- **Tables**: body cells stay; only narrative around them rewrites.
- **Section structure (H2/H3)**: order and titles stay.

### 3. Scan for content conflicts

Checklist against pentajunior-v2 SEO conventions:

- **Food / medical / FDA / BfR**: only ТСМ-1 is allowed. Strip from tables, lists, headings, body — even "при наличии сертификации".
- **"От производителя"**: only for Penta Junior's own production. Replace with "купить", "в Москве", "официальный дистрибьютор ООО «ТЕХГРАНТ»" (for ТЕХМОЛ).
- **"Производитель выпускает"** / "Производитель Пента Юниор...": rephrase as "линейка включает", "марки серии", "поставка".
- **"Цена ₽/кг, от …"** in `meta_description`: forbidden.
- **"Материал дышит", "кожа дышит", "разведение"**: replace with "паропроницаемый", "концентрат", "разбавляется водой".

### 4. SERP research

Use the Playwright + Xvfb pattern from `playwright-web-search` skill. Tech note: the venv at `/mnt/data/natan-storage/playwright-search/.venv` does NOT have `requests` — use `urllib.parse.quote` instead.

```python
import asyncio, urllib.parse, json
from playwright.async_api import async_playwright

QUERIES = ["query 1", "query 2", ...]  # 4-6 from keywords[] + related

async def main():
    out = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="/mnt/data/natan-storage/.chrome-vk-profile",
            headless=False,
            viewport={"width": 1920, "height": 1080},
            args=["--disable-blink-features=AutomationControlled"],
        )
        for q in QUERIES:
            page = await browser.new_page()
            url = "https://yandex.ru/search/?text=" + urllib.parse.quote(q)
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
            results = await page.eval_on_selector_all(
                "a.Link",
                "els => els.slice(0,12).map(e => ({href: e.href, text: (e.innerText||'').trim()})).filter(x => x.href && !x.href.includes('yandex.ru') && x.text.length > 8)"
            )
            out[q] = results
            await page.close()
        await browser.close()
    print(json.dumps(out, ensure_ascii=False, indent=2))

asyncio.run(main())
```

Run with:
```bash
xvfb-run -a --server-args="-screen 0 1920x1080x24" \
  /mnt/data/natan-storage/playwright-search/.venv/bin/python /tmp/your_script.py
```

Then fetch top 1–2 organic competitors to extract `title`, `meta_desc`, `h1`, `h2[]`, first paragraphs. Use the same browser context.

Identify LSI anchors from SERP (related terms the user sees in competitor intros): e.g., «двухкомпонентный», «литьевой», «жидкий», «катализатор», «гидросилилирование», «усадка».

### 5. Draft 3 intro variants (A/B/C)

Show ALL three to the user. User picks one. Don't pick for them.

**A: definition + описание + анонс структуры** (default, AI-search friendly)

```
<h2>{H2 in question form or with key term}</h2>
<p>DEFINITION SENTENCE — first sentence defines the term with core SEO keywords.</p>
<p>STRUCTURE ANNOUNCEMENT — list what the article covers (parameters, марки, tables, FAQ).</p>
<p>PRODUCT BRIDGE — note ties to {"product:ID"} marker as soft commercial anchor.</p>
```

**B: short/punchy** (high LSI density, no definition)

```
<h2>{H2}</h2>
<p>TASK-FIRST SENTENCE — starts with the user's job or comparison.</p>
<p>JUST ENOUGH CONTEXT — 1 sentence, no fluff.</p>
```

**C: AI-search / GEO friendly** (YandexGPT quotation)

```
<h2>{H2}</h2>
<p>DIRECT ANSWER — answers "what is X" and "how to choose X" in the first 2 sentences.</p>
<p>NUMBERED CRITERIA — 4 user-actionable items.</p>
```

### 6. Wait for "давай"

Do not proceed to rewrite without explicit user approval of the chosen variant.

### 7. Apply rewrite via `write_file`

Full overwrite is usually cleaner than per-section `patch` because the changes touch most paragraphs and tables.

### 8. Build gate

```bash
export PATH="/home/natan/.nvm/versions/node/v24.13.1/bin:$PATH"
cd /home/natan/pentajunior-v2
./node_modules/.bin/tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
./node_modules/.bin/next build
```

Expected:
- `tsc --noEmit`: exit 0, no output.
- `next build`: `Compiled successfully` + `Generating static pages (157/157)`.

If `npm` or `pnpm` is asked — they are NOT in PATH. Use `./node_modules/.bin/next build` directly.

### 9. Show diff

Brief diff against the user's expectations:
- Meta fields: untouched.
- Markers: same positions.
- New intro: variant chosen.
- Conflicts removed: list (e.g., "food/medical claims at lines X, Y, Z").
- 70–80% of body rewritten.

### 10. Wait for "давай" before commit. Never commit unless explicit.

User pattern: deploy follows commit only after explicit "задеплой".

## Worked examples from the project

- **article-01.ts** — first article. SERP: `sintez-mold.ru` was top competitor. LSI: «двухкомпонентный компаунд», «жидкий силикон», «полиуретан», «эпоксид», «гипс», «бетон». Intro A picked. 4 food/medical mentions removed. Table cell `unisil-9500` rewritten.
- **article-02.ts** — variant A. One table row dropped ("Пищевой контакт") per user direction. Price error 70–120% → 50–70% fixed. Маркер `{product:unisil-9629}` description rephrased.
- **article-03.ts** — H3 "Медицина и пищевая промышленность" renamed to "Специальные технические применения". 1 table cell rewritten (`unisil-9638`).

## Anti-patterns

- **Don't move product markers** — even shifting `{product:unisil-9110}` to another paragraph risks breaking the catalog linker component.
- **Don't restate "Производитель"** — Vercel-style SEO is OK, but sales pitch is not.
- **Don't batch-rewrite without SERP research** — each article has different competitors and LSI landscape.
- **Don't trust tsc vs build output divergence** — both must pass. tsc catches type errors; build catches runtime / static-generation errors.
- **Don't use `npm` / `pnpm`** — broken in PATH. Use `./node_modules/.bin/next` directly.
- **Don't pick the intro variant yourself** — user wants to choose. Show A/B/C, wait for "давай".
- **Don't commit without explicit "давай"** — push and deploy are distinct user-granted actions.
