# Modal Scroll Lock Pattern

## Problem

When a modal is open, scrolling inside it can "leak" to the underlying page
once the modal reaches its top or bottom boundary. Users also expect the page
behind the modal to remain stationary.

With a smooth-scroll library such as **Lenis** active, the conflict is worse:
Lenis keeps its own animation loop and can continue moving the viewport even
after `body.style.overflow = "hidden"` is set. A naive lock implementation is
not enough.

## Solution

Combine five mechanisms:

1. **Body scroll lock** — freeze the page by setting `overflow: hidden` on both
   `html` and `body`, plus `touch-action: none` on `body` and
   `overscroll-behavior: none` on `html`. Record `window.scrollY` before
   locking and restore it on unlock.
2. **Document-level scroll event capture** — intercept `wheel`, `touchmove`, and
   scroll keys (`ArrowUp/Down`, `PageUp/Down`, `Home/End`, `Space`) at the
   `document` capture phase so they never reach the page or a smooth-scroll
   library. Allow `Ctrl`/`Cmd`+wheel for pinch-zoom.
3. **Modal overscroll containment** — add `overscroll-behavior: contain` to the
   scrollable modal content so rubber-banding on macOS/iOS does not propagate.
4. **Modal wrapper** — render the modal in a single fixed full-screen flex
   container (backdrop + content together) so it can be centered without
   pointer-event layering bugs.
5. **Focus trap + Escape** — keep `Tab` cycling inside the modal, restore focus
   on close, and close the modal on `Escape`.

## Hook: useScrollLock

Use `useLayoutEffect` so the lock is applied synchronously before paint and
avoids a visible flash of the background scrolling.

```typescript
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

function preventEvent(e: Event) {
  e.preventDefault();
  e.stopPropagation();
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
        requestAnimationFrame(() => window.scrollTo(0, stored));
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
      if (!e.ctrlKey && !e.metaKey) preventEvent(e);
    };
    const touchMoveHandler = (e: TouchEvent) => preventEvent(e);
    const keyDownHandler = (e: KeyboardEvent) => {
      if (isScrollKey(e)) preventEvent(e);
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

## Lenis Coordination

If the landing page uses Lenis, make it respect the lock class:

```typescript
useEffect(() => {
  const lenis = new Lenis({ /* options */ });

  // ...raf loop and anchor handling...

  const observer = new MutationObserver(() => {
    const locked = document.documentElement.classList.contains("scroll-locked");
    locked ? lenis.stop() : lenis.start();
  });

  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class"],
  });

  return () => {
    observer.disconnect();
    lenis.destroy();
  };
}, []);
```

## Scrollable Modal Component

A reusable wrapper that combines the lock, focus trap, Escape handling, and
CSS transitions.

```tsx
import { useEffect, useRef } from "react";
import { useScrollLock } from "@/hooks/useScrollLock";

interface ScrollableModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  maxWidth?: string;
}

export default function ScrollableModal({
  isOpen,
  onClose,
  children,
  maxWidth = "md:max-w-2xl",
}: ScrollableModalProps) {
  const contentRef = useRef<HTMLDivElement>(null);
  const backdropRef = useRef<HTMLDivElement>(null);
  const previouslyFocusedRef = useRef<HTMLElement | null>(null);

  useScrollLock(isOpen);

  useEffect(() => {
    if (isOpen) {
      previouslyFocusedRef.current = document.activeElement as HTMLElement | null;
      requestAnimationFrame(() => contentRef.current?.focus());
    } else {
      previouslyFocusedRef.current?.focus?.();
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
        return;
      }

      if (e.key === "Tab" && contentRef.current) {
        const focusable = contentRef.current.querySelectorAll<HTMLElement>(
          "button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])"
        );
        if (focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    const backdrop = backdropRef.current;
    if (!backdrop) return;
    if (isOpen) {
      requestAnimationFrame(() => backdrop.classList.add("open"));
    } else {
      backdrop.classList.remove("open");
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      ref={backdropRef}
      className="modal-backdrop fixed inset-0 z-[100] flex items-start md:items-center justify-center p-4 md:p-6 bg-black/80 backdrop-blur-sm overflow-hidden"
      onClick={onClose}
      data-testid="modal-backdrop"
    >
      <div
        ref={contentRef}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        className={`modal-content relative w-full ${maxWidth} max-h-[90vh] overflow-y-auto overscroll-contain bg-surface border border-stroke rounded-3xl shadow-2xl my-auto md:my-0`}
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
}
```

## CSS Transitions

```css
.modal-backdrop {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.modal-backdrop.open {
  opacity: 1;
}

.modal-content {
  opacity: 0;
  transform: translateY(60px) scale(0.96);
  transition: opacity 0.45s cubic-bezier(0.16, 1, 0.3, 1),
              transform 0.45s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-backdrop.open .modal-content {
  opacity: 1;
  transform: translateY(0) scale(1);
}
```

## Notes

- Use `items-start` on small screens so the modal starts at the top and the
  user can reach the close button; center on desktop with `md:items-center`.
- `my-auto` plus `max-h-[90vh]` lets the modal shrink to its content while
  staying vertically centered on desktop.
- `onClick={onClose}` on the outer container plus `stopPropagation` on the
  content makes backdrop clicks close the modal and content clicks stay inside.
- `overscroll-contain` (Tailwind's `overscroll-contain`) maps to
  `overscroll-behavior: contain` and prevents rubber-band scroll propagation.
- `tabIndex={-1}` on the modal content makes it focusable programmatically
  without adding it to the normal tab order.
- **Do not** rely solely on a wheel trap inside the modal content. Events over
  the backdrop, trackpad inertia, and keyboard scrolling can all bypass it.
  The document-level capture handler is the reliable defense.
- **Playwright testing pitfall:** `page.locator(...).click()` scrolls the target
  into view before clicking, which can shift `window.scrollY` during a modal
  test and produce false failures. Use `page.evaluate(() => btn.click())` to
  invoke the real click handler without Playwright's auto-scroll, or assert
  on a reference element's `getBoundingClientRect()` position instead of raw
  `window.scrollY`.
- Write Playwright tests for modal open/close, Escape, backdrop click,
  background-scroll lock, and wheel-over-backdrop isolation. They catch
  regressions that manual dev-server checks miss.
