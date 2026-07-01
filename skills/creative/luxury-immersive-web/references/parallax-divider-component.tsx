// ParallaxDivider.tsx — drop-in full-screen parallax break between sections
// Use between every two major sections to create breathing room + depth

"use client";

import { useEffect, useRef } from "react";
import Image from "next/image";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

interface ParallaxDividerProps {
  src: string;            // "public/images/nature.jpg" or unsplash URL
  alt: string;
  speed?: number;         // 0.3 slow, 0.5 medium (default), 0.7 fast
  overlay?: string;       // e.g. "bg-black/50"
  minHeight?: string;     // "100vh" default, use "60vh" before footer
  children?: React.ReactNode;
}

export default function ParallaxDivider({
  src, alt, speed = 0.5, overlay = "bg-black/40", minHeight = "100vh", children,
}: ParallaxDividerProps) {
  const sectionRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sectionRef.current || !imgRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(imgRef.current,
        { yPercent: -30 * speed },
        {
          yPercent: 30 * speed,
          ease: "none",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top bottom",
            end: "bottom top",
            scrub: true,
          },
        }
      );
    }, sectionRef);
    return () => ctx.revert();
  }, [speed]);

  return (
    <section ref={sectionRef} className="relative w-full overflow-hidden"
             style={{ minHeight }}>
      <div ref={imgRef} className="absolute inset-0 h-[130%] -top-[15%]"
           style={{ willChange: "transform" }}>
        <Image src={src} alt={alt} fill className="object-cover"
               sizes="100vw" quality={90} />
      </div>
      <div className={`absolute inset-0 ${overlay}`} />
      <div className="absolute inset-0 bg-gradient-to-b
                      from-[#0a0a0a] via-transparent to-[#0a0a0a]" />
      {children && <div className="relative z-10 flex flex-col items-center
                                   justify-center min-h-screen px-4">{children}</div>}
    </section>
  );
}
