---
name: verifying-live-service-changes
description: Use when proving a live service change took effect. Verify from the real caller, not just local files or curl.
category: devops
---

# Verifying live service changes

## When to Use

- You edited code, a prompt, a template or a config file in a service that is already running.
- The behaviour "does not change" no matter what you edit, while the file on disk looks correct.
- A local `curl` succeeds but the **real caller** (device, platform, browser, mobile app) still sees
  old, wrong, or censored output.
- You are about to write "verified", "fixed" or "works" in a report.

When NOT to use: a first-time bring-up with nothing to compare against; unit-test-only changes.

## Rules, in the order they are applied

### 1. Prove the running process serves your change

```bash
systemctl show <unit> -p ActiveEnterTimestamp   # when did the live process start?
stat -c '%y %n' <changed-file>                  # when did the edit land?
```

If the process started **before** the file changed, your change is not live — no matter how correct
the file looks. Services do not watch their own source, prompts or configs unless you made them.
Never debug behaviour while a stale build is running: reload first, then re-test.

### 2. Read operator-tunable text from disk on every request

Prompts, greetings, allowlists, templates, feature masks: read them **per request**, not once in
`__init__` or at startup. Then the operator edits a text file and the next request obeys it — no
restart, no code change, no `sudo`. Cost is one small file read; the alternative is a privileged
restart for every tuning attempt. Decide this early — it removes the whole class of "the edit did
not work" reports instead of paying for it once per iteration.

### 3. Reproduce the caller's own input, at least five times

Behaviour produced by a model, a heuristic or a rate-limited third party depends on the exact input
phrasing and is **stochastic**. A pass on an input you invented proves nothing about the input the
user actually sends — theirs can fail on every attempt.

- run ≥5 trials of the **exact** input the user reports, not a paraphrase;
- count outcomes explicitly (`6/6 refusals`, `0/6`) — a count is evidence, "it worked for me" is not;
- when a result is inconsistent, suspect non-determinism before suspecting a race in your code.

### 4. Inspect every output field the caller consumes, separately

One response usually carries several output fields (display text, spoken audio text, structured
payload). A platform may censor, rewrite or drop one and leave the others intact. "The model answered
correctly" is not the same as "the user receives it correctly" — assert on the field the client
actually uses, and check the rest for divergence.

If the gap is after your service — output censored, words replaced, a beep over a term — that is
platform-side post-processing, not your logic. See
`references/platform-output-post-processing.md`.

### 5. Read your own request log before theorising

Log, per request: caller address, caller identity, session, status, elapsed ms, input and output.
That log separates cases which look identical from outside but have opposite fixes:

| Log evidence | Meaning | Fix direction |
|---|---|---|
| no entry for the attempt | the caller never reached you | endpoint, tunnel, routing, session window |
| entry with refusal / 4xx | your own guard rejected it | allowlist, token, validation |
| entry 200, wrong or stale answer | your logic ran but served stale state or unwanted content | stale build, cached config, content policy |

Log the **rejected identity value** whenever a guard fires — that is how you discover which value a
caller really sends. The same account can present a different id per surface or app; an allowlist
collected from one surface silently rejects another, and the symptom reads as "works in the console,
fails on the device".

Prefer the caller's logged latency to any probe of your own. Your probe travels a different path
than the caller's infrastructure: aggregate the elapsed times your log recorded for caller-originated
requests (median, max, how many broke the contract budget) before chasing a stall that only your
own uplink sees. An anomaly your service never logged is not the caller's problem.

### 6. Never `pkill -f <pattern>` from an agent shell

The pattern also matches the agent's own command line, so the shell kills itself mid-run (SIGTERM,
exit `-15`) and every step after that silently never runs. Resolve the target explicitly:

```bash
pkill -f "[t]oken_proxy"       # bracket trick: the pattern no longer matches itself
ss -tlnp | grep ":PORT"       # or find the owner and kill by PID
pgrep -af "[p]attern"          # inventory before acting
```

Same family as unquoted shell globs: the command you type is part of the environment it runs in.

### 7. Reload without a privileged restart when the unit is yours

If the unit runs as your own user (`User=<you>`) and has `Restart=always`, `kill <MainPID>` makes
systemd respawn it in ~3 s with the new code — no password prompt, no privileged restart.

```bash
systemctl show <unit> -p MainPID,ActiveEnterTimestamp
kill <MainPID>            # systemd brings it straight back
```

Confirm the timestamp moved, then re-run step 3. A restart is a precondition for verification, not
verification itself.

## Reporting rule

State the evidence, not the adjective: which build was live, the exact input reproduced, the trial
count, and the field inspected. Report an unverified result as unverified — a premature "verified"
costs the user a round of testing and discredits the next report.

## References

- `references/platform-output-post-processing.md` — when the caller's output differs from yours
  because the platform post-processes it (censorship, beeps, rewrites): how to prove it, and how to
  run a by-ear calibration in one round instead of five.
