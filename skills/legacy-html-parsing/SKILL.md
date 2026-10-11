---
name: legacy-html-parsing
description: Use when parsing legacy web apps or CRM panels. Modify and debug Python HTML extractors where no API exists.
category: software-development
related_skills:
  - code-quality-gates
  - superpowers-workflow
---

# Legacy HTML Parsing

Guides the modification and debugging of Python HTML parsers that extract data from legacy web applications, CRM systems, and admin panels where no structured API exists.

## When to use

- The target data lives in rendered HTML from a web app, not in JSON/XML APIs.
- Selectors rely on CSS classes, inline styles, `data-*` attributes, or sibling/parent traversal rather than stable IDs.
- The source HTML changes subtly across records (e.g., active customers vs. terminated customers).
- You are adding a fallback extraction path because the primary selector sometimes misses records.

## Core principles

1. **Extract IDs from the most specific stable attribute.** Prefer `data-uid`, `data-id`, or hidden inputs over row `id` prefixes or visible text. Row IDs like `customer_12345` are secondary because special states (terminated, reserved, vacant) often omit them.
2. **Never trust one selector for all record types.** Build a small selector ladder and return the first match with a valid identifier.
3. **Test BeautifulSoup class matching on the real markup before shipping.** `class_="foo bar"` matches only elements whose class list is exactly `foo bar`; additional classes like `c-p` break the match. Use `class_=["foo", "bar"]` or `class_="bar"` when legacy pages add helper classes to the same element.
4. **Fail soft and log context.** If a selector returns nothing, return a sentinel value and log a short warning with the expected identifier, so callers can decide whether to abort or fallback.
4. **Keep parsing pure.** Parser functions receive `str` HTML and return plain data structures. They must not make HTTP calls or hold state.
5. **Match selector specificity to the data source.** Use exact class strings for Bootstrap-era markup (`span5`, `badge`, `table-condensed`) instead of modern CSS combinators that may fail on malformed or minified HTML.

## Selector ladder pattern

Use this pattern when a single row type can appear in multiple shapes:

```python
def parse_switch_rows(html: str) -> List[Tuple[str, List[str]]]:
    soup = make_soup(html)
    result: List[Tuple[str, List[str]]] = []
    for tr in soup.find_all("tr"):
        # Primary: stable data-* attribute on the badge
        # Use a list of classes because legacy markup adds extra helper classes.
        badge = tr.find("span", class_=["badge", "switch-port-badge"])
        customer_id = badge.get("data-uid", "").strip() if badge else ""

        # Secondary: row id prefix (legacy rows)
        if not customer_id:
            row_id = tr.get("id", "")
            if row_id.startswith("customer_"):
                customer_id = row_id.replace("customer_", "")

        if not customer_id:
            continue

        raw = tr.get_text(" ", strip=True).split()
        user_dt = raw[:3] + [" ".join(raw[3:])] if len(raw) > 3 else raw
        result.append((customer_id, user_dt))
    return result
```

**Why:** `data-uid` is present for both active and terminated rows in LigaCRM; `id="customer_*"` is absent for terminated rows. Falling back to `id` preserves backward compatibility.

## Fallback extraction pattern

When a detail endpoint sometimes returns an empty page for a valid identifier, add a search-then-redetail fallback in the HTTP layer, not the parser:

```python
async def fetch_user_card(crm, customer_id: str, user_dt: List[str], switch_ip: str):
    modal = await crm.get_customer_details_html(customer_id)
    addr, order = extract_addr_and_order_from_modal(modal)

    if addr[0] == ["Адрес не найден"] and order == "unknown":
        log.info("Fallback search by id for customer %s", customer_id)
        found = await crm.search_customer_by_id(customer_id)
        if found.get("data"):
            real_id = str(found["data"][0]["Customer"]["id"])
            modal = await crm.get_customer_details_html(real_id)
            addr, order = extract_addr_and_order_from_modal(modal)

    # ... continue with cable diagnostics
```

**Pitfall:** Do not put the fallback inside `extract_addr_and_order_from_modal`; that function should stay synchronous and pure. The caller owns the retry logic and concurrency semaphore.

## Writing a new CRM search method

When adding a POST-based search endpoint, mirror the existing form payload exactly and replace only the target field:

```python
async def search_customer_by_id(self, customer_id: str) -> Dict[str, Any]:
    form = {**POST_DATE, "data[Search][id]": customer_id}
    return await self._request_with_retry(
        "POST", "/customers", data=form, referer=f"{self.base_url}/customers"
    )
```

**Rule:** Reuse the full base form from the existing config (`POST_DATE`, `SWITCH_POST_DATE`, etc.) instead of building a minimal payload. Legacy CRM forms often require every field to be present, even when empty.

## Testing parsers locally

Before deploying, verify parser behavior against real HTML fragments:

1. Save representative HTML snippets (one per record state: active, terminated, vacant, reserved).
2. Run `parse_switch_rows` and `extract_addr_and_order_from_modal` on each snippet.
3. Assert the returned identifier and address are non-empty for states that should produce output.
4. Keep the snippets in a `tests/fixtures/` directory, not in the skill.

## CRM address extraction and normalization

When a legacy CRM stores the full postal address in a customer detail modal and downstream searches need only *street + house number*, extract the raw address first, then normalize it.

### Extraction from a Bootstrap-era modal

Typical markup wraps the address in a labeled block:

```html
<div class="span5">
  <strong>АДРЕС</strong>
  <div>ул. Солнечная д. 23, кв. 113, подъезд 2, этаж 14</div>
</div>
```

Find the label by exact text, then read the next sibling:

```python
def extract_raw_address(modal_html: str) -> str:
    soup = make_soup(modal_html)
    label = soup.find("strong", string="АДРЕС")
    if not label:
        return ""
    container = label.find_parent("div") or label.parent
    addr_div = container.find("div") if container else None
    return addr_div.get_text(" ", strip=True) if addr_div else ""
```

### Normalizing a Russian address to *street + house*

Remove prefixes and everything after the house number:

```python
import re

PREFIXES = re.compile(r"^\s*(ул|улица|пр-т|проспект|пер|переулок|б-р|бульвар)\b[.\s]*", re.IGNORECASE)
HOUSE = re.compile(r"\s+(д\.?|дом\.?)\s*", re.IGNORECASE)
CUTOFF = re.compile(r"[,\s]+(кв\.?|к\.?|квартира|подъезд|под\.|этаж|корп\.?|корпус)", re.IGNORECASE)

def clean_address(raw: str) -> str:
    s = raw.replace(",", " ")
    s = re.sub(PREFIXES, "", s)
    s = re.sub(HOUSE, " ", s)
    s = re.sub(CUTOFF, "", s)
    return re.sub(r"\s+", " ", s).strip()

def split_address(cleaned: str) -> tuple[str, str]:
    # last token is the house number; everything before it is the street
    parts = cleaned.rsplit(" ", 1)
    return (parts[0], parts[1]) if len(parts) == 2 else (cleaned, "")
```

**Pitfall:** replacing `д.` with an empty string removes the house number too (`ул. Солнечная д. 23` → `Солнечная`). Replace `д.` with a space so the digit stays in the string.

**Pitfall:** `rsplit(" ", 1)` fails for compound street names without spaces (`40летПобеды15`) or fractional houses written without separators (`23/1`). Validate the house part with a regex and fall back to a permissive parser if it is not numeric.

### Chaining: address → switch search → cables

Use the cleaned address to drive another legacy POST search endpoint (e.g. `/switch_house_links`), then expand each returned switch and parse its port table with the same selector-ladder rules. Show progress messages during the multi-switch walk so the user knows the bot is still alive.

### Chaining: customer search → detail modal → address-driven switch search

A customer search response often contains the same fields the detail modal does (e.g. `Customer.full_name`, `Customer.basic_account`). Prefer taking fields like `full_name` from the search response and only fall back to the modal when they are missing. This avoids extra modal round-trips and makes the bot faster and more robust.

```python
async def fetch_customer_summary(crm, basic_account: str):
    result = await crm.search_customer_by_basic_account(basic_account)
    customer = result["data"][0]["Customer"]
    full_name = customer.get("full_name", "").strip()
    cust_id = str(customer["id"])

    details_html = await crm.get_customer_details_html(cust_id)
    if not full_name:
        # Fallback to the modal header
        h5_text = make_soup(details_html).find("h5").get_text(" ", strip=True)
        if ":" in h5_text:
            full_name = h5_text.split(":", 1)[1].strip()

    address = extract_raw_address(details_html)
    return {"full_name": full_name, "address": address, "id": cust_id}
```

**Pitfall:** relying on the modal for every field means an extra HTTP request per customer and couples the parser to the modal's HTML structure. Extract stable identifiers and summary fields from the search response first.

---

## Common pitfalls

- **Exact-class BeautifulSoup matching on legacy markup.** Legacy Bootstrap pages often add helper classes (`c-p`, `hide`, `pull-right`) to the same element. `soup.find(class_="badge switch-port-badge")` will miss `class="badge switch-port-badge c-p"`; prefer `class_=["badge", "switch-port-badge"]` or `class_="switch-port-badge"`.
- **Visible text as identifier.** Markers like `--- РАСТОРЖЕНИЕ (UID = 2499) ---` are display labels. Parse the `data-uid` attribute for the actual ID; use the text only for human-readable classification.
- **Sibling traversal overreliance.** Code like `addr_container.next.next.next.next.next.text` is brittle. If the markup changes even by one whitespace node, it breaks. Prefer named elements or `find(string=...)` when possible, and always wrap traversal in `try/except` with a default value.
- **Mixing string and list for returned address fields.** Functions that join address parts inconsistently (string in one path, list in another) cause callers to misuse `str.join`. Standardize the return shape: either always a string or always a list.
- **Changing parser return shape without updating all callers.** If `extract_addr_and_order_from_modal` is used by `handlers/cables.py`, `handlers/client.py`, and `handlers/repairs.py`, update every call site or keep the shape backward-compatible.
- **Silent data loss from empty rows.** If a new selector is too strict, entire record categories disappear. Compare output counts before and after the change on a representative HTML sample.

## Anti-patterns

- Adding browser automation where a POST search endpoint already exists.
- Parsing HTML with regex for nested structures.
- Caching HTML responses in parser functions instead of the HTTP client layer.
- Returning `None` from a parser when a sentinel value (empty list, `unknown`, `N/A`) is safer for downstream formatting.

## Verification checklist

Before claiming a parser change works:
- [ ] Representative HTML for every record state has been tested.
- [ ] Output counts match expectations for the sample.
- [ ] Callers that consume the new identifier path are updated.
- [ ] Existing call sites still receive the same return shape.
- [ ] No parser function performs I/O or holds mutable state.
