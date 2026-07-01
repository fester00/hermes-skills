# Параллельный поиск через Chrome CDP (multi-tab)

## Проблема

Последовательный поиск на нескольких площадках занимает много времени (6-8 секунд на сайт). Параллельный поиск через отдельные вкладки ускоряет в 2-3 раза.

## Решение

### Шаг 1: Создать вкладки через HTTP API

```python
import requests

# Create tabs for parallel search
r1 = requests.put('http://127.0.0.1:9222/json/new?url=https://www.ozon.ru/search/?text=QUERY')
tab_ozon = r1.json()

r2 = requests.put('http://127.0.0.1:9222/json/new?url=https://market.yandex.ru/search?text=QUERY')
tab_ym = r2.json()

ws_url_ozon = tab_ozon['webSocketDebuggerUrl']
ws_url_ym = tab_ym['webSocketDebuggerUrl']
```

### Шаг 2: Параллельная обработка через threading

```python
import websocket, json, base64, time
import threading

results = {'ozon': None, 'ym': None}
screenshots = {'ozon': '/tmp/ozon-search.png', 'ym': '/tmp/ym-search.png'}

def process_site(name, ws_url, query_url):
    ws = websocket.create_connection(ws_url)
    
    cid = 1
    def send(method, params=None):
        nonlocal cid
        msg = {"id": cid, "method": method}
        if params: msg["params"] = params
        ws.send(json.dumps(msg))
        cid += 1
        return cid - 1
    
    def recv_res(target_id, timeout=25):
        t0 = time.time()
        while time.time() - t0 < timeout:
            raw = ws.recv()
            d = json.loads(raw)
            if d.get("id") == target_id:
                return d
        return None
    
    # Enable + viewport
    for dom in ["Page", "Runtime", "DOM"]:
        send(f"{dom}.enable")
        ws.recv()
    
    emu_id = send("Emulation.setDeviceMetricsOverride", {
        "width": 1920, "height": 1080,
        "deviceScaleFactor": 1, "mobile": False
    })
    recv_res(emu_id, timeout=5)
    
    # Navigate
    navi_id = send("Page.navigate", {"url": query_url})
    recv_res(navi_id, timeout=20)
    
    # Wait for render (different sites need different times)
    wait_time = 8 if name == 'ym' else 6
    time.sleep(wait_time)
    
    # Screenshot
    ss_id = send("Page.captureScreenshot", {"format": "png", "fromSurface": True})
    ss_res = recv_res(ss_id, timeout=10)
    if ss_res and "result" in ss_res:
        data = base64.b64decode(ss_res["result"]["data"])
        with open(screenshots[name], "wb") as f:
            f.write(data)
    
    # Extract data
    js = """... product extraction JS ..."""
    eval_id = send("Runtime.evaluate", {"expression": js, "returnByValue": True})
    eval_res = recv_res(eval_id, timeout=10)
    
    if eval_res and "result" in eval_res:
        val = eval_res["result"].get("result", {}).get("value", "[]")
        results[name] = json.loads(val)
    
    ws.close()

# Run threads
urls = {
    'ozon': 'https://www.ozon.ru/search/?text=QUERY&from_global=true',
    'ym': 'https://market.yandex.ru/search?text=QUERY'
}

threads = []
for name in ['ozon', 'ym']:
    t = threading.Thread(target=process_site, args=(name, ws_url_map[name], urls[name]))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
```

### Шаг 3: Vision анализ (если JS extraction не сработал)

```python
# Если JS extraction вернул 0 товаров — используем vision_analyze
# На скриншоте часто видно больше, чем в DOM (особенно для динамических сайтов)
```

## Результаты производительности

| Подход | Время |
|--------|-------|
| Последовательный (Ozon → ЯМ → Citilink) | ~20-25 сек |
| Параллельный (Ozon + ЯМ одновременно) | ~10-12 сек |
| + Citilink параллельно | ~12-15 сек |

## Питфолы

1. **WebSocket закрывается при ошибке** — один упавший поток не должен ломать остальные
2. **Shared Chrome process** — все вкладки делят один Chrome, память ограничена
3. **CDP порты** — одна вкладка = один WebSocket, не путать `page/` с `browser/`
4. **Время ожидания** — Next.js (Citilink) нужно 8с+, Ozon 6с, ЯМ 6-8с

## Таблица времени ожидания по сайтам

| Сайт | Минимальное ожидание | Примечание |
|------|---------------------|------------|
| Ozon | 6 секунд | React, быстрый рендер |
| Яндекс Маркет | 8 секунд | Сложный layout |
| Citilink | 8-10 секунд | Next.js, медленный hydrate |
| DNS | Не работает | 403 Forbidden |

## Проверка вкладок

```python
import requests
r = requests.get('http://127.0.0.1:9222/json/list')
tabs = r.json()
print(f"Active tabs: {len(tabs)}")
for t in tabs:
    print(f"  {t['id'][:8]} | {t.get('title','')[:40]}")
```

## Очистка старых вкладок

```python
# Закрыть все вкладки кроме первой
for tab in tabs[1:]:
    requests.delete(f'http://127.0.0.1:9222/json/close/{tab["id"]}')
```
