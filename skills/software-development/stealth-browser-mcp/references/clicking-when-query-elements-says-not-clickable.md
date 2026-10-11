# Clicking elements when query_elements reports is_clickable=false

## Symptom

`mcp__stealth_browser__query_elements` returns a visible element with:

```json
{"is_visible": true, "is_clickable": false, ...}
```

A `false` `is_clickable` flag does **not** mean the element cannot be clicked. The CDP "clickable" heuristic often fails on simple anchor tags, especially in headless mode. Use a JavaScript click instead.

## Working pattern from a live session

Step 1 — query the element to get its selector and bounding box:

```json
{
  "instance_id": "<instance_id>",
  "selector": "a[href]",
  "text_filter": "Learn more",
  "visible_only": true
}
```

Response:

```json
{
  "selector": "a[href]",
  "tag_name": "a",
  "text": "Learn more",
  "attributes": {"href": "https://iana.org/domains/example"},
  "is_visible": true,
  "is_clickable": false,
  "bounding_box": {"x": 384.0, "y": 228.0, "width": 91.25, "height": 19.0}
}
```

Step 2 — click via `execute_script`:

```json
{
  "instance_id": "<instance_id>",
  "script": "(() => {\n  const a = document.querySelector('a[href*=\"iana.org\"]');\n  if (!a) return {error: 'not found'};\n  a.click();\n  return {clicked: true, text: a.textContent.trim(), href: a.href};\n})()"
}
```

Result is CDP-serialized:

```json
{
  "success": true,
  "result": [
    ["clicked", {"type": "boolean", "value": true}],
    ["text",    {"type": "string",  "value": "Learn more"}],
    ["href",    {"type": "string",  "value": "https://iana.org/domains/example"}]
  ],
  "error": null
}
```

Step 3 — verify navigation with `get_page_content`:

```json
{
  "instance_id": "<instance_id>"
}
```

Returns `url`, `title`, and `text` of the new page.

## When to prefer each tool

| Situation | Use |
|---|---|
| Element visible, `is_clickable` is true | `click_element` or `click_at_xy` |
| Element visible, `is_clickable` is false | `execute_script` with `.click()` |
| Need coordinates from `bounding_box` | `click_at_xy` after center calculation |
| Complex multi-step interaction | `execute_script` with custom JS logic |

## Notes

- `execute_script` accepts only `instance_id`, `script`, and optional `args`.
- Do not pass `function_name` or other CDP-style parameters; they will cause validation errors.
- Always verify navigation or state after a JS click, because `.click()` does not wait for page load.
