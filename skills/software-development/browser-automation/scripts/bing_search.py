#!/usr/bin/env python3
"""
Bing search script.
Usage: python3 bing_search.py "query" [max_results]
"""
import re
import urllib.parse
import subprocess
import json
import sys


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

    # Bing results are in <li class="b_algo"> blocks
    blocks = re.findall(r'<li class="b_algo"[^>]*>(.*?)</li>', html, re.DOTALL)

    for block in blocks[:max_results]:
        # Title + URL inside h2 > a
        title_match = re.search(r'<h2[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?</h2>', block, re.DOTALL)
        # Snippet — usually a <p> after h2
        snippet_match = re.search(r'<p[^>]*>(.*?)</p>', block, re.DOTALL)

        if title_match:
            url = title_match.group(1)
            title = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()
            title = re.sub(r'\s+', ' ', title)

            snippet = ""
            if snippet_match:
                snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()
                snippet = re.sub(r'\s+', ' ', snippet)

            results.append({
                "title": title,
                "url": url,
                "snippet": snippet,
                "engine": "bing"
            })

    return {
        "results": results,
        "engine": "bing",
        "count": len(results),
        "query": query
    }


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "python tutorial"
    max_r = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    result = bing_search(query, max_r)
    print(json.dumps(result, ensure_ascii=False, indent=2))
