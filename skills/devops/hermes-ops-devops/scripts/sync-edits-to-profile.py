#!/usr/bin/env python3
"""Carry this session's edits from one Hermes skill tree into another profile's tree.

A profile is NOT a mirror of the default tree: most shared skills differ by pre-existing drift
(an older copy, a profile-specific rewrite). Copy only the files whose divergence is small enough
to be *your edit from today*, back every target up first, then verify byte parity.

Usage:
    python3 sync-edits-to-profile.py --source "$HOME/.hermes/skills" \
        --target "$HOME/.hermes/profiles/maximus/skills" [--since-hours 30] [--max-lines 12] [--apply]

Dry run by default: prints the plan and touches nothing. Re-run with --apply to copy.
Exit codes: 0 = done (or nothing to do), 2 = refused (paths missing / verification failed).

Deletions are deliberately NOT inferred: when a skill was removed upstream, delete the profile
copy by path and prove it — `grep -rli <name> <profile>/skills <profile>/memories <profile>/SOUL.md`.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Runtime bookkeeping each profile keeps for itself — never copy these.
EXCLUDE_NAMES = {".usage.json", ".curator_state", ".curator_ledger.jsonl",
                 ".skills_prompt_snapshot.json"}


def recent_files(root: Path, since: float) -> list[Path]:
    out = []
    for p in root.rglob("*"):
        if not p.is_file() or p.name in EXCLUDE_NAMES or p.name.endswith(".pyc"):
            continue
        try:
            if p.stat().st_mtime >= since:
                out.append(p)
        except OSError:
            continue
    return sorted(out)


def divergence(a: Path, b: Path) -> int:
    r = subprocess.run(["diff", str(a), str(b)], capture_output=True, text=True)
    return sum(1 for line in r.stdout.splitlines() if line[:1] in "<>")


def digest(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="the tree you edited (default profile)")
    ap.add_argument("--target", required=True, help="the profile tree to update")
    ap.add_argument("--since-hours", type=float, default=30.0)
    ap.add_argument("--max-lines", type=int, default=12,
                    help="above this diff size the divergence is pre-existing drift, not your edit")
    ap.add_argument("--apply", action="store_true", help="default is a dry run")
    args = ap.parse_args()

    src = Path(args.source).expanduser()
    dst = Path(args.target).expanduser()
    for d in (src, dst):
        if not d.is_dir():
            print(f"refused: not a directory: {d}", file=sys.stderr)
            return 2

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = dst.parent / "backups" / f"profile-sync-{stamp}"
    since = time.time() - args.since_hours * 3600

    plan, drift, absent = [], [], []
    for f in recent_files(src, since):
        rel = f.relative_to(src)
        tgt = dst / rel
        if not tgt.exists():
            absent.append(rel)
            continue
        n = divergence(f, tgt)
        if n == 0:
            continue
        (drift if n > args.max_lines else plan).append((rel, f, tgt, n))

    print(f"source {src}\ntarget {dst}")
    print(f"window last {args.since_hours:g}h · threshold {args.max_lines} lines · "
          f"{'APPLY' if args.apply else 'DRY RUN'}")
    print(f"\ncarry ({len(plan)}):")
    for rel, _, _, n in plan:
        print(f"  {rel}  ({n} lines)")
    print(f"\nleft alone — pre-existing drift ({len(drift)}):")
    for rel, _, _, n in drift:
        print(f"  {rel}  ({n} lines)")
    print(f"\nabsent in the profile ({len(absent)}): "
          f"{', '.join(str(r) for r in absent[:8])}{' …' if len(absent) > 8 else ''}")

    if not args.apply:
        print("\nplan only; re-run with --apply")
        return 0

    failed = []
    for rel, f, tgt, _ in plan:
        dest = backup / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tgt, dest)          # back up before writing
        shutil.copy2(f, tgt)
        if digest(f) != digest(tgt):
            failed.append(rel)

    print(f"\ncopied {len(plan)} file(s); backups in {backup}")
    if failed:
        print("VERIFICATION FAILED for: " + ", ".join(str(r) for r in failed), file=sys.stderr)
        return 2
    print("verified: every copied file is byte-identical with the source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
