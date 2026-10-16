---
name: hermes-profile-management
description: Use when aligning models across Hermes profiles. Mirror providers and model lists between profiles.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, profiles, config, providers, models, multi-agent, devops]
    related_skills: [hermes-agent, hermes-internal-operations, hermes-ops-devops]
triggers:
  - "port instructions to another profile"
  - "same persona in another profile"
  - "copy a skill into a profile"
  - "same models as in this profile"
  - "add models to another profile"
  - "mirror profile models"
  - "profile missing a provider"
  - "align profiles"
  - "profile config differs"
  - "can this profile use model X"
---

# Hermes Profile Management

Use this skill when the task is about the *configuration* of a Hermes profile rather than about an external project: mirroring models between profiles, adding a provider to one profile, aligning defaults, or checking which model a profile actually runs on.

## Profile anatomy

| Path | Holds |
|------|-------|
| `$HERMES_HOME/config.yaml`, `$HERMES_HOME/.env` | the default/root profile |
| `$HERMES_HOME/profiles/<name>/config.yaml`, `.env`, `auth.json` | a named profile, fully isolated |

- **Profiles do not inherit each other's `.env` or `os.environ`.** Hermes resolves env references against *that profile's own* `.env`; a miss is a miss, never another profile's value.
- **Provider keys ship as commented placeholders** in every profile `.env` (`# OPENCODE_GO_API_KEY=...`), so a bare `grep OPENCODE` "finds" a key that is not active.
- Named profiles do not appear in the active session's `skills_list`; inspect them on disk or via `hermes -p <name> ...`.
- The active/sticky profile is marked ◆ in `hermes profile list`; `hermes profile show <name>` prints its path, effective model, gateway state, skill count.

## The model surface

"The same models" is not one setting. These keys together are the model surface — mirror the ones the user asked about, and say which you changed:

| Key | Effect |
|-----|--------|
| `model.default`, `model.provider`, `model.base_url` | the model the profile actually runs on |
| `providers.<p>.models` | the list offered in the model picker |
| `providers.<p>.default_model` | per-provider fallback when no model is named |
| a whole missing `providers.<p>` block | a provider the target profile lacks (copy `name`, `api`, `default_model`, `models`) |
| `delegation.model` / `.provider` / `.base_url` | the model subagents run on; empty = inherit the main model |

`auxiliary.*` model entries are normally `auto` + `''` in every profile — check before assuming work is needed. `model.base_url: ''` and the provider's explicit `api:` URL are equivalent (the provider supplies it), so aligning them is cosmetic; do it anyway when parity was requested.

## Procedure: mirroring models between profiles

1. **Identify source and target.** Active profile from `hermes profile list` (◆); target config is `$HERMES_HOME/profiles/<name>/config.yaml`.
2. **Back up first, preserving modes** (profile configs are 0600 inside a 0700 dir, so use `cp -a`):
   ```bash
   cp -a profiles/<name>/config.yaml profiles/<name>/config.yaml.bak.$(date +%Y%m%d_%H%M%S)
   cp -a profiles/<name>/.env        profiles/<name>/.env.bak.$(date +%Y%m%d_%H%M%S)
   ```
3. **Diff before editing** to see the real scope: `diff -u profiles/<name>/config.yaml config.yaml`. Two profiles differ in far more than models (browser `cdp_url`, MCP server lists, `agent.max_turns`, checkpoint limits, personality text) — mirror only the model keys; **never `cp` one config over the other**.
4. **Edit with targeted text patches, not a YAML round-trip.** `yaml.safe_load` + `yaml.dump` reorders keys and reflows multi-line personality/text blocks. Patch each model key in place; insert an entire missing provider block as one unit.
5. **Give every newly added provider an ACTIVE key in the target profile's `.env`** (see Pitfalls) — without it the models appear in the picker and fail on first use.
6. **Verify two ways** (see below): a programmatic set comparison of both configs, plus Hermes' own view of the effective model.
7. **Report**: which keys changed, that a **new session** is required (a running session keeps its old model list), and the backup paths for a one-command revert.

## Procedure: porting instructions and persona into a profile

Instructions live in **three separate carriers**, and a profile inherits none of them:

| Carrier | File in the profile | Port with |
|---|---|---|
| Skills | `profiles/<name>/skills/<category>/<skill>/` | `cp -r $HERMES_HOME/skills/<cat>/<skill> profiles/<name>/skills/` — the global tree is *not* visible to the profile |
| Persona | `profiles/<name>/SOUL.md` | copy the root `SOUL.md` when it is meant to be identical, then `diff -q` the two |
| Personality overlay | `agent.personalities.<name>` in the profile config | `hermes --profile <name> config set agent.personalities.<name> '<text>' --force` |

1. **Snapshot first:** `cp -a` the profile's `SOUL.md` and `config.yaml` into your own backup tree (the profile dir is `0700`, files `0600`).
2. **Read what is already there before writing.** The profile may already carry the right setting — an empty `delegation.model`, for instance, already means "children inherit this profile's model", so there is nothing to port there. Report what needed no change instead of rewriting it.
3. **Write the carrier that actually wins.** `available_personalities()` merges a root `personalities` block and then `agent.personalities`, the latter winning on a name clash (`hermes_cli/personality.py` docstring) — a root-level write beside an existing `agent.personalities.<name>` is silently ignored.
4. **Config writes go through the CLI, not the file tools** (they refuse a Hermes config by design), and this nested path needs `--force`; without the flag the setter answers "Did you mean: personalities.<name>" and writes nothing.
5. **Port instructions, leave settings alone.** Model, delegation and MCP keys belong to that contour's own tuning — verify they are untouched afterwards instead of mirroring them out of habit.
6. **Verify with the profile's own eyes, then report:**
   ```bash
   hermes --profile <name> skills list | grep <skill>     # the profile sees and enables it
   diff -q $HERMES_HOME/SOUL.md profiles/<name>/SOUL.md    # when identity was the goal
   ```
   Plus: the profile's YAML still parses, the rewritten value contains the new wording and not the old, and its key count is unchanged. State the backup path and that the profile's cached skill index (`.skills_prompt_snapshot.json`) refreshes on its next session.

## Verify

```bash
# 1. Parity of the model surface, set-difference style (never eyeball 30-item lists)
$HERMES_HOME/skills/devops/hermes-profile-management/scripts/compare-profile-models.py \
    $HERMES_HOME/config.yaml $HERMES_HOME/profiles/<name>/config.yaml

# 2. What Hermes itself resolves
hermes profile list                  # Model column per profile (◆ = sticky default)
hermes -p <name> config              # effective '◆ Model' mapping, paths, secrets file
```

The script exits non-zero when the target is missing anything the source offers, so it doubles as a pre/post check. It needs PyYAML — run it with the Hermes venv interpreter if the system python lacks it.

## Pitfalls

- **A copied provider without an active key is a dead picker entry.** Profiles do not inherit another profile's `.env`; add the key line to the target's `.env`, copied from the source (never echo the value). Match the anchored active form — a commented placeholder satisfies a naive grep:
  ```bash
  grep -n '^OPENCODE_GO_API_KEY=' profiles/<name>/.env | sed -E 's/=.*/=<hidden>/'
  ```
- **Check for an editor swap file** (`..env.swp` beside `profiles/<name>/.env`) before appending: if the user has that file open in vim, your append vanishes when they save the buffer. Tell them to close the editor first.
- **Additive, not destructive.** If the target already has a picker entry the source lacks, leave it — deleting a model entry is a destructive act the user must explicitly ask for.
- **Changing `model.default` is a behavior change.** "The same models" reads as the same model surface including the default, but state the changed default explicitly so the user can revert if they only wanted the list.
- **Prefer a targeted key addition over copying a whole `.env`** between profiles: a full copy also drags unrelated secrets and can clobber profile-specific tokens.
- `hermes profile list` warns when two profiles share one Telegram bot token (a bot can belong to only one profile). Surface that warning; do not fix it unasked.
- Config and `.env` changes apply to **new** sessions; the WebUI/gateway read them at startup.
- **A profile is a separate contour: touch it only when asked, and only the part that was asked for.** Port what was requested, report everything else you noticed as "not touched" — extending the scope of a port is the fastest way to lose trust in it.
- **`hermes config set` without `--profile` writes to the ROOT profile.** Porting into a named profile while the flag is missing edits the wrong contour silently; pass `--profile <name>` on every setter call.
- **A skill copied into a profile must be verified from that profile**, not from the global tree: `hermes --profile <name> skills list`. The global `skills_list` of the active session never shows another profile's skills.

## Reporting

Answer in the user's language (Russian for this user). Lead with a small table of the changed keys (before → after), then the verification output you actually observed, then backup paths and the revert command. Flag incidental findings (shared bot tokens, stale swap files) separately as "not touched".
