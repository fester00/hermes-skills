# Mini App release checklist

## Hosting and headers

- HTTPS with a publicly trusted certificate (no self-signed, no plain IP, no http redirect the client can't follow).
- Do **not** send `X-Frame-Options: DENY` or `Content-Security-Policy: frame-ancestors 'none'` — Desktop and Web
  load the app in an iframe from `web.telegram.org` / `*.telegram.org`. If you need a CSP, allow those ancestors.
- Allow the app origin in CORS for the API; credentials mode if you use cookie sessions.
- `index.html`: `Cache-Control: no-store`. Hashed asset filenames: `Cache-Control: public, max-age=31536000, immutable`.
- Service worker: only if you know what you're doing — a stale SW is the most common "deploy didn't land" cause in
  WebViews. Version it and skip-waiting on update.

## Launch configuration

- BotFather: `/newapp` for a named Mini App (short name, title, 640×360 preview), `/setmenubutton` or `/myapps` to
  bind the entry button.
- One bot = one token = one signing key. A second environment (staging) needs its own bot, otherwise staging data
  validates against production and sessions mix.
- Deep links: document the `startapp` contract (`A-Za-z0-9_-`, ≤512) and reject unknown values before routing.
- If the app opens invoices, register the payment provider in BotFather and test with the Stars sandbox first.

## Backend

- Validate `initData` on auth **and** on money/write endpoints; enforce own session TTL.
- Reject stale `auth_date` (>15 min for a fresh launch token).
- Rate limit auth and invoice endpoints per `user.id`.
- Log `user.id`, `platform`, `version`, and `start_param` per session — the first thing you need for a bug report.
- Idempotency keys on payments and on any "claim" action: the client can retry after a network flap.

## Frontend

- `WebApp.ready()` + `expand()` on boot; skeleton until data arrives.
- Guard the bridge: `const tg = window.Telegram?.WebApp` — a plain desktop browser (and most CI browsers) has none.
- Theme from CSS vars; test light, dark and a custom Telegram theme.
- `MainButton` shown only on the route that uses it; `BackButton` mirrors your router history.
- `enableClosingConfirmation()` on forms with unsaved input.
- Bundle budget: the WebView is often a mid-range Android on mobile data — keep the first screen small, defer the rest.

## Test matrix (minimum)

| Client | What to check |
|---|---|
| Android | keyboard + viewport, safe area, back button, haptics, invoices |
| iOS | notch inset, sheet pull-down, no console available (ship an in-app debug overlay) |
| Desktop | iframe loads (frame headers), full-screen absent, external links open outside |
| Web (web.telegram.org) | session persistence, storage fallbacks |
| Cold start | first paint < 2 s on throttled 3G; `ready()` not blocked by analytics |

## Pre-release smoke

1. Fresh account that never opened the app → onboarding renders, `initData` validates.
2. Deep link with `startapp=test` → router receives the param server-side, not only client-side.
3. Reopen after 30 min → session resumes without a new `initData` round-trip.
4. Payment: invoice → pay → entitlement appears after the bot's update, not only after the client callback.
5. Deploy a new build → hard-reload inside the client shows the new version (no stale HTML).
