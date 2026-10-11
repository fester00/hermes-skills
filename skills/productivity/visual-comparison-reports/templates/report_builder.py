#!/usr/bin/env python3
"""Starter for a self-contained visual comparison report (no CDN, no JS).

Copy, replace the DATA block, run: python3 report_builder.py
Then verify: python3 scripts/verify_report.py <out.html>

Everything numeric is computed here -- never hand-type a figure into the HTML.
"""
import html
import os

OUT = os.path.join(os.getcwd(), "comparison-report.html")

# ---------------------------------------------------------------- DATA
TITLE = "Сравнение N вариантов"
SUBTITLE = "Оси сравнения: цена · качество · доступность · поддержка языка"
CHECKED = "<дата проверки>"
TLDR = ["<вывод по варианту 1: на какой оси выигрывает, на какой проигрывает>"]

# one row per candidate; match the columns to the decision axes
SPEC_HEAD = ["Вариант", "Ключевые параметры", "Ограничение A", "Ограничение B", "Цена", "Доступно у тебя"]
SPEC_ROWS = [
    ["Вариант 1", "...", "...", "...", "$0.00 / $0.00", "✅ уже есть"],
    ["Вариант 2", "...", "...", "...", "$0.00 / $0.00", "❌ только по API"],
]

# charts: (label, value, optional qualifier)
CHART_RATING = [("Вариант 1", 1484, " · #6"), ("Вариант 2", 1439, " · #64")]
CHART_PRICE = [("Вариант 1", 0.15, " (off-peak)"), ("Вариант 2", 0.50, "")]

METRIC_HEAD = ["Метрика", "Вариант 1", "Вариант 2", "Источник"]
METRIC_ROWS = [
    ["Общий балл (вендор)", "62.5%", "56.6%", "вендор"],
    ["Независимый рейтинг", "1439", "1484", "arena.ai, <дата снимка>"],
]

# unit prices per 1M as (cache_hit, cache_miss, output)
PRICES = {"Вариант 1": (0.003, 0.15, 0.60), "Вариант 2": (0.05, 0.50, 3.00)}
SCENARIOS = [("Разовая сессия", 300_000, 0.70, 25_000), ("День работы", 2_000_000, 0.80, 200_000)]

CARDS = [dict(
    name="Вариант 1", org="Поставщик", tag="краткая роль",
    spec=[("Архитектура", "..."), ("Ограничение A", "..."), ("Цена", "..."), ("Доступ у тебя", "...")],
    pros=["..."], cons=["..."], fit="...",
)]

VERDICTS = [("Задача 1", "Вариант 1 как основной инструмент; Вариант 2 — если упирается в X."),
            ("Задача 2", "Вариант 2")]

RISKS = ["Промо-цена истекает — реальная стоимость ×N.", "Часть цифр вендорские, независимой проверки нет."]

SOURCES = ["Официальная страница: https://...", "Карточка модели: https://...", "Рейтинг: https://..."]


# ---------------------------------------------------------------- HELPERS
def hbars(items, unit="", scale_max=None, fmt="{:.0f}", color="#b5563f"):
    """Horizontal bars as divs. Always pass scale_max for score charts so a
    small subset does not stretch to 100% and imply dominance."""
    mx = scale_max or max(v for _, v, *_ in items)
    out = []
    for label, val, *rest in items:
        note = rest[0] if rest else ""
        width = max(2, round(val / mx * 100))
        out.append(
            f'<div class="barrow"><div class="barlabel">{html.escape(label)}</div>'
            f'<div class="bartrack"><div class="barfill" style="width:{width}%;background:{color}"></div></div>'
            f'<div class="barval">{fmt.format(val)}{unit}{html.escape(note)}</div></div>'
        )
    return "\n".join(out)


def table(head, rows, row_headers=False):
    th = "".join(f"<th>{html.escape(h)}</th>" for h in head)
    body = ""
    for row in rows:
        cells = ""
        for i, cell in enumerate(row):
            cells += (f"<th class='rowh'>{html.escape(cell)}</th>" if row_headers and i == 0
                      else f"<td>{cell}</td>")
        body += f"<tr>{cells}</tr>"
    return f"<div class='scroll'><table class='grid'><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>"


def cost(model, volume, hit_ratio, out, multiplier=1.0):
    hit_p, miss_p, out_p = PRICES[model]
    hit, miss = volume * hit_ratio, volume * (1 - hit_ratio)
    return (hit / 1e6 * hit_p + miss / 1e6 * miss_p + out / 1e6 * out_p) * multiplier


def cost_table():
    head = "".join(f"<th>{html.escape(m)}</th>" for m in PRICES)
    body = ""
    for name, volume, ratio, out in SCENARIOS:
        vals = {m: cost(m, volume, ratio, out) for m in PRICES}
        best = min(vals.values())
        cells = ""
        for v in vals.values():
            klass = " class='best'" if abs(v - best) < 1e-9 else ""
            cells += f"<td{klass}>${v:,.2f}</td>"
        body += (f"<tr><th class='rowh'>{html.escape(name)}"
                 f"<span class='muted'> · {volume // 1000}K вход / {out // 1000}K выход"
                 f" / {int(ratio * 100)}% кэш</span></th>{cells}</tr>")
    return f"<div class='scroll'><table class='grid'><thead><tr><th>Сценарий</th>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def card(c):
    spec = "".join(f"<div><dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd></div>" for k, v in c["spec"])
    pros = "".join(f"<li>{html.escape(x)}</li>" for x in c["pros"])
    cons = "".join(f"<li>{html.escape(x)}</li>" for x in c["cons"])
    return (f"<article class='card'><div class='cardtop'><h3>{html.escape(c['name'])}</h3>"
            f"<span class='org'>{html.escape(c['org'])}</span>"
            f"<span class='tag'>{html.escape(c['tag'])}</span></div>"
            f"<dl class='spec'>{spec}</dl><div class='two'>"
            f"<div><h4 class='pos'>Сильные стороны</h4><ul class='poslist'>{pros}</ul></div>"
            f"<div><h4 class='neg'>Ограничения</h4><ul class='neglist'>{cons}</ul></div></div>"
            f"<p class='fit'><strong>Под твои задачи:</strong> {html.escape(c['fit'])}</p></article>")


CSS = """
:root{--bg:#faf7f2;--paper:#fffdf9;--ink:#221e19;--muted:#7a6f63;--line:#e6dfd4;
--accent:#b5563f;--sage:#5f7a52;--gold:#c08a2e;--blue:#4a6b8a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.62 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:48px 28px 80px}
header.top{border-bottom:3px double var(--ink);padding-bottom:26px;margin-bottom:34px}
.kicker{font:600 12px/1 ui-monospace,Menlo,monospace;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}
h1{font-family:Georgia,serif;font-size:clamp(30px,4.4vw,50px);line-height:1.08;margin:14px 0 10px}
h2{font-family:Georgia,serif;font-size:27px;margin:54px 0 14px;padding-bottom:9px;border-bottom:1px solid var(--line)}
h3{font-family:Georgia,serif;font-size:22px;margin:0}
h4{font-size:13px;text-transform:uppercase;letter-spacing:.09em;margin:0 0 8px}
.pos{color:var(--sage)}.neg{color:var(--accent)}
.lede{background:var(--paper);border:1px solid var(--line);border-left:4px solid var(--gold);border-radius:10px;padding:20px 24px}
.lede li{margin:7px 0}
table.grid{width:100%;border-collapse:collapse;background:var(--paper);border:1px solid var(--line);border-radius:10px;font-size:14.5px;margin:14px 0}
table.grid th,table.grid td{padding:11px 13px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
table.grid thead th{background:#f2ece3;font-size:12.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
table.grid td.best{background:#eef5ea;font-weight:700;color:#3d5c33}
table.grid th.rowh{background:#f7f2ea;font-weight:600}
.muted{color:var(--muted);font-weight:400;font-size:12.5px}
.scroll{overflow-x:auto}
.chart{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:20px 22px;margin:16px 0}
.barrow{display:grid;grid-template-columns:190px 1fr 130px;gap:12px;align-items:center;margin:9px 0}
.barlabel{font-size:14px;font-weight:600}
.bartrack{background:#efe8dd;border-radius:5px;height:22px;overflow:hidden}
.barfill{height:100%;border-radius:5px}
.barval{font:600 13px/1 ui-monospace,Menlo,monospace;color:var(--muted);text-align:right}
.cards{display:grid;gap:22px}
.card{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:24px 26px}
.cardtop{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:16px}
.org{font-size:13px;color:var(--muted)}
.tag{font:600 11.5px/1 ui-monospace,Menlo,monospace;background:#f4ede2;border:1px solid var(--line);border-radius:999px;padding:6px 11px;color:var(--accent);text-transform:uppercase}
dl.spec{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:0 0 18px}
dl.spec dt{font-size:11.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin-bottom:3px}
dl.spec dd{margin:0;font-size:14.5px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:24px}
ul.poslist li::marker{color:var(--sage)}ul.neglist li::marker{color:var(--accent)}
.fit{margin:18px 0 0;padding-top:14px;border-top:1px solid var(--line)}
.vrow{background:var(--paper);border:1px solid var(--line);border-left:4px solid var(--blue);border-radius:9px;padding:16px 20px;margin-top:14px}
.warn{background:#fdf3ee;border:1px solid #efd9cd;border-left:4px solid var(--accent);border-radius:10px;padding:18px 22px}
code{background:#f2ece3;border:1px solid var(--line);border-radius:4px;padding:1px 6px;font:13px ui-monospace,monospace}
@media(max-width:760px){.two{grid-template-columns:1fr}.barrow{grid-template-columns:1fr;gap:4px}.barval{text-align:left}}
"""


def build():
    doc = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(TITLE)}</title><style>{CSS}</style></head><body><div class="wrap">
<header class="top"><div class="kicker">Сводка · {html.escape(CHECKED)}</div>
<h1>{html.escape(TITLE)}</h1><p class="sub">{html.escape(SUBTITLE)}</p></header>
<h2>Короткий вывод</h2>
<div class="lede"><ul>{''.join(f'<li>{html.escape(x)}</li>' for x in TLDR)}</ul></div>
<h2>1. Характеристики</h2>{table(SPEC_HEAD, SPEC_ROWS, row_headers=True)}
<h2>2. Диаграммы</h2>
<div class="chart"><h4>Рейтинг (больше — лучше)</h4>{hbars(CHART_RATING, '', 1529, '{:.0f}', '#4a6b8a')}</div>
<div class="chart"><h4>Цена, $/1M (меньше — лучше)</h4>{hbars(CHART_PRICE, '', None, '{:.2f}', '#5f7a52')}</div>
<h2>3. Метрики</h2>{table(METRIC_HEAD, METRIC_ROWS)}
<h2>4. Стоимость на твоих сценариях</h2>{cost_table()}
<h2>5. Разбор по вариантам</h2><div class="cards">{''.join(card(c) for c in CARDS)}</div>
<h2>6. Что брать под какую задачу</h2>
{''.join(f'<div class="vrow"><b>{html.escape(k)}</b> → {html.escape(v)}</div>' for k, v in VERDICTS)}
<h2>7. Риски и что перепроверить</h2>
<div class="warn"><ul>{''.join(f'<li>{html.escape(r)}</li>' for r in RISKS)}</ul></div>
<h2>8. Источники</h2><ol class="src">{''.join(f'<li>{html.escape(s)}</li>' for s in SOURCES)}</ol>
<footer>Файл: {os.path.basename(OUT)} · проверено {html.escape(CHECKED)}</footer>
</div></body></html>"""
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"written: {OUT}  ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    build()
