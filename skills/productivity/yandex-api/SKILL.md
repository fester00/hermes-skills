---
name: yandex-api
description: |
  Яндекс API — Диск (OAuth REST) и Почта (IMAP/SMTP через пароль приложения).
  Загрузка файлов, публичные ссылки, чтение почты через Python IMAP (рекомендуется) или Himalaya CLI.
  Для Диска требуется OAuth токен. Для Почты — пароль приложения типа «Почта» (не основной пароль!).
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [yandex, disk, mail, cloud-storage, email, imap, smtp, oauth, russia]
    related_skills: [himalaya, obsidian, russian-retail-search]
---

# Yandex API

Работа с Яндекс экосистемой: Диск (хранение файлов, публичные ссылки) и Почта (IMAP/SMTP чтение/отправка).

> ⚠️ **Критическое различие:** OAuth токен работает только для **Диска**.
> Для **Почты** нужен отдельный **пароль приложения** (генерируется в настройках Яндекс ID).

---

## 1. Yandex Disk (OAuth REST API)

### Предварительные условия

OAuth токен вида `y0_...` получен через [Яндекс OAuth](https://yandex.ru/dev/disk/poligon).

**Сохранение токена:**
```bash
echo "YANDEX_DISK_TOKEN=y0_..." >> ~/.hermes/.env
```

### Загрузка файла

```bash
TOKEN=$(grep YANDEX_DISK_TOKEN ~/.hermes/.env | cut -d= -f2)
FILE="archive.zip"
LOCAL="/tmp/$FILE"

# 1. Получить URL для загрузки
UPLOAD_URL=$(curl -s -H "Authorization: OAuth $TOKEN" \
  "https://cloud-api.yandex.net/v1/disk/resources/upload?path=app:/$FILE&overwrite=true" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['href'])")

# 2. Залить файл PUT-ом
curl -s -T "$LOCAL" "$UPLOAD_URL"

# 3. Опубликовать (публичная ссылка)
curl -s -H "Authorization: OAuth $TOKEN" -X PUT \
  "https://cloud-api.yandex.net/v1/disk/resources/publish?path=app:/$FILE"

# 4. Получить ссылку
PUB_URL=$(curl -s -H "Authorization: OAuth $TOKEN" \
  "https://cloud-api.yandex.net/v1/disk/resources?path=app:/$FILE" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('public_url','NOT_FOUND'))")

echo "Public URL: $PUB_URL"
```

### Скачивание файла

```bash
# Публичная ссылка → прямая загрузка
curl -sL -o local.zip "$PUB_URL"
```

### API ограничения

- Макс размер файла: 1 GB (бесплатно), 50 GB (платно)
- Всего места: 10 GB (бесплатно)

---

## 2. Yandex Mail (IMAP/SMTP)

### Yandex Mail App Password Types (Critical)

**Пароли приложений Яндекс имеют ТИПЫ. Тип определяет, для какого сервиса работает пароль:**

| Тип | Работает для | НЕ работает для |
|-----|-------------|-----------------|
| **Почта** | IMAP, SMTP, web-почта | Диск, API |
| **Диск** | REST API, WebDAV | IMAP, SMTP |
| **Все сервисы** | Всё (если создан до 2024) | — |

**Если IMAP возвращает `[UNAVAILABLE] LOGIN internal server error`:**
- Пароль создан для **Диска** — пересоздайте с типом **Почта**
- IMAP отключён в настройках аккаунта — включите: [mail.yandex.ru](https://mail.yandex.ru) → Настройки → Почтовые программы

**Пароли приложений показываются один раз при создании.** При повторном открытии страницы пароля они скрыты. Записывайте сразу.

> ⚠️ **Пароли могут содержать спецсимволы** (`$`, `!`, `"`, `\`` и др.), которые ломают shell-команды типа `echo "..." >> file`. Сохраняйте через `write_file` (Python/heredoc) или `printf '%s\n'`, а не bare `echo`.

### Предварительные условия

**OAuth токен НЕ работает для почты.** Нужен **пароль приложения**:

1. [id.yandex.ru/security](https://id.yandex.ru/security) → Безопасность
2. Пароли приложений → Создать пароль
3. Выбрать тип: **Почта**
4. Скопировать 16-значный код вида `xxxxxxxxxxxxxxxx`

**Сохранение пароля (safe method):**
```python
import os

env_path = os.path.expanduser("~/.hermes/.env")
# append — НЕ перезаписывает существующие переменные
with open(env_path, "a") as f:
    f.write("YANDEX_MAIL_APP_PASSWORD=your_app_password\n")
    f.write("YANDEX_MAIL_USER=your_login@yandex.ru\n")
```

⚠️ **НЕ используйте** `echo "..." >> ~/.hermes/.env` — спецсимволы (`$`, `"`, `\``) в пароле сломают запись.

**Чтение пароля из .env (safe method):**
```python
with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        if line.startswith("YANDEX_MAIL_APP_PASSWORD="):
            password = line.strip().split("=", 1)[1]
            break
```

⚠️ **НЕ используйте** `grep ... | cut -d= -f2` — пароли с `=` внутри обрезаются неправильно.

### Чтение почты — варианты

#### A) Himalaya CLI (не рекомендуется в headless/non-TTY)

Установка:
```bash
curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh
```

**Проблемы v1.2.0 (обнаружено 2026-06-04):**
- Конфиг v1.2 требует `auth.type = "password"` + `auth.raw = "..."`, старый `password.cmd` не работает
- `himalaya account configure` — wizard требует TTY, падает с `cannot prompt boolean` в headless
- Воспользуйтесь **Python IMAP** (вариант B) — надёжнее и проще

#### B) Python IMAP (рекомендуется)

```python
import imaplib, ssl

with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        if line.startswith("YANDEX_MAIL_APP_PASSWORD="):
            password = line.strip().split("=", 1)[1]

conn = imaplib.IMAP4_SSL("imap.yandex.ru", 993, ssl_context=ssl.create_default_context())
conn.login("your_login@yandex.ru", password)  # пароль приложения
conn.select("INBOX")
status, messages = conn.search(None, "ALL")
# ... обработка писем
conn.logout()
```

**Если получаете `[AUTHENTICATIONFAILED] LOGIN invalid credentials or IMAP is disabled`:**
1. Пароль приложения создан для **Диска**, а не **Почты** — пересоздайте с типом «Почта»
2. IMAP отключён в настройках — включите: [mail.yandex.ru](https://mail.yandex.ru) → Настройки → Почтовые программы
3. Пароль устарел — пароли приложений показываются один раз, при повторном открытии они не отображаются

### Команды Himalaya (если всё же настроен)

```bash
# Список писем (inbox)
himalaya envelope list

# Прочитать письмо №3
himalaya message read 3

# Удалить письмо №5
himalaya message delete 5

# Отправить письмо
himalaya message write --to recipient@example.com --subject "Test"
```

---

## 4. Tokens with Special Characters (Critical Pitfall)

**OAuth tokens may contain quotes, backticks, `$`, `!`, and other shell-metacharacters.** Standard shell tools (`grep | cut`, `sed`, `printf`, `echo`) **break** when these characters appear:

```bash
# ❌ BROKEN: cut splits on ALL '=' tokens; quotes/backticks break shell parsing
TOKEN=$(grep YANDEX_DISK_TOKEN ~/.hermes/.env | cut -d= -f2)
# ❌ BROKEN: sed mangles quotes and backticks
sed -i "s/.../.../" .env.local
```

**Always use Python `split("=", 1)` for reading/writing `.env` files with opaque tokens:**

```python
import os

# ─── Read ───
env_path = os.path.expanduser("~/.hermes/.env")
with open(env_path) as f:
    for line in f:
        key, val = line.strip().split("=", 1)
        if key == "YANDEX_DISK_TOKEN":
            token = val

# ─── Write / append ───
# Use write_file (Python) or heredoc, NEVER bare echo
def append_env(key: str, value: str):
    with open(env_path, "a") as f:
        f.write(f"{key}={value}\n")
```

**For `.env.local` in a project repo (e.g. Next.js):**
```python
import os

env_local = "/path/to/project/.env.local"
# Filter out old key (preserving other lines)
lines = []
if os.path.exists(env_local):
    with open(env_local) as f:
        for line in f:
            if not line.startswith("YANDEX_DISK_TOKEN="):
                lines.append(line.rstrip("\n"))

# Append fresh token
with open(env_local, "w") as f:
    for line in lines:
        f.write(line + "\n")
    f.write(f"YANDEX_DISK_TOKEN={token}\n")
```

> ⚠️ **Never use `sed`, `cut`, `printf`, or bare `echo` with tokens that may contain `"`, `'`, `` ` ``, `$`, `!`.** These tools interpret the characters as shell syntax, corrupting the value. Python `split("=", 1)` is the safe canonical method.

---

## 5. Next.js: live xlsx from Yandex Disk (SSR + fallback)

When a Next.js page needs **live data** from an `.xlsx` on Yandex Disk on every request, use `force-dynamic` Server Components with a shared fetcher library and graceful JSON fallback.

**Overview:**
- `src/lib/yandex-disk.ts` — shared `fetchWorkbook()` + typed parsers (`parseCategories`, `parseProducts`, `parseTemplates`)
- `src/app/price/page.tsx` — async Server Component, `export const dynamic = "force-dynamic"`, reads xlsx live
- `src/lib/db.ts` — sync JSON fallback (zero latency, build-safe)
- `src/app/api/products/route.ts` — API route with 5-min cache for client components
- `src/app/api/sync/route.ts` — admin endpoint to refresh committed JSON

**Full recipe with code, architecture decisions, and verified pitfalls:**
`references/nextjs-live-xlsx-ssr.md`

**Key pitfall — token corruption:**
If the API returns `401` despite the token working via direct curl, the token was likely corrupted during shell-based write to `.env.local`. Re-write via Python `split("=", 1)` (see Section 4 above).

**Key pitfall — static generation:**
Without `export const dynamic = "force-dynamic"`, Next.js builds the page once at deploy and never re-reads the xlsx. Always add this export to pages that fetch remote data at request time.

---

## 6. Проверка токенов

```bash
# Disk — должен вернуть JSON с total_space
# Use the token value directly (already extracted via Python)
curl -s -H "Authorization: OAuth $TOKEN" https://cloud-api.yandex.net/v1/disk/ | head -c 200

# User info
curl -s -H "Authorization: OAuth $TOKEN" https://login.yandex.ru/info?format=json
```

---

## 7. Python: скачивание публичной папки целиком

Публичная папка на Яндекс.Диске (`https://disk.yandex.ru/d/XXXX`) не всегда удобно скачать одним zip: прямая ссылка `downloader.disk.yandex.ru/zip/...` часто таймаутится на больших проектах, а API даёт рекурсивный обход с прямыми ссылками на каждый файл.

**Решение:** `scripts/download-public-yandex-disk-folder.py` — resilient recursive downloader:
- обходит дерево через `cloud-api.yandex.net/v1/disk/public/resources`
- скачивает файлы через `/download` endpoint с retry
- работает пачками (`--batch-size`) и сохраняет state (`--state`) для resume
- 4 параллельных потока по умолчанию

**Запуск:**
```bash
python ~/.hermes/skills/productivity/yandex-api/scripts/download-public-yandex-disk-folder.py \
  "https://disk.yandex.ru/d/nD9JyCAGE4jJmQ" \
  /mnt/data/natan-storage/silicone-landing
```

**Параметры:**
| Флаг | Значение |
|------|----------|
| `--state` | путь к pickle-файлу для докачки (default: `.yandex-download-state.pkl`) |
| `--batch-size` | сколько файлов скачать за один вызов (default: 700) |
| `--workers` | потоков параллельно (default: 4) |
| `--no-resume` | проигнорировать state и начать заново |

**Почему не zip:**
- `downloader.disk.yandex.ru/zip/...` таймаут на >120 с для папок с `node_modules`
- API-обход стабилен, докачивает, не кладёт сеть

### Питфоллы recursive download
- Большие `node_modules` дают тысячи файлов — используйте `--batch-size` и state-файл
- Сетевые таймауты случайны; скрипт делает 4 попытки с backoff
- Не увеличивайте `--workers` сильно — Яндекс начинает рвать соединения при >6
- State-файл перезаписывается после каждой пачки; при успешном завершении останется пустой список

---

## 8. Питоны-скрипт (полная загрузка на Диск)

```python
import subprocess, json, os

def upload_to_yandex_disk(local_path: str, remote_name: str) -> str:
    """Залить файл и вернуть публичную ссылку."""
    env = os.path.expanduser("~/.hermes/.env")
    token = None
    with open(env) as f:
        for line in f:
            if line.startswith("YANDEX_DISK_TOKEN="):
                token = line.strip().split("=", 1)[1]
                break
    
    # Upload URL
    r1 = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: OAuth {token}",
         f"https://cloud-api.yandex.net/v1/disk/resources/upload?path=app:/{remote_name}&overwrite=true"],
        capture_output=True, text=True
    )
    upload_url = json.loads(r1.stdout)["href"]
    
    # Upload file
    subprocess.run(["curl", "-s", "-T", local_path, upload_url], capture_output=True)
    
    # Publish
    subprocess.run(
        ["curl", "-s", "-H", f"Authorization: OAuth {token}", "-X", "PUT",
         f"https://cloud-api.yandex.net/v1/disk/resources/publish?path=app:/{remote_name}"],
        capture_output=True
    )
    
    # Get public URL
    r4 = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: OAuth {token}",
         f"https://cloud-api.yandex.net/v1/disk/resources?path=app:/{remote_name}"],
        capture_output=True, text=True
    )
    return json.loads(r4.stdout).get("public_url", "NOT_FOUND")
```

---

## 4.5. Round-trip workflow: download → process → upload

Common pattern: file lives on Диске, обрабатывается локально, возвращается обратно.

```python
import subprocess, json, os

def read_token():
    with open(os.path.expanduser("~/.hermes/.env")) as f:
        for line in f:
            if line.startswith("YANDEX_DISK_TOKEN="):
                return line.strip().split("=", 1)[1]

def download_from_disk(remote_path: str, local_path: str) -> None:
    """Скачать файл с Диска по пути (например /products.xlsx)."""
    token = read_token()
    r = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: OAuth {token}",
         f"https://cloud-api.yandex.net/v1/disk/resources/download?path={remote_path}"],
        capture_output=True, text=True
    )
    download_url = json.loads(r.stdout)["href"]
    subprocess.run(["curl", "-sL", "-o", local_path, download_url], check=True)

def upload_to_disk(local_path: str, remote_path: str, publish: bool = True) -> str:
    """Залить файл, перезаписать если есть, опубликовать, вернуть public_url."""
    token = read_token()
    r1 = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: OAuth {token}",
         f"https://cloud-api.yandex.net/v1/disk/resources/upload?path={remote_path}&overwrite=true"],
        capture_output=True, text=True
    )
    upload_url = json.loads(r1.stdout)["href"]
    subprocess.run(["curl", "-s", "-T", local_path, upload_url], capture_output=True)
    if publish:
        subprocess.run(
            ["curl", "-s", "-H", f"Authorization: OAuth {token}", "-X", "PUT",
             f"https://cloud-api.yandex.net/v1/disk/resources/publish?path={remote_path}"],
            capture_output=True
        )
        r4 = subprocess.run(
            ["curl", "-s", "-H", f"Authorization: OAuth {token}",
             f"https://cloud-api.yandex.net/v1/disk/resources?path={remote_path}"],
            capture_output=True, text=True
        )
        return json.loads(r4.stdout).get("public_url", "NOT_FOUND")
    return "uploaded"
```

**О чём помнить:**
- `overwrite=true` — обязательно при повторных загрузках
- `path=/filename` — путь от корня; `app:/filename` — папка приложения (резервуар, не видна пользователю в вебе)
- После загрузки файл может не мгновенно обновиться в веб-предпросмотре — нужно пару минут или перезагрузить страницу

---

## 5. Next.js runtime: чтение xlsx с Яндекс.Диска

Pattern для сайтов, где данные живут в таблице на Диске, а сайт читает их runtime.

### Гибридная архитектура (рекомендуется)

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Яндекс.Диск     │────▶│  Next.js API     │────▶│  React Pages     │
│  products.xlsx   │     │  /api/products   │     │  (SSR/CSR)       │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                │                           │
                                ▼                           ▼
                         ┌──────────────────┐     ┌──────────────────┐
                         │  src/data/       │     │  src/lib/db.ts   │
                         │  products.json   │     │  (sync JSON)     │
                         └──────────────────┘     └──────────────────┘
```

**Почему гибрид:** Server Components Next.js синхронны. `fetch()` из Диска — асинхронный. Если массово переписывать все страницы под `async/await`, получается каскад async-заразы. Лучше:
1. `src/lib/db.ts` — sync import JSON (zero latency, SSR-safe, zero code changes in pages)
2. `src/lib/data.ts` — async fetcher с кешем 5 мин + fallback на JSON
3. `src/app/api/products/route.ts` — API route для клиентских компонент
4. `src/app/api/sync/route.ts` — admin endpoint для ручной синхронизации
5. `scripts/sync-products.js` — CLI: `npm run sync`

### Runtime fetcher (data.ts)
```typescript
import * as XLSX from "xlsx";

async function fetchWorkbook() {
  const token = process.env.YANDEX_DISK_TOKEN;
  const metaRes = await fetch(
    "https://cloud-api.yandex.net/v1/disk/resources?path=/products.xlsx",
    { headers: { Authorization: `OAuth ${token}` } }
  );
  const meta = await metaRes.json();
  const fileRes = await fetch(meta.file, { redirect: "follow" });
  const buf = await fileRes.arrayBuffer();
  return XLSX.read(new Uint8Array(buf), { type: "array" });
}
```

### Sync adapter (db.ts) — сохраняет старый интерфейс
```typescript
import data from "@/data/products.json";

export function getAllCategories() { return data.categories; }
export function getAllProducts()    { return data.products; }
```

### Синхронизация JSON из xlsx
```bash
npm run sync   # node scripts/sync-products.js
```

Скрипт скачивает xlsx с Диска, парсит листы, пишет `src/data/products.json`.

**См. `references/sqlite-to-xlsx-disk-roundtrip.md` — полная рецептура с кодом всех файлов, архитектурными решениями и питфоллами миграции.**

### Питфоллы Next.js + xlsx
- `import * as XLSX from "xlsx"` работает с `"moduleResolution": "bundler"` в tsconfig
- JSON-колонки (template_data, features as JSON arrays) не roundtrip-ятся через xlsx чисто — нужен парсинг строк в массивы
- Spec tables лучше выносить в отдельный лист xlsx или хранить в JSON-файле отдельно
- Build всегда использует JSON → билд не ломается если Диск недоступен
- Диск-API для чтения требует OAuth токен с scope `cloud_api:disk.read` — проверяйте

---

## 6. Fallback File Hosting

| Сервис | Лимит | Надёжность | Примечание |
|--------|-------|------------|------------|
| **litterbox.catbox.moe** | 1 GB | ✅ Высокая | Лучший fallback. `curl -F "reqtype=fileupload" -F "time=1h" -F "fileToUpload=@file.zip"` |
| transfer.sh | 10 GB | ⚠️ Таймауты | Медленная сеть → провал |
| file.io | 100 MB | ⚠️ Таймауты | Ненадёжно для 5MB+ |
| 0x0.st | 512 MB | ❌ Отключён | Заблокирован из-за спама ботов (mid-2026) |

См. `references/file-hosting-fallbacks.md` — полная сводка.

---

## Ссылки

- [Яндекс Disk REST API](https://yandex.ru/dev/disk/rest/)
- [Яндекс OAuth](https://yandex.ru/dev/oauth/)
- [Himalaya CLI](https://github.com/pimalaya/himalaya)
- [Яндекс Пароли приложений](https://id.yandex.ru/security)
- [[Himalaya — Loaded Skills Reference]] — выжимка по email CLI
- `references/file-hosting-fallbacks.md` — tested file hosting fallbacks
- `references/sqlite-to-xlsx-disk-roundtrip.md` — SQLite → multi-sheet xlsx → Yandex Disk upload/publish pattern
- `scripts/upload-to-yandex-disk.py` — reusable Python script: upload a file to Yandex Disk, publish it, return public URL
- `scripts/download-public-yandex-disk-folder.py` — recursive downloader for public Yandex.Disk folders with resume, batching, and retry
