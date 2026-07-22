# Case Study — Evaluating upstash/context7

**Date:** 2026-07-10
**External repo:** https://github.com/upstash/context7
**Decision:** Do not integrate as MCP/dependency; build a local docs mirror strategy instead.

## What the repo offers

Context7 (58.8k stars) provides up-to-date, version-specific documentation
for libraries via an MCP server and CLI (`ctx7`). It fetches docs from an
external index and injects them into the agent context.

## Critical observation

Context7 is a **paid/external service** for live library documentation. The
value is real, but it conflicts with the local-first, self-hosted bias of
the current setup:

- Requires API key for meaningful rate limits.
- Documentation lives on an external server, not in the local knowledge base.
- No direct integration with Obsidian or the existing skill library.

## Local alternative

A **Docs Mirror** approach replaces Context7 for the libraries we actually use:

- Clone library docs from GitHub (e.g. `vercel/next.js/docs`).
- Convert to Markdown and store under
  `~/obsidian-memory/Knowledge/Technical/Libraries/<lib>/`.
- Refresh weekly with `git pull` or a cronjob.
- For docs-only-on-website libraries, use Playwright/CDP extraction.

This is free, offline-capable, and integrates with the existing Obsidian search
and skill workflow.

## What we did

The user deferred implementation, but the analysis is captured here for the
next session. Candidate first libraries for mirroring:

- Next.js 15 / React 19 (pentajunior-v2)
- vkbottle (Liga_vkBot)
- httpx (Liga_vkBot)
- better-sqlite3 (pentajunior-v2)
- Kokoro / Piper / edge-tts (TTS project)

## Lesson

When an external tool is a paid SaaS wrapper around information that can be
fetched directly, prefer a local mirror integrated with the existing
knowledge base. Only adopt the SaaS if the maintenance burden of the mirror
exceeds its value or if the index quality is materially better.
