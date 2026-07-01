# Skill Profile Synchronization Between Hermes Profiles

**Trigger:** User notices skill count discrepancy between profiles (e.g., `default` shows 79, `shifu` shows 95), or asks to consolidate skills from a secondary profile into the default one.

**Core principle:** Profiles under `~/.hermes/profiles/<name>/skills/` are isolated trees. The default profile's built-in skills live in code, while its disk skills live in `~/.hermes/skills/`. Shifu profile skills live in `~/.hermes/profiles/shifu/skills/`. When syncing, **never overwrite** — always check for existing files first.

---

## Step-by-Step Sync Procedure

### 1. Inventory Both Profiles

```python
import os

# Default: built-in + disk
# Built-in count from skills_list API
default_builtin = 79  # or query dynamically

# Default: physical files on disk
default_dir = os.path.expanduser("~/.hermes/skills")
default_physical = []
for root, dirs, files in os.walk(default_dir):
    if "SKILL.md" in files:
        rel = os.path.relpath(root, default_dir)
        default_physical.append(rel)

# Shifu: all physical
shifu_dir = os.path.expanduser("~/.hermes/profiles/shifu/skills")
shifu_skills = []
for root, dirs, files in os.walk(shifu_dir):
    if "SKILL.md" in files:
        rel = os.path.relpath(root, shifu_dir)
        shifu_skills.append(rel)

print(f"Default: {len(default_physical)} physical + {default_builtin} built-in")
print(f"Shifu: {len(shifu_skills)} physical")
```

### 2. Build the Diff (Name-Based, Not Path-Based)

Names matter more than paths. Two profiles may nest the same skill under different categories (e.g., `github/github-auth` vs `software-development/github-auth`).

```python
default_names = set()
for p in default_physical:
    default_names.add(os.path.basename(p))

shifu_names = set()
for p in shifu_skills:
    shifu_names.add(os.path.basename(p))

only_in_shifu = shifu_names - default_names
only_in_default = default_names - shifu_names
common = default_names & shifu_names

print(f"Only in shifu: {len(only_in_shifu)}")
print(f"Only in default: {len(only_in_default)}")
print(f"Common (already synced): {len(common)}")
```

### 3. Resolve Common Skills — Skip, Don't Overwrite

For skills present in **both** profiles:
- **Do NOT blindly overwrite** — the default profile may have a newer version, or the shifu version may be stale.
- **Strategy:** Compare timestamps. If shifu is newer, prompt user. If default is newer (or same), **skip**.
- In this session: 7 skills were skipped because they already existed in default.

```python
import shutil

for name in common:
    # Get full paths
    default_path = [p for p in default_physical if os.path.basename(p) == name][0]
    shifu_path = [p for p in shifu_skills if os.path.basename(p) == name][0]
    
    default_mtime = os.path.getmtime(os.path.join(default_dir, default_path, "SKILL.md"))
    shifu_mtime = os.path.getmtime(os.path.join(shifu_dir, shifu_path, "SKILL.md"))
    
    if shifu_mtime > default_mtime:
        print(f"WARN: {name} is newer in shifu — review manually")
    else:
        print(f"SKIP: {name} already in default (up to date)")
```

### 4. Copy Missing Skills with Category Preservation

For skills only in shifu: copy the **entire directory tree** preserving category structure.

```python
for name in only_in_shifu:
    shifu_rel = [p for p in shifu_skills if os.path.basename(p) == name][0]
    src = os.path.join(shifu_dir, shifu_rel)
    dst = os.path.join(default_dir, shifu_rel)
    
    # Create parent categories if needed
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    
    if os.path.exists(dst):
        print(f"SKIP: {name} already exists (unexpected)")
        continue
    
    shutil.copytree(src, dst)
    print(f"COPY: {name} → {shifu_rel}")
```

### 5. Verify Post-Migration

```python
# Re-count
new_default_physical = []
for root, dirs, files in os.walk(default_dir):
    if "SKILL.md" in files:
        new_default_physical.append(os.path.relpath(root, default_dir))

print(f"Before: {len(default_physical)} | After: {len(new_default_physical)}")
print(f"Expected: {len(default_physical)} + {len(only_in_shifu)} = {len(default_physical) + len(only_in_shifu)}")
```

### 6. Update Obsidian Registry

After physical migration, update the canonical registry in Obsidian:

```bash
# Create or update:
# ~/obsidian-memory/Operations/Skills/Hermes — Skills Registry.md
```

Sections:
- **Statistics:** total unique, physical count, built-in count, archived count
- **Active by Category:** each skill with ✅ (disk) or 🔧 (built-in) marker
- **Archive:** skills in `.archive/`
- **Builtin-only:** skills that exist in `skills_list` but not on disk
- **Links:** to `MOC — Skills.md` and `Hermes — Loaded Skills Reference.md`

---

## Key Pitfalls

| Pitfall | Why it happens | Prevention |
|---------|---------------|------------|
| **Overwriting newer default skills** | Blind `cp -r` without checking | Always diff by name + compare mtimes |
| **Category misalignment** | Same skill in different categories (shifu: `github/auth`, default: `software-development/github-auth`) | Use `basename` for identity, `dirname` for placement |
| **Built-in vs physical confusion** | `skills_list` shows 79, but only 2 on disk | Remember: built-in skills are in code, not files |
| **Stale Obsidian registry** | Reference files point to skills that were moved/deleted | Update registry immediately after migration |
| **Archiving instead of deleting** | Old skills accumulate in `.archive/` | Keep `.archive/` for history, but don't count as active |
| **Profile isolation surprises** | `skill_manage(action='create')` writes to `~/.hermes/skills/` (default), not `profiles/shifu/` | Know which profile is active before creating skills |

---

## Quick One-Liner Summary

```
Inventory → Diff (by name) → Skip common → Copy missing → Verify count → Update Obsidian
```

---

## Related
- [[hermes-ops-devops/SKILL.md]] — system health, zombie cleanup, gateway diagnostics
- [[hermes-agent-skill-authoring/SKILL.md]] — creating and editing SKILL.md files
- `references/superpowers-mapping.md` — adapting external skill libraries into Hermes
