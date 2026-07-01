# Profile Skill Sync — Command Reference

Session: 2026-07-01  
Use case: copy updated skills from default profile to `maximus` profile.

## One skill

```bash
SKILL=claude-design
SRC=~/.hermes/skills/creative/$SKILL
DST=~/.hermes/profiles/maximus/skills/creative/$SKILL

# Backup
cp -r "$DST" "$DST.bak"

# Sync
rsync -av --delete "$SRC/" "$DST/"
```

## Multiple skills in one category

```bash
PROFILE=maximus
CATEGORY=creative
SKILLS=(claude-design ui-ux-pro-max popular-web-designs)

for SKILL in "${SKILLS[@]}"; do
  SRC=~/.hermes/skills/$CATEGORY/$SKILL
  DST=~/.hermes/profiles/$PROFILE/skills/$CATEGORY/$SKILL
  [ -d "$SRC" ] || continue
  [ -d "$DST" ] && cp -r "$DST" "$DST.bak"
  rsync -av --delete "$SRC/" "$DST/"
done
```

## Verify sync

```bash
cd ~/.hermes/profiles/maximus/skills/creative
sha256sum claude-design/SKILL.md ui-ux-pro-max/SKILL.md popular-web-designs/SKILL.md
sha256sum ~/.hermes/skills/creative/claude-design/SKILL.md \
  ~/.hermes/skills/creative/ui-ux-pro-max/SKILL.md \
  ~/.hermes/skills/creative/popular-web-designs/SKILL.md
```

## Cleanup backups (after verification)

```bash
find ~/.hermes/profiles/maximus/skills -type d -name '*.bak' -exec rm -rf {} +
```

## Document in Obsidian

After sync, update:

- `~/obsidian-memory/Operations/Skills/<skill>.md`
- `~/obsidian-memory/Operations/MOC — Skills.md`
- `git add -A && git commit -m "docs(skills): sync X to maximus profile" && git push origin main`
