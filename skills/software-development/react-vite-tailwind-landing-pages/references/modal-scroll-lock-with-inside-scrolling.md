# Scroll-Lock Hook That Allows Scrolling Inside the Modal

A common bug in React/Tailwind/Vite landings: the modal body scroll lock blocks
**all** wheel/touch/keyboard scroll events, including the modal content itself.
The page stays locked, but the modal content becomes unscrollable. The fix is to
inspect the event target and only prevent the event when it would scroll the
page, not when it would scroll an element inside the modal.

Use this hook for CSS-only smooth-scroll landings where `Lenis` is not present.
If you use Lenis, coordinate through a `scroll-locked` class or pause Lenis
explicitly instead.

## The hook

```typescript
// src/hooks/useScrollLock.ts
import { useLayoutEffect, useRef } from "react";

const SCROLL_KEYS = new Set([
  "ArrowUp",
  "ArrowDown",
  "PageUp",
  "PageDown",
  "Home",
  "End",
  " ",
]);

function isScrollable(element: Element | null): boolean {
  if (!element) return false;
  const style = window.getComputedStyle(element);
  const overflowY = style.overflowY;
  if (overflowY === "hidden" || overflowY === "visible" || overflowY === "clip") return false;
  return element.scrollHeight > element.clientHeight;
}

function getScrollableParent(element: Element | null): Element | null {
  let current = element;
  while (current) {
    if (isScrollable(current)) return current;
    current = current.parentElement;
  }
  return null;
}

function isInsideModal(target: EventTarget | null): boolean {
  if (!(target instanceof Element)) return false;
  return !!target.closest("[role='dialog']");
}

function isScrollKey(e: KeyboardEvent) {
  return SCROLL_KEYS.has(e.key) && !e.ctrlKey && !e.altKey && !e.metaKey;
}

export function useScrollLock(isLocked: boolean) {
  const scrollYRef = useRef<number | null>(null);

  useLayoutEffect(() => {
    if (!isLocked) {
      if (scrollYRef.current !== null) {
        const stored = scrollYRef.current;
        scrollYRef.current = null;
        requestAnimationFrame(() => {
          window.scrollTo(0, stored);
        });
      }
      return;
    }

    scrollYRef.current = window.scrollY;
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    const originalOverflow = document.body.style.overflow;
    const originalHtmlOverflow = document.documentElement.style.overflow;
    const originalPaddingRight = document.body.style.paddingRight;
    const originalTouchAction = document.body.style.touchAction;
    const originalOverscrollBehavior = document.documentElement.style.overscrollBehavior;

    document.documentElement.classList.add("scroll-locked");
    document.documentElement.style.overflow = "hidden";
    document.documentElement.style.overscrollBehavior = "none";
    document.body.style.overflow = "hidden";
    document.body.style.touchAction = "none";
    if (scrollbarWidth > 0) {
      document.body.style.paddingRight = `${scrollbarWidth}px`;
    }

    window.scrollTo(0, scrollYRef.current);

    const wheelHandler = (e: WheelEvent) => {
      if (e.ctrlKey || e.metaKey) return; // allow pinch-zoom
      if (isInsideModal(e.target)) {
        const target = e.target instanceof Element ? e.target : null;
        const scrollable = getScrollableParent(target);
        if (scrollable) {
          const { scrollTop, scrollHeight, clientHeight } = scrollable;
          const deltaY = e.deltaY;
          const atTop = deltaY < 0 && scrollTop <= 0;
          const atBottom = deltaY > 0 && scrollTop + clientHeight >= scrollHeight - 1;
          if (!atTop && !atBottom) return; // modal handles it
        }
      }
      e.preventDefault();
      e.stopPropagation();
    };

    const touchMoveHandler = (e: TouchEvent) => {
      if (isInsideModal(e.target)) return;
      e.preventDefault();
      e.stopPropagation();
    };

    const keyDownHandler = (e: KeyboardEvent) => {
      if (!isScrollKey(e)) return;
      if (isInsideModal(e.target)) {
        const target = e.target instanceof Element ? e.target : null;
        const scrollable = getScrollableParent(target);
        if (scrollable) {
          const { scrollTop, scrollHeight, clientHeight } = scrollable;
          const atTop =
            (e.key === "ArrowUp" || e.key === "PageUp" || e.key === "Home") && scrollTop <= 0;
          const atBottom =
            (e.key === "ArrowDown" || e.key === "PageDown" || e.key === "End" || e.key === " ") &&
            scrollTop + clientHeight >= scrollHeight - 1;
          if (!atTop && !atBottom) return;
        }
      }
      e.preventDefault();
      e.stopPropagation();
    };

    document.addEventListener("wheel", wheelHandler, { passive: false, capture: true });
    document.addEventListener("touchmove", touchMoveHandler, { passive: false, capture: true });
    document.addEventListener("keydown", keyDownHandler, { capture: true });

    return () => {
      document.removeEventListener("wheel", wheelHandler, { capture: true });
      document.removeEventListener("touchmove", touchMoveHandler, { capture: true });
      document.removeEventListener("keydown", keyDownHandler, { capture: true });

      document.documentElement.classList.remove("scroll-locked");
      document.documentElement.style.overflow = originalHtmlOverflow;
      document.documentElement.style.overscrollBehavior = originalOverscrollBehavior;
      document.body.style.overflow = originalOverflow;
      document.body.style.touchAction = originalTouchAction;
      document.body.style.paddingRight = originalPaddingRight;
    };
  }, [isLocked]);
}
```

## Tailwind / CSS pairing

```css
html.scroll-locked {
  scroll-behavior: auto;
}
```

## Modal container

The modal content element must have `role="dialog"`, `overflow-y-auto`, and
preferably `max-h-[90dvh]` so the hook can detect a real scrollable region:

```tsx
<div
  role="dialog"
  aria-modal="true"
  className="relative w-full md:max-w-2xl max-h-[90dvh] overflow-y-auto overscroll-contain ..."
>
  {children}
</div>
```

## Why this beats a naive lock

A naive lock does `e.preventDefault()` on every `wheel` / `touchmove` /
`keydown`. That makes the modal unusable on small screens because the user
expects to scroll the modal content. This hook checks:

1. Is the event target inside the modal?
2. If yes, is there a scrollable ancestor inside the modal?
3. If yes, is that ancestor **not** at its top/bottom boundary?

Only when the answer is "no" does it prevent the event. Playwright tests for
`modal content scrolls independently from page` should verify both directions.

## Playwright verification snippets

```typescript
// Page scroll stays locked while modal content scrolls
await modal.evaluate((el) => el.scrollTo(0, 200));
const modalScroll = await modal.evaluate((el) => el.scrollTop);
expect(modalScroll).toBeGreaterThan(0);

const pageScrollAfter = await page.evaluate(() => window.scrollY);
expect(pageScrollAfter).toBe(pageScrollBefore);

// Wheel over modal boundary must not leak to page
await page.mouse.move(modalBox.x + modalBox.width / 2, modalBox.y + 20);
await page.mouse.wheel(0, 500);
const pageScrollAfterBoundaryWheel = await page.evaluate(() => window.scrollY);
expect(pageScrollAfterBoundaryWheel).toBe(pageScrollBefore);
```
