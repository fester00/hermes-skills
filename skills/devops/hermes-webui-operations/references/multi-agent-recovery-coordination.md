---
title: "WebUI recovery when multiple agents are active"
tags: [hermes, webui, systemd, multi-agent, coordination]
---

# WebUI recovery when multiple agents are active

## The hazard

Two independent agents can inspect WebUI state at nearly the same time. Because `systemctl --user status` output and the set of running `server.py` processes change second-to-second, one agent's stale read can contradict another agent's fresh read. If both agents try to "fix" the situation, the result is a ping-pong: one agent starts `hermes-webui.service`, the other kills the PID it just saw, then both restart, then one kills again.

## Correct procedure

When you are asked to recover WebUI and another agent may also be active:

1. **Take ownership.** Tell the user (or the other agent) that you are handling it and ask them not to touch WebUI until you confirm.
2. **Get fresh state yourself.** Do not trust another agent's printed PID or status.
   ```bash
   systemctl --user status hermes-webui.service --no-pager | head -5
   ss -tlnp | grep 18789
   ps aux | grep 'hermes-webui/server.py' | grep -v grep
   ```
3. **Decide on one action** based on your own read:
   - Service `active (running)` and port owned by the same PID → nothing to fix. Verify endpoints and stop.
   - Service `activating (auto-restart)` or `deactivating`, port still owned → orphan process. Use the hard-recovery sequence in SKILL.md.
   - No service and port free → start via systemd.
4. **Verify after the action** before declaring success:
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18789/health
   curl -s -o /dev/null -w "%{http_code}\n" -k https://130.255.9.9:8443/health
   ```
5. **Communicate the final state** clearly so the other agent (or the user) does not re-intervene.

## Anti-pattern: acting on another agent's stale output

If agent A printed `PID 686498` and agent B later runs `ps -f -p 686498`, that command can return nothing if the process has already exited. Agent B might conclude "the process is gone, I must start the service," while agent A may have already started a new PID. Always re-query live state with `systemctl` + `ss` before making a state-changing move.

## Anti-pattern: parallel `kill` and `start`

Never run `kill <PID>` and `systemctl start` concurrently from different agents. The kill may land on the freshly started process. Sequence the recovery in one place.
