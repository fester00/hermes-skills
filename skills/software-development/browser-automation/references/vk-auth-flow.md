# VK ID Auth Flow — Browser Automation Reference

Reference for automating VK (vk.com) login and auth state verification via browser tools.

---

## Page Architecture

VK uses a **cross-origin iframe** for authentication:

- **Outer page:** `https://vk.com/` — landing page, search bar, "Вход ВКонтакте" heading
- **Auth iframe:** `id.vk.com` embedded in outer page — shows QR code + login form
- **Direct auth URL:** `https://id.vk.com/auth?app_id=7913379&v=1.68.0&...` — standalone auth flow

```
vk.com (outer frame)
  └── iframe: id.vk.com/qr_auth?...
        └── VK ID auth UI (QR code, phone input, password form)
```

**Critical implication:** `browser_click` and `browser_type` with refs from the outer page snapshot **do NOT work** on iframe elements. The iframe elements are not included in the outer-page accessibility tree. Refs from `vk.com` snapshot are for outer-page elements only.

---

## Flow (Browser Automation Path)

### Step 1: Navigate to VK
```
browser_navigate → https://vk.com/
```

Outer snapshot shows:
- `e11` — searchbox "Поиск ВКонтакте"
- `e14` — heading "Вход ВКонтакте"
- `e16` — button "Войти другим способом" (outer page, NOT in iframe — this ref does not target the iframe button)
- `e13` — `Iframe` node (child frame indicator only)

### Step 2: Access iframe via CDP

**Option A — Navigate to iframe src directly (simpler):**
```
browser_navigate → https://id.vk.com/auth?app_id=7913379&origin=https%3A%2F%2Fvk.com
```

**Option B — Interact with iframe in place via `browser_cdp`:**
```json
{
  "method": "Runtime.evaluate",
  "frame_id": "A3FC1AD24772ED15D6D54CD9415BB18A",
  "params": {
    "expression": "(() => { const btns = document.querySelectorAll('button'); for (let b of btns) { if (b.textContent.includes('другим')) { b.click(); return 'clicked'; } } return 'no button'; })()"
  }
}
```

Get child `frame_id` from `browser_snapshot` → `frame_tree.children[].frame_id`.

### Step 3: Phone input form (on id.vk.com/auth)

After clicking "Войти другим способом", the iframe shows:

| Element | Type | Notes |
|---------|------|-------|
| Textbox with `+7` prefix | `phone` input | Type 10 digits without country code |
| "Страна или код" | dropdown | Usually Russia (+7) preselected |
| "Продолжить" | submit button | Disabled until 10 digits entered |
| "Назад" | button | Returns to QR code view |

```
// Type phone (without +7 prefix)
browser_type(ref=textbox, text="9773134407")

// Re-snapshot to verify button is no longer [disabled]
browser_snapshot

// Click Continue
browser_click(ref=continue_button)
```

### Step 4: QR confirmation (hard stop for automation)

After phone/password entry, VK may redirect to QR confirmation:
- Large QR code centered on page
- Instruction: "Наведите камеру устройства на QR-код"
- No SMS code input — requires scanning with phone app

**Agent cannot proceed.** Options:
1. Capture screenshot → ask user to scan (manual intervention)
2. Abort → recommend VK API alternative (see below)

---

## Cookie Analysis — Auth State Verification

VK sets many cookies. Most are **tracking/preference**, not auth. Key distinction:

| Cookie | Type | Presence = Logged In? | Description |
|--------|------|----------------------|-------------|
| `_ga`, `_ym_*` | Tracking | No | Google Analytics / Яндекс.Метрика |
| `remixscreen_*` | Preference | No | Screen resolution, zoom, orient |
| `remixcolor_scheme_mode`, `remixdark_color_scheme` | Preference | No | Light/dark theme |
| `remixlang` | Preference | No | Language code (0 = ru) |
| `remixrefkey`, `remixua`, `remixgp` | Tracking | No | Referral, UA fingerprint, group |
| `remixstlid`, `remixstid` | Session | No | Session tracking IDs (NOT login session) |
| `remixsf`, `remixdt` | Feature | No | Search/filter, device type flags |
| `remixcurr_audio` | State | No | Audio player state |
| `remixseenads` | Ads | No | Ad impression counter |
| `remixpuad` | Unknown | No | Some user/device fingerprint |
| **`remixsid`** | **Auth** | **Yes** | **Main VK login session token. Present only after successful auth.** |
| `remixusid` | Auth | No (supplementary) | User identity token |
| `remixttpid` | Auth | No (supplementary) | Device trust token (after 2FA/device confirmation) |

**Verification:** `document.cookie.includes('remixsid=')` → true means authenticated.

**Pitfall:** Users often copy "all cookies from browser" thinking it enables auth. Without `remixsid`, VK sees an anonymous visitor. Always verify auth state by checking for `remixsid` before assuming automation can proceed as logged-in user.

---

## Anti-Bot & Detection

- **Without residential proxies:** VK's anti-bot is aggressive. `browser_navigate` shows warning: "Running WITHOUT residential proxies. Bot detection may be more aggressive."
- **CDP override:** Hermes applies `cdp_override` stealth features automatically
- **Headless detection:** VK may block headless Chrome. If `browser_navigate` to `id.vk.com/auth` returns error/block page, try launching Chrome with `--user-agent` override
- **IP reputation:** Residential/mobile IPs fare better than datacenter IPs

---

## Recommended Alternative: VK API

For reliable VK automation, use the official API instead of browser scraping:

**Setup:**
1. Go to https://dev.vk.com/apps → "Создать приложение"
2. Choose "Standalone-приложение"
3. Get `app_id` and `client_secret`
4. Request `access_token` with needed `scope` (permissions)

**Token acquisition (implicit flow for standalone):**
```
https://oauth.vk.com/authorize?client_id=APP_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends,wall,groups,photos&response_type=token
```

**API call:**
```bash
curl "https://api.vk.com/method/wall.get?owner_id=GROUP_ID&count=10&access_token=TOKEN&v=5.199"
```

**Advantages over browser automation:**
- No anti-bot detection
- Not affected by UI redesigns
- Structured JSON responses
- Stable selectors (API fields, not DOM refs)
- Works from headless server without Chrome

**Limitation:** Some user-facing features (e.g. feed algorithm, certain UI actions) have no API equivalent. Browser automation still needed for those.

---

## Session-Specific Observations

### May 2026 session notes
- `browser_click(ref=e16)` on outer page for "Войти другим способом" did not change iframe content
- `browser_cdp` with `Runtime.evaluate` on child `frame_id` successfully clicked the button inside the iframe
- Direct navigation to `id.vk.com/auth` returned VK ID block page — site-level restriction, not form
- QR-first design is default; password form requires explicit click-through
