---
name: knowledge-base-audit
description: Use when auditing a knowledge base or skill library. Detect drift, stale facts, and mismatches across sources.
category: devops
version: 1.2.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [audit, knowledge-base, skills, repair, purge]
    related_skills: [knowledge-first-protocol, hermes-internal-operations, hermes-profile-management]
---

# Auditing a knowledge base, a skill library and a host record

## When to Use

- The user asks «проверь, чтобы записи были актуальны» — whether the vault, docs or notes are still true.
- Two sources describe the same system differently: a README structure table against the repo constitution, two registry notes with the same filename, a skill's numbers against the real count.
- Before a migration or a large rename, or after months of drift nobody watched.
- You are about to quote a dashboard, registry or agent report as fact.

When NOT to use: ordinary retrieval (see `knowledge-first-protocol`), or maintaining one known note.

## Scope split

Split the audit into four independent scopes and run one **read-only** subagent per scope in parallel:

1. **Knowledge base** — dead links, contradictions between notes, stale claims about live state.
2. **Skill library** — overlapping skills, contradictory instructions, description-format drift, live skills directory against its git repo.
3. **Host and environment** — measured reality against what the notes claim.
4. **The rule and structure documents themselves** — constitution folder map, retrieval protocol, registries.

Do scope 4 yourself while the others run: it defines what "correct" means for every other scope.

## Briefing a read-only audit subagent

Every brief must state all five:

- **read-only** — no file writes, no state-changing git commands;
- **evidence per claim** — file path with line number, or the command output that proves it;
- **structured output** — summary, then findings as *problem → evidence → proposed fix → priority*;
- **a cap** — roughly 40 items, most important first, no narrative;
- **an honest exit** — «if you cannot verify a claim, mark it uncertain and say what evidence is missing».

Child summaries are self-reports: verify the load-bearing claims yourself (open the file, run the command) before acting on them or repeating them to the user. Counts inflate predictably — a child measuring «broken links», «notes without frontmatter» or «violations» applies no exclusion classes, so its total lands two to three times the truth. Demand a **breakdown by class** in the brief instead of one total, state in the brief what must not count, and re-derive the figure with your own script before it reaches the user or a note.

## Checks that pay off

- **Dead wikilinks.** Validate every `[[...]]` against the set of note stems. Before counting anything, strip fenced code blocks **and inline code spans**: array/JSON fragments (`[[1, 2, 3]]`, `[[None]]`, `[[ndarray]]`, `[['*' for k in range(s)]]`) are code, not links, and they dominate a naive count. `[[../path/Name\|Name]]` inside a table is **valid** — the pipe is escaped for Markdown tables, so a scanner that stops at `|` reads the backslash as part of the name and reports breaks that do not exist.
- **Wikilinks to skills can never resolve.** A skill is not a note, so `[[browser-automation]]` is broken by construction no matter how many indexes use it. Classify every surviving target before reporting: live skill name (match case-insensitively; apply prefix maps or treat the entry as plain text); near-miss on a note stem → fix the typo; junk → ignore. Then publish the number as *claimed → verified* («заявлено 280, настоящих 211»), never the raw scanner total.
- **Exit codes, not eyeballs.** A command that prints a warning and then fails still exits non-zero. Check `$?`/`exit_code` before writing «the config check passes» into a note — an unverified reassurance is a defect you will have to correct later.
- **Probe a service in the scope where it is declared.** A **user** unit that is running fine answers `inactive` or `not-found` to a system-scope `systemctl is-active`. Before recording «service down», list `systemctl --user list-units --type=service --state=running`; a scope artefact written into the record is a defect you injected yourself. Full rule: `hermes-ops-devops`.
- **Ambiguous links.** A bare `[[Name]]` resolves unpredictably once two notes share that filename. Find duplicates with `find . -name '*.md' -printf '%f\n' | sort | uniq -d` and fix by collapsing the duplicate note, not by rewriting every link that points at it.
- **Case-only directory twins** (`Projects/` beside `projects/`). Compare directory names case-insensitively; on a case-insensitive filesystem they collide. Merging is an owner decision.
- **Dashboards and health notes presented as current state.** Compare every row against live reality (`systemctl is-active`, `crontab -l`, `df -h`, version commands). Rows timestamped months ago are not current state: regenerate, or label the note «as of <date>» so nobody quotes it as today.
- **Cron and registry notes.** Diff the documented list against `crontab -l`. Documented jobs that do not exist and live jobs that are undocumented are both defects — the undocumented one is usually the newest work, and its absence from the record is the more dangerous half.
- **Duplicated rule documents.** Several docs describing one protocol (retrieval order, working rules) drift apart by construction. Diff them pairwise, keep one canonical document, reduce the rest to pointers.
- **Structure docs against the tree.** A folder map in the constitution or a README structure table must match `ls`: undocumented folders, described-but-absent folders, and notes orphaned in the root are all findings.
- **Frontmatter presence** (title/date/tags) where the convention requires it.
- **Live skills directory against its git repo.** `diff -r <live> <repo>` — content on only one side is lost work. Also flag archived skills still cited as live examples, and counts asserted in an index («~128 skills») against the real count. Sync direction is one-way and additive: see recipe 5 in `references/dead-link-and-duplicate-repair.md`.
- **Search the archive and the repo before «it does not exist».** A skill or note reported missing is usually sitting in `.archive/` (local) or still live in the repo — the two trees drift apart in both directions. An archived copy of a skill that is also active is a finding in itself: a stale second source of truth nobody reconciled.
- **Reparented orphans.** Count processes whose parent is the user's `systemd --user`: servers spawned per session (MCP servers, watchers) are not reaped when their client dies and hold tens of MB each. An orphan is the one whose parent is the user manager, not a live service — kill only those.

## Auditing a library against its upstream sources

A skill library accumulates derivatives of outside repositories. When the owner asks «сверь наши навыки с их источниками», that is a fifth scope — and a different one from the four above:

- **Establish provenance by string, never by resemblance.** Grep the upstream tree for the distinctive phrases the derived skill actually uses before asserting derivation: a brief that assumes «наши knowledge-first / anti-duplication / kung-fu пришли из ECC» collapses when a grep returns zero hits. State the negative result explicitly — it is a finding («гипотеза не подтверждена»), and it stops the next session from repeating the claim.
- **Verify each claim by quotation and re-derive every number.** A delegated auditor invents duplicates that do not exist (`name` fields are unique), reports a rule as «lost» when it sits in our file word-for-word, and misquotes benchmarks. Quote the line for what you keep, and say plainly which claims you refuted.
- **Close the uncertain ones instead of parking them.** Resolve «version unknown», «is this feature real» with an authoritative lookup or a live probe; a stub tool reveals itself in its own description («graph edge creation is not implemented»). Publish three buckets: verified / refuted / open, each with its evidence.
- **Keep the distilled report, drop the bulk.** Archive the agents' reports and briefs plus only the upstream files a later fix will need into the vault; then delete the clones. Reports survive, tens of gigabytes of somebody else's history do not earn their place on disk.
- **«N rules of the source» is a claim too.** When a derived skill asserts coverage («учтены 22 правила эталона»), verify it against the source's own list: extract the source's bullets, map them to our lines by keyword overlap, then read every unmapped one by hand. A source bullet list mixes real rules with example lines and sample instructions written for the reader, so both the claimed count and a mechanical recount land wrong — publish the count you actually verified and name the rules that are genuinely absent.
- **Default to folding, not adding a sibling skill.** The owner treats a new skill as a cost: its description is loaded into every session, and it competes for the same triggers as the skills it overlaps. A capability worth a handful of lines belongs inside the existing skill that already governs the class (a debt scan into the lens that mandates the markers, a repo-wide mode into the review skill). Before adopting a sibling, read it and answer three questions — what it does, what it costs, what it overlaps — and say which of the three the owner is trading away. Foreign-ecosystem skills (Claude Code, plugin marketplaces) also carry **slash-command UX that does not exist here**: convert `/skill-name` into a phrase trigger, and delete the references the decision orphans (`/` left behind in a rule line is a dead reference exactly like a dead skill name). Port as its own skill only when nothing local covers the class and the capability is too large to fold.

Full recipe — briefing the per-source agents, verifying a claimed coverage, and the adopt/fold/skip test — `references/upstream-provenance-audit.md`.

## Repair recipes

Ready-to-run recipes — the dead-link classifier, the lossless skill merge, the registry recount, the duplicate-note merge, the additive repo sync and the bulk description sweep — are in `references/dead-link-and-duplicate-repair.md`. A structural fix that silently drops content is worse than the defect it removes: absorb, never discard.

## Deleting content across the trees

Removing a family and every mention of it («удалим эти навыки и все упоминания со всех мест») is a deletion sweep, not an audit and not a merge. Always-on rules:

- **Inventory first, and include the profile copies.** Live skills, every `profiles/<name>/skills/`, vault registries and MOCs, derived packages, memory files, runtime state (`.usage.json`, `.curator_ledger.jsonl`, `.hub/index-cache`), cron and config. Report the list before editing, and **name the profiles you will touch**: another profile is a separate contour the owner tracks on its own, so extending «everywhere» into it is something he expects to hear, not to discover afterwards.
- **Back up before the first write, and know the rollback source per tree.** Profile copies and the local `.archive/` usually have no git mirror — those are the trees you can destroy irrecoverably.
- **Never normalise whitespace on a line you edit — and never across the file.** Split indent from content and tidy only the content: collapsing spaces inside a line rewrites frontmatter indentation and silently unparses the skill, and running `re.sub(r"\s{2,}", " ", text)` over a whole document eats the newlines themselves, flattening every heading, bullet and code fence into one paragraph. Parse and validate frontmatter after every edit and write nothing when it does not load.
- **A validator must assert its match.** A check shaped `try: yaml.safe_load(m.group(1)) if m else None` reports «0 broken» while quietly skipping every file whose frontmatter block did not match — that is the worst case, not a clean one. Fail when the match is missing, and report inspected versus matched counts.
- **Prefer dropping a line to shipping a mangled one.** If the cleaned line still matches an artefact pattern (`docs//`, `(, `, `non-`), delete the line or item and list it for the owner.
- **Verify deletions by re-grepping.** A delete loop that only reports deletions leaves the tree intact and the report perfect; zero hits in the live trees is the only proof. When the owner doubts a deletion, print the backup archive's file listing (`tar tzf <backup> | head`) — the record of what came out is more convincing than a count.
- **Sweep the carriers, not only the skill files.** The skills tree is the first place the term lives, never the last: after every skill file is gone the name survives in each profile's `memories/USER.md`, in the per-profile `.skills_prompt_snapshot.json` prompt cache, in `.usage.json` keys and the curator ledger. Grep the **whole profile**, not its `skills/`, before calling a purge complete — the second pass is where the survivors are found, and finding them only because the owner asked costs trust.
- **Machine state and history stay out of scope.** `state.db`, session transcripts, `state-snapshots/`, `checkpoints/`, curator logs and git commit history hold the term forever; editing the state of a live profile risks it. Report the counts carrier by carrier, offer the purge as an explicit next step, and never read «везде» as consent to rewrite history.
- **Another tool's own installation is out of scope until the owner says so.** A purge of our notes and skills does not extend to a program's own directory — its `skills/`, agents, plugins, config. Those files *are* the live behaviour of a tool he uses, so report what you found and ask. Read the config before answering: an entry can be a phantom (declared, never installed), which is exactly the finding that decides the question for him.
- **Editing a live tool's config: back up outside its own directory, validate string-aware, roll back on failure, then run the tool once.** A `.bak` beside the file re-introduces the very string you are removing; put the copy in your own backup tree. Finish by running the tool (`<tool> models`, `--version`) to prove it still reads what you wrote — a config edit nobody verified is indistinguishable from a broken install.
- **The sweeper is a script, not a one-liner.** `scripts/dangling-ref-sweep.py` scans and cleans dead frontmatter maps and `skill_view()` calls across every library (global plus each profile), preserves indentation, validates frontmatter before writing, and can diff the result against a pristine mirror.

Full recipe, cleaner patterns and the verification triad — `references/bulk-purge-and-rollback.md`.

## Reporting, then fixing

- Findings with evidence and priorities first; then the fix plan, and approval before mass edits. A vault constitution that forbids bulk renames or migrations without approval binds you too.
- **Tier the plan and let the owner choose per tier:** ① actualize facts (dashboards, cron list, structure docs, one canonical host map); ② structural repair (registry consolidation, duplicate merges, link hygiene); ③ legacy — do not touch. Name tier ③ explicitly as *not outstanding work*: a large imported corpus (book notes, design dumps) without frontmatter is not a defect, and saying so stops the raw number from reading as a backlog.
- Ask **one question per independent decision** (which registry survives, whether to merge the case-twin directory, which fix groups to apply) instead of one blanket «shall I proceed».
- End by **recording** the outcome, not just fixing it: the audit note itself, a link from the relevant MOC, the remaining tiers in `tasks.md`, commits pushed to both the vault and the skills repo. Work not recorded does not survive the session.
- Never invent the correct value for a stale claim. If you cannot verify it, list it as an open question for the owner.
- Safe immediately: add a missing cross-link, correct a fact you just verified with a command, put an «as of» label on a frozen snapshot.
- Keep **procedure in the skill, facts in the vault**, and have the skill point at the vault note as «the live instance» (service names, ports, tokens, current persona) instead of copying values that change — a copied value is tomorrow's contradiction.

## Pitfalls

- A note written by an agent is not evidence. Verify with a command before repeating it; a note is stale the moment the live list it describes changes.
- Automated dead-link checks over-report: anchors, aliases, embedded images and plain file links are not notes.
- «Check that everything is current» is not approval to rewrite the vault. Audit, report, then ask.
- Two notes covering one topic are not automatically a duplicate to delete: an umbrella and its case study are legitimate layers. Read both before recommending a merge.
- Parallel read-only auditors overlap on shared files; that costs less than serialising them. Deduplicate their findings and keep the evidence, not the repetition.
- **Your own first classification is as likely to be wrong as the subagent's.** After each repair pass, re-run the count and correct the number in the audit note rather than leaving the old figure standing next to a fixed tree. When a check of yours put a wrong fact into the record, add a short «corrections to this report» section naming it: a reader who spots one uncorrected claim stops trusting the rest.
- A duplicate is resolved by **merging the unique half across**, not by picking the winner: two versions of one project note usually diverge into complementary halves (infrastructure and DB here, deploy and known-issues there). Read both, merge into the canonical one, verify the contested facts against the live system, then delete the twin.
- **A bulk pass that reports success is not a verified pass.** Read back one changed file in full after the run, not just the diff of the lines you meant to touch: cross-line regexes and structure guards only surface their damage when something downstream refuses the file. When a structure guard rejects a write, believe it and inspect the file — that is the signal, not an obstacle.
- **A guard that skips what it cannot parse reports success on exactly the damaged files.** A frontmatter check written as «if the regex matches, parse it» keeps returning clean after a collapse: the flattened file no longer matches the pattern, so it drops into the skipped set while the count of valid files stays the same. Make the guard compare *files seen* against *files validated* and fail on the difference, and re-run it over the whole tree after every bulk pass — not only on the files the pass touched.
