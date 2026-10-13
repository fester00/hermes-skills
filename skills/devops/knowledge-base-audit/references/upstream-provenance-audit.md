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
