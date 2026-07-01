# GitHub-Synced Obsidian Vault Setup

Set up a GitHub-synced Obsidian vault to serve as external, version-controlled memory for Hermes Agent. User can edit the same vault locally via Obsidian Desktop while the agent reads/writes on the server.

## Prerequisites

- GitHub CLI (`gh`) authenticated: `gh auth status` must show a valid user
- Git configured (if not, set identity: `git config --global user.email "..."` etc.)

---

## 1. Create the private repo on GitHub

```bash
gh repo create OWNER/REPO_NAME --private --description "External memory vault for Hermes Agent"
```

Replace `OWNER/REPO_NAME` with your username and desired repo name (e.g. `fester00/obsidian-memory`).

---

## 2. Clone it locally and set up git auth for push

**Important:** Standard `git clone https://...` may prompt for username/password in headless environments. Use `gh repo clone` instead — it uses the authenticated `gh` session:

```bash
# In home directory (or wherever you keep agent data)
cd ~
gh repo clone OWNER/REPO_NAME obsidian-memory

# If this is an empty repo, GitHub will warn you — that's expected
cd obsidian-memory
```

If plain `git push origin main` later fails with *"could not read Username for 'https://github.com'"*, run `gh auth setup-git` in the repo directory to configure the `gh` credential helper.

---

## 3. Initialize vault structure

```bash
cd ~/obsidian-memory

cat > .gitignore << 'EOF'
.DS_Store
.obsidian/workspace*
.obsidian/cache

EOF

mkdir -p Daily Projects Knowledge Scratch Templates
```

### Optional seed files

```bash
cat > README.md << 'EOF'
# Obsidian Memory Vault

External memory for Hermes Agent. Synced via GitHub.

Feel free to edit in Obsidian Desktop on your local machine.
EOF

cat > Welcome.md << 'EOF'
# 🧠 Welcome

This vault is shared between Hermes Agent (server) and you (desktop).

Use `[[Note Name]]` for wikilinks. Obsidian will build the knowledge graph.
EOF

cat > "Knowledge/MOC — Index.md" << 'EOF'
---
tags: [moc, meta, index]
---

# 🗺️ Map of Content

## 📁 Projects
- [[MOC — Projects]]

## 🏛️ Knowledge
- (populate as you go)
EOF

cat > "Projects/MOC — Projects.md" << 'EOF'
---
tags: [project, moc, index]
---

# 🗺️ MOC — Projects

Index of all projects tracked in this vault.

## Active
*(add projects here)*
EOF
```

---

## 4. Commit and push initial structure

```bash
cd ~/obsidian-memory
git add -A
git commit -m "feat: initialize obsidian vault structure"
git push origin main
```

---

## 5. Set the environment variable

Add `OBSIDIAN_VAULT_PATH` to `~/.hermes/.env` (or your agent's environment file):

```bash
echo 'OBSIDIAN_VAULT_PATH=/home/USER/obsidian-memory' >> ~/.hermes/.env
```

Restart the agent or reload the environment so the variable is picked up.

---

## 6. Verify the agent can access it

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
echo "Vault location: $VAULT"
ls "$VAULT"
cat "$VAULT/Welcome.md"
```

---

## Daily workflow (agent)

| Action | Command |
|--------|---------|
| Read a note | `cat "$VAULT/Note Name.md"` |
| Create a note | `cat > "$VAULT/Knowledge/Topic.md" << 'EOF'` |
| Commit daily | `cd "$VAULT" && git add -A && git commit -m "..." && git push origin main` |
| Pull user changes | `cd "$VAULT" && git pull origin main` |

---

## Daily workflow (user desktop)

```bash
# Clone the same repo on your computer
git clone https://github.com/OWNER/REPO_NAME.git obsidian-memory

# Open the folder as a vault in Obsidian Desktop
# Edit, create notes, use wikilinks, add tags
# Push when done:
git add . && git commit -m "user: notes update" && git push origin main
```

---

## Pitfalls

- **`git clone` fails with no device for username/password** → Use `gh repo clone` or run `gh auth setup-git`.
- **Commit fails with "Author identity unknown"** → Run `git config --global user.email "..."` and `git config --global user.name "..."`.
- **Agent can't find vault** → Check that `OBSIDIAN_VAULT_PATH` is set and the agent process has reloaded its environment.
- **Conflicts from simultaneous edits** → Treat this like any shared Git repo. The agent should `git pull` before writing if user changes are expected.
