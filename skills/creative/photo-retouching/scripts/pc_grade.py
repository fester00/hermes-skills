#!/usr/bin/env python3
"""PhotoCraft grade runner: open a file -> steps -> save -> then_steps -> second save.
One CLI process, waits for every reply, so document state is never raced.

usage: pc_grade.py job.json
job = {
  "open": "/abs/path/under/read/root.jpg",
  "steps": [{"id": "image.adjustments.levels", "params": {...}}, ...],
  "save_main": "/abs/path/main.jpg",
  "then_steps": [{"id": "filter.gallery.filmGrain", "params": {"grain": 3}}],
  "save_grain": "/abs/path/grain.jpg"
}
Both roots must sit under --automation-read-root / --automation-write-root below.
"""
import json, subprocess, sys, time, select

CLI = "/mnt/data/artcraft/photocraft/usr/bin/photocraft-cli"
ROOT = "/mnt/data/natan-storage"
ARGS = [CLI, "mcp", "--automation-read-root", ROOT, "--automation-write-root", ROOT]
job = json.load(open(sys.argv[1]))

p = subprocess.Popen(ARGS, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, text=True, bufsize=1)
_id = [0]


def call(method, params, timeout=600):
    _id[0] += 1
    mid = _id[0]
    p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": mid, "method": method, "params": params}) + "\n")
    p.stdin.flush()
    deadline = time.time() + timeout
    while time.time() < deadline:
        r, _, _ = select.select([p.stdout], [], [], 2.0)
        if not r:
            continue
        line = p.stdout.readline()
        if not line:
            break
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("id") != mid:
            continue
        if "error" in d:
            return {"isError": True, "text": json.dumps(d["error"], ensure_ascii=False)[:300]}
        res = d.get("result", {})
        c = res.get("content") or []
        text = c[0].get("text") if c and isinstance(c[0], dict) else json.dumps(res, ensure_ascii=False)
        return {"isError": bool(res.get("isError")), "text": text}
    return {"isError": True, "text": "timeout"}


def tool(name, args, timeout=600):
    return call("tools/call", {"name": name, "arguments": args}, timeout)


# initialize MUST be first and answered before notifications/initialized, else the server exits.
print("init ok:", not call("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                           "clientInfo": {"name": "grade", "version": "1"}})["isError"])
p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}) + "\n")
p.stdin.flush()

print("open:", tool("doc_open", {"path": job["open"]})["text"][:200])

fails = 0
for phase, steps in (("A", job.get("steps", [])), ("B", job.get("then_steps", []))):
    for i, s in enumerate(steps, 1):
        r = tool("command_run", {"id": s["id"], "params": s["params"]})
        print(f"  [{phase}{i:02d}] {'ok ' if not r['isError'] else 'FAIL'} {s['id']} {s['params']}"
              f"{'  ' + r['text'][:120] if r['isError'] else ''}")
        fails += bool(r["isError"])
    key = "save_main" if phase == "A" else "save_grain"
    if job.get(key):
        print(f"  save {key} ->", tool("doc_save", {"path": job[key], "format": "jpg", "quality": 96})["text"][:140])

print("ошибок:", fails)
p.stdin.close()
try:
    p.terminate()
except Exception:
    pass
