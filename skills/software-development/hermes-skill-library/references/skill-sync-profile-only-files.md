# Preserving Profile-Only Files During Skill Sync

When syncing a skill from the default `~/.hermes/skills/` tree into a
Hermes profile (`~/.hermes/profiles/<profile>/skills/`), the profile copy may
contain files that the source-of-truth skill does not have. A common example
is a profile-specific note such as `references/hermes-profile-isolation.md`
that explains why the skill was copied into the profile in the first place.

## Why this matters

If you run a blind `rsync -av --delete` or `cp -r source/* target/`, these
profile-only files are overwritten or deleted. They are usually lightweight
metadata that should survive future syncs.

## Recipe

```bash
SKILL=socratic-course-architect
CATEGORY=education
PROFILE=shifu
SRC="$HOME/.hermes/skills/$CATEGORY/$SKILL"
DST="$HOME/.hermes/profiles/$PROFILE/skills/$CATEGORY/$SKILL"

# 1. Backup the existing profile skill
[ -d "$DST" ] && cp -r "$DST" "$DST.bak"

# 2. Copy the updated source skill into the profile
mkdir -p "$DST"
cp -r "$SRC"/* "$DST/"

# 3. Restore any profile-only files that do not exist in the source
if [ -d "$DST.bak" ]; then
  (cd "$DST.bak" && find . -type f) | while read -r rel; do
    [ ! -e "$DST/$rel" ] && \
      mkdir -p "$(dirname "$DST/$rel")" && \
      cp "$DST.bak/$rel" "$DST/$rel"
  done
  rm -rf "$DST.bak"
fi
```

## Verification

After syncing, list both trees and confirm that profile-only files are still
present:

```bash
diff -qr "$SRC" "$DST" | grep 'Only in'
```

Any "Only in $DST" entries that are expected profile additions mean the sync
preserved them correctly.

## Example from a real sync

- Source skill `socratic-course-architect` had no
  `references/hermes-profile-isolation.md`.
- Profile `shifu` had this file from an earlier copy.
- After sync, the file remained in the profile copy because the source did
  not contain it.
