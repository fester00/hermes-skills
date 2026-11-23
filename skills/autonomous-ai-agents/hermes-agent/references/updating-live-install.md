# Updating a live Hermes install (gateway running, local patches present)

Procedure for pulling a new revision into a git-installed Hermes that is serving traffic right now and whose
checkout carries local edits. Order matters: every step exists because skipping it costs a restart loop, a
lost patch, or a half-updated fleet.

## 1. Pre-flight (read-only)

```bash
hermes update --check                 # available version on the channel
hermes update --plan                  # install kind, profiles, every running service + supervisor + restart method
git -C ~/.hermes/hermes-agent status --short   # local modifications?
git -C ~/.hermes/hermes-agent stash list
```

- Local edits are **autostashed** by the updater (`hermes-update-autostash-<timestamp>`). Without
  `--keep-stash` the stash is dropped after a successful run and the only copy of the work is gone.
- Save what you actually need as a patch **outside the checkout** before updating:
  ```bash
  mkdir -p ~/.hermes/local-patches
  git -C ~/.hermes/hermes-agent diff > ~/.hermes/local-patches/<name>.patch
  git -C ~/.hermes/hermes-agent diff <file> > ~/.hermes/local-patches/<file>.patch
  ```
  A patch outside the tree survives every update; a local commit inside it does not.
- Check whether upstream already carries the local fix — reapplying a fix that landed upstream breaks the build:
  ```bash
  git -C ~/.hermes/hermes-agent show origin/main:<file> | grep -n <symbol>
  ```
- Separate the substantive patch from cosmetic churn in the working tree (comment scrubs, formatting): carry
  only the fix forward, let the rest go — every reapplied hunk is a future update conflict.

## 2. Run the update

```bash
hermes update --yes --backup --keep-stash --no-gateway-restart
```

- `--backup` forces the full pre-update zip. **Needed when `state.db` is near the snapshot limit** (~1 GB):
  the quick snapshot silently skips an oversized DB (`⚠ Snapshot: skipping state.db … exceeds limit`), so
  the zip is the only real backup.
- `--no-gateway-restart` keeps this session usable for verification. Without it the updater drains and
  restarts the gateway *after* the current turn: the reply goes out and no further tool call can run.
- Run it as a background terminal process with completion notification — git pull plus venv sync exceeds a
  foreground timeout.
- **Trust the artifacts, not the backup line.** A run can log `⚠ Backup skipped (no files found or write
  failed); continuing update` and still leave a usable `pre-update-<ts>.incomplete.zip` plus a
  `state-snapshots/<ts>-pre-update/` directory. After such a warning, check before reporting "no backup":
  `unzip -t <zip> | tail -3` (integrity), `unzip -l <zip> | grep state.db` (the DB actually made it),
  `du -sh $HERMES_HOME/state-snapshots/*-pre-update | tail -2`, and `df -h` on the backup filesystem.

## 3. Reapply local patches

```bash
git -C ~/.hermes/hermes-agent apply --check <patch>   # must apply cleanly first
git -C ~/.hermes/hermes-agent apply <patch>
python3 -c "import ast; ast.parse(open('<file>').read())"   # syntax before any restart
```

A patch that no longer applies cleanly means the surrounding code moved: read both versions and port the
intent, never force it. Revert is `git checkout -- <file>`.

## 4. Verify before restarting

Run a read-only check (see `scripts/post-update-check.sh`): version, checkout revision and dirty count,
gateway unit state plus `MainPID` and start time, cron job count, MCP server list, and a real one-token
model call through the provider endpoint. Config values read back only prove what was written.

The shipped script **cannot be executed from inside the gateway**: its last lines print the reminder
`systemctl --user restart hermes-gateway`, and the terminal guard reads the whole referenced file, so
`bash post-update-check.sh` is refused with "command or referenced script cannot restart…". Don't fight it —
run the same commands inline (they are all read-only), or copy the script without the reminder lines. A real
model call is `timeout 150 hermes -z 'Reply with exactly: ok'` (a fresh process, therefore the new modules).

## 5. Restart — from outside, then prove it

The agent **cannot** restart or stop the gateway from inside the gateway session: the terminal guard refuses
any command whose target stops/restarts/uninstalls the gateway, and it also inspects referenced scripts — so
even `bash -n script.sh` is refused when the script stops the unit. The guard is right: SIGTERM propagates to
the command's own process tree, which would leave the units down with nobody to restart them. Do not engineer
around it (transient units, detached shells) — hand the action to the user.

- Correct path: the user sends `/restart` in chat; the gateway delivers the pending reply first, then reloads.
  A human in a separate shell uses `systemctl --user restart hermes-gateway`.
- Until that restart the process keeps serving pre-update modules and `hermes mcp list` warns about mixed
  `sys.modules`.
- Prove it from live state, not from the log alone: new `MainPID`, `ActiveEnterTimestamp` minutes old, a
  behavior only the new revision shows (e.g. the cron scheduler announcing all profiles), and one **actual
  MCP tool call** — a call returning data is the proof the MCP children reconnected.

## 6. Reclaim space in `state.db` (optional)

```bash
hermes sessions optimize-storage
```

- It refuses while any process holds `state.db` and lists the holder PIDs — the gateway and the WebUI backend
  always do. Refusing beats corrupting: rewriting the file under a live writer produces `retired state.db-wal`
  errors and an agent that rejects turns afterwards.
- Correct sequence from a shell outside Hermes: stop `hermes-webui` and `hermes-gateway` → wait until
  `fuser state.db` reports nothing → run the command → start both. The WebUI backend picks up new modules on
  that restart as a side effect.
- The agent cannot stop those units either (same guard), so deliver a script the user runs: stop both, poll
  `fuser` up to a timeout, optimize, restart, print size before/after and both unit states.
- This is housekeeping, not a fix: if the disk has room, deferring it costs nothing.
