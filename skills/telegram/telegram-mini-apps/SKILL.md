---
name: telegram-mini-apps
description: Use when building a Telegram Mini App (web app in Telegram).
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [telegram, mini-app, webapp, bots, initdata, webview]
    homepage: https://core.telegram.org/bots/webapps
---

# Telegram Mini Apps

A Mini App is an ordinary HTTPS web page opened inside the Telegram client: Android/iOS use a native WebView,
Desktop and Web use an **iframe**. There is no Telegram-specific framework — the only difference from a normal
site is the JS bridge (`window.Telegram.WebApp`) and the signed `initData` the client injects.

A Mini App always hangs off a **bot**: the bot owns the launch entry points, the signature key (`initData` is
signed with the bot token) and the payments.

## When to Use

- The user asks for a "site/app inside Telegram", a Mini App / Web App, a Telegram shop or game,
  web-based checkout inside a bot, or a webview page opened from a bot button.
- Debugging an existing Mini App: blank page on Desktop, `hash` validation failure, `initData` ignored,
  lost session, broken layout under the notch, stale build after deploy.
- Choosing between a Mini App and a lighter option (a plain link with preview, a Telegraph page, a bot
  conversation with inline buttons) — Mini Apps buy interactivity, auth and payments, and cost a web deploy.

## Architecture

```
Bot (token) ──► entry point (menu button | inline web_app | t.me/<bot>?startapp=…)
                    │
                    ▼
        WebView / iframe  ──►  your SPA  ──WebApp bridge──►  client APIs (theme, buttons, storage, payments)
                    │
                    ▼  initData (query string, HMAC-signed with bot token)
              your backend  ──► validate signature ──► own session (JWT/cookie) ──► Bot API
```

## Launch wiring (pick per use case)

| Entry point | How | Since |
|---|---|---|
| Menu button | BotFather `/setmenubutton`, or Bot API `setChatMenuButton({menu_button:{type:'web_app',text,web_app:{url}}})` | Bot API 6.0 |
| Inline `web_app` button | message `reply_markup` → `inline_keyboard` → button `{text, web_app:{url}}` | 6.0 |
| Direct link | `https://t.me/<botusername>?startapp=<param>` — opens the bot's **main** Mini App in the current chat | 6.7 |
| Inline query result | `answerWebAppQuery` to send the result back and close the app | 6.7 |
| Attachment menu | bot added to the attachment menu (groups too) | 6.1 |
| Home-screen shortcut | `WebApp.addToHomeScreen()` / `checkHomeScreenStatus()` | 8.0 |

- `startapp` value arrives as `initData.start_param` **and** as the `tgWebAppStartParam` GET parameter. Allowed
  chars `A-Za-z0-9_-`, max 512 — validate the shape server-side before using it as a key/router.
- The URL must be **HTTPS** with a valid certificate; self-signed is rejected. The domain is bound to the bot
  through BotFather (`/newapp`, `/myapps`) — that also enables the app in search and the Apps tab.

## Auth: never trust the client

Two fields matter:

- `Telegram.WebApp.initData` — raw query string, **the only thing you send to the backend**.
- `Telegram.WebApp.initDataUnsafe` — parsed object, for UI only. Treat as user-editable text.

Algorithm (documented form):

```
data_check_string = all fields sorted alphabetically, "key=value", joined by "\n", excluding hash
secret_key       = HMAC_SHA256(key="WebAppData", msg=<bot_token>)   # key is the string, msg is the token
valid            = hex(HMAC_SHA256(key=secret_key, msg=data_check_string)) == hash
```

Plus an `auth_date` (unix ts) staleness check — the hash itself never expires.

Working implementations (stdlib Python, FastAPI/aiogram, Node), the Ed25519 third-party variant, and the
"exchange initData for your own session" pattern: `references/initdata-validation.md`.

**Do not** invent workarounds (`initDataUnsafe.user.id` trust, referer checks, User-Agent sniffing). The HMAC is
the whole security model.

## Bridge surface (what you actually use)

Grouped summary with Bot API versions: `references/webapp-api-cheatsheet.md`. The essentials:

- Lifecycle: `ready()`, `expand()`, `close()`, `isExpanded`, `viewportHeight` / `viewportStableHeight`,
  events `viewportChanged`, `themeChanged`, `activated` / `deactivated`.
- Chrome: `MainButton` (text/color/progress/onClick), `BackButton`, `SettingsButton`, `SecondaryButton`,
  `showAlert` / `showConfirm` / `showPopup` (native `alert()`/`confirm()` are unreliable in a WebView),
  `enableClosingConfirmation()`, `HapticFeedback`, `openLink(url, {try_instant_view})`.
- Layout: `themeParams` + CSS variables `var(--tg-theme-*)`, `colorScheme`, `safeAreaInset`,
  `contentSafeAreaInset`, `requestFullscreen()` / `exitFullscreen()` (8.0+), `isFullscreen`.
- Storage (never rely on `localStorage` here — it can be wiped):
  - `CloudStorage` — 1024 items per user, key 1–128 chars (`A-Za-z0-9_-`), value 0–4096 chars, synced across devices.
  - `DeviceStorage` — 5 MB per user per bot, local (Bot API 9.0+).
  - `SecureStorage` — 10 items per user, iOS Keychain / Android Keystore (9.0+).
- Payments: bot-side `createInvoiceLink` → client `openInvoice(link, cb)`; Telegram Stars works for digital goods.
- Sharing / social: `shareMessage`, `switchInlineQuery`, `readTextFromClipboard`, `showScanQrPopup`,
  `requestContact`, `requestWriteAccess`.
- Platform: `platform` (`android|ios|tdesktop|web|…`), `version` (Bot API version of the **client**, gate features on it),
  `isVersionAtLeast()`, `isPremium`.

## Layout and styling rules that bite

- Start every app with `WebApp.ready()` then `expand()`; without `ready()` the client keeps a loading state and
  the viewport height can be wrong for a frame.
- Size by `viewportStableHeight` (stable across the keyboard/panel) and pad for `safeAreaInset` /
  `contentSafeAreaInset` — otherwise content slides under the notch and the pull-down sheet.
- Colours only from `themeParams` / `var(--tg-theme-*)`; hard-coded palettes break in custom Telegram themes.
- Desktop is an iframe: full-screen, haptics and biometrics are unavailable or degraded there. Branch on
  `platform`, never assume mobile.

## Common failure modes

- **`hash` mismatch on the backend** — wrong secret derivation (HMAC arguments swapped, `WebAppData` used as
  message instead of key), or fields re-serialised/normalised before hashing. Hash the raw key/value strings as
  received; only `hash` is excluded.
- **Works on mobile, blank on Desktop** — an API missing in the iframe (full-screen, biometrics) or a CSP / frame
  header (`X-Frame-Options: DENY`, `frame-ancestors`) blocking the iframe. Telegram cannot load a page that
  refuses framing.
- **Stale build after deploy** — WebView caches aggressively. Version asset filenames, serve `index.html` with
  `Cache-Control: no-store`, keep the SPA shell small.
- **Session lost on every open** — the app must exchange `initData` for a cookie/JWT; `initData` itself is
  re-issued per launch and must not be stored as the session.
- **Buttons not visible** — `MainButton`/`BackButton` need `show()` and are drawn by the client outside the DOM;
  they don't respond to CSS. Hide them (`hide()`) on routes where they don't apply, or the app looks broken.
- **`startapp` deep link does nothing** — the parameter is only delivered when opening the bot's **main** app
  (BotFather `/newapp` short name), not an arbitrary `web_app` URL.
- **Debugging**: inject `eruda`/`vConsole` behind a `?debug=1` flag; Android can be inspected with
  `chrome://inspect` on a USB-connected device. There is no console for iOS.

Release checklist (hosting, headers, caching, test matrix per platform, payments):
`references/deployment-checklist.md`.

## Local development loop

1. Any HTTPS tunnel in front of the dev server (Telegram rejects http and plain IPs).
2. Open through the real client — a desktop browser without the bridge has no `window.Telegram`, so guard code with
   `window.Telegram?.WebApp?.initData` and provide a dev fallback user.
3. Validate `initData` on every backend call that can spend money or change data — not only on `/auth`.
4. Keep the real bot token in server-side `.env` only; the frontend never needs it.
