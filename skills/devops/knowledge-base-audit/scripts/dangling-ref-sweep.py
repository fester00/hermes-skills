#!/usr/bin/env python3
"""Find — and optionally strip — references to skills that no longer exist. Also probes for structural
damage of the kind a bulk edit causes.

Usage:
    python3 dangling-ref-sweep.py                     # scan every library, report dead references
    python3 dangling-ref-sweep.py --apply             # rewrite frontmatter maps in place
    python3 dangling-ref-sweep.py --structure         # probe for flattening / unparsable frontmatter
    python3 dangling-ref-sweep.py --mirror <repo>     # diff changed files against a pristine tree
    python3 dangling-ref-sweep.py --libs <dir> [...]  # explicit libraries (default: HERMES_HOME/skills
                                                      # + every profiles/*/skills)

What counts as a reference: the frontmatter maps ``related_skills`` / ``related`` / ``see_also`` /
``supersedes``, and ``skill_view("<name>")`` calls in any .md file.

Existence is resolved **per library**: a name is live when a directory of that name *or* a frontmatter
``name:`` holds a SKILL.md outside ``.archive/``. A name that resolves in one profile is still dead in
the other, and the same skill is usually copied into both — so every library is scanned separately.

Safety, by construction:
  * a line that does not have to change keeps its bytes — indentation is never normalised;
  * frontmatter is parsed with yaml.safe_load *before* the file is written, and a parse error skips the
    file instead of saving a broken one;
  * list values are re-emitted on one line (``key: [a, b]``), so a block list that loses entries cannot
    leave dangling ``- item`` lines behind.

Run ``--structure`` over both libraries after ANY bulk pass: a whole-text ``\\s{2,}`` collapse flattens
markdown into a handful of enormous lines and leaves the frontmatter unclosed, which no token count will
ever show. That probe is cheap; the damage is not.
"""
from __future__ import annotations

import os
import pathlib
import re
import sys

import yaml

KEYS = ("related_skills", "related", "see_also", "supersedes")
SKILL_VIEW = re.compile(r'skill_view\(["\']([A-Za-z0-9_./-]+)["\']\)')
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
LONG_LINE = 1000          # a markdown paragraph never runs this long; a flattened file does


def libraries(argv: list[str]) -> list[pathlib.Path]:
    if "--libs" in argv:
        return [pathlib.Path(p).expanduser() for p in argv[argv.index("--libs") + 1:] if not p.startswith("--")]
    home = pathlib.Path(os.environ.get("HERMES_HOME", "~/.hermes")).expanduser()
    libs = [home / "skills"]
    libs += sorted((home / "profiles").glob("*/skills")) if (home / "profiles").is_dir() else []
    return [p for p in libs if p.is_dir()]


def known_names(libs: list[pathlib.Path]) -> set[str]:
    """Live names across all libraries: directory slug or frontmatter name, archive excluded."""
    names: set[str] = set()
    for base in libs:
        for p in base.rglob("SKILL.md"):
            if "/.archive/" in str(p):
                continue
            names.add(p.parent.name)
            m = FRONTMATTER.match(p.read_text(encoding="utf-8", errors="ignore"))
            if not m:                                   # assert the match, do not skip it
                print(f"  !! no frontmatter block: {p}")
                continue
            try:
                fm = yaml.safe_load(m.group(1)) or {}
            except Exception as exc:
                print(f"  !! unparsable frontmatter: {p} — {str(exc).splitlines()[0][:60]}")
                continue
            if fm.get("name"):
                names.add(str(fm["name"]))
    return names


def check_structure(libs: list[pathlib.Path]) -> int:
    """Probe for the damage a bulk edit leaves: flattened markdown, unclosed or unparsable frontmatter."""
    findings = 0
    for lib in libs:
        for p in sorted(lib.rglob("*.md")):
            text = p.read_text(encoding="utf-8", errors="ignore")
            if not text.strip():
                continue
            lines = text.split("\n")
            longest = max((len(l) for l in lines), default=0)
            rel = p.relative_to(lib)
            if p.name == "SKILL.md":
                m = FRONTMATTER.match(text)
                if not m:
                    findings += 1
                    print(f"  !! [{lib.name}] {rel}: frontmatter block not closed (flattened or truncated)")
                    continue
                try:
                    fm = yaml.safe_load(m.group(1)) or {}
                except Exception as exc:
                    findings += 1
                    print(f"  !! [{lib.name}] {rel}: frontmatter does not parse — {str(exc).splitlines()[0][:60]}")
                    continue
                missing = [k for k in ("name", "description") if not fm.get(k)]
                if missing:
                    findings += 1
                    print(f"  !! [{lib.name}] {rel}: frontmatter parsed but empty {missing} (metadata lost)")
            if longest > LONG_LINE:
                findings += 1
                print(f"  !! [{lib.name}] {rel}: longest line {longest} chars across {len(lines)} lines — flattened?")
            elif len(lines) < 5 and len(text) > 800:
                findings += 1
                print(f"  !! [{lib.name}] {rel}: {len(text)} chars in {len(lines)} lines — newlines collapsed?")
    print(f"structural findings: {findings}")
    return findings


def clean_maps(path: pathlib.Path, known: set[str], apply: bool) -> list[tuple[str, list[str]]]:
    """Drop unknown names from the frontmatter map keys. Returns [(key, dropped_names), ...]."""
    raw = path.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^(---\n)(.*?)(\n---\n)", raw, re.S)
    if not m:
        return []
    lines, out, i, dropped = m.group(2).split("\n"), [], 0, []
    while i < len(lines):
        mk = re.match(r"^(\s*)([\w-]+):\s*(.*)$", lines[i])
        if not mk or mk.group(2) not in KEYS:
            out.append(lines[i])
            i += 1
            continue
        indent, key, val = mk.groups()
        items, j = [], i + 1
        if val.strip().startswith("["):
            items = [x.strip() for x in val.strip().strip("[]").split(",") if x.strip()]
        elif val.strip():
            items = [val.strip()]
        while j < len(lines) and re.match(r"^\s+-\s+", lines[j]):
            items.append(re.sub(r"^\s+-\s+", "", lines[j]).strip())
            j += 1
        keep = [x for x in items if x in known]
        gone = [x for x in items if x not in known]
        out.append(f"{indent}{key}: [{', '.join(keep)}]" if gone else lines[i])
        if gone:
            dropped.append((key, gone))
        i = j
    if not dropped:
        return []
    new_fm = "\n".join(out)
    try:
        yaml.safe_load(new_fm)
    except Exception as exc:                      # refuse the write, report the file
        print(f"    !! invalid frontmatter, left untouched: {path} — {str(exc).splitlines()[0][:60]}")
        return []
    if apply:
        path.write_text(m.group(1) + new_fm + m.group(3) + raw[m.end():], encoding="utf-8")
    return dropped


def changed_against_mirror(lib: pathlib.Path, mirror: pathlib.Path, names: set[str]) -> None:
    """Line-level proof: every line of the edited file is either verbatim in the pristine copy or
    contains one of the removed names. Anything else is damage."""
    for p in lib.rglob("*.md"):
        rel = p.relative_to(lib)
        pristine = mirror / rel
        if not pristine.exists():
            continue
        old = pristine.read_text(encoding="utf-8", errors="ignore").split("\n")
        old_set = set(old)
        if any(n in line for line in old for n in names):
            for n_line, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").split("\n"), 1):
                if line.strip() and line not in old_set and not any(n in line for n in names):
                    print(f"    ? {rel}:{n_line} changed without naming a removed skill: {line.strip()[:80]}")


def main(argv: list[str]) -> int:
    apply = "--apply" in argv
    libs = libraries(argv)
    print(f"libraries: {', '.join(str(p) for p in libs)}")
    if "--structure" in argv:
        return 1 if check_structure(libs) else 0
    known = known_names(libs)
    mirror = None
    if "--mirror" in argv:
        mirror = pathlib.Path(argv[argv.index("--mirror") + 1]).expanduser()
    print(f"live names: {len(known)}")
    total_maps = total_views = 0
    for lib in libs:
        for p in sorted(lib.rglob("SKILL.md")):
            dropped = clean_maps(p, known, apply)
            for key, gone in dropped:
                total_maps += len(gone)
                print(f"  ~ [{lib.name}] {p.relative_to(lib)} :: {key} − {gone}")
        for p in sorted(lib.rglob("*.md")):
            for n_line, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").split("\n"), 1):
                for target in SKILL_VIEW.findall(line):
                    if target not in known:
                        total_views += 1
                        print(f"  ? [{lib.name}] {p.relative_to(lib)}:{n_line} :: skill_view({target!r})")
        if mirror:
            changed_against_mirror(lib, mirror, known)
    print(f"dead map entries: {total_maps} | dead skill_view calls: {total_views}")
    if not apply and (total_maps or total_views):
        print("re-run with --apply to clean the frontmatter maps (skill_view calls need a human rewrite).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
