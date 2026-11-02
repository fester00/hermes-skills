---
name: content-parity-verification
description: "Use when porting: match the original's content and SEO."
version: 1.0.0
author: Hermes Agent + Natan
license: MIT
category: software-development
metadata:
  hermes:
    tags: [porting, redesign, verification, seo, parity]
    related_skills: [five-stages, pentajunior-v2-seo, verifying-live-service-changes]
---

# content-parity-verification

A port, redesign, migration or rebuild may change how a page looks and how it is built. It may not change
what the page says. This skill proves the information survived — same words, same internal links, same
prices, same meta, canonical and JSON-LD — and it tells a real loss apart from an artifact of the check.

## When to use

- a design layer is ported into a live project, or pages are rebuilt against a live site;
- the owner edited the original while the work was in flight («я внёс правки — сверься»);
- any question of the form «ссылки/мета/контент остались теми же?».

## Procedure

1. **Fix the baseline before comparing anything.** The target is the original as it is *now*.
   - If the owner changed data after your snapshot, do not compare against your own working copy — pull the
     previous state out of history: `git show <commit>^:<file> > /tmp/before`. This works for a tracked
     SQLite database too, and it is the only way to know which rows actually moved (an owner's «новые
     цены» can be ten products out of seventy-four, and a shared value will lie to you).
   - Bring the owner's commits into your feature branch before comparing (`git merge master`, then assert
     `git diff --name-only --diff-filter=U` is empty). A redesign branch that trails the original compares
     against the wrong content.
2. **Refresh the working copy from the branch, not by hand**, then rebuild and restart the server:
   `rm -rf src && git -C <repo> archive <branch> | tar -x -C <copy>`. A server left running serves the
   previous build, and every measurement after that lies — including the quiet failure where pages arrive
   with links to stylesheets that no longer exist.
3. **Compare page pair by page pair, semantically:**
   - **words** — multiset of tokens, not lines and not sentences. A moved block (a new header, a sidebar
     gone) reorders lines and makes text comparison announce losses that do not exist;
   - **links** — sets of *targets*. A static prototype links files (`catalog.html`), the live site links
     paths (`/production`); map the prototype's pages onto their twins and compare the resolved targets;
   - **prices** — the *value* before the currency sign, as a set: a name glued to the number, `&nbsp;`
     before the sign, thousands separators and a price repeated in a summary block all produce fake
     differences;
   - **meta / JSON-LD** — parse and compare as sorted sets, normalising build-time fields first: the build
     id, and dates the original computes instead of storing («today + a year» matches a static copy only on
     the day the copy was taken). Write the pattern with `\s*` after the colon (`json.dumps` prints
     `"key": "value"` with a space).
4. **Classify every difference before editing anything:** real loss / deliberate change (an approved fix,
   new design wording) / artifact of the comparison. Only real losses get fixed; the other two get named in
   the report with their reason.
5. **Fix by entity, never by value.** A blanket replace of a shared number hits rows that never changed —
   a product priced the same as the ones the owner repriced. Locate the row by name or id, edit inside it,
   then verify row by row (`name → values`) for the whole table. A name-keyed map collapses duplicates, so
   it cannot see a row you inserted twice: count the rows and the table's wrapper tags as well, and hold
   that count against the original's.
6. **Re-run the same checker and report numbers** for the owner: pages compared, words lost, links lost,
   prices equal — «проверено: 13 страниц, 0 потерянных слов, 0 потерянных ссылок». Run it yourself after
   helpers edit the pages, and add the structural count from step 5: an agent can introduce and repair a
   defect in one pass, and the comparison it ran cannot see the damage it caused.

## Pitfalls

- **A checker that reports a loss is a suspect.** When a check announces lost links or diverging content,
  ask what form each side is in before ordering rework: a difference in *syntax* (relative vs absolute
  links, a glued price token, a repeated price, an ordered list where a set belongs) looks exactly like a
  loss. Rework ordered on an artifact costs the same as rework ordered on a loss, and it corrupts pages
  that were already correct. Print the two concrete values first, then decide.
- **Count crawlable links as `<a href>` only.** A `<link rel="preconnect" href="/">` is not a link a
  crawler follows, and counting it makes the report demand markup the original never had — the quick way to
  silence that is to add a pointless tag to the page. Fix the selector, not the page.
- **Row surgery by regex must not cross a row boundary.** `<tr[^>]*>.*?</tr>` under `re.S` starts at the
  table's *first* row and its lazy `.*?` runs forward to the needle, so «copy this row» copies a chunk —
  head, wrapper tags, a dozen rows — and the file quietly gains a duplicate block. Anchor inside a row
  (`<tr[^>]*>(?:(?!</tr>).)*?NEEDLE(?:(?!</tr>).)*?</tr>`) and re-count rows and wrapper tags after.
- **A URL segment is usually a database id, and it is not always pretty.** Before «correcting» a link ask
  the server: `curl -s -o /dev/null -w '%{http_code}'` on both forms. When `/…/-9220` answers 200 and
  `/…/unisil-9220` answers 404, the odd slug *is* the canonical address; renaming it changes indexed URLs
  and needs a plan, not a cosmetic fix.
- **A row can be invented.** A prototype row whose product exists in neither the database, nor the live
  catalogue, nor the page itself (its link 404s) is fabricated content: delete the row, do not hunt for
  something real to match it to.
- **`&nbsp;` between a number and its unit defeats naive matching.** Normalise the entity before matching
  values — and never by collapsing whitespace across the whole file: line by line, or not at all.
- **Moving a link is not losing it.** A link moved from the header to the footer keeps its target but
  changes both blocks; say where it went instead of reporting a loss in one and an addition in the other.
- **A screenshot taken before lazy images load shows empty frames.** Scroll to the bottom, wait for
  `document.images.every(i => i.complete)`, then capture — otherwise a healthy gallery looks broken and
  you set off to fix nothing.
- **Anchor a count before putting it in the report.** A substring pattern matches its own renamed
  neighbours: `-9220` matches inside `unisil-9220`, so «two old addresses are still in the sitemap» came
  from the two new ones. When a number is going to the owner, print the matched lines, not just the total.
- **Compare the built output when the question is about the visitor.** Content can be assembled at build
  time; a source-level check cannot see what the page renders.
- **Deliberate differences are reported, not normalised away.** If the redesign fixed a grammar bug
  («1 товаров» → «1 товар»), the numbers stay and the difference gets named — silence about an approved
  change is as bad as silence about a loss.

## Tooling

- `scripts/parity-report.py` — page-pair comparison of word multisets, link targets and price values, with
  optional resolution of a static prototype's file links onto live paths; prints one line per page and
  writes a JSON report for the owner.

## Boundaries

- Parity is evidence for the owner, not a permission to deploy: the deploy gate is his word.
- The check needs a running build on both sides; without both, there is nothing to compare.
