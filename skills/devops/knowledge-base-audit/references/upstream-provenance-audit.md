# Auditing a skill library against the upstream repositories it derives from

## Why this is a separate scope

The four scopes in `SKILL.md` compare our records with each other and with the live host. This one
compares them with the **outside world** the library grew from: the upstream repos whose ideas were
re-implemented as local skills. The failure mode is different too — nothing is inconsistent inside our
tree; a skill is simply **older or thinner** than the source it claims to track, and the drift is
invisible until someone reads the upstream again.

## Procedure

1. **Collect the source list from the owner.** The URLs they name are the scope; do not widen it on
   your own initiative.
2. **Clone shallow, locally, into one scratch directory** — one clone per source, outside the vault and
   outside the skills tree:

   ```bash
   git clone --depth 1 <url> /tmp/upstream-audit/<name>
   ```

   Local clones let the agents read without network flakiness and let you re-grep a claim yourself in
   seconds. Nothing here needs write access to the upstreams.
3. **Write one brief per source** into the scratch directory, then run one read-only agent per source in
   parallel (see the briefing rules in `SKILL.md`). Add to every brief:
   - the exact local clone path and the exact local skill path for our derivative;
   - «прочитай нашу версию целиком, не цитируй её по названию»;
   - «если гипотеза из брифа не подтверждается — опровергни её, это результат, а не провал»;
   - the report path to write to, so the finding survives a context reset.
4. **Verify, then classify.** For every load-bearing claim: `grep` the upstream for the quoted string,
   `grep` our tree for the rule said to be missing, recount any figure. Bucket the results into
   **verified** (with the quote), **refuted** (with what is actually true) and **open** (with what
   lookup would close it, and then close it).
5. **Fix in the order: correctness, then coverage, then convention.** Wrong config keys, a destructive
   default in your own workflow, an inverted priority list — those first; missing depth next; cosmetic
   wording last.
6. **Do not duplicate on import.** When the upstream has a skill we cover inside a broader local one
   (gates, umbrella), extend the local skill and write an explicit `upstream → ours` mapping instead of
   creating a parallel skill. Port as a new skill only where nothing locally covers the class.
7. **Record and trim.** Write the audit note with the three buckets and the fix plan, archive the agent
   reports, briefs and the handful of upstream files a later fix needs, add the MOC link, commit both
   repos — then delete the clones.

## What such an audit routinely finds

- Stale numbers in a derivation note («67 agents, 281 skills» against the source's own current count).
- Features of the upstream absent locally (levels/modes, a preparation step, a naming convention the
  upstream's own tooling greps for).
- Our own deliberate deviation recorded as if it were fidelity — a scope narrowed «to keep it focused»,
  which silently drops the upstream's first criterion.
- Actions we take that the upstream gates behind approval (creating a repository, an initial commit).
- Dead config blocks the wrong example was copied from — the stale snippet that seeded a wrong instruction.

## Delegated auditors in this scope

They over-report in both directions:

- **Invented duplication.** «У нас дубли kanban» → zero skills share a `name`, zero directories collide.
  Re-derive with a script over every `SKILL.md` before deleting anything.
- **Invented loss.** A rule reported as dropped turns up verbatim, same line numbers, in our file.
- **Misquoted evidence.** A benchmark figure cited in a sense the source does not support.

A claim that survives your own greps earns a place in the plan; the rest is a hypothesis that died in
review, and saying so — in the note and to the owner — is the deliverable, not an embarrassment.

## Verifying a claimed coverage

A derived skill often asserts completeness («учтены 22 правила эталона», «покрыты все пункты»). Treat that
as an unverified claim, and re-derive it in three passes:

1. **Extract both sides mechanically.** Bullet and numbered lines from the source (its `SKILL.md`, and
   the repo `README` when the skill cites a rule count — the numbers often come from there); numbered rows
   from our coverage table.
2. **Map by keyword overlap, not by reading.** Words of four characters or more, ratio of shared words
   per source item; flag everything under roughly a third as a candidate miss. This runs in seconds and
   survives language mismatch badly, so treat a flag as a question, never as a verdict.
3. **Read every flag by hand, and read the source's non-rules as well.** A source bullet list is not a
   rule list: it contains example lines (a plan-format skeleton), sample instructions written for the
   reader (a line to paste into their `AGENTS.md`), and section theses. Counting those as rules is how a
   skill ends up with an inflated number that a later audit has to correct. Report three numbers: what the
   source really holds, what we cover, what is genuinely missing.

When items are genuinely missing, port them in the source's own words before paraphrasing; the owner can
edit a faithful line, not a paraphrase he has to re-check against the source.

## Adopt, fold, or skip

The owner pays for every skill: its description sits in the context of every session, and it competes for
the triggers of the skills it overlaps. So the default for a newly discovered upstream sibling is **fold
it into the skill that already governs the class**, not a new file. Run this test before proposing a port:

| Question | What decides it |
|---|---|
| What does it do? | One-shot report, persistent mode, or a scan. A one-shot display card earns almost nothing. |
| What does it cost? | Description length (always loaded), trigger overlap with existing skills, and whether it depends on the other tool's UX (slash commands, plugin config, flag files) that does not exist here. |
| Where else could it live? | A section in the umbrella, a mode of an existing skill, or a line in a rule the umbrella already enforces. |

Folding recipe — add one section, keep it short, and make it read-only:

- state the trigger phrase the owner will actually use;
- give the exact command (and run it once to prove it works — an embedded `grep` nobody executed is a
  guess);
- fix the output format in one line so the next session reports the same shape;
- end with the honest-empty case («nothing found») so an empty run is not read as a failure.

Then clean up after the decision: grep the library for the sibling names you considered and for
`/skill-name` mentions, convert the survivors into phrase triggers, and re-verify the umbrella still loads
(YAML) after the insertion.
