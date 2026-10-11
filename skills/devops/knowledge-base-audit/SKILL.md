---
name: knowledge-base-audit
description: Use when auditing a knowledge base or skill library. Detect drift, stale facts, and mismatches across sources.
category: devops
---

# Auditing a knowledge base, a skill library and a host record

## When to Use

- The user asks «проверь, чтобы записи были актуальны» — whether the vault, docs or notes are still true.
- Two sources describe the same system differently: a README structure table against the repo
  constitution, two registry notes with the same filename, a skill's numbers against the real count.
- Before a migration or a large rename, or after months of drift nobody watched.
- You are about to quote a dashboard, registry or agent report as fact.

When NOT to use: ordinary retrieval (see `knowledge-first-protocol`), or maintaining one known note.

## Scope split

Split the audit into four independent scopes and run one **read-only** subagent per scope in parallel:

1. **Knowledge base** — dead links, contradictions between notes, stale claims about live state.
2. **Skill library** — overlapping skills, contradictory instructions, description-format drift,
   live skills directory against its git repo.
3. **Host and environment** — measured reality against what the notes claim.
4. **The rule and structure documents themselves** — constitution folder map, retrieval protocol,
   registries.

Do scope 4 yourself while the others run: it defines what "correct" means for every other scope.

## Briefing a read-only audit subagent

Every brief must state all five:

- **read-only** — no file writes, no state-changing git commands;
- **evidence per claim** — file path with line number, or the command output that proves it;
- **structured output** — summary, then findings as *problem → evidence → proposed fix → priority*;
- **a cap** — roughly 40 items, most important first, no narrative;
- **an honest exit** — «if you cannot verify a claim, mark it uncertain and say what evidence is missing».

Child summaries are self-reports: verify the load-bearing claims yourself (open the file, run the
command) before acting on them or repeating them to the user.

## Checks that pay off

- **Dead wikilinks.** Validate every `[[...]]` against the set of note stems. Before counting anything,
  strip fenced code blocks **and inline code spans**: array/JSON fragments (`[[1, 2, 3]]`, `[[None]]`,
  `[[ndarray]]`, `[['*' for k in range(s)]]`) are code, not links, and they dominate a naive count.
  `[[../path/Name\|Name]]` inside a table is **valid** — the pipe is escaped for Markdown tables, so a
  scanner that stops at `|` reads the backslash as part of the name and reports breaks that do not exist.
- **Wikilinks to skills can never resolve.** A skill is not a note, so `[[browser-automation]]` is broken
  by construction no matter how many indexes use it. Classify every surviving target before reporting:
  live skill name (match case-insensitively; apply prefix maps such as `writing-plans` →
  `superpowers-writing-plans`, `local-tts-selection` → `tts-selection`) → rewrite as plain `` `code` ``
  text; near-miss on a note stem → fix the typo; junk → ignore. Then publish the number as
  *claimed → verified* («заявлено 280, настоящих 211»), never the raw scanner total.
- **Exit codes, not eyeballs.** A command that prints a warning and then fails still exits non-zero. Check
  `$?`/`exit_code` before writing «the config check passes» into a note — an unverified reassurance is a
  defect you will have to correct later.
- **Ambiguous links.** A bare `[[Name]]` resolves unpredictably once two notes share that filename.
  Find duplicates with `find . -name '*.md' -printf '%f\n' | sort | uniq -d` and fix by collapsing the
  duplicate note, not by rewriting every link that points at it.
- **Case-only directory twins** (`Projects/` beside `projects/`). Compare directory names
  case-insensitively; on a case-insensitive filesystem they collide. Merging is an owner decision.
- **Dashboards and health notes presented as current state.** Compare every row against live reality
  (`systemctl is-active`, `crontab -l`, `df -h`, version commands). Rows timestamped months ago are not
  current state: regenerate, or label the note «as of <date>» so nobody quotes it as today.
- **Cron and registry notes.** Diff the documented list against `crontab -l`. Documented jobs that do
  not exist and live jobs that are undocumented are both defects — the undocumented one is usually
  the newest work, and its absence from the record is the more dangerous half.
- **Duplicated rule documents.** Several docs describing one protocol (retrieval order, working
  rules) drift apart by construction. Diff them pairwise, keep one canonical document, reduce the rest
  to pointers.
- **Structure docs against the tree.** A folder map in the constitution or a README structure table
  must match `ls`: undocumented folders, described-but-absent folders, and notes orphaned in the root
  are all findings.
- **Frontmatter presence** (title/date/tags) where the convention requires it.
- **Live skills directory against its git repo.** `diff -r <live> <repo>` — content on only one side
  is lost work. Also flag archived skills still cited as live examples, and counts asserted in an index
  («~128 skills») against the real count.

## Repair recipes

Ready-to-run recipes — the dead-link classifier, the lossless skill merge, the registry recount, the
duplicate-note merge — are in `references/dead-link-and-duplicate-repair.md`. A structural fix that
silently drops content is worse than the defect it removes: absorb, never discard.

## Reporting, then fixing

- Findings with evidence and priorities first; then the fix plan, and approval before mass edits. A
  vault constitution that forbids bulk renames or migrations without approval binds you too.
- **Tier the plan and let the owner choose per tier:** ① actualize facts (dashboards, cron list,
  structure docs, one canonical host map); ② structural repair (registry consolidation, duplicate
  merges, link hygiene); ③ legacy — do not touch. Name tier ③ explicitly as *not outstanding work*: a
  large imported corpus (book notes, design dumps) without frontmatter is not a defect, and saying so
  stops the raw number from reading as a backlog.
- Ask **one question per independent decision** (which registry survives, whether to merge the
  case-twin directory, which fix groups to apply) instead of one blanket «shall I proceed».
- End by **recording** the outcome, not just fixing it: the audit note itself, a link from the relevant
  MOC, the remaining tiers in `tasks.md`, commits pushed to both the vault and the skills repo. Work not
  recorded does not survive the session.
- Never invent the correct value for a stale claim. If you cannot verify it, list it as an open
  question for the owner.
- Safe immediately: add a missing cross-link, correct a fact you just verified with a command, put an
  «as of» label on a frozen snapshot.
- Keep **procedure in the skill, facts in the vault**, and have the skill point at the vault note as
  «the live instance» (service names, ports, tokens, current persona) instead of copying values that
  change — a copied value is tomorrow's contradiction.

## Pitfalls

- A note written by an agent is not evidence. Verify with a command before repeating it; a note is
  stale the moment the live list it describes changes.
- Automated dead-link checks over-report: anchors, aliases, embedded images and plain file links are
  not notes.
- «Check that everything is current» is not approval to rewrite the vault. Audit, report, then ask.
- Two notes covering one topic are not automatically a duplicate to delete: an umbrella and its case
  study are legitimate layers. Read both before recommending a merge.
- Parallel read-only auditors overlap on shared files; that costs less than serialising them.
  Deduplicate their findings and keep the evidence, not the repetition.
- **Your own first classification is as likely to be wrong as the subagent's.** After each repair pass,
  re-run the count and correct the number in the audit note rather than leaving the old figure standing
  next to a fixed tree.
- A duplicate is resolved by **merging the unique half across**, not by picking the winner: two versions
  of one project note usually diverge into complementary halves (infrastructure and DB here, deploy and
  known-issues there). Read both, merge into the canonical one, verify the contested facts against the
  live system, then delete the twin.
