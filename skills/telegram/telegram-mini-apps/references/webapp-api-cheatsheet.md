# WebApp bridge cheatsheet

Version numbers are Bot API versions (the value of `WebApp.version` in the client). Gate optional UI on
`WebApp.isVersionAtLeast('9.0')` rather than on the client brand wherever possible.

## Lifecycle and viewport

| Field / method | Notes |
|---|---|
| `ready()` | Tell the client the UI is painted; call once, early |
| `expand()` | Request full available height (default since 7.6 for apps opened from a button) |
| `close()` | Close the app (`WebApp.close()`) |
| `isExpanded`, `viewportHeight`, `viewportStableHeight` | Layout off `viewportStableHeight` |
| event `viewportChanged` | Fires on keyboard/panel/sheet resize |
| `requestFullscreen()` / `exitFullscreen()` (8.0+) | Portrait and landscape full-screen; `isFullscreen`, events `fullscreenChanged`, `fullscreenFailed` |
| `isActive`, events `activated` / `deactivated` (8.0+) | Pause animations/timers when the user leaves the app |
| `enableClosingConfirmation()` / `disableClosingConfirmation()` (6.2+) | Guard unsaved form state |
| `hideKeyboard()` (9.1+) | Mobile keyboard dismissal |

## Theme and safe area

- `themeParams` → CSS vars `--tg-theme-bg-color`, `--tg-theme-text-color`, `--tg-theme-button-color`,
  `--tg-theme-secondary-bg-color`, … `colorScheme` is `light` / `dark`, event `themeChanged`.
- `safeAreaInset` / `contentSafeAreaInset` (8.0+) + events `safeAreaChanged` / `contentSafeAreaChanged`.
- `setHeaderColor()`, `setBackgroundColor()` (6.1+/6.9+) to avoid a visible seam at the top edge.

## Buttons and chrome

- `MainButton`: `setText`, `onClick`, `show`/`hide`, `enable`/`disable`, `showProgress`/`hideProgress`,
  `setParams({color,text_color,is_active,is_visible,has_shine_effect})`, `offClick` (6.7+).
- `BackButton` (6.1+): `onClick`, `show`/`hide`; event `backButtonClicked`.
- `SettingsButton` (6.1+), `SecondaryButton` (7.10+, `BottomButton` — `iconCustomEmojiId` since 9.5).
- `showPopup`, `showAlert`, `showConfirm` (6.2+); `showScanQrPopup` / `closeScanQrPopup` (6.4+).

## Data passing

- `initData` (raw, validate server-side), `initDataUnsafe` (use for UI), `start_param` (from `?startapp=`).
- `chat_type`, `chat_instance`, `chat` (6.9+/7.0+) — when launched from a group; enables shared/live experiences.
- `chat_join_request_query_id` (10.1+) — approve join requests from the app.

## Storage

| Object | Limits | Lifetime |
|---|---|---|
| `CloudStorage` (6.9+) | 1024 items/user; key 1–128 `A-Za-z0-9_-`; value 0–4096 chars | Cross-device, per bot |
| `DeviceStorage` (9.0+) | 5 MB per user per bot | Local to the device |
| `SecureStorage` (9.0+) | 10 items per user; iOS Keychain / Android Keystore | Local, encrypted; `restoreItem` for reinstall |

All three are callback-based (`setItem(key, value, cb)`, `getItem(key, cb)`) with an error-first convention —
wrap them in promises once.

## Payments and monetisation

- Bot calls `createInvoiceLink` (`currency: 'XTR'` for Stars) → app calls `openInvoice(url, status => …)`;
  event `invoiceClosed` with `status` (`paid|cancelled|failed|pending`).
- Verify the payment server-side via the bot's payment update — never trust the client callback for entitlement.
- `shareMessage` (8.0+) with `prepareMessage` for referral/sharing flows.

## Platform capabilities

| API | Mobile | Desktop/Web |
|---|---|---|
| `HapticFeedback` | yes | no-op |
| `BiometricManager` (7.2+) | yes | no |
| `LocationManager`, `Accelerometer`, `DeviceOrientation` (8.0+) | yes (permission) | no |
| `requestFullscreen` (8.0+) | yes | not supported |
| `addToHomeScreen` (8.0+) | yes | no |
| `openLink`, `openTelegramLink`, `readTextFromClipboard` | yes | yes |
| `CloudStorage`, `DeviceStorage` | yes | yes (browser storage behind it) |

Branch with `platform` (`android`, `ios`, `tdesktop`, `macos`, `web`, `weba`, `webk`) and degrade gracefully —
a feature-detected no-op is better than a thrown error.
