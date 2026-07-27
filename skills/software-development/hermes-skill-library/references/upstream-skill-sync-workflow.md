# Syncing User-Local Skills with Upstream Source Repos

Session: 2026-07-27  
Skills updated: `ui-ux-pro-max` (2.0.0 → 2.11.0), `popular-web-designs` (1.0.0 → 2.0.0)

## When to use this workflow

Use when the user asks to "check for updates" or "sync" skills that are mirrored from an external repository (e.g. `nextlevelbuilder/ui-ux-pro-max-skill`, `VoltAgent/awesome-design-md`).

## Workflow

1. **Identify upstream repo**
   - Read the skill's SKILL.md frontmatter or Hermes Implementation Notes.
   - Get the `repository` / `homepage` / source attribution.

2. **Fetch fresh upstream data without hitting GitHub API rate limits**
   ```bash
   cd /tmp
   https_proxy=http://127.0.0.1:1081 git clone --depth 1 <upstream-repo-url>.git
   ```
   Use `https_proxy=http://127.0.0.1:1081` because raw HTTPS git/curl is blocked at TLS level in this environment.

3. **Compare versions**
   - `skill.json` or upstream `README.md` will list version, counts, last push.
   - If upstream version > local version, proceed.
   - If counts changed (e.g. 54 → 74 design systems), note the delta for the catalog.

4. **Backup the local skill**
   ```bash
   cp -r ~/.hermes/skills/<category>/<skill> ~/.hermes/skills/<category>/<skill>-backup-v<old-version>
   ```

5. **Sync data files**
   - For CSV-driven skills (`ui-ux-pro-max`): replace `data/` and `data/stacks/` from upstream `src/<skill>/data/`.
   - Preserve local-only helper scripts (`scripts/*.py`) and SKILL.md prose.
   - Update `version`, `description`, and counts in frontmatter.

6. **For narrative template skills (`popular-web-designs`)**
   - Upstream may switch format. In this session upstream moved from narrative markdown to YAML-frontmatter `DESIGN.md`.
   - Convert each upstream `DESIGN.md` back into the local narrative template shape used by the skill.
   - Keep the Hermes Implementation Notes block at the top (source attribution, Google Fonts fallback, verification reminder).
   - Delete old local templates that no longer exist upstream; add new ones.
   - Update the SKILL.md catalog count and category tables.

7. **Clean stale references**
   - Deleted skills often linger in `related_skills`, runbooks, and MOCs.
   - Search the whole library:
     ```bash
     rg -n "deleted-skill-name" ~/.hermes/skills
     ```
   - Patch every remaining skill that mentions a deleted skill.
   - Common dead references to also remove: `generative-widgets` (no longer exists), project-specific deleted skills.

8. **Verify**
   - Run the skill's own scripts/searches to confirm data loads.
   - `skill_view(name="<skill>")` on the updated skill to check frontmatter still validates.
   - Ensure no broken references remain via ripgrep.

9. **Commit**
   - Commit Obsidian skill registry updates first if the user keeps one.
   - Commit local skill changes via git in the Hermes skill repo (if tracked) or note that `~/.hermes/skills/` is not a git repo.

## Pitfalls

- **GitHub API rate limits** — use `git clone --depth 1` instead of `curl` on `api.github.com`.
- **Format drift** — upstream may restructure data or change frontmatter keys. Read a few sample files before bulk-copying.
- **Proprietary fonts** — when converting upstream DESIGN.md tokens, always map custom fonts to Google Fonts substitutes in the template notes.
- **Backup before overwrite** — CSV/template bulk replace is destructive; keep a versioned backup until verification passes.
- **Don't leave dead `related_skills`** — a deleted skill referenced in `metadata.hermes.related_skills` will cause other agents to try to load a missing skill.

## Verification commands

```bash
# Check updated skill loads
hermes skills view <skill-name>

# Confirm no dead references to common deleted skills
rg -n "luxury-immersive-web|nextjs-luxury-landing-to-catalog|nextjs-product-catalog-admin|pentajunior-v2-nextjs-sqlite|generative-widgets" ~/.hermes/skills

# Confirm template count
ls ~/.hermes/skills/creative/popular-web-designs/templates/ | wc -l

# Test CSV-driven search still works
cd ~/.hermes/skills/creative/ui-ux-pro-max/scripts && python3 search.py "luxury gallery" --domain product --max-results 3
```
