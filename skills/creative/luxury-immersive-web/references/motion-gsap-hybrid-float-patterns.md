# Motion + GSAP Hybrid — Floating Elements inside CSS 3D Scene

Session: VIDVIS v3 — replaced GSAP floating animations with declarative `framer-motion` inside a GSAP-driven `preserve-3d` PerspectiveScene.

## The Problem

In a CSS 3D atmospheric scene, floating cards and decorative elements need **two kinds of animation simultaneously**:

1. **Scroll-driven depth** — GSAP ScrollTrigger scrub on parent container (mandatory, Motion has no ScrollTrigger equivalent).
2. **Continuous float / hover entrance** — declarative motion components with spring physics.

## Solution Pattern

Keep the **parent scene** as GSAP land → child **floating items** as Motion land.

### Floating Decorative Elements (Motion)

Replace GSAP `repeat: -1` yoyo loops with Motion `animate` + `Infinity` transitions:

```tsx
<motion.div
  animate={{
    y: [0, i % 2 === 0 ? 20 : -20],
    x: [0, i % 2 === 0 ? 12 : -12],
    rotate: [0, i % 2 === 0 ? 6 : -6],
  }}
  transition={{
    duration: 3 + i * 0.4,
    repeat: Infinity,
    repeatType: "reverse",
    ease: "easeInOut",
    delay: i * 0.25,
  }}
>
  {/* decorative line, cross, dot, etc. */}
</motion.div>
```

Benefits over GSAP:
- No `useEffect` + event listeners
- No manual cleanup on unmount
- Spring physics built-in
- React-friendly render cycle

### Floating Card with 3D Tilt + Shine (Motion)

```tsx
<motion.div
  className="relative overflow-hidden cursor-pointer border border-vidvis-gold/30"
  style={{
    width: "140px",
    height: "180px",
    transformStyle: "preserve-3d",
    perspective: "600px",
  }}
  whileHover={{
    rotateY: 18,
    rotateX: -12,
    translateZ: 40,
    scale: 1.05,
  }}
  transition={{
    type: "spring",
    stiffness: 200,
    damping: 15,
  }}
>
  <Image src="/images/card.jpg" fill className="object-cover" sizes="140px" />
  {/* Shine overlay via CSS pseudo or extra motion.div */}
  <div className="absolute inset-0 pointer-events-none
    bg-[radial-gradient(circle_at_50%_0%,rgba(255,255,255,0.15)_0%,transparent_60%)]
    opacity-0 hover:opacity-100 transition-opacity duration-300" />
</motion.div>
```

### Spring Parameters That Feel Luxurious

| Context | Stiffness | Damping | Duration Equivalent |
|---------|-----------|---------|---------------------|
| Preloader exit | — | — | custom `cubic-bezier [0.76, 0, 0.24, 1]` |
| Floating card hover tilt | 200 | 15 | ~0.3s snappy |
| Particle float | 100 | 20 | ~0.5s gentle |
| Elastic return on mouseleave | — | — | GSAP `elastic.out(1, 0.5)` or spring `damping: 8` |

### Preloader with Motion (full replacement)

Replace GSAP exit animation with `AnimatePresence`:

```tsx
"use client";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function Preloader({ onDone }: { onDone: () => void }) {
  const [progress, setProgress] = useState(0);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          clearInterval(interval);
          setTimeout(() => setIsExiting(true), 300);
          return 100;
        }
        return Math.min(p + Math.random() * 15 + 5, 100);
      });
    }, 150);
    return () => clearInterval(interval);
  }, []);

  return (
    <AnimatePresence onExitComplete={onDone}>
      {!isExiting && (
        <motion.div
          className="preloader fixed inset-0 z-[10001] bg-[#0a0a0a]"
          initial={{ opacity: 1 }}
          exit={{
            y: "-100%",
            transition: { duration: 1.2, ease: [0.76, 0, 0.24, 1] },
          }}
        >
          {/* logo, progress bar, percentage */}
          <motion.div
            className="font-playfair text-6xl font-black mb-8"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.76, 0, 0.24, 1] }}
          >
            VIDVIS
          </motion.div>
          <div className="w-48 h-[1px] bg-white/10 relative overflow-hidden">
            <motion.div
              className="absolute inset-y-0 left-0 bg-vidvis-gold"
              animate={{ width: `${progress}%` }}
              transition={{ type: "tween", duration: 0.15 }}
            />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

### What stays GSAP

- Mouse tilt on the **scene container** (not individual cards)
- ScrollTrigger parallax on **background layers**
- Scroll-scrub on **depth layers**
- Horizontal scroll pin in `HomeTextile`

### What becomes Motion

- Preloader entrance/exit
- Floating decorative elements (continuous loops)
- Floating card hover (3D tilt + shine)
- Hero typography entrance stagger
- Particle opacity pulse (optional)

## Key Rule

> **One animation engine per element.** Don't `gsap.to()` and `<motion.div animate>` on the same ref/div. Either GSAP owns it (scroll-linked) or Motion owns it (declarative).

## Bundle Impact

Adding `framer-motion` v11 to Next.js 14 increases First Load JS by ~35–45 KB (from ~148 KB to ~185 KB in our session). Acceptable for luxury landing pages.
