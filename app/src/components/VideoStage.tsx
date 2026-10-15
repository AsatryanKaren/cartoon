import { useEffect, useImperativeHandle, useRef, useState, type Ref } from "react";

export interface StageHandle {
  /**
   * Must be called inside a tap/click handler. Browsers (Safari especially) only let a video
   * play with sound after it has been started by a user gesture; this starts both video
   * elements once so every later clip can play by itself.
   */
  unlock(firstSrc: string): void;
  /** Resume the current clip (used by the "tap to continue" fallback, also inside a tap). */
  resume(): void;
}

interface Props {
  /** Clip to show; null shows nothing yet. */
  src: string | null;
  loop: boolean;
  onEnded: () => void;
  /** Called when the browser refuses to play (autoplay blocked); the Player asks for a tap. */
  onBlocked: () => void;
  stageRef?: Ref<StageHandle>;
}

/**
 * Two stacked <video> elements: the next clip loads in the hidden one and is swapped in
 * only once it is playing, so clip changes are seamless (no black flash).
 */
export function VideoStage({ src, loop, onEnded, onBlocked, stageRef }: Props) {
  const refs = [useRef<HTMLVideoElement>(null), useRef<HTMLVideoElement>(null)];
  const [front, setFront] = useState(0);
  const shown = useRef<string | null>(null);
  const ended = useRef(onEnded);
  ended.current = onEnded;
  const blocked = useRef(onBlocked);
  blocked.current = onBlocked;

  useImperativeHandle(stageRef, () => ({
    unlock(firstSrc: string) {
      refs.forEach((r, i) => {
        const v = r.current;
        if (!v) return;
        v.src = firstSrc;
        const p = v.play();
        // keep the first element playing the opening clip; the second one was only being unlocked
        if (i === 1) p.then(() => v.pause()).catch(() => {});
        else p.catch(() => blocked.current());
      });
      shown.current = firstSrc;
      setFront(0);
    },
    resume() {
      refs[front].current?.play().catch(() => blocked.current());
    },
  }));

  useEffect(() => {
    if (src === null || shown.current === src) return;
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
    v.play().catch(() => blocked.current());
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
