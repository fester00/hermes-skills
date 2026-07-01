"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export default function PerspectiveScene() {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    const scene = sceneRef.current;
    if (!container || !scene) return;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
      const y = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
      gsap.to(scene, { rotateY: x * 5, rotateX: -y * 5, duration: 0.8, ease: "power2.out" });
    };
    container.addEventListener("mousemove", handleMouseMove);
    container.addEventListener("mouseleave", () => {
      gsap.to(scene, { rotateY: 0, rotateX: 0, duration: 1.2, ease: "elastic.out(1, 0.5)" });
    });

    const floatEls = scene.querySelectorAll(".float-item");
    floatEls.forEach((el, i) => {
      gsap.to(el, {
        y: "+=15", x: "+=10", rotation: i % 2 === 0 ? 5 : -5,
        duration: 3 + i * 0.5, repeat: -1, yoyo: true, ease: "sine.inOut", delay: i * 0.3,
      });
    });

    const layers = scene.querySelectorAll(".depth-layer");
    layers.forEach((layer, i) => {
      gsap.to(layer, { y: -(i + 1) * 20, ease: "none", scrollTrigger: {
        trigger: container, start: "top bottom", end: "bottom top", scrub: true,
      }});
    });
    gsap.to(scene, { rotateZ: 2, ease: "none", scrollTrigger: {
      trigger: container, start: "top bottom", end: "bottom top", scrub: true,
    }});

    return () => { container.removeEventListener("mousemove", handleMouseMove); };
  }, []);

  return (
    <section ref={containerRef} className="relative h-screen w-full overflow-hidden bg-[#0a0a0a]"
      style={{ perspective: "2000px" }}
    >
      <div ref={sceneRef} className="relative w-full h-full" style={{ transformStyle: "preserve-3d" }}>
        {/* Layer -500: Blurred background shapes */}
        <div className="depth-layer absolute inset-0 flex items-center justify-center pointer-events-none"
          style={{ transform: "translateZ(-500px)" }}
        >
          <div className="absolute w-[600px] h-[600px] rounded-full bg-gold/5 blur-[120px] top-[10%] left-[5%]" />
          <div className="absolute w-[400px] h-[400px] rounded-full bg-cream/5 blur-[100px] bottom-[20%] right-[10%]" />
        </div>

        {/* Layer -200: Decorative lines */}
        <div className="depth-layer absolute inset-0 pointer-events-none"
          style={{ transform: "translateZ(-200px)" }}
        >
          <div className="float-item absolute top-[15%] left-[20%]"><div className="w-[1px] h-[80px] bg-gold/20" /></div>
          <div className="float-item absolute top-[25%] right-[25%]"><div className="w-[60px] h-[1px] bg-gold/15" /></div>
        </div>

        {/* Layer 0: Main content */}
        <div className="depth-layer absolute inset-0 flex flex-col items-center justify-center z-10"
          style={{ transform: "translateZ(0px)" }}
        >
          <h1 className="font-display text-[clamp(5rem,18vw,14rem)] leading-none tracking-tight text-cream select-none"
            style={{ textShadow: "0 1px 0 rgba(244,241,234,0.1), 0 2px 0 rgba(244,241,234,0.09), 0 4px 0 rgba(244,241,234,0.08), 0 8px 0 rgba(244,241,234,0.07), 0 16px 0 rgba(244,241,234,0.06), 0 32px 0 rgba(244,241,234,0.05), 0 64px 40px rgba(0,0,0,0.4)" }}
          >
            BRAND
          </h1>
          <p className="font-serif text-2xl md:text-4xl text-gold/80 mt-6 tracking-wide font-light italic">
            Tagline goes here
          </p>
        </div>

        {/* Layer 100: Floating cards */}
        <div className="depth-layer absolute inset-0 pointer-events-none"
          style={{ transform: "translateZ(100px)" }}
        >
          <div className="float-item absolute top-[20%] left-[8%]">
            <div className="w-[100px] h-[130px] border border-gold/30 bg-black/60 backdrop-blur-sm p-2 rotate-[-6deg]">
              <div className="w-full h-full bg-gradient-to-br from-gold/20 to-transparent" />
            </div>
          </div>
        </div>

        {/* Layer 300: Sparkles */}
        <div className="depth-layer absolute inset-0 pointer-events-none"
          style={{ transform: "translateZ(300px)" }}
        >
          {[...Array(12)].map((_, i) => (
            <div key={i} className="float-item absolute"
              style={{ top: `${15 + (i * 7) % 70}%`, left: `${10 + (i * 13) % 80}%` }}
            >
              <div className="rounded-full bg-gold"
                style={{ width: `${2 + (i % 3)}px`, height: `${2 + (i % 3)}px`, opacity: 0.2 + (i % 4) * 0.1 }}
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
