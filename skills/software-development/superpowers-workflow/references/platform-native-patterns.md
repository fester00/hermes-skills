# Platform-native patterns

Quick-reference for choosing stdlib, native platform, or already-installed
solutions before adding new dependencies.

Only add a row after confirming the project actually targets that stack.

---

## Web front-end (browser APIs)

| Instead of adding... | Use this native feature |
|---|---|
| Date picker library | `<input type="date">`, `<input type="datetime-local">` |
| Modal/dialog library | `<dialog>` + `.showModal()` / `.close()` |
| Color picker library | `<input type="color">` |
| Range slider library | `<input type="range">` |
| File drag-and-drop lib | Native drag events + `DataTransfer` |
| Debounce/throttle library | 3-line closure with `setTimeout` + `clearTimeout` |
| `query-string` | `URLSearchParams` |
| `lodash.clonedeep` | `structuredClone()` |
| `uuid` v4 | `crypto.randomUUID()` |
| `isomorphic-fetch` (modern browsers) | `fetch()` |
| `intersection-observer` polyfill | `IntersectionObserver` API |
| `resize-observer` polyfill | `ResizeObserver` API |
| `matchmedia` polyfill | `window.matchMedia()` |
| `clipboard` library | `navigator.clipboard` |
| `local-storage` wrapper | `localStorage` / `sessionStorage` |

## CSS

| Instead of adding... | Use this CSS feature |
|---|---|
| Container query polyfill | `@container` |
| Clamp utility | `clamp(min, preferred, max)` |
| Aspect ratio helper | `aspect-ratio` |
| Scroll-snap library | `scroll-snap-type` / `scroll-snap-align` |
| CSS reset/normalize (basic) | `*{box-sizing:border-box}` + modern browser defaults |

## Node.js / JavaScript runtime

| Instead of adding... | Use this built-in |
|---|---|
| `mkdirp` | `fs.mkdirSync(path, { recursive: true })` |
| `rimraf` | `fs.rmSync(path, { recursive: true, force: true })` |
| `glob` (simple cases) | `fs.glob()` (Node 22+) or `fs.readdir()` + regex |
| `dotenv` (simple) | `process.env` + shell export, or native `--env-file` (Node 20+) |
| `uuid` v4 | `crypto.randomUUID()` |
| `deep-equal` | `util.isDeepStrictEqual()` or `JSON.stringify(a) === JSON.stringify(b)` (careful with keys) |
| `chalk` (simple) | ANSI escape codes or `console.log('\x1b[32m%s\x1b[0m', text)` |

## Python

| Instead of adding... | Use this stdlib |
|---|---|
| `python-dateutil` basic parsing | `datetime.fromisoformat()` |
| `pytz` | `zoneinfo.ZoneInfo()` |
| `attrs` simple classes | `@dataclass` |
| `simplejson` basic use | `json` stdlib |
| `requests` for one GET | `urllib.request.urlopen()`; keep `requests` for real work |
| `pydantic` simple validation | `dataclasses` + manual checks, or `typing` |
| `jinja2` for one template | `str.format()` / f-strings |
| `pathlib2` | `pathlib` (Python 3.6+) |
| `cached-property` | `functools.cached_property` (Python 3.8+) |
| `backports.zoneinfo` | `zoneinfo` (Python 3.9+) |
| `toml` (read) | `tomllib` (Python 3.11+) |

## Database / SQL

| Instead of app-level... | Push to schema |
|---|---|
| Uniqueness check | `UNIQUE` constraint |
| Referential integrity | `FOREIGN KEY` |
| Range validation | `CHECK (price > 0)` |
| Default timestamp | `DEFAULT CURRENT_TIMESTAMP` |
| Cascading delete/update | `ON DELETE CASCADE` |
| Index for frequent lookups | `CREATE INDEX` |

## General

| Rule of thumb | Example |
|---|---|
| Prefer stdlib over dependency | `datetime` over `arrow` |
| Prefer native API over wrapper | `fetch` over `axios` in simple cases |
| Prefer DB constraint over app check | `UNIQUE` over `SELECT` then `INSERT` |
| Prefer CSS over JS animation | `transition` / `animation` over JS tween |
| Prefer composition over abstraction | Helper function over interface + factory |

---

**Remember:** this is a ladder, not a law. The right tool depends on the project's
existing dependencies, team conventions, and actual requirements. When in doubt,
ask before adding.
