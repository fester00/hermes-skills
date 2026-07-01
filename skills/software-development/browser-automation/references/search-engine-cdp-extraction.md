# Search Engine CDP Extraction

Session-tested JS snippets for extracting search results via Chrome CDP Runtime.evaluate.
Tested on server IP 130.255.9.9 where curl triggers CAPTCHA on all search engines.

## DuckDuckGo HTML

Navigate to: `https://html.duckduckgo.com/html/?q=QUERY`
Wait 4 seconds, then evaluate:

```javascript
(() => {
  const r = [];
  const links = document.querySelectorAll('a.result__a');
  const snippets = document.querySelectorAll('a.result__snippet');
  for (let i = 0; i < Math.min(links.length, 10); i++) {
    const a = links[i];
    let url = a.href;
    if (url.includes('/l/?')) {
      const m = url.match(/uddg=([^&]+)/);
      if (m) url = decodeURIComponent(m[1]);
    }
    r.push({
      title: a.innerText.trim(),
      url: url,
      snippet: snippets[i] ? snippets[i].innerText.trim().substring(0, 200) : '',
      engine: 'duckduckgo'
    });
  }
  return JSON.stringify(r, null, 2);
})()
```

Alternative (Google classic layout): `document.querySelectorAll("#search .g")` — iterate `.g` blocks, find `h3` and `a` inside.

## Google Search

Navigate to: `https://www.google.com/search?q=QUERY&gl=us&hl=en`
Wait 4 seconds, then evaluate:

```javascript
(() => {
  const results = [];
  const containers = document.querySelectorAll("div[data-ved]");
  for (const container of containers.slice(0, 10)) {
    const h3 = container.querySelector("h3");
    const link = container.querySelector("a[href^='http']");
    const spans = container.querySelectorAll("span");
    let snippet = "";
    for (const s of spans) {
      const text = s.innerText;
      if (text.length > 30 && text.length < 300) {
        snippet = text.substring(0, 200);
        break;
      }
    }
    if (h3 && link) {
      results.push({
        title: h3.innerText.trim(),
        url: link.href,
        snippet: snippet,
        engine: 'google'
      });
    }
  }
  return JSON.stringify(results, null, 2);
})()
```

**Why `gl=us`:** Skips EU cookie consent popup. Without it, Google shows "Before you continue" screen that blocks results.

## Anti-bot Fallback Chain

1. DuckDuckGo HTML (browser/CDP) — fastest, usually works
2. Google (browser/CDP + gl=us) — if DDG shows CAPTCHA
3. Direct page curl — for Wikipedia, docs, GitHub (not search engines)
4. Abort with explanation — if all search engines blocked

## Debugging: No Results?

```javascript
// Check page title
document.title

// Check for CAPTCHA keywords
document.body.innerText.includes('captcha') || document.body.innerText.includes('robot')

// Get page structure hint
document.querySelectorAll('a').length  // total links on page
```

## CDP call pattern (Hermes)

```json
{
  "method": "Runtime.evaluate",
  "params": {
    "expression": "...JS snippet...",
    "returnByValue": true
  },
  "target_id": "PAGE_TARGET_ID"
}
```

Get `target_id` via `Target.getTargets`, filter `type: "page"`.
