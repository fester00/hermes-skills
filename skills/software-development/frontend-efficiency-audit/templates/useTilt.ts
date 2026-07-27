"use client";

import { useEffect, RefObject } from "react";
import { gsap } from "@/lib/gsap";
import { useReducedMotion } from "@/hooks/useReducedMotion";

interface UseTiltOptions {
  magnitude?: number;
  duration?: number;
  resetDuration?: number;
}

/**
 * Stable 3D card-tilt hook for GSAP + React.
 *
 * Use this when multiple mapped cards share the same mousemove/mouseleave tilt
 * logic. The hook owns its own DOM listeners and cleanup, so the parent
 * `gsap.context` only needs to manage scroll/reveal tweens.
 *
 * Uses gsap.quickTo to avoid queueing overlapping tweens on every mousemove
 * and throttles raw mousemove events to ~60 fps for smoother main-thread
 * performance.
 *
 * IMPORTANT: callback refs in React 18 are read-only. If you combine this hook
 * with a parent ref array, type the ref as a MutableRefObject and assign it in
 * the render callback:
 *
 *   const tiltRef = useRef<HTMLAnchorElement | null>(null)
 *     as React.MutableRefObject<HTMLAnchorElement | null>;
 *   useTilt(tiltRef, { magnitude: 8 });
 *   return (
 *     <Link ref={(el) => { tiltRef.current = el; parentRef(el); }} ... />
 *   );
 */
export function useTilt(
  ref: RefObject<HTMLElement | null>,
  options: UseTiltOptions = {}
) {
  const { magnitude = 10, duration = 0.4, resetDuration = 0.6 } = options;
  const reduced = useReducedMotion();

  useEffect(() => {
    if (reduced) return;
    const el = ref.current;
    if (!el) return;

    const tiltX = gsap.quickTo(el, "rotateX", { duration, ease: "power2.out" });
    const tiltY = gsap.quickTo(el, "rotateY", { duration, ease: "power2.out" });

    let lastMove = 0;
    const onMove = (e: MouseEvent) => {
      const now = performance.now();
      if (now - lastMove < 16) return;
      lastMove = now;

      const rect = el.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      tiltY(x * magnitude);
      tiltX(-y * magnitude);
    };

    const onLeave = () => {
      tiltX(0);
      tiltY(0);
    };

    el.addEventListener("mousemove", onMove);
    el.addEventListener("mouseleave", onLeave);

    return () => {
      el.removeEventListener("mousemove", onMove);
      el.removeEventListener("mouseleave", onLeave);
      tiltX.revert();
      tiltY.revert();
    };
  }, [ref, magnitude, duration, resetDuration, reduced]);
}

export default useTilt;
