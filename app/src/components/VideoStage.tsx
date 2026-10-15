import { useEffect, useRef, useState } from "react";

interface Props {
  src: string;
  loop: boolean;
  onEnded: () => void;
}

/**
 * Two stacked <video> elements: the next clip loads in the hidden one and is swapped in
 * only once it is playing, so clip changes are seamless (no black flash).
 */
export function VideoStage({ src, loop, onEnded }: Props) {
  const refs = [useRef<HTMLVideoElement>(null), useRef<HTMLVideoElement>(null)];
  const [front, setFront] = useState(0);
  const shown = useRef<string | null>(null);
  const ended = useRef(onEnded);
  ended.current = onEnded;

  useEffect(() => {
    if (shown.current === src) return;
    const target = shown.current === null ? front : 1 - front;
    const v = refs[target].current;
    if (!v) return;
    shown.current = src;
    v.src = src;
    v.currentTime = 0;
    const swap = () => {
      setFront(target);
      const other = refs[1 - target].current;
      if (other && other !== v) other.pause();
    };
    v.addEventListener("playing", swap, { once: true });
    v.play().catch(() => {
      /* autoplay blocked: the user tapped Start, so this should not happen */
    });
    return () => v.removeEventListener("playing", swap);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [src]);

  return (
    <div className="stage">
      {refs.map((r, i) => (
        <video
          key={i}
          ref={r}
          className={i === front ? "clip front" : "clip back"}
          playsInline
          preload="auto"
          loop={i === front && loop}
          onEnded={() => {
            if (i === front) ended.current();
          }}
        />
      ))}
    </div>
  );
}
