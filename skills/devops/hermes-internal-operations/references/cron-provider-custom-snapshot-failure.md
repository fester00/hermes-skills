# Case study: cron job dies with `provider 'custom' resolved without credentials`

## Symptom

A weekly Hermes cron job (`mcp-update-checker`) had been succeeding for months, then one Monday:

```
Status: error
RuntimeError: provider 'custom' resolved without credentials (no endpoint or API key configured).
If this is a named custom provider, use its real name (see providers: in config.yaml).
```

The error document was delivered to the user's Telegram (the job's `deliver: origin` target).

## Triage (order that worked)

1. **Job record** — `$HERMES_HOME/cron/jobs.json`: the failing job had `provider: null` but
   `provider_snapshot: "custom"`. That asymmetry is the whole story.
2. **Execution ledger** — `$HERMES_HOME/cron/executions.db`: `status=failed`, `delivery_outcome=delivered`,
   error = the `RuntimeError`. Timestamps showed the run lasted ~1 minute: a setup failure, not a
   model timeout.
3. **Traceback** (in `cron/output/<job_id>/<ts>.md`) pointed at
   `cron/scheduler.py::_resolve_job_runtime` -> `runtime_provider.py::_raise_for_credentialless_bare_custom`.
   No LLM call had been made.
4. **Config diff** — `config.yaml` had a `config.yaml.bak.pre-set.*` backup from the day before. Diffing
   showed the user had migrated from a bare `custom` provider (with `model.base_url` at
   `http://127.0.0.1:11434/v1`) to a named `providers: ollama-launch` and cleared `model.base_url`. That
   is what turned a previously-resolvable `custom` into a dead request.

## Why it worked before and not after

`_snapshot_pin()` replays `provider_snapshot` as the requested provider so a global default change never
silently changes spend. While `model.base_url` still pointed at the local Ollama endpoint, the
local-endpoint bypass rung resolved the bare `custom` request. Clearing `model.base_url` removed that
rung, so `custom` fell through to the credentialless OpenRouter default and raised `AuthError`.

## The upstream bug

`hermes cron resnap <job>` is the documented companion for "global default changed, adopt it" — but it
reproduced the failure verbatim: it re-wrote `provider_snapshot: "custom"`.

Cause: `cron/jobs.py::_compute_provider_model_snapshots` persisted `snap["provider"]`, and
`resolve_runtime_provider()` returns the bare billing class `"custom"` for **every** named `providers:`
entry — the configured identity survives only in `requested_provider`. So **any** unpinned job on a named
custom provider gets a snapshot that can never resolve, and `resnap` cannot heal it. Hermes already has
`hermes_cli/fallback_config.py::effective_runtime_provider()` for exactly this (the docstring cites the
same bug class, #98739), but this function did not use it.

Verified still present at upstream `HEAD` (`git show HEAD:cron/jobs.py | grep -n 'provider_snapshot = str(snap.get'`).

## Fix applied

```python
# cron/jobs.py :: _compute_provider_model_snapshots
-from
 provider_snapshot = str(snap.get("provider") or "").strip().lower() or None
+to
 from hermes_cli.fallback_config import effective_runtime_provider
 provider_snapshot = str(effective_runtime_provider(None, snap) or "").strip().lower() or None
```

Then, for the live job: pin first (`hermes cron edit <id> --provider ollama-launch`) to unblock, and if the
job should stay unpinned, clear the pin with `hermes cron edit <id> --provider ""` — with the patch in
place the recomputed snapshot is the real name (`ollama-launch`).

## Verification that actually proves it

Do not stop at "jobs.json looks right". Run the **exact scheduler path**:

```python
import json
from cron.scheduler import _load_cron_job_config, _resolve_job_runtime
job = json.load(open(f"{HERMES_HOME}/cron/jobs.json"))["jobs"][0]
jc = _load_cron_job_config(job, job["id"], job["name"])
print(_resolve_job_runtime(job, job["id"], jc))   # must not raise
```

Then force a real run (`hermes cron run <id>`, synchronous) and confirm the ledger row ends
`completed` with `error: None`. In the observed case: `started 11:11:10Z -> finished 11:14:45Z`,
`delivery_outcome=delivered`, `last_status: ok`, `failure_streak: 0`, the config incident moved to
`resolved`, and `hermes cron doctor` reported no issues.

## Gotchas

- `cron doctor` still shows the old error immediately after the fix — it reads persisted `last_status`.
- The failure is pre-LLM: no tokens billed, task body never executed.
- `resnap` also moves the **model** snapshot to the current global default; re-pin a model if needed.
- Keep backups outside the git checkout (a stray `.bak` inside `hermes-agent/` shows up in `git status`
  and can block/stink up `hermes update`).
