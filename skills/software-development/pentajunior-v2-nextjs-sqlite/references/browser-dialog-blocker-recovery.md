# Browser dialog blocker recovery

When using Hermes browser tools to click through an admin panel, it is easy to accidentally hit a `confirm()` / `alert()` / `prompt()` button (e.g. "Удалить товар?"). The browser automation becomes blocked because there is no built-in `dialog accept/dismiss` tool.

## What happens
Subsequent `browser_navigate`, `browser_click`, `browser_type`, and `browser_console` calls all return:
```
A JavaScript confirm dialog is blocking the page: "...". Resolve it with `dialog accept` or `dialog dismiss`.
```

## Recovery options

1. **Kill and restart the dev server** — usually not enough; the dialog is in the browser tab, not the server.
2. **Navigate the browser tab away from the page** — also blocked by the same dialog.
3. **Ask the user to dismiss the dialog manually** in their local browser, then continue automation. This is the fastest practical path when the agent is running headless browser automation against a local dev server.
4. **Avoid the trap in the first place:**
   - When clicking action buttons in tables with adjacent "Edit" / "Delete" buttons, verify the button label or use `document.querySelector` with a specific selector in `browser_console` instead of relying on `@ref` ordering.
   - Example safe edit click:
     ```js
     document.querySelector('button.btn-warning')?.click();
     ```
   - Or scope by product row text:
     ```js
     [...document.querySelectorAll('tr')].find(r => r.textContent.includes('Люминофор')).querySelector('button.btn-warning').click();
     ```

## If a product was almost deleted
If you only opened the confirm dialog but never confirmed it, the entity is safe. Dismissing the dialog (Cancel / Escape) leaves the DB unchanged.

## Lesson
Browser `confirm()` dialogs are an automation blocker in the current Hermes toolset. Prefer programmatic actions (`fetch`, API calls, direct DB edits) over clicking destructive buttons when unattended verification is required. When visual verification is required, ask the user to perform the risky click or confirm that it is safe to proceed.