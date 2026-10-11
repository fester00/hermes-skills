---
name: browser-use-agent
description: Use when an LLM-driven browser agent with a persistent Chrome profile is needed to handle complex pages.
category: software-development
related_skills:
  - browser-automation
---

# browser-use-agent

Use the `browser-use` Python library as an LLM-driven browser agent from the headless Linux server.

## When to use

- Task requires real browser interaction (search, extract, fill forms, click).
- Anti-bot blocks anonymous headless browsers.
- Need to reuse a persistent Chrome profile.
- Deterministic Playwright script is insufficient and LLM-driven reasoning is required.

## Setup

Environment already installed at `/mnt/data/natan-storage/browser-use`:

```bash
cd /mnt/data/natan-storage/browser-use
source .venv/bin/activate
```

Browser-use version: `0.13.7`.

Persistent Chrome profile: `/mnt/data/natan-storage/.chrome-vk-profile`.

## Working launch pattern

```bash
cd /mnt/data/natan-storage/browser-use
source .venv/bin/activate
xvfb-run -a --server-args="-screen 0 1920x1080x24" python your_task.py
```

## Python template

```python
import asyncio
from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI

async def main():
    llm = ChatOpenAI(
        model='kimi-k2.7-code:cloud',
        base_url='http://127.0.0.1:11434/v1',
        api_key='ollama',
        temperature=0.0,
    )
    browser = Browser(
        headless=False,
        user_data_dir='/mnt/data/natan-storage/.chrome-vk-profile',
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
        ],
        viewport={'width': 1920, 'height': 1080},
        chromium_sandbox=False,
    )
    agent = Agent(
        task='Your task description here',
        llm=llm,
        browser=browser,
        use_vision=True,
    )
    result = await agent.run()
    print('RESULT:', result.final_result())

if __name__ == '__main__':
    asyncio.run(main())
```

## Verified tasks

- Search `Mac mini` on ozon.ru and return top 3 options with price/quality.
- Find latest React Native docs at https://reactnative.dev and summarize current stable version.

## Common flags

| Flag | Why |
|---|---|
| `--no-sandbox` | Required on server Linux without user namespaces |
| `--disable-setuid-sandbox` | Companion to no-sandbox |
| `--disable-gpu` | Avoid GPU init errors in virtual display |
| `--disable-dev-shm-usage` | Prevent /dev/shm exhaustion |
| `--disable-blink-features=AutomationControlled` | Reduce anti-bot fingerprint |

## Pitfalls

- Local Ollama models (gemma4, minimax, kimi via proxy) can fail JSON schema parsing. `kimi-k2.7-code:cloud` via local Ollama proxy has been verified working.
- Browser profile is copied to a temp directory before launch; original profile is not mutated.
- Must run under `xvfb-run` when `headless=False` on a server without real display.
- Run from `terminal()` with the project venv, not inside Hermes `execute_code` sandbox.

## See also

- `browser-automation` skill — CDP/Playwright recipes and anti-bot patterns.
- `references/playwright-persistent-chrome-ozon-template.md` — deterministic Playwright fallback.
