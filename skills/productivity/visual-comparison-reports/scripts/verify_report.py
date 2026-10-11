#!/usr/bin/env python3
"""Structural + render verification for a self-contained HTML report.

Usage: python3 verify_report.py /abs/path/report.html [out.png]

Checks:
  1. tag balance for the structural tags a report uses
  2. consistent cell count per table row
  3. builder leakage (nan / None / unreplaced placeholders)
  4. headless-Chrome render -> PNG exists with sane dimensions
Exit code 0 = all checks passed.
"""
import html.parser
import os
import re
import shutil
import struct
import subprocess
import sys

VOID = ("br", "img", "meta", "link", "input", "hr", "source")


class Probe(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.tables, self.cur, self.row = [], [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.cur = []
            self.tables.append(self.cur)
        elif tag == "tr" and self.cur is not None:
            self.row = 0
        elif tag in ("td", "th") and self.row is not None:
            self.row += 1
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "tr" and self.cur is not None and self.row is not None:
            self.cur.append(self.row)
            self.row = None
        elif tag == "table":
            self.cur = None
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            self.stack.remove(tag)  # tolerate recoverable nesting errors


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = os.path.abspath(sys.argv[1])
    out_png = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else "/tmp/report-verify.png"
    if not os.path.isfile(path):
        print(f"FAIL: no such file: {path}")
        return 2
    src = open(path, encoding="utf-8").read()
    ok = True
    print(f"file: {path}  ({len(src)} chars, {os.path.getsize(path)} bytes)")

    probe = Probe()
    probe.feed(src)
    if probe.stack:
        ok = False
        print(f"  FAIL unclosed tags: {probe.stack[:8]}")
    else:
        print("  OK   tags balanced")

    for i, rows in enumerate(probe.tables, 1):
        if len(set(rows)) == 1:
            print(f"  OK   table {i}: {len(rows)} rows x {rows[0]} cells")
        else:
            ok = False
            print(f"  FAIL table {i}: ragged rows {rows}")

    leaks = [tok for tok in ("nan", "None", "undefined") if tok in src]
    if leaks:
        ok = False
        print(f"  FAIL builder leakage: {leaks}")
    else:
        print("  OK   no builder leakage")

    bars = re.findall(r'class="barfill"[^>]*width:(\d+)%', src)
    print(f"  INFO chart bars: {len(bars)} -> widths {bars[:12]}")

    chrome = next((c for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")
                   if shutil.which(c)), None)
    if not chrome:
        print("  SKIP render: no Chrome/Chromium on PATH")
        return 0 if ok else 1
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
           "--window-size=1280,2400", "--virtual-time-budget=6000",
           f"--screenshot={out_png}", f"file://{path}"]
    subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    size = png_size(out_png) if os.path.exists(out_png) else None
    if not size:
        ok = False
        print("  FAIL render produced no valid PNG")
    else:
        w, h = size
        verdict = "OK" if w >= 800 and h >= 600 else "SUSPECT"
        if verdict == "SUSPECT":
            ok = False
        print(f"  {verdict:<8} render: {w}x{h} -> {out_png}")
        print("  NEXT   zoom one chart region in the PNG and confirm the longest bar matches the largest printed value")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
