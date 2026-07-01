---
name: russian-retail-search
description: Поиск товаров на российских маркетплейсах (Ozon, DNS, Citilink, Яндекс.Маркет) через браузер с профилем Натана. Chrome CDP с viewport 1920x1080, автозапуск Xvfb+Chrome, извлечение цен и ссылок.
---

# Поиск товаров на российских площадках

## Запуск Chrome с профилем Натана

### 1. Проверить/запустить Xvfb

```bash
# Проверить, работает ли Xvfb
ps aux | grep Xvfb | grep -v grep

# Если не работает — запустить
Xvfb :100 -screen 0 1920x1080x24 -nolisten tcp > /tmp/xvfb.log 2>&1 &
```

### 2. Проверить/запустить Chrome

```bash
# Проверить порт CDP
ss -tlnp | grep 9222

# Если Chrome не слушает — запустить с профилем
DISPLAY=:100 google-chrome \
  --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir=/home/natan/.chrome-vk-profile \
  --no-first-run --no-default-browser-check \
  --window-size=1920,1080 \
  "about:blank" > /tmp/chrome.log 2>&1 &
```

### 3. Проверить подключение

```bash
curl -s http://127.0.0.1:9222/json/version | grep webSocketDebuggerUrl
curl -s http://127.0.0.1:9222/json/list | python3 -c "import sys,json; [print(f\"{t['id'][:8]} | {t.get('title','')[:40]} | {t.get('url','')[:60]}\") for t in json.load(sys.stdin)]"
```

## Поиск на Ozon (профиль Натан)

### Шаг 1: Создать/получить вкладку

```python
import requests
# Получить список вкладок
r = requests.get('http://127.0.0.1:9222/json/list')
pages = r.json()
page_id = pages[0]['id']  # или создать новую
ws_url = pages[0]['webSocketDebuggerUrl']
```

### Шаг 2: Подключиться и настроить viewport

```python
import websocket, json, base64, time

ws = websocket.create_connection(ws_url)

cid = 1
def send(method, params=None):
    global cid
    msg = {"id": cid, "method": method}
    if params: msg["params"] = params
    ws.send(json.dumps(msg))
    cid += 1
    return cid - 1

def recv_res(target_id, timeout=20):
    t0 = time.time()
    while time.time() - t0 < timeout:
        raw = ws.recv()
        d = json.loads(raw)
        if d.get("id") == target_id:
            return d
    return None

# Enable domains
for dom in ["Page", "Runtime", "DOM"]:
    send(f"{dom}.enable")
    ws.recv()

# Set Full HD viewport
emu_id = send("Emulation.setDeviceMetricsOverride", {
    "width": 1920, "height": 1080,
    "deviceScaleFactor": 1, "mobile": False
})
recv_res(emu_id, timeout=5)
```

### Шаг 3: Перейти на Ozon

```python
# Проверить залогинен ли пользователь
eval_id = send("Runtime.evaluate", {"expression": """
(function() {
    const profile = document.querySelector('a[href*="/my/"]');
    return profile ? profile.textContent.trim() : 'NOT_LOGGED_IN';
})()
""", "returnByValue": True})
profile_res = recv_res(eval_id, timeout=10)
name = profile_res.get("result",{}).get("result",{}).get("value","Unknown")
print(f"Profile: {name}")

# Navigate to search
search_url = "https://www.ozon.ru/search/?text=QUERY&from_global=true"
navi_id = send("Page.navigate", {"url": search_url})
recv_res(navi_id, timeout=20)
time.sleep(6)  # Ждём загрузку JS
```

### Шаг 4: Скриншот + извлечение

```python
# Screenshot
ss_id = send("Page.captureScreenshot", {"format": "png", "fromSurface": True})
ss_res = recv_res(ss_id, timeout=10)
if ss_res and "result" in ss_res:
    data = base64.b64decode(ss_res["result"]["data"])
    with open("/tmp/ozon-search.png", "wb") as f:
        f.write(data)

# Extract product data via JS
js = """
(function() {
    const products = [];
    const cards = document.querySelectorAll('[data-widget="searchResultsV2"] .ts, [data-widget="catalogResults"] .ts, .tile-root');
    cards.forEach((card, i) => {
        if (i > 20) return;
        const nameEl = card.querySelector('[class*="tsBody"]') || card.querySelector('span');
        const priceEl = card.querySelector('[class*="Price"]') || card.querySelector('[class*="price"]');
        const oldPriceEl = card.querySelector('[class*="oldPrice"]') || card.querySelector('[class*="del"]');
        const badgeEl = card.querySelector('[class*="badge"]') || card.querySelector('[class*="Badge"]');
        const linkEl = card.querySelector('a');
        if (nameEl) {
            products.push({
                name: (nameEl.textContent || '').trim().substring(0, 120),
                price: priceEl ? (priceEl.textContent || '').trim().substring(0, 40) : 'N/A',
                oldPrice: oldPriceEl ? (oldPriceEl.textContent || '').trim().substring(0, 40) : '',
                badge: badgeEl ? (badgeEl.textContent || '').trim().substring(0, 30) : '',
                link: linkEl ? linkEl.href : ''
            });
        }
    });
    return JSON.stringify(products.slice(0, 15));
})()
"""
eval_id = send("Runtime.evaluate", {"expression": js, "returnByValue": True})
eval_res = recv_res(eval_id, timeout=10)
if eval_res and "result" in eval_res:
    val = eval_res["result"].get("result", {}).get("value", "[]")
    products = json.loads(val)
    for i, p in enumerate(products, 1):
        print(f"{i}. {p['name']}")
        print(f"   💰 {p['price']}")
        if p['oldPrice']: print(f"   ~~{p['oldPrice']}~~")
        if p['badge']: print(f"   🏷 {p['badge']}")
        print(f"   🔗 {p['link'][:80]}")
        print()

ws.close()
```

## Поиск на Citilink

Citilink менее агрессивен к ботам, но товары загружаются динамически.

```python
# Navigate to Citilink search
url = "https://www.citilink.ru/search/?text=QUERY&available=1&order=price:asc"
navi_id = send("Page.navigate", {"url": url})
recv_res(navi_id, timeout=20)
time.sleep(8)  # Дольше ждём рендер Next.js

# Если товары не видны — скролл + повторный скриншот
for i in range(3):
    scroll_id = send("Runtime.evaluate", {"expression": "window.scrollBy(0, 600); 'scrolled'"})
    recv_res(scroll_id, timeout=5)
    time.sleep(2)
```

## DNS — проблемы

DNS блокирует ботов жёстко (403 Forbidden). Прямые ссылки работают только из обычного браузера.

```bash
# DNS всегда вернёт 403 через curl/CDP
# Решение: дать пользователю прямую ссылку
# https://www.dns-shop.ru/search/?q=QUERY
```

## Яндекс.Маркет — капча

ЯМ показывает капчу для датацентровых IP. Прямые поисковые ссылки:
```
https://market.yandex.ru/search?text=QUERY
```

## Формат ответа пользователю

```
🔍 Результаты поиска: QUERY
👤 Профиль: Натан

---

### Модель 1
💰 Цена: X ₽ (было Y ₽, -Z%)
⭐ Рейтинг: N (M отзывов)
🏷 Бейдж: Акция/Распродажа
🔗 Ссылка: ozon.ru/product/...

### Модель 2
...

---
💡 Совет: сравни с DNS/Citilink по прямым ссылкам:
- DNS: https://www.dns-shop.ru/search/?q=...
- Citilink: https://www.citilink.ru/search/?text=...
```

## 7. Поиск через Яндекс и Google

### Яндекс Поиск
- **URL:** `https://yandex.ru/search/?text=QUERY`
- **Статус:** ✅ Работает через CDP (25 млн результатов, без капчи)
- **Использование:** Быстрый поиск цен, обзоров, новостей

### Google Поиск
- **URL:** `https://www.google.com/search?q=QUERY`
- **Статус:** ✅ Работает через CDP
- **Использование:** Англоязычные обзоры, сравнения, характеристики

### Яндекс Маркет
💡 Совет: сравни с DNS / Citilink по прямым ссылкам:
- DNS: https://www.dns-shop.ru/search/?q=...
- Citilink: https://www.citilink.ru/search/?text=...
```

---

## 8. Обновлённая матрица доступных мостов

| Площадка | Статус | Способ | Примечание |
|----------|--------|--------|------------|
| **Ozon** | ✅ | Браузер + CDP | Профиль Натан168 |
| **Яндекс Маркет** | ✅ | Браузер + CDP | Раньше 403, теперь работает! |
| **Яндекс Поиск** | ✅ | Браузер + CDP | Без капчи |
| **Google Поиск** | ✅ | Браузер + CDP | Англоязычные результаты |
| **Citilink** | ✅ | Браузер + CDP | Next.js ждать 8с |
| **DNS** | ❌ | Только прямые ссылки | 403 даже с профилем |

---

## 9. Параллельный поиск

Для ускорения: запускать Ozon + Яндекс Маркет одновременно в разных вкладках через threading.

**Reference:** `references/parallel-cdp-search.md` — полный код, таблица таймаутов по сайтам, очистка вкладок.

---

## 10. Справочные материалы

| Файл | Что внутри |
|------|------------|
| `references/ozon-extraction-patterns.md` | Рабочие селекторы Ozon, JS-шаблоны извлечения цен, питфолы |
| `references/parallel-cdp-search.md` | Параллельный поиск через threading, таблица таймаутов, очистка вкладок |

---

## 11. Питфолы

| Проблема | Решение |
|----------|---------|
| Chrome не запускается (sandbox) | `--no-sandbox` обязателен |
| CDP WebSocket 403 | `--remote-allow-origins=*` |
| Ozon блокирует (нет соединения) | Использовать профиль с cookies, не curl |
| Товары не видны на скриншоте | Увеличить `time.sleep()` до 8с, скролл |
| Цены не извлекаются | Проверить селекторы, Ozon меняет классы |
| DNS 403 | Не искать через браузер, давать прямую ссылку |
| Вкладки CDP устаревают | Проверять `json/list` перед подключением |

---

## 12. Ссылки и команды

### Быстрый старт (одна команда):
```bash
Xvfb :100 -screen 0 1920x1080x24 > /tmp/xvfb.log 2>&1 & sleep 2 && DISPLAY=:100 google-chrome --no-sandbox --disable-gpu --disable-dev-shm-usage --remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir=/home/natan/.chrome-vk-profile --window-size=1920,1080 "about:blank" > /tmp/chrome.log 2>&1 &
```

### Профиль и порты:
- **Профиль Chrome:** `/home/natan/.chrome-vk-profile`
- **Xvfb дисплей:** `:100`
- **CDP порт:** `9222`
- **Skill файл:** `~/.hermes/skills/software-development/russian-retail-search/SKILL.md`
# Запуск всего стека одной командой
Xvfb :100 -screen 0 1920x1080x24 > /tmp/xvfb.log 2>&1 & sleep 2 && DISPLAY=:100 google-chrome --no-sandbox --disable-gpu --disable-dev-shm-usage --remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir=/home/natan/.chrome-vk-profile --window-size=1920,1080 "about:blank" > /tmp/chrome.log 2>&1 &

# Проверка
sleep 3 && curl -s http://127.0.0.1:9222/json/list | python3 -c "import sys,json; d=json.load(sys.stdin); print('Chrome OK:', len(d), 'tabs')"
```