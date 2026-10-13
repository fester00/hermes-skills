---
name: xiaozhi-esp32-voice-assistant
description: Use when deploying a xiaozhi ESP32 voice device.
version: 1.0.0
author: Master Ugwai
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [xiaozhi, esp32, voice, asr, tts, deepseek, openai-compatible]
    related_skills: [piper-tts, bridging-alice-to-own-llm, tts-selection]
---

# xiaozhi-esp32 voice assistant with your own LLM

Covers the server side, custom OpenAI-compatible providers, Russian ASR/TTS, and hardware hookup.

## When to Use

* The user has a xiaozhi / "小智" ESP32 voice device (or plans one) and wants it to talk to a specific model
  (DeepSeek, OpenRouter, a local vLLM/Ollama, OpenCode Zen Go, any OpenAI-compatible endpoint).
* The device answers in the wrong language, stays silent, or reports errors like `400 MissingSessionID`,
  `402 Insufficient account funds`, `实例化组件失败: 'X'`.
* You need to deploy `xinnan-tech/xiaozhi-esp32-server` without Docker and verify it without hardware.

## Architecture first — this saves hours

The ESP32 firmware (`78/xiaozhi-esp32`) does NOT call any LLM. It streams Opus over WebSocket to a server
(`xinnan-tech/xiaozhi-esp32-server`), which runs VAD -> ASR -> LLM -> TTS and streams Opus back.
So "connect the device to model X" always means: run the server, configure the LLM there,
then point the device at your server. Plan ASR and TTS too, or you get a silent brick.

## Point the device at your server without reflashing

Stock firmware >= 1.6.1 lets you set the OTA URL from the Wi-Fi setup page
("advanced options"): `http://<LAN-IP>:8003/xiaozhi/ota/`. The device then asks your server for
`server.websocket` and the auth token. Rebuilding with ESP-IDF (v6.0.1+) is only needed for an old firmware
or a custom wake word / board. The OTA URL and WebSocket address must be reachable from the device — a public
IP alone means nothing if the device is on another LAN.

## Config lives in `main/xiaozhi-server/data/.config.yaml`

It is DEEP-MERGED over `config.yaml` (`config/config_loader.py:merge_configs`), so keep it a small override
file and never copy the whole 1175-line default. `selected_module.<X>` picks the provider name, and the
provider's `type:` picks the file `core/providers/{llm,tts,asr,vad}/<type>.py`.

## Custom OpenAI-compatible LLM: what the stock provider cannot do

`core/providers/llm/openai/openai.py` builds `openai.OpenAI(api_key, base_url, timeout)` — no custom headers.
If the endpoint needs one (OpenCode Zen Go needs `x-opencode-session`, else HTTP 400), patch the provider to
pass `default_headers=config.get("default_headers")` and an `extra_body` from config, then set both keys in
`.config.yaml`. Keep the patch generic instead of hardcoding the vendor.

## Reasoning models go silent in a voice pipeline

The provider only reads `delta.content`; a reasoning model streams `reasoning_content` separately and can
burn the whole `max_tokens` on thinking, returning empty content = silence in the speaker. Pass the vendor's
switch (`thinking: {type: disabled}` for DeepSeek V4) through `extra_body`, and keep `max_tokens` >= 800.
The upstream only auto-disables thinking for a hardcoded domain list, so anything else needs the override.

## Language is two separate switches

The conversation language comes from `TTS.<selected>.language` — it is injected into the system prompt as
`{{language}}` (`core/utils/prompt_manager.py`). The persona comes from `prompt`. Set BOTH: a Chinese persona
plus default `Chinese` makes the model answer in Chinese even when the user speaks Russian.

## Russian ASR/TTS choices that actually work

* ASR: upstream defaults to FunASR/SenseVoice (zh/en/ja/ko only — it mangles Russian). Use `VoskASR` with
  `vosk-model-small-ru-0.22` (~45 MB) or `vosk-model-ru-0.42` (~1.8 GB). Cloud alternatives are better quality
  but need an account.
* Model downloads: `alphacephei.com` throttles to ~200 B/s from Russian networks. Pull Vosk models from the
  HuggingFace mirror `Derur/vosk-models` (`stt/ru/<model>/...`) and Piper voices from `rhasspy/piper-voices`
  (`ru/ru_RU/<voice>/medium/*`) via `huggingface_hub.snapshot_download`. GitHub release assets can also stall.
* TTS: Microsoft EdgeTTS broke in 2026-10 (old consumer endpoint 403; upstream already monkeypatches
  `edge_tts.communicate.WSS_URL` to `api.msedgeservices.com`, which is itself unreachable from some networks).
  A local Piper provider (`type: piper`) with `ru_RU-dmitri-medium` removes the dependency: the file must
  return bytes when called as `text_to_speak(text, None)` and write a file when given a path.
* Voice names are easy to get wrong: EdgeTTS uses `ru-RU-DmitryNeural` (not Dmitri); Piper uses
  `ru_RU-dmitri-medium`.

## Installing the server without Docker

Python 3.10-3.11 venv, `libopus0` + `ffmpeg` from the distro, then a lite dependency set — torch/funasr/
modelscope are only needed for FunASR, saving ~5 GB. Do not guess the full dependency list: start the server,
read `ModuleNotFoundError`/`ImportError` from its output, and install what it names (pin the package to the
version in the upstream `requirements.txt` when the error is a renamed symbol, e.g. `mcp==1.22.0`).
Model files must be in place BEFORE the first start: `WebSocketServer.__init__` initializes VAD/ASR/LLM/TTS
immediately and dies if a model path is missing.

## Verify without hardware

Speak the WebSocket protocol directly (`docs/websocket.md`): headers `Authorization`/`Protocol-Version`/
`Device-Id`/`Client-Id`, send `{"type":"hello",...}`, then `{"type":"listen","state":"start","mode":"manual"}`,
stream 60 ms Opus frames (16 kHz mono), then `listen/stop`. Print `stt`, `llm` and `tts` messages and decode the
returned Opus frames to a WAV. `http://<IP>:8003/xiaozhi/ota/` returning 200 proves the HTTP side is up.
A startup log line containing `Websocket地址是 ws://<ip>:8000/xiaozhi/v1/` means the server is ready.

## Pitfalls

* `zen/v1` and `zen/go/v1` are different services with different balances — a Go key returns 402 on plain Zen,
  and OpenCode's free tier only works inside the OpenCode client itself.
* Frame pacing matters: the server's VAD needs real-time-ish audio to detect the end of speech, so sleep ~60 ms
  between Opus frames when simulating a device.
* Editing YAML with `str.replace`/index slicing silently corrupts configs when the anchor text moved — validate
  the parsed file afterwards (`yaml.safe_load` + assert keys), or regenerate from a template.
* `run.sh --daemon` + `server.log` is enough for a first deployment; add a systemd unit once it works, and keep
  `server.auth.enabled: false` only until the device is proven, then turn it on (the token arrives via OTA).
