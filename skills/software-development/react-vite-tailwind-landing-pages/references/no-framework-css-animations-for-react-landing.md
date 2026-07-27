# CSS-Only Animation Replacement for React + Vite Landing Pages

## When to use this recipe

User wants to remove `framer-motion`, `GSAP`, or `Lenis` from a React landing page and replace the motion with plain CSS + native browser APIs. Common triggers:

- "можешь ли ты эту страницу реализовать без фреймворка framer-motion?"
- "плавность мы можем и без фреймворка сделать"
- bundle-size or dependency-reduction goal
- scroll-lock conflicts with a smooth-scroll library

This guide shows the replacement patterns that worked in a real Vite + React + Tailwind project.

## 1. Replace scroll-triggered reveals

Before (`framer-motion`):

```tsx
<motion.div
  initial={{ opacity: 0, y: 30 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: "-100px" }}
  transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
>
  ...
</motion.div>
```

After (CSS + IntersectionObserver):

```tsx
// src/hooks/useInView.ts
import { useEffect, useRef, useState } from "react";

export function useInView<T extends HTMLElement = HTMLDivElement>(
  options: { threshold?: number; rootMargin?: string; triggerOnce?: boolean } = {}
) {
  const { threshold = 0.1, rootMargin = "0px", triggerOnce = true } = options;
  const ref = useRef<T>(null);
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          if (triggerOnce) observer.unobserve(el);
        } else if (!triggerOnce) {
          setIsInView(false);
        }
      },
      { threshold, rootMargin }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [threshold, rootMargin, triggerOnce]);

  return { ref, isInView };
}
```

```tsx
// src/components/InView.tsx
import { useInView } from "@/hooks/useInView";

export function InView({
  children,
  className = "",
  delay = 0,
  threshold = 0.1,
  rootMargin = "-50px",
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  threshold?: number;
  rootMargin?: string;
}) {
  const { ref, isInView } = useInView({ threshold, rootMargin });
  const delayClass = delay > 0 ? `reveal-delay-${Math.min(delay, 5)}` : "";
  return (
    <div ref={ref} className={`reveal ${delayClass} ${isInView ? "in-view" : ""} ${className}`}>
      {children}
    </div>
  );
}
```

```css
/* index.css or App.css */
.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1),
              transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.reveal.in-view {
  opacity: 1;
  transform: translateY(0);
}
.reveal-delay-1 { transition-delay: 0.1s; }
.reveal-delay-2 { transition-delay: 0.2s; }
.reveal-delay-3 { transition-delay: 0.3s; }
.reveal-delay-4 { transition-delay: 0.4s; }
.reveal-delay-5 { transition-delay: 0.5s; }
```

Usage:

```tsx
<InView rootMargin="-100px" delay={1}>
  <h2>Section title</h2>
</InView>
```

## 2. Replace modal enter/exit animations

Before (`framer-motion` + `AnimatePresence`):

```tsx
<AnimatePresence>
  {isOpen && (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div initial={{ opacity: 0, y: 60, scale: 0.96 }} animate={{ opacity: 1, y: 0, scale: 1 }}>
        ...
      </motion.div>
    </motion.div>
  )}
</AnimatePresence>
```

After (CSS classes + conditional render):

```tsx
export default function ScrollableModal({ isOpen, onClose, children }) {
  const contentRef = useRef<HTMLDivElement>(null);
  const backdropRef = useRef<HTMLDivElement>(null);

  useScrollLock(isOpen);

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
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
        role="dialog"
        aria-modal="true"
        className="modal-content relative w-full md:max-w-2xl max-h-[90vh] overflow-y-auto bg-surface border border-stroke rounded-3xl shadow-2xl my-auto md:my-0"
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
}
```

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

## 3. Replace `whileHover` / `whileTap`

Use Tailwind + CSS transition classes:

```tsx
// was <motion.a whileHover={{ scale: 1.1 }} ...>
<a className="hover:scale-110 transition-transform duration-200" href="#hero">
  ...
</a>
```

## 4. Replace animated loading-screen word carousel

Before (`framer-motion` `AnimatePresence`):

```tsx
<AnimatePresence mode="wait">
  <motion.span key={wordIndex} initial exit animate>
    {words[wordIndex]}
  </motion.span>
</AnimatePresence>
```

After (CSS keyframes + React state):

```tsx
const [wordIndex, setWordIndex] = useState(0);
const [wordState, setWordState] = useState<"enter" | "exit">("enter");

useEffect(() => {
  const interval = setInterval(() => {
    setWordState("exit");
    setTimeout(() => {
      setWordIndex((i) => (i + 1) % words.length);
      setWordState("enter");
    }, 400);
  }, 900);
  return () => clearInterval(interval);
}, [words.length]);
```

```css
.loading-word-enter { animation: loading-word-in 0.4s forwards; }
.loading-word-exit  { animation: loading-word-out 0.4s forwards; }

@keyframes loading-word-in {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
@keyframes loading-word-out {
  0% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-30px); }
}
```

## 5. Replace GSAP marquee

Before (`gsap` + ScrollTrigger):

```tsx
useEffect(() => {
  const tween = gsap.to(el, { xPercent: -50, duration: 45, ease: "none", repeat: -1 });
  return () => tween.kill();
}, []);
```

After (CSS animation):

```css
@keyframes marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
.animate-marquee {
  animation: marquee 45s linear infinite;
}
```

```tsx
<div className="flex whitespace-nowrap animate-marquee">
  {Array.from({ length: 10 }).map((_, i) => (
    <span key={i} className="px-4">MARQUEE TEXT • </span>
  ))}
</div>
```

## 6. Replace smooth scroll library

Before (`Lenis`):

```tsx
const lenis = new Lenis({ duration: 1.2, smoothWheel: true });
```

After (native smooth scroll):

```css
html {
  scroll-behavior: smooth;
}
html.scroll-locked {
  scroll-behavior: auto;
}
html.scroll-locked body {
  overflow: hidden;
}
```

Anchor links still work because the browser handles them. If you need offset for a fixed header, intercept the click and use `element.scrollIntoView({ behavior: "smooth" })` or `window.scrollTo({ top: y - offset, behavior: "smooth" })`.

## 7. Body scroll lock without smooth-scroll library

When `Lenis` is removed, a simpler `overflow: hidden` lock is enough:

```tsx
import { useLayoutEffect, useRef } from "react";

export function useScrollLock(isLocked: boolean) {
  const scrollYRef = useRef<number | null>(null);

  useLayoutEffect(() => {
    if (isLocked) {
      scrollYRef.current = window.scrollY;
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
      const originalOverflow = document.body.style.overflow;
      const originalPaddingRight = document.body.style.paddingRight;

      document.documentElement.classList.add("scroll-locked");
      document.body.style.overflow = "hidden";
      if (scrollbarWidth > 0) {
        document.body.style.paddingRight = `${scrollbarWidth}px`;
      }
      window.scrollTo(0, scrollYRef.current);

      return () => {
        document.documentElement.classList.remove("scroll-locked");
        document.body.style.overflow = originalOverflow;
        document.body.style.paddingRight = originalPaddingRight;
      };
    }

    if (scrollYRef.current !== null) {
      const stored = scrollYRef.current;
      scrollYRef.current = null;
      requestAnimationFrame(() => window.scrollTo(0, stored));
    }
  }, [isLocked]);
}
```

## 8. Verification checklist after removing animation libraries

```bash
npm uninstall framer-motion gsap lenis tailwindcss-animate
# remove tailwindcss-animate from tailwind.config.js plugins
npm run build
npx oxlint
npx playwright test
```

Also manually verify:

- Page still renders; no JS errors in console
- Loading screen text/animation works
- Hero text animations work
- Scroll reveals fire as sections enter viewport
- Modals open/close with CSS transitions
- Modal body scroll lock works
- Hover states preserved
- Mobile menu open/close works
- Form validation and submit still function
- Bundle size decreased

## Real-world result

In the silicone-landing project, removing `framer-motion`, `gsap`, and `lenis`:

- dropped the JS bundle from ~1022 KB to ~758 KB (gzipped from 326 KB to 233 KB);
- eliminated scroll-lock conflicts caused by the smooth-scroll library;
- made all entrance animations, hover states, modals, loading screen, and marquee run on CSS;
- kept Playwright tests passing for modal behavior and page smoke tests.
