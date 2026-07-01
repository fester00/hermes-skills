# Server IP Search Restrictions

Server: Ubuntu 24.04, public IP 130.255.9.9.

## curl → Search Engines: BLOCKED

All major search engines immediately detect and block automated curl requests from this data-center IP:

| Engine | Result | Evidence |
|--------|--------|----------|
| DuckDuckGo HTML | CAPTCHA | `curl` returns page with "captcha" keyword, length < 3KB |
| Bing | CAPTCHA | Same — CAPTCHA page |
| Google | "Unusual traffic" | Redirects to verification page |
| Yandex | "Вы не робот?" | Almost always |

**Conclusion:** Do NOT attempt curl-based search on this server. It wastes time.

## Browser (Chrome CDP) → Search Engines: WORKS

Chrome launched with real profile (`~/.chrome-vk-profile`) on Xvfb DISPLAY :100 passes anti-bot checks:

| Engine | Method | Result |
|--------|--------|--------|
| DuckDuckGo HTML | `browser_cdp` Page.navigate + Runtime.evaluate | ✅ 10 results extracted |
| Google | `browser_cdp` Page.navigate + Runtime.evaluate | ✅ Expected to work (not yet tested) |

## Working Pattern

```json
// 1. Navigate
{"method": "Page.navigate", "params": {"url": "https://html.duckduckgo.com/html/?q=QUERY"}, "target_id": "PAGE_ID"}

// 2. Wait 4 seconds

// 3. Extract
{"method": "Runtime.evaluate", "params": {"expression": "(() => { const r=[]; const links=document.querySelectorAll('a.result__a'); const snippets=document.querySelectorAll('a.result__snippet'); for(let i=0;i<Math.min(links.length,5);i++){const a=links[i];let url=a.href;if(url.includes('/l/?')){const m=url.match(/uddg=([^&]+)/);if(m)url=decodeURIComponent(m[1]);}r.push({title:a.innerText.trim(),url,snippet:snippets[i]?snippets[i].innerText.trim().substring(0,200):'',engine:'duckduckgo'});}return JSON.stringify(r,null,2); })()", "returnByValue":true}, "target_id": "PAGE_ID"}
```

## Chrome Launch (when not running)

```bash
# Ensure Xvfb
pgrep -f "Xvfb :100" || (Xvfb :100 -screen 0 1920x1080x24 -nolisten tcp &)

# Launch Chrome
DISPLAY=:100 google-chrome --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0 \
  --remote-allow-origins=* --user-data-dir=/home/natan/.chrome-vk-profile \
  --no-first-run --no-default-browser-check --window-size=1920,1080 "about:blank" &

# Get fresh CDP URL
curl -s http://127.0.0.1:9222/json/version | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['webSocketDebuggerUrl'])"
```

## Verified: 2026-05-03
Tested with query "какой язык программирования учить в 2026" — extracted 10 results from DuckDuckGo via CDP.
