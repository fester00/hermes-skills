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
# names the indexes use that exist only with a prefix, or that were renamed.
# Keep only entries whose target really exists in the library — stale aliases make
# later audits report phantom skills:
ALIAS = {"local-tts-selection": "tts-selection"}

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

## 5. Syncing the live skills tree into its git repo — additively

The repo is not a mirror: it can legitimately hold skills that are not installed locally (a published
collection, another profile's set). A `--delete` mirror destroys them. Measure the asymmetry first:

```python
live_files = {p.relative_to(live) for p in live.rglob("*") if p.is_file() and ".git" not in p.parts}
only_repo = [p for p in repo.rglob("*") if p.relative_to(repo) not in live_files]
```

Then push in one direction only — copy new and changed files, delete nothing:

```python
for p in live.rglob("*"):
    if not p.is_file() or ".archive" in p.parts:
        continue                                   # the local archive stays out of the repo
    target = repo / p.relative_to(live)
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, target); added += 1
    elif not filecmp.cmp(p, target, shallow=False):
        shutil.copy2(p, target); updated += 1
```

- Report `added / updated / unchanged`. Never «synced, N changes» — the reader cannot tell an addition
  from a deletion.
- Deletions are a separate, owner-approved action and belong to a merge (recipe 2), never to a bulk sync.
  After the sync `git status --porcelain | grep -c '^ D'` must be `0`.
- Leave the repo-only remainder in place and report it (count plus top categories) as an open question.
- Runtime state files swept in by the copy (`.*lock.json`, `.*state`, `.*manifest`) may already be
  tracked — flag that as a pre-existing defect; do not untrack them unasked.
- Large deltas are the point of the exercise: a skill whose live copy differs by hundreds of lines is
  exactly the work that existed only on the server and would have been lost.

## 6. Normalising skill descriptions in bulk

Convention: `description: Use when <trigger>. <behaviour>.` — the first 57 characters are the trigger and
must stand alone, the whole value stays under ~200 characters, written in English.

1. Select the targets with a script that also matches block scalars (`description: |` with the text on the
   following lines); a single-line regex reports those as empty and hides the worst offenders:
   ```python
   m = re.search(r"^description:\s*(\||>)?\s*\n((?:[ \t]+.*\n)+)", txt, re.M)
   ```
2. Read each skill's overview before rewriting. The trigger names the **situation** («Use when the built-in
   browser is blocked on X»), not the topic («About browser automation»).
3. Split the set across two subagents by category range (A–M / N–Z); the halves cannot collide on a file
   and the wall time halves.
4. Verify instead of trusting the report: (a) re-run the selector — zero remaining; (b) `yaml.safe_load`
   every frontmatter — zero errors, which also catches unescaped colons; (c) compare line and section
   counts against before to prove the body survived; (d) quote five old→new pairs.
5. Change the `description` line only. Quote the value when it contains a colon or quotes, and collapse
   block descriptions to one line so the next scanner sees them.

## 7. Removing references to skills that no longer exist

Run this after any deletion, or when a profile is trimmed. A «reference» is anything that makes a reader
or a tool reach for a name: `related_skills` / `related` / `see_also` / `supersedes` in frontmatter,
`skill_view("<skill-name>")` calls, «see the `<skill-name>` skill» sentences, index and registry rows, cards named after the skill.

1. Resolve existence **per library**: a name is live if a directory of that name *or* a frontmatter `name:`
   holds a `SKILL.md` outside `.archive/`. Check the profile tree and the global tree separately — a name
   that resolves in one profile is dead in the other, and the same skill is often copied into both, so fix
   every copy (a first pass looks clean only because the scanner read a single tree).
2. Strip names from list values with a **line-based pass that never touches leading whitespace**. Collapsing
   `\s{2,}` on an edited line destroys YAML indentation and silently invalidates frontmatter — the damage
   surfaces only when the skill refuses to load. Never reformat a line you did not have to change.
3. `yaml.safe_load` every touched frontmatter *before* writing; refuse the write and report the file instead
   of saving something broken.
4. Prefer a conditional rewrite over deletion when the sentence carries meaning: «supersedes the earlier
   single-purpose nearby-search skill», «attach a debugger» instead of «use the `<old-name>` skill». Re-point a
   dead `skill_view()` at the live equivalent (`autonomous-coding-agents`, `excalidraw`, `jupyter-live-kernel`)
   rather than dropping the row.
5. **These are not references** — leave them: MCP server names, CLI tools, category slugs, file paths,
   attribution to upstream authors (licence and credit), and historical records of a deliberate deletion
   (erasing the name destroys the record's meaning).
6. Prove it against the pristine copy: the git mirror of the global tree holds the pre-edit state, so a diff
   shows that only lines containing the name changed and no indentation moved. Then re-run the counter
   (zero dead maps, zero dead `skill_view` calls) and re-validate every `SKILL.md`.
7. Sweep the runtime registries as well (`.usage.json` keeps a key per skill, `.curator_ledger.jsonl` one per
   action): stale keys are harmless, but they make the next audit report phantom skills.
