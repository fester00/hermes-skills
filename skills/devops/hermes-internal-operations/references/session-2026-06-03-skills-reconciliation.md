# Session: Skills Reconciliation (2026-06-03)

## Trigger
User asked: "А почему у угвея 80 скиллов а у гифк в профиле 95 ? Можешь проверить ?"

## Three-Layer Results

| Layer | Default (Ugwai) | Shifu Profile | Note |
|-------|-----------------|---------------|------|
| API merged (`skills_list`) | **79** | N/A (inactive) | Built-in + physical root |
| Physical `~/.hermes/skills/` | 2 (`dogfood`, `yuanbao`) | — | Only root profile |
| Physical `~/.hermes/profiles/shifu/skills/` | — | **95** | All real SKILL.md files |
| Built-in derived | 79 - 2 = **77** | 95 - 95 = **0** | — |

## MCP Obsidian Timeout

`mcp_obsidian_list_available_vaults` timed out after 120s × 3 consecutive failures.

**Fallback used:**
```bash
find /home/natan/obsidian-memory -name "*.md" | grep -iE "skill|moc"
read_file /home/natan/obsidian-memory/Operations/Skills/Hermes\ —\ Loaded\ Skills\ Reference.md
read_file /home/natan/obsidian-memory/Operations/MOC\ —\ Skills.md
read_file /home/natan/obsidian-memory/Knowledge/Technical/Hermes/Skills\ Hub.md
```

## Stale Documentation Found

Obsidian file `Hermes — Loaded Skills Reference.md` (2026-05-03) references:
- `systematic-debugging` → `~/.hermes/skills/software-development/systematic-debugging/SKILL.md` ❌ **Does not exist on disk**
- `requesting-code-review` → same path ❌ **Does not exist**

These skills were likely merged into built-ins or moved to another profile.

## Lesson
When asked about skill counts:
1. Always distinguish **merged API count** vs **physical files on disk**.
2. Built-in skills inflate API count by ~77 for default profile.
3. Named profiles only show via `find`, never via `skills_list` when inactive.
4. Obsidian docs rot. Cross-check links against disk before quoting.
5. MCP timeout → use `read_file` on vault filesystem paths directly.
