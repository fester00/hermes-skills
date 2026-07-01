#!/usr/bin/env python3
"""
Verify static site paths + search data validity.
Run from project root. Exits 0 if clean, prints issues otherwise.
"""
import os, sys, re, json

def check_project(project_dir):
    errors = []
    html_files = []
    for root, dirs, fnames in os.walk(project_dir):
        for f in fnames:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))

    for path in html_files:
        rel = os.path.relpath(path, project_dir)
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Check for bad patterns
        if '../pages/' in html:
            errors.append(f"{rel}: contains '../pages/' (wrong depth)")
        if 'pages/pages/' in html:
            errors.append(f"{rel}: contains 'pages/pages/' (double dir)")

        # Check app.js path depth
        depth = rel.count(os.sep)
        if depth == 0:
            if 'src="assets/app.js"' not in html:
                errors.append(f"{rel}: root page missing src=\"assets/app.js\"")
        elif depth == 1:  # pages/*.html (should not exist in this structure)
            pass
        elif depth >= 2:
            if 'src="../../assets/app.js"' not in html:
                errors.append(f"{rel}: missing or wrong app.js path (needs ../../assets/app.js)")
            if 'src="../assets/app.js"' in html:
                errors.append(f"{rel}: app.js path too shallow (../assets/)")

        # Check style.css path depth
        if depth == 0:
            if 'href="assets/style.css"' not in html:
                errors.append(f"{rel}: root page missing href=\"assets/style.css\"")
        elif depth >= 2:
            if 'href="../../assets/style.css"' not in html:
                errors.append(f"{rel}: missing or wrong style.css path")

        # Check double nav-link active class
        if 'nav-link nav-link active' in html:
            errors.append(f"{rel}: double 'nav-link nav-link active' class")

        # Check for CSS calc() without spaces around + (breaks CSS parsing)
        css_path = os.path.join(project_dir, 'assets', 'style.css')
        if os.path.exists(css_path) and not any('calc-without-spaces' in e for e in errors):
            with open(css_path, 'r', encoding='utf-8') as cf:
                css = cf.read()
            bad_calcs = re.findall(r'calc\([^)]*\+[0-9]', css)
            if bad_calcs:
                errors.append(f"assets/style.css: calc() without spaces around '+' operator — {len(bad_calcs)} occurrence(s)")

    # Check search data valid JSON
    search_path = os.path.join(project_dir, 'assets', 'search-data.json')
    if os.path.exists(search_path):
        try:
            with open(search_path, 'r') as f:
                data = json.load(f)
            if not isinstance(data, list):
                errors.append("search-data.json: root is not a list")
            for idx, item in enumerate(data):
                for key in ('title', 'keywords', 'href'):
                    if key not in item:
                        errors.append(f"search-data.json item {idx}: missing '{key}'")
        except Exception as e:
            errors.append(f"search-data.json: {e}")
    else:
        errors.append("search-data.json: missing")

    # Check app.js contains reliable searchUrl fallback
    js_path = os.path.join(project_dir, 'assets', 'app.js')
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            js = f.read()
        if 'searchUrl' not in js:
            errors.append("assets/app.js: missing searchUrl() function")
        if 'location.pathname' not in js and 'document.currentScript' not in js:
            errors.append("assets/app.js: searchUrl does not use pathname or currentScript for depth calculation")
        if 'window.__SEARCH_DATA__' not in js:
            errors.append("assets/app.js: missing inline-search fallback (window.__SEARCH_DATA__)")
    else:
        errors.append("assets/app.js: missing")

    if errors:
        print("ISSUES FOUND:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {len(html_files)} HTML files, clean paths, valid JSON, inline fallback present")
    return 0

if __name__ == '__main__':
    d = sys.argv[1] if len(sys.argv) > 1 else '.'
    sys.exit(check_project(d))
