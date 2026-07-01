# File Hosting Fallbacks

Tested 2026-06-04 during Yandex Disk upload attempts.

## Status

| Service | Max Size | Reliability | Status | Command |
|---------|----------|-------------|--------|---------|
| **litterbox.catbox.moe** | 1 GB | ✅ High | Working | `curl -F "reqtype=fileupload" -F "time=1h" -F "fileToUpload=@file.zip" https://litterbox.catbox.moe/resources/internals/api.php` |
| transfer.sh | 10 GB | ⚠️ Timeouts | Intermittent | `curl --upload-file file.zip https://transfer.sh/file.zip` |
| file.io | 100 MB | ⚠️ Timeouts | Intermittent | `curl -F "file=@file.zip" https://file.io` |
| 0x0.st | 512 MB | ❌ Disabled | **Dead** — blocked bot spam |

## Notes

- **litterbox** — best fallback for quick 1-hour transfers. Returns direct download URL.
- **transfer.sh** — fails on slow networks (>50 sec for 6MB due to rate limiting)
- **0x0.st** — permanently disabled for uploads as of mid-2026. Will "be back at some point" per their message.

## When Yandex Disk OAuth Works

Use Yandex Disk when:
- OAuth token `y0_...` is available in `~/.hermes/.env`
- File needs permanent hosting (public link)
- File > 100 MB

Fallback to litterbox when:
- No Yandex OAuth token
- Quick temporary share (< 1 hour)
- Yandex API rate limited
