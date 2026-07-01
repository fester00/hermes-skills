# Yandex Quick Links (Быстрые ссылки) — SEO Audit Checklist

**Trigger:** User asks "как получить быстрые ссылки в Яндексе", "навигация под сниппетом", «сайтлинки», «extra links in Yandex search».

**Hard rule:** These are **fully algorithmic** since ~2021. Manual control was removed from Yandex.Webmaster. You can only influence them, not guarantee them.

---

## What Yandex Quick Links Are

Below the main search result, Yandex may show 4-6 deep links into your site sections:
- Продукция, Прайс-лист, Контакты, О компании, etc.

These are **not** sitelinks you buy or configure. They appear when the algorithm has high confidence in your site structure and user traffic patterns.

---

## Diagnostic Checklist (run this on any site)

### 1. Navigation ↔ URL Mapping
```bash
curl -s -L -A "Mozilla/5.0" https://SITE.COM/ | grep -o 'href="/[^"]*"' | sort | uniq -c | sort -rn
curl -s https://SITE.COM/robots.txt
curl -s https://SITE.COM/sitemap.xml | grep '<loc>' | head -20
```

**Pitfall I personally found on pentajunior.ru:**
Header nav links pointed to `/products` and `/information`, but actual working pages were `/production` and `/info`. Those broken nav links returned **404 + `noindex`**.

**Fix:** Ensure every `<a>` in header/footer matches a real 200-OK page. Broken nav links confuse the algorithm.

### 2. Sitemap Health
```bash
curl -s https://SITE.COM/sitemap.xml | xmllint --format -
```

- URLs must all return 200
- `<priority>` must reflect hierarchy (main 1.0, sections 0.8, articles 0.7)
- `<lastmod>` should be realistic

### 3. JSON-LD / Microdata Presence
```bash
curl -s -L -A "Mozilla/5.0" https://SITE.COM/ | grep -o 'SiteNavigationElement\|BreadcrumbList\|WebSite\|WebPage\|CollectionPage'
```

**Recommended schema per page:**
- Homepage: `Organization` + `WebSite` (with `url` + `potentialAction`SearchAction``)
- Section pages: `WebPage` or `CollectionPage`
- Product/article pages: `Product` / `Article` + `BreadcrumbList`

**Missing on pentajunior.ru:** `SiteNavigationElement` and `BreadcrumbList`. Adding them is the single strongest technical signal for quick-link confidence.

### 4. Canonical & Noindex Traps
```bash
curl -s -L -A "Mozilla/5.0" https://SITE.COM/SECTION | grep -o '<meta name="robots" content="[^"]*"'
```

A 404 page that incorrectly serves `noindex` is harmless — BUT if your nav links hit 404, search crawler marks them as dead.

### 5. Title + H1 Uniqueness
Every page should have a unique `<title>` and a single `<h1>` that matches the nav label. If «Продукция» is the nav label, the page `/production` should have `<h1>Продукция</h1>` and `<title>Продукция — Сайт</title>`.

---

## When Quick Links Appear

| Factor | Influence |
|--------|-----------|
| Site age + traffic | High — new/low-traffic sites may never get them |
| Stable nav structure | High — changing URLs resets confidence |
| Clear section hierarchy | Medium — header + footer nav + breadcrumbs |
| Microdata (BreadcrumbList) | Medium — helps algorithm map structure |
| Yandex.Metrica or Search Console registration | Low — registration alone doesn't force them |

**Timeline:** Weeks to months after fixing all issues. Do not expect instant results.

---

## Do-NOTs

- Do NOT rename section URLs after they gain quick links — algorithm resets
- Do NOT expect manual control from Yandex.Webmaster — feature removed
- Do NOT create thin «doorway» pages just for quick links — Yandex penalizes this

---

## Reference commands (copy-paste)

```bash
# Full one-shot audit
SITE="https://pentajunior.ru"
for page in / /production /price /info /contacts /news; do
    echo "=== $page ==="
    code=$(curl -s -o /dev/null -w "%{http_code}" -L -A "Mozilla/5.0" "${SITE}${page}")
    echo "HTTP: $code"
    curl -s -L -A "Mozilla/5.0" "${SITE}${page}" | grep -o '<title>[^<]*</title>'
done

curl -s "${SITE}/sitemap.xml" | grep -o '<loc>[^<]*</loc>' | while read loc; do
    url=$(echo "$loc" | sed 's/<loc>//;s/<\/loc>//')
    code=$(curl -s -o /dev/null -w "%{http_code}" -L -A "Mozilla/5.0" "$url")
    [ "$code" != "200" ] && echo "BROKEN: $url -> $code"
done
```
