#!/usr/bin/env python3
"""
DuckDuckGo HTML search script.
Usage: python3 ddg_search.py "query" [max_results]
"""
import re
import urllib.parse
import subprocess
import json
import sys


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

    # Check for CAPTCHA / block
    lower_html = html.lower()
    if any(k in lower_html for k in ["captcha", "robot", "challenge", "verify", "капча", "робот"]):
        return {"error": "CAPTCHA", "engine": "duckduckgo", "html_length": len(html)}
    if len(html) < 3000:
        return {"error": "EMPTY_RESPONSE", "engine": "duckduckgo", "html_length": len(html)}

    results = []

    # DuckDuckGo HTML results are in <div class="result"> blocks
    # Each block contains:
    #   <a class="result__a" href="...">title</a>
    #   <a class="result__snippet">snippet</a>

    # Strategy: find all result blocks, then extract within each
    # DDG structure: <div class="result results_links results_links_deep web-result"> ... </div>
    blocks = re.findall(r'<div class="result[^"]*"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)

    if not blocks:
        # Alternative pattern: broader match
        blocks = re.findall(r'<div class="result[^"]*"[^>]*>.*?</div>\s*</div>', html, re.DOTALL)

    for block in blocks[:max_results]:
        # URL from result__a href
        url_match = re.search(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"', block)
        # Title
        title_match = re.search(r'<a[^>]+class="result__a"[^>]*>(.*?)</a>', block, re.DOTALL)
        # Snippet
        snippet_match = re.search(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', block, re.DOTALL)

        if url_match and title_match:
            raw_url = url_match.group(1)
            # Decode DuckDuckGo redirect: /l/?uddg=URL
            if raw_url.startswith("/l/?"):
                uddg_match = re.search(r'uddg=([^&]+)', raw_url)
                if uddg_match:
                    raw_url = urllib.parse.unquote(uddg_match.group(1))
            elif raw_url.startswith("/l/"):
                # Alternative format
                uddg_match = re.search(r'uddg=([^&]+)', raw_url)
                if uddg_match:
                    raw_url = urllib.parse.unquote(uddg_match.group(1))

            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
            title = re.sub(r'\s+', ' ', title)
            snippet = ""
            if snippet_match:
                snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()
                snippet = re.sub(r'\s+', ' ', snippet)

            results.append({
                "title": title,
                "url": raw_url,
                "snippet": snippet,
                "engine": "duckduckgo"
            })

    return {
        "results": results,
        "engine": "duckduckgo",
        "count": len(results),
        "query": query
    }


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "python tutorial"
    max_r = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    result = ddg_search(query, max_r)
    print(json.dumps(result, ensure_ascii=False, indent=2))
