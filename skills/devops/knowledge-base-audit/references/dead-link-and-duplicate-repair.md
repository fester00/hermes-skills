# Repair recipes

Concrete, re-runnable steps for the four repairs an audit usually ends with. Every recipe is
lossless by construction: absorb content, never discard it.

## 1. Dead-link classifier (run before publishing any number)

Do **not** count `[[...]]` matches in raw text — code and escaped pipes dominate the total. Strip code
first, then classify each surviving target.

```python
import re, collections
from pathlib import Path

SKILL_DIRS = [Path("$HERMES_HOME/skills"), Path("$HERMES_HOME/plugins")]
SKILLS = {d.name.lower(): d.name for base in SKILL_DIRS for d in base.rglob("*") if d.is_dir()}
# names the indexes use that exist only with a prefix, or were renamed:
ALIAS = {"writing-plans": "superpowers-writing-plans", "brainstorming": "superpowers-brainstorming",
         "subagent-driven-development": "superpowers-subagent-driven-development",
         "local-tts-selection": "tts-selection"}

files = [p for p in Path(".").rglob("*.md") if ".git" not in p.parts and ".trash" not in p.parts]
stems = {p.stem.lower() for p in files}

def strip_code(t):
    t = re.sub(r"```.*?```", "", t, flags=re.S)   # fenced blocks
    return re.sub(r"`[^`]*`", "", t)              # inline code spans

skill_refs, typos, unknown = collections.Counter(), collections.Counter(), collections.Counter()
for p in files:
    for raw in re.findall(r"\[\[([^\]|#]+)", strip_code(p.read_text(encoding="utf-8", errors="replace"))):
        bare = raw.rstrip("\\").split("/")[-1].strip()
        if bare.lower().endswith(".md"):
            bare = bare[:-3]
        if not bare or bare.lower() in stems:
            continue                                    # resolves, or is a valid alias link
        if bare.lower() in SKILLS:  skill_refs[bare] += 1
        elif bare in ALIAS:         skill_refs[bare] += 1
        elif re.search(r"[\"',()0-9]", bare) or len(bare) < 3:
            continue                                    # code/data fragment, not a link
        else:                       unknown[bare] += 1
```

- `skill_refs` → rewrite each as plain `` `canonical-name` `` text. A skill is not a note; the link can
  never resolve, and leaving it makes the index look broken forever. Apply the case-insensitive and
  prefix mapping in the same pass, otherwise a second sweep is needed (`[[PowerPoint]]`, `[[OCR-and-documents]]`).
- `unknown` → only these are candidates for «create the note or drop the link». Check each with
  `difflib.get_close_matches(target, stems, cutoff=0.72)` to catch typos before flagging a missing note.
- Report as *claimed → verified*, and re-run the counter after each pass.

## 2. Lossless merge of duplicate skills

Keep the survivor that carries the most assets and inbound references (a skill linked from other skills
or the vault). Back up first:

```bash
cp -a <live>/<absorbed> /tmp/backup-<absorbed>     # cheap undo, do it before touching anything
```

Absorb:

1. The absorbed skill's `SKILL.md` becomes `references/<topic>.md` **inside the survivor**, with a header:
   `# <what it covers>` + `> Absorbed <date> from skill \`<name>\` (skill removed, content kept here).`
   Strip its frontmatter — keeping `name:` would advertise a skill that no longer exists.
2. Move its `references/`, `templates/`, `scripts/`, `assets/` into the survivor, renaming on collision
   (`<absorbed>-<file>`).
3. Delete the absorbed directory, add a pointer line for each new file to the survivor's `References`
   section, then verify nothing in those files still points at the dead skill name.
4. Mirror the change to the skills repo **including the deletion** (`rm -rf <repo>/<absorbed>`), copy the
   survivor across, and `diff -r` to prove parity.
5. Recount the library and update any registry or index number the merge invalidated.

Before merging, check that the pair is actually a duplicate. A *router* skill (routing table plus a deep
`references/` set) and a *family* of granular skills covering the same subject are different layers —
merge neither, cross-link both with a `## Related` section instead.

## 3. Registry/index hygiene

Recount from the tree, never from the previous figure:

```bash
cd "$HERMES_HOME/skills"
for d in */; do n=$(find "$d" -name SKILL.md -not -path "*/.archive/*" | wc -l);
  [ "$n" -gt 0 ] && printf '%-28s %s\n' "${d%/}" "$n"; done | sort -k2 -rn
find . -name SKILL.md -not -path './.archive/*' | wc -l   # active
find ./.archive -name SKILL.md | wc -l                    # archived
```

- Embed that command block in the registry itself as «how to recount», so the next session refreshes the
  numbers instead of trusting them.
- When two notes share a filename, a bare `[[Name]]` is ambiguous — write the path explicitly
  (`[[Operations/Hermes — Skills Registry|Hermes — Skills Registry]]`) in every referring note.
- Reduce the loser to a pointer or delete it only after moving its unique half (per-section stats,
  link lists, procedures) into the survivor.

## 4. Duplicate notes that turn out to be complementary

Two versions of one project note usually split the knowledge: infrastructure/DB/PM2 in one, deploy
procedure/known issues/changelog in the other. Merge, do not choose:

1. Read both fully; list the sections unique to each.
2. Pick the canonical path; write the union there, keeping the newer frontmatter and dating the note.
3. Verify every contested fact against the live system (the version a running process reports, the port
   `ss -tlnp` shows) — merge is the moment when stale halves get laundered into the canonical note.
4. Fix stale absolute paths found in either half (projects move: `~/project` → `/mnt/data/.../project`).
5. Delete the twin, then `grep -rn` the old path/name to catch referrers, and update the project MOC.
