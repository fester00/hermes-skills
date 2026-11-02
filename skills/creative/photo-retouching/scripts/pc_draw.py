#!/usr/bin/env python3
"""PhotoCraft draw runner: new document -> steps -> save .pcraft/.png/.jpg.
Use with a parametric generator that writes steps.json (coordinates in Python, art in the engine).

usage: pc_draw.py steps.json
steps = [{"id": "shape.create", "params": {...}}, ...]
"""
import json, subprocess, sys, time, select

CLI = "/mnt/data/artcraft/photocraft/usr/bin/photocraft-cli"
ROOT = "/mnt/data/natan-storage"
ARGS = [CLI, "mcp", "--automation-read-root", ROOT, "--automation-write-root", ROOT]
steps = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "steps.json"))
W, H = 1600, 2000
OUT = ROOT + "/photos/art/"

p = subprocess.Popen(ARGS, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, text=True, bufsize=1)
_id = [0]


def call(method, params, timeout=180):
    _id[0] += 1
    mid = _id[0]
    p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": mid, "method": method, "params": params}) + "\n")
    p.stdin.flush()
    deadline = time.time() + timeout
    while time.time() < deadline:
        r, _, _ = select.select([p.stdout], [], [], 1.0)
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


def tool(name, args, timeout=180):
    return call("tools/call", {"name": name, "arguments": args}, timeout)


# initialize first, await the reply, then initialized — batching lines races "no document open".
print("init ok:", not call("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                           "clientInfo": {"name": "draw", "version": "1"}})["isError"])
p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}) + "\n")
p.stdin.flush()

# mode/background must be lowercase/string — "RGB"/"fill" silently leaves you with no document.
print("doc_new:", tool("doc_new", {"width": W, "height": H, "mode": "rgb", "depth": 8,
                                    "background": "white", "name": "draw"})["text"][:120])

fails = []
for i, s in enumerate(steps):
    r = tool("command_run", {"id": s["id"], "params": s["params"]})
    if r["isError"]:
        fails.append((i, s["id"], r["text"][:180]))

print(f"шагов ок: {len(steps) - len(fails)} из {len(steps)}")
for f in fails[:12]:
    print("  ОШИБКА #%d %s: %s" % f)

for name, arg in (("draw.pcraft", {"path": OUT + "draw.pcraft"}),
                  ("draw.png", {"path": OUT + "draw.png", "format": "png"}),
                  ("draw.jpg", {"path": OUT + "draw.jpg", "format": "jpg", "quality": 95})):
    print("save", name, "->", tool("doc_save", arg)["text"][:140])

p.stdin.close()
try:
    p.terminate()
except Exception:
    pass
