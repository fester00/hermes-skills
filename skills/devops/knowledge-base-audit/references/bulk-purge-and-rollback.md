# Bulk purge: removing a skill family and every mention of it

For «удалим эти навыки и все упоминания со всех мест». This is a scoped deletion sweep across every
tree — not an audit and not a merge. The order of operations matters more than the script.

## 1. Inventory before touching anything

Enumerate and report the places; the count is always larger than the owner expects:

- live skills tree **and each profile's copy** (`profiles/<name>/skills/`);
- vault: registries, MOCs, skill cards, audit notes, integration notes;
- docs and packages derived from the skills (doc mirrors, workflow packages, archives);
- memory files (`MEMORY.md`, `USER.md`) and persona/role documents;
- runtime state: `.usage.json`, `.curator_ledger.jsonl`, `.hub/index-cache/*.json`;
- cron jobs, configs, plugin manifests — check them, they are usually clean (say so).

Classify every hit before rewriting: files **about** the family (delete whole), files **mentioning** it
in a list, table or link (drop the item/row), and files where the term is legitimate content (leave).

## 2. Back up, and know your pristine sources

Before the first write: tar the family directories (both trees) plus a file list of everything the sweep
will edit into `backups/<slug>-<timestamp>/`, and tell the owner the path.

Find the rollback source per tree — it decides how you repair your own mistakes:

| tree | pristine source |
| --- | --- |
| live skills | the skills git mirror (copy back per file or `git checkout`) |
| vault | its git repo — `git checkout -- .` restores every swept file at once |
| profile copies | **none** — back these up explicitly |
| `.archive/` in the skills tree | usually excluded from the mirror sync — **no pristine source** |

## 3. The sweep: never normalise whitespace on a line you edit

Collapsing runs of spaces while stripping a term rewrites YAML frontmatter indentation and nested-list
structure; the skill then silently stops parsing. Split the line and tidy only the tail:

```python
indent, rest = re.match(r"^(\s*)(.*)$", line).groups()
new = tidy(TOKENS.sub("", rest))     # never touch `indent`
out.append(indent + new)
```

- **Frontmatter is parsed, not regexed.** Rewrite only keys whose value holds a hit, then
  `yaml.safe_load` the whole block; on error write nothing and report the file. Drop whole block items
  (`- name`) instead of leaving `related_skills: [, ]`; collapse an emptied list to `[]`.
- **Never leave mangled prose.** Gate the cleaned line with an artefact regex —
  `\(\s*[,;]|[,;]\s*\)|,\s*,|[^\s(]//|[\w)`»]\.md\b|non-\s|\(\s*\)|\s{3,}` — and when it matches,
  **drop the line** (or the whole item/row) rather than emitting a half-sentence like `docs//specs/`
  or `(, Stitch)`. Print every dropped line in the dry run so the owner sees what left.
- **Phrase rules before token rules**: `non-<Family>` → `non-upstream`, `docs/<family>/specs/` →
  `docs/specs/`, a conjunction glued to the term → drop the conjunction. Generic removal alone mangles.
- **Skip false positives by path**, not by cleverness: a shared word inside imported book or manual notes
  (a language reference, a textbook) is content, not a mention. Keep an allowlist and report what you
  left and why.
- Dry run first: counts, a before/after preview of a few files, and the full list of lines to be deleted.

## 4. Deletions must actually delete — verify by re-grep

A script that appends paths to a `deleted` list and prints them has deleted nothing, and the report looks
flawless. Delete from the deepest path up, then re-check:

```bash
grep -rli "<term>" <each tree> --exclude-dir=.git | wc -l     # expect 0 in live trees
```

Non-zero means the unlink loop never ran. Removing a dedicated file also leaves referrers behind —
re-run the sweep afterwards, then re-grep again.

## 5. Prove nothing else was damaged

1. `grep` → zero in the live trees (allowlist aside).
2. `yaml.safe_load` every `SKILL.md` frontmatter in every tree → zero errors, `name` and `description` present.
3. **Diff against the pristine source and explain every hunk**: collect the live lines absent from the
   pristine copy — each must have contained the term or be a deliberate, artefact-free rewrite. This is
   the check that catches indentation damage the regex gate cannot see.

For files a scripted pass cannot fix (broken frontmatter in trees with no pristine source), repair by
inference: re-indent the orphaned list key to its siblings' indent, strip a leading `[, ` and a trailing
`, ]`, validate, and fix in place — never append an «UPDATE:» note underneath.

## 6. Close out: mirror, commit, memory, history boundary

- Mirror the live tree into the skills repo **including the deletions** (here they are owner-approved),
  commit, push; same for the vault. Verify `HEAD == origin/HEAD` for both.
- Rebuild any archive derived from the swept files. A path carrying the family name in a deliverable
  (the family's private state directory) is renamed, not deleted — a shipped artefact must not keep the family's fingerprint.
- Memory: remove the entries describing the removed method, then read the file back — an earlier inline
  strip can leave a hole («workflow — :») that survives as nonsense in every future session.
- **History is a separate decision.** Past session transcripts and git commit history still contain the
  term and always will. Rewriting published history or deleting transcripts is destructive and never
  implied by «везде»: leave it, report the counts, offer it as an explicit next step.
