#!/usr/bin/env python3
"""
Web search via direct CDP WebSocket.
Usage: python3 browser_search.py "query" [engine: duckduckgo|google] [max_results]

Connects directly to Chrome CDP, navigates to search engine, extracts results.
"""
import websocket
import json
import base64
import sys
import time
import urllib.parse
import subprocess


def get_cdp_ws_url(port=9222):
    """Get fresh CDP WebSocket URL from Chrome."""
    try:
        result = subprocess.run(
            ["curl", "-s", f"http://127.0.0.1:{port}/json/version"],
            capture_output=True, text=True, timeout=5
        )
        data = json.loads(result.stdout)
        return data.get("webSocketDebuggerUrl")
    except Exception as e:
        print(json.dumps({"error": f"Failed to get CDP URL: {e}"}, ensure_ascii=False))
        return None


def search_via_cdp(query, engine="duckduckgo", max_results=10, port=9222):
    ws_url = get_cdp_ws_url(port)
    if not ws_url:
        return {"error": "CDP_NOT_AVAILABLE", "advice": "Start Chrome with --remote-debugging-port=9222"}

    # Build search URL
    if engine == "duckduckgo":
        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    elif engine == "google":
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&gl=us&hl=en"
    else:
        return {"error": f"Unknown engine: {engine}"}

    ws = None
    try:
        ws = websocket.create_connection(ws_url, timeout=10)

        # 1. Get targets and find page target
        ws.send(json.dumps({"id": 1, "method": "Target.getTargets", "params": {}}))
        resp = ws.recv()
        msg = json.loads(resp)
        target_id = None
        for t in msg.get("result", {}).get("targetInfos", []):
            if t.get("type") == "page":
                target_id = t.get("targetId")
                break

        if not target_id:
            return {"error": "NO_PAGE_TARGET"}

        # 2. Attach to target
        ws.send(json.dumps({
            "id": 2,
            "method": "Target.attachToTarget",
            "params": {"targetId": target_id, "flatten": True}
        }))
        resp = ws.recv()
        msg = json.loads(resp)
        session_id = msg.get("params", {}).get("sessionId")

        if not session_id:
            # Try getting from result
            ws.send(json.dumps({"id": 3, "method": "Target.getTargets", "params": {}}))
            ws.recv()  # consume
            return {"error": "NO_SESSION_ID", "response": str(msg)}

        # 3. Enable page events
        ws.send(json.dumps({
            "id": 4, "method": "Page.enable", "params": {}, "sessionId": session_id
        }))
        ws.recv()

        # 4. Navigate
        ws.send(json.dumps({
            "id": 5,
            "method": "Page.navigate",
            "params": {"url": search_url},
            "sessionId": session_id
        }))
        ws.recv()  # Page.navigate response

        # 5. Wait for load (simplified: fixed sleep + check)
        time.sleep(4)

        # Wait for Page.loadEventFired
        # Just consume any pending messages
        ws.settimeout(2)
        try:
            while True:
                msg = json.loads(ws.recv())
                if msg.get("method") == "Page.loadEventFired":
                    break
        except websocket.WebSocketTimeoutException:
            pass  # timeout is fine, page probably loaded

        # 6. Extract results via Runtime.evaluate
        if engine == "duckduckgo":
            js = """
            (() => {
                const results = [];
                const links = document.querySelectorAll("a.result__a");
                const snippets = document.querySelectorAll("a.result__snippet");
                for (let i = 0; i < Math.min(links.length, """ + str(max_results) + """); i++) {
                    const a = links[i];
                    let url = a.href;
                    if (url.includes("/l/?")) {
                        const m = url.match(/uddg=([^&]+)/);
                        if (m) url = decodeURIComponent(m[1]);
                    }
                    results.push({
                        title: a.innerText.trim(),
                        url: url,
                        snippet: snippets[i] ? snippets[i].innerText.trim().substring(0, 200) : "",
                        engine: "duckduckgo"
                    });
                }
                return JSON.stringify(results);
            })()
            """
        elif engine == "google":
            js = """
            (() => {
                const results = [];
                const containers = document.querySelectorAll("div[data-ved]");
                for (const container of containers.slice(0, """ + str(max_results) + """)) {
                    const h3 = container.querySelector("h3");
                    const link = container.querySelector("a[href^='http']");
                    const spans = container.querySelectorAll("span");
                    let snippet = "";
                    for (const s of spans) {
                        const text = s.innerText;
                        if (text.length > 30 && text.length < 300) {
                            snippet = text.substring(0, 200);
                            break;
                        }
                    }
                    if (h3 && link) {
                        results.push({
                            title: h3.innerText.trim(),
                            url: link.href,
                            snippet: snippet,
                            engine: "google"
                        });
                    }
                }
                return JSON.stringify(results);
            })()
            """

        ws.send(json.dumps({
            "id": 10,
            "method": "Runtime.evaluate",
            "params": {"expression": js, "returnByValue": True},
            "sessionId": session_id
        }))
        resp = ws.recv()
        msg = json.loads(resp)

        result_value = msg.get("result", {}).get("result", {}).get("value", "[]")
        results = json.loads(result_value) if isinstance(result_value, str) else result_value

        return {
            "results": results,
            "engine": engine,
            "count": len(results),
            "query": query
        }

    except Exception as e:
        return {"error": str(type(e).__name__), "message": str(e), "query": query}
    finally:
        if ws:
            try:
                ws.close()
            except:
                pass


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "python tutorial"
    engine = sys.argv[2] if len(sys.argv) > 2 else "duckduckgo"
    max_r = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    result = search_via_cdp(query, engine, max_r)
    print(json.dumps(result, ensure_ascii=False, indent=2))
