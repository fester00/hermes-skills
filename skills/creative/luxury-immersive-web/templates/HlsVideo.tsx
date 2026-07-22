import { useEffect, useRef } from "react";
import Hls from "hls.js";

interface HlsVideoProps {
  src: string;
  className?: string;
  flipped?: boolean;
}

export default function HlsVideo({ src, className = "", flipped = false }: HlsVideoProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let hls: Hls | null = null;
    const onLoadedMetadata = () => {
      video.play().catch(() => {
        // autoplay may be blocked
      });
    };

    if (Hls.isSupported()) {
      hls = new Hls({ autoStartLoad: true, debug: false });
      hls.loadSource(src);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play().catch(() => {
          // autoplay may be blocked
        });
      });
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = src;
      video.addEventListener("loadedmetadata", onLoadedMetadata);
    }

    return () => {
      hls?.destroy();
      video.removeEventListener("loadedmetadata", onLoadedMetadata);
      video.pause();
      video.removeAttribute("src");
      video.load();
    };
  }, [src]);

  return (
    <video
      ref={videoRef}
      autoPlay
      muted
      loop
      playsInline
      className={`${className} ${flipped ? "scale-y-[-1]" : ""}`}
      style={{ willChange: "transform" }}
    />
  );
}
