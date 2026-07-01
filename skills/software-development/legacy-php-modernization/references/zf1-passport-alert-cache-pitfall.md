---
title: ZF1 passport alert + cache pitfall (LigaLink)
updated: 2026-06-15
---

# Passport alert not showing after deleting data in UTM5

## Symptom

After manually removing passport data from UTM5 (or after a user clears it via the cabinet form), the cabinet home page (`/user/index`) still does not show the "personal data needs updating" alert. The `/user/passport` page itself shows the warning correctly.

## Root cause

`Billing_IndexController::indexAction()` loads `userData` from `Zend_Cache` with the lifetime configured in `billing.ini` (default 120 seconds). The alert logic checks the cached `userData['passport']`, not the live UTM5 state. If the cache still holds the old passport string, `$passportAlert` stays `false`.

## Fix

1. **Invalidate the main user cache after any passport mutation.**
   In `passportAction()` (or any action that edits personal data), after the change succeeds:
   ```php
   $this->cache->remove($this->cache_basic_account);
   ```

2. **Invalidate derived cache keys if used.**
   The alert also checks `_passport_additional_params`, so remove that key too:
   ```php
   $this->cache->remove($this->cache_basic_account . '_passport_additional_params');
   ```

3. **Do not rely on cache expiration during testing.**
   When testing alerts or deletions, either wait for `cache.lifetime` or clear the `application/cache/` directory manually.

## Development workflow note: VSCode SFTP + Git

If the local project folder is synced to production via the VSCode SFTP extension with auto-upload, a `git pull` can silently overwrite production files. To keep Git-based review safe:

- Disable auto-upload in VSCode before pulling/pushing, or
- Work in a separate clone/staging copy and deploy via explicit upload step, or
- Restrict prod routes (e.g., `/user/passport`) at the web-server level while testing.
