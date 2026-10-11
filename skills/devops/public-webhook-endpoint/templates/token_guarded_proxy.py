#!/usr/bin/env python3
"""Secret-path edge proxy for a public webhook endpoint.

Copy and modify. Place this in front of the real service and point the tunnel/Funnel at this port
instead of the app: the secret path, caller allowlist, opening greeting, request log and the
"never leak an upstream failure" guarantee then live OUTSIDE the app, so they keep working without
editing or restarting it.

Run:
    SKILL_PATH_TOKEN=<token> uvicorn edge_proxy:app --host 127.0.0.1 --port 8788

Env:
    TARGET            upstream URL (default http://127.0.0.1:8787/alice)
    SKILL_PATH_TOKEN  required path segment; without it every request is 404
    ALLOWLIST_FILE    one allowed id per line; missing/empty file = allow all; '#' comments ok
    REQUEST_LOG       append-only request log (default /tmp/requests.log)
    UPSTREAM_TIMEOUT  keep JUST ABOVE the app's own internal budget (default 5.0, not 12)
    GREETING/REFUSAL/FILLER  texts for the opening turn, a rejected caller, an upstream failure
"""
import json
import os
import secrets
import time
from datetime import datetime

import httpx
from fastapi import FastAPI, Request, Response

TARGET = os.environ.get("TARGET", "http://127.0.0.1:8787/alice")
TOKEN = os.environ.get("SKILL_PATH_TOKEN", "")
ALLOW_FILE = os.environ.get("ALLOWLIST_FILE", ".allowlist")
REQUEST_LOG = os.environ.get("REQUEST_LOG", "/tmp/requests.log")
UPSTREAM_TIMEOUT = float(os.environ.get("UPSTREAM_TIMEOUT", "5.0"))
GREETING = os.environ.get("GREETING", "Здравствуйте! Слушаю вас.")
REFUSAL = os.environ.get("REFUSAL", "Извините, доступ закрыт.")
FILLER = os.environ.get("FILLER", "Секунду, я подумаю.")

app = FastAPI(title="edge-proxy")


def _log(line: str) -> None:
    try:
        with open(REQUEST_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def _allowed_ids() -> set[str]:
    """Empty or missing file means allow everyone; comments (#) ignored.
    Re-read per request on purpose: the list becomes fillable from a live session
    without restarting the app behind this proxy."""
    try:
        with open(ALLOW_FILE, encoding="utf-8") as f:
            return {ln.strip() for ln in f if ln.strip() and not ln.startswith("#")}
    except OSError:
        return set()


def _answer(text: str, end: bool = False) -> Response:
    """Yandex Dialogs answer shape: version + response, end_session INSIDE response.
    Swap this for the target platform's shape."""
    payload = {"version": "1.0", "response": {"text": text, "tts": text, "end_session": end}}
    return Response(content=json.dumps(payload).encode("utf-8"), media_type="application/json")


@app.get("/health")
async def health() -> dict:
    # This address is public and gets scanned in batches: answer as little as possible.
    return {"status": "ok"}


@app.post("/alice/{token}")
async def handle(token: str, request: Request) -> Response:
    # Constant-time compare: never let the token leak through timing.
    if not TOKEN or not secrets.compare_digest(token, TOKEN):
        return Response(content=b'{"error":"not found"}', status_code=404,
                        media_type="application/json")

    body = await request.body()
    try:
        data = json.loads(body or b"{}")
    except ValueError:
        data = {}
    sess = data.get("session") or {}
    req = data.get("request") or {}
    text = (req.get("original_utterance") or req.get("command") or "").strip()
    user_id = sess.get("user_id", "-")
    caller = request.headers.get("x-forwarded-for") or (
        request.client.host if request.client else "?")
    stamp = datetime.now().isoformat(timespec="seconds")

    allowed = _allowed_ids()
    if allowed and user_id not in allowed:
        _log(f"{stamp} caller={caller} user_id={user_id} status=REFUSED")
        return _answer(REFUSAL, end=True)

    # Opening turn arrives with an empty utterance: greet instead of complaining.
    if sess.get("new") and not text:
        _log(f"{stamp} caller={caller} user_id={user_id} status=200 (greeting, no upstream call)")
        return _answer(GREETING)

    started = time.perf_counter()
    try:
        # trust_env=False: never route a loopback call through HTTP_PROXY from the environment.
        async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT, trust_env=False) as client:
            upstream = await client.post(TARGET, content=body,
                                         headers={"Content-Type": "application/json"})
        content, status_code = upstream.content, upstream.status_code
    except Exception as exc:  # noqa: BLE001
        # The platform shows the caller the raw error, so a 500 (or an empty body) is the worst
        # possible answer. Reply with a contract-valid filler and log the real cause.
        ms = int((time.perf_counter() - started) * 1000)
        _log(f"{stamp} caller={caller} user_id={user_id} status=UPSTREAM_ERROR ms={ms} "
             f"error={type(exc).__name__}: {exc}")
        return _answer(FILLER)

    ms = int((time.perf_counter() - started) * 1000)
    answer = ""
    try:
        answer = (json.loads(content or b"{}").get("response") or {}).get("text", "")
    except ValueError:
        pass
    # ms= lets you check the real latency against the platform's budget from live traffic.
    _log(f"{stamp} caller={caller} user_id={user_id} status={status_code} ms={ms} "
         f"Q={text[:120]!r} A={answer[:160]!r}")

    return Response(content=content, status_code=status_code,
                    media_type="application/json")
