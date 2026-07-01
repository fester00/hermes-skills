---
name: text-field-extraction
description: Extract structured fields (series, number, date, issuer, codes) from messy real-world text records with wildly inconsistent formatting. Handles Russian/Ukrainian/Belarusian labeled passport, form, and invoice dumps.
trigger: user provides large text file or paste where each line is a record with semi-structured fields like Серия/№/Выдан/Дата/Код подразделения, but formatting varies line-to-line.
---

# Text Field Extraction from Messy Records

## 1. DO NOT write one mega-regex

The instinct to craft a single perfect `re.search` pattern is a trap. In real-world labeled text (passport scans, OCR exports, form dumps), field order and separators change per record.

**Instead:** extract each field independently with the simplest reliable pattern, then assemble.

```python
import re

def extract_fields(text: str) -> dict:
    # Field 1: date — just grab the first dd.mm.yyyy
    issue_date = re.search(r'\b\d{2}\.\d{2}\.\d{4}\b', text)
    issue_date = issue_date.group(0) if issue_date else None

    # Field 2: unit code (ddd ddd or ddd-ddd) — simple standalone
    unit_code = re.search(r'\b\d{3}\s*[- ]\s*\d{3}\b', text)
    unit_code = unit_code.group(0) if unit_code else None

    # Field 3: series + number — try 3-5 mini-patterns in priority order
    series, number = extract_series_number(text)

    # Field 4: issuer — USE STRING FINDING, NOT GREEDY REGEX
    issuer = extract_issuer_safe(text, issue_date)

    return {
        'issue_date': issue_date,
        'unit_code': unit_code,
        'series': series,
        'number': number,
        'issuer': issuer,
    }
```

## 2. Issuer extraction: hard delimiters, not `.*?`

The most common failure mode: writing `(?<=Выдан[:\s]+)(.+?)(?=\s+\d{2}\.)`.  
This captures **field labels** like `Дата выдачи паспорта:` because they sit between the keyword and the date.

**Correct approach:**

```python
def extract_issuer_safe(text: str, issue_date: str | None) -> str | None:
    issuer = None

    # Step A: look for explicit anchors with KNOWN END markers
    def between(src: str, start: str, end_markers: list[str]) -> str | None:
        i = src.find(start)
        if i == -1:
            return None
        pos = i + len(start)
        end_pos = len(src)
        for em in end_markers:
            fi = src.find(em, pos)
            if fi != -1 and fi < end_pos:
                end_pos = fi
        candidate = src[pos:end_pos].strip()
        return candidate if candidate else None

    # Try the most specific label first
    for pair in [
        ('Кем выдан:',    ['Дата выдачи', 'Дата', 'Код подразделения']),
        ('Орган, выдавший документ:', ['Дата рождения', 'Дата выдачи документа', 'Дата', 'Код']),
        ('Орган, выдавший паспорт:',  ['Дата выдачи паспорта', 'Дата', 'Код']),
        ('Орган, выдавший',           ['Дата', 'Код подразделения']),
    ]:
        issuer = between(text, pair[0], pair[1])
        if issuer:
            break

    # Step B: fallback — regex up to the first date, BUT only if Step A missed
    if not issuer and issue_date:
        m = re.search(r'[Вв]ыдан[: ]+(.+?)\s*\d{2}\.\d{2}\.\d{4}\b', text)
        if m:
            issuer = m.group(1).strip()

    # Step C: post-clean — strip trailing field labels that leaked in
    if issuer:
        for _ in range(3):
            issuer = re.sub(
                r'[\s,;.]*(?:Дата|Код|Номер|Серия)\s*(?:выдачи|подразделения|паспорта|документа|рождения)?\s*[：:]?\s*$',
                '', issuer, flags=re.I
            ).strip()
            issuer = issuer.rstrip(':;., ')
        # Kill if it's just a technical word
        if re.search(r'^(?:Дата|Номер|Код|Вид|Серия|паспорт)', issuer, re.I):
            issuer = None

    return issuer
```

## 3. Series + Number mini-patterns

Try these **in order** — first success wins. Each uses the simplest possible regex.

```python
import re

def extract_series_number(text: str) -> tuple[str | None, str | None]:
    series = number = None

    # Pattern A: standard "Серия X № Y"
    m = re.search(
        r'[Сс]ер(?:ия|ия:)?\s*[: ]*\s*'
        r'(?P<series>[A-ZА-Я0-9\s]{0,12}?)\s*(?:№|Номер|номер)\s*[: ]*\s*'
        r'(?P<number>[0-9A-ZА-Я\s]{2,18}?)'
        r'(?=\s|$|\s*[Вв]ыдан|\s*Дата|\s*Код|\s*\d{2}\.)',
        text, re.X
    )

    # Pattern B: "Серия АС 2358189" (no № sign)
    if not m:
        m = re.search(r'[Сс]ерия\s+(?:паспорта[: ]*)?\s*([A-ZА-Я]{1,3})\s+(\d{4,8})', text)

    # Pattern C: "Серия X Номер Y"
    if not m:
        m = re.search(r'[Сс]ерия\s+([A-ZА-Я0-9\s]{0,12}?)\s+(?:Номер|номер)\s*[: ]*\s*([0-9\s]{2,18})', text)

    # Pattern D: raw "4612№816426"
    if not m:
        m = re.search(r'(?<!\S)(?:с/)?[№]?\s*(\d{2,4}|[A-ZА-Я]{1,3}\d{0,3})\s*[№:]\s*([0-9\s]{2,8})\s', text)

    # Pattern E: "Серия и номер( паспорта): X № Y"
    if not m:
        m = re.search(r'[Сс]ерия[, ]*\s*(?:и\s*)?номер[а ]*[: ]*\s*([A-ZА-Я0-9\s]{0,10})\s*№\s*([0-9\s]{2,18})', text)

    if m:
        ser = (m.group('series') if 'series' in m.groupdict() else m.group(1)).strip().rstrip(':;')
        num = (m.group('number') if 'number' in m.groupdict() else m.group(2)).strip().rstrip(':;')
        if ser is not None and num and len(num.replace(' ', '')) >= 2:
            return ' '.join(ser.split()), ' '.join(num.split())

    return None, None
```

## 4. Pitfalls

1. **Greedy regex capture swallows field labels.** If you capture `Выдан(.+?)дата`, and the line says `Выдан ОВД Дата выдачи: 01.01.2001`, you'll get `ОВД Дата выдачи:` as issuer. Use hard delimiters (`find()` + end-marker list) instead.

2. **Labels appear both before and after.** One line: `Серия 46 05 № 90274 Выдан ОВД 01.01.2001`. Another: `Орган, выдавший паспорт: ОВД Дата выдачи: 01.01.2001 Серия: 46 05`. Field order is not guaranteed — extract independently.

3. **Number may contain spaces.** `46 05 № 90274` — `46 05` is series, `90274` is number. But `№ 73 13 63` — the number itself has spaces. Don't strip all spaces indiscriminately; differentiate series and number.

4. **Pre-clean OCR/input typos before parsing.** Common: `сери я`, `cерия`, `с. `, `№  ` (double space), `Серия:`. Run a `replace()` pass first.

5. **Empty records look like real ones.** Lines like `Серия  №  Выдан` have all labels but no data. After parsing, validate: `if not result['series'] or not result['number']: skip`.

## 5. Files

- `references/passport-parser-template.py` — a fully working, field-tested parser on 600+ mixed-format passport lines (Russian, Ukrainian, Belarusian, Moldovan, Tajik, Uzbek, Kyrgyz). Reuse as-is or adapt field names.
