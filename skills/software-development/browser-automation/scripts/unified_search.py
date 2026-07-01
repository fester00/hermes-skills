#!/usr/bin/env python3
"""
Unified web search with auto-fallback.
Usage: python3 unified_search.py "query" [max_results]
Tries: DuckDuckGo → Bing → Google (browser, not implemented in this script)
Returns JSON with results or error.
"""
import re
import urllib.parse
import subprocess
import json
import sys
import time


def ddg_search(query, max_results=10):
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    cmd = [
        "curl", "-sL", "--max-time", "15",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-H", "Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    html = result.stdout

    lower_html = html.lower()
    if any(k in lower_html for k in ["captcha", "robot", "challenge", "verify", "капча", "робот"]):
        return {"error": "CAPTCHA", "engine": "duckduckgo", "html_length": len(html)}
    if len(html) < 3000:
        return {"error": "EMPTY_RESPONSE", "engine": "duckduckgo", "html_length": len(html)}

    results = []
    blocks = re.findall(r'<div class="result[^"]*"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)

    for block in blocks[:max_results]:
        url_match = re.search(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"', block)
        title_match = re.search(r'<a[^>]+class="result__a"[^>]*>(.*?)</a>', block, re.DOTALL)
        snippet_match = re.search(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', block, re.DOTALL)

        if url_match and title_match:
            raw_url = url_match.group(1)
            if raw_url.startswith("/l/?"):
                uddg_match = re.search(r'uddg=([^&]+)', raw_url)
                if uddg_match:
                    raw_url = urllib.parse.unquote(uddg_match.group(1))

            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
            title = re.sub(r'\s+', ' ', title)
            snippet = ""
            if snippet_match:
                snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()
                snippet = re.sub(r'\s+', ' ', snippet)

            results.append({"title": title, "url": raw_url, "snippet": snippet, "engine": "duckduckgo"})

    return {"results": results, "engine": "duckduckgo", "count": len(results), "query": query}


def bing_search(query, max_results=10):
    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&setmkt=en-US&setlang=en"
    cmd = [
        "curl", "-sL", "--max-time", "15",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-H", "Accept-Language: en-US,en;q=0.9",
        "-H", "Accept: text/html,application/xhtml+xml",
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    html = result.stdout

    lower_html = html.lower()
    if any(k in lower_html for k in ["captcha", "robot", "challenge", "verify"]):
        return {"error": "CAPTCHA", "engine": "bing"}
    if len(html) < 5000:
        return {"error": "EMPTY_RESPONSE", "engine": "bing", "html_length": len(html)}

    results = []
    blocks = re.findall(r'<li class="b_algo"[^>]*>(.*?)</li>', html, re.DOTALL)

    for block in blocks[:max_results]:
        title_match = re.search(r'<h2[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?</h2>', block, re.DOTALL)
        snippet_match = re.search(r'<p[^>]*>(.*?)</p>', block, re.DOTALL)

        if title_match:
            url = title_match.group(1)
            title = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()
            title = re.sub(r'\s+', ' ', title)
            snippet = ""
            if snippet_match:
                snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()
                snippet = re.sub(r'\s+', ' ', snippet)

            results.append({"title": title, "url": url, "snippet": snippet, "engine": "bing"})

    return {"results": results, "engine": "bing", "count": len(results), "query": query}


def search_web(query, max_results=10):
    """Try DuckDuckGo → Bing → return error with advice."""

    # 1. Try DuckDuckGo
    ddg_result = ddg_search(query, max_results)
    if "error" not in ddg_result:
        return ddg_result

    # 2. Wait briefly, then try Bing
    time.sleep(1)
    bing_result = bing_search(query, max_results)
    if "error" not in bing_result:
        return bing_result

    # 3. Both failed
    return {
        "error": "ALL_ENGINES_BLOCKED",
        "engines_tried": ["duckduckgo", "bing"],
        "errors": {
            "duckduckgo": ddg_result.get("error"),
            "bing": bing_result.get("error")
        },
        "advice": "Use browser_navigate to https://www.google.com/search?q=QUERY for manual search",
        "query": query
    }


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "python tutorial"
    max_r = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    result = search_web(query, max_r)
    print(json.dumps(result, ensure_ascii=False, indent=2))
