#!/usr/bin/env python3
"""
Inline CSS, JS, and per-directory search data into static HTML files.

Solves two file:// protocol problems:
1. ERR_FILE_NOT_FOUND — browsers resolve ../../assets/style.css inconsistently
   across folder boundaries on file://. Fix: inline CSS + JS.
2. fetch() is forbidden on file:// — search data must be injected inline.
   BUT hrefs in search data must be relative to EACH page's directory, not global.
   Fix: rewrite hrefs per-file using os.path.relpath.

Usage:
    python inline-assets.py /path/to/project

Expects:
    project/
    ├── index.html
    ├── pages/
    │   └── .../*.html
    └── assets/
        ├── style.css
        ├── app.js
        └── search-data.json   (hrefs must be root-relative, e.g. "pages/core/intro.html")

Replaces <link rel="stylesheet" href="...style.css"> with inline <style>,
<script src="...app.js" defer></script> with inline <script defer>,
and injects per-page window.__SEARCH_DATA__ with correctly relative hrefs.
"""

import os, re, sys, json

def inline_assets(project_dir: str):
    css_path = os.path.join(project_dir, "assets", "style.css")
    js_path = os.path.join(project_dir, "assets", "app.js")
    json_path = os.path.join(project_dir, "assets", "search-data.json")

    if not os.path.exists(css_path):
        print(f"ERROR: {css_path} not found")
        sys.exit(1)
    if not os.path.exists(js_path):
        print(f"ERROR: {js_path} not found")
        sys.exit(1)

    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()
    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()

    # Load root-relative search data once; hrefs will be rewritten per-file
    search_data = []
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            search_data = json.load(f)
        # Sanity check: warn if hrefs already contain ../ or ./ — they must be root-relative
        for entry in search_data:
            href = entry.get("href", "")
            if href.startswith(("../", "./")):
                print(f"WARNING: search-data.json contains relative href '{href}'. "
                      "Expected root-relative paths (e.g. 'pages/core/intro.html').")

    # Patch JS to use window.__SEARCH_DATA__ instead of fetch()
    patched_js = js.replace("fetch(searchUrl())", "Promise.resolve(window.__SEARCH_DATA__ || [])")

    html_files = []
    for root, dirs, files in os.walk(project_dir):
        for fname in files:
            if fname.endswith(".html"):
                html_files.append(os.path.join(root, fname))

    for html_path in html_files:
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Replace CSS link with inline style (handles assets/style.css or ../../assets/style.css)
        html = re.sub(
            r'<link rel="stylesheet" href="[^"]*style\.css">',
            f'<style>\n{css}\n</style>',
            html
        )

        # Build per-file search data: rewrite every href relative to THIS html file
        file_search_data = []
        for entry in search_data:
            new_entry = dict(entry)
            href = entry.get("href", "")
            if href:
                from_dir = os.path.dirname(html_path)
                to_path = os.path.join(project_dir, href)
                rel = os.path.relpath(to_path, from_dir).replace("\\", "/")
                new_entry["href"] = rel
            file_search_data.append(new_entry)

        data_tag = f'<script>window.__SEARCH_DATA__ = {json.dumps(file_search_data, ensure_ascii=False)};</script>\n'

        # Replace JS script with inline script (handles relative paths)
        html = re.sub(
            r'<script src="[^"]*app\.js" defer></script>',
            data_tag + f'<script defer>\n{patched_js}\n</script>',
            html
        )

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        rel = os.path.relpath(html_path, project_dir)
        print(f"  inlined: {rel}  ({len(file_search_data)} search entries)")

    print(f"\nDone. Processed {len(html_files)} HTML files.")
    print("Note: Each file gets its own window.__SEARCH_DATA__ with directory-relative hrefs.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inline-assets.py /path/to/project")
        sys.exit(1)
    inline_assets(sys.argv[1])
