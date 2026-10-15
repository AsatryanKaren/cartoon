import { useCallback, useEffect, useReducer, useRef, useState } from "react";
import { allSources, initialState, reduce, type EngineEvent, type EngineState } from "../engine/storyEngine";
import { useSpeechRecognition } from "../speech/useSpeechRecognition";
import type { Story } from "../types/story";
import { ListeningIndicator } from "./ListeningIndicator";
import { VideoStage, type StageHandle } from "./VideoStage";

const BASE = import.meta.env.BASE_URL + "stories/";

interface Props {
  storyId: string;
  onExit: () => void;
}

/** Loads a story and all its clips (so switching between clips is instant), then runs it. */
export function Player({ storyId, onExit }: Props) {
  const [story, setStory] = useState<Story | null>(null);
  const [urls, setUrls] = useState<Record<string, string> | null>(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const created: string[] = [];
    (async () => {
      try {
        const s: Story = await fetch(`${BASE}${storyId}/story.json`).then((r) => r.json());
        if (cancelled) return;
        setStory(s);
        const srcs = allSources(s);
        const map: Record<string, string> = {};
        let done = 0;
        await Promise.all(
          srcs.map(async (src) => {
            const res = await fetch(`${BASE}${storyId}/${src}`);
            if (!res.ok) throw new Error(`${src}: HTTP ${res.status}`);
            // a dev server answers a missing file with the web page itself, so check it really is a video
            const type = res.headers.get("content-type") ?? "";
            if (!type.startsWith("video/")) throw new Error(`clip "${src}" is missing`);
            const url = URL.createObjectURL(await res.blob());
            created.push(url);
            map[src] = url;
            done += 1;
            if (!cancelled) setProgress(done / srcs.length);
          }),
        );
        if (!cancelled) setUrls(map);
      } catch (e) {
        if (!cancelled) setError(String(e));
      }
    })();
    return () => {
      cancelled = true;
      created.forEach((u) => URL.revokeObjectURL(u));
    };
  }, [storyId]);

  if (error) return <Message text={`Could not load the story: ${error}`} onExit={onExit} />;
  if (!story || !urls) {
    return (
      <div className="loading">
        <div className="bar"><div style={{ width: `${Math.round(progress * 100)}%` }} /></div>
        <p>Getting the story ready…</p>
      </div>
    );
  }
  return <StoryRunner story={story} urls={urls} onExit={onExit} />;
}

function Message({ text, onExit }: { text: string; onExit: () => void }) {
  return (
    <div className="loading">
      <p>{text}</p>
      <button className="big" onClick={onExit}>Back</button>
    </div>
  );
}

interface RunnerProps {
  story: Story;
  urls: Record<string, string>;
  onExit: () => void;
}

function StoryRunner({ story, urls, onExit }: RunnerProps) {
  const [state, dispatch] = useReducer(
    (s: EngineState, e: EngineEvent | { type: "RESTART" }) =>
      e.type === "RESTART" ? initialState(story) : reduce(story, s, e),
    story,
    initialState,
  );
  const [showHeard, setShowHeard] = useState(false);
  // Nothing plays until a tap: browsers only allow video with sound after a user gesture.
  const [started, setStarted] = useState(false);
  const [needsTap, setNeedsTap] = useState(false);
  const stage = useRef<StageHandle>(null);
  const listening = started && state.kind === "listening";

  // Only listen during the silent "listening" loop, so the microphone never hears the cartoon's own question.
  const onText = useCallback((text: string) => dispatch({ type: "HEARD", text }), []);
  const speech = useSpeechRecognition(listening, onText);

  // Silence timer: re-ask (or choose automatically) if nobody answers. Talking pushes it back.
  const timer = useRef<number | undefined>(undefined);
  const timeoutSec = listening ? (story.nodes[state.nodeId] as { timeoutSec: number }).timeoutSec : 0;
  useEffect(() => {
    if (!listening) return;
    timer.current = window.setTimeout(() => dispatch({ type: "TIMEOUT" }), timeoutSec * 1000);
    return () => window.clearTimeout(timer.current);
  }, [listening, timeoutSec, state]);
  useEffect(() => {
    if (!listening || !speech.heard) return;
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => dispatch({ type: "TIMEOUT" }), 3000);
  }, [listening, speech.heard]);

  // Testing shortcuts (not shown to children): 1/2 answer, N skips a clip, H shows what was heard.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (state.kind === "listening" || state.kind === "reasking") {
        const q = story.nodes[state.nodeId];
        if (q.type === "question") {
          const c = q.choices[Number(e.key) - 1];
          if (c) dispatch({ type: "HEARD", text: c.keywords[0] });
        }
      }
      if (e.key === "n") dispatch(state.kind === "listening" ? { type: "TIMEOUT" } : { type: "CLIP_ENDED" });
      if (e.key === "h") setShowHeard((v) => !v);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [state, story]);

  if (state.kind === "finished") {
    return (
      <div className="end">
        <h2>The End</h2>
        <p>Thank you for helping Whiskers and Luna!</p>
        <div className="row">
          <button className="big" onClick={() => dispatch({ type: "RESTART" })}>Play again</button>
          <button className="big secondary" onClick={onExit}>Other stories</button>
        </div>
      </div>
    );
  }

  const start = () => {
    stage.current?.unlock(urls[state.src]);
    setStarted(true);
  };

  return (
    <div className="player">
      <VideoStage
        stageRef={stage}
        src={started ? urls[state.src] : null}
        loop={listening}
        onEnded={() => dispatch({ type: "CLIP_ENDED" })}
        onBlocked={() => setNeedsTap(true)}
      />
      {!started && (
        <button className="start" onClick={start} aria-label="Start the story">
          {story.cover && <img src={`${BASE}${story.id}/${story.cover}`} alt="" />}
          <span className="play">▶</span>
        </button>
      )}
      {needsTap && (
        <button
          className="start tap"
          onClick={() => {
            setNeedsTap(false);
            stage.current?.resume();
          }}
          aria-label="Continue"
        >
          <span className="play">▶</span>
        </button>
      )}
      {listening && <ListeningIndicator heard={speech.heard} showHeard={showHeard} />}
      {!speech.supported && (
        <div className="banner">Voice answers need Chrome, Edge or Safari. The story will choose by itself.</div>
      )}
      {speech.error === "not-allowed" && (
        <div className="banner">The microphone is blocked. Allow it in the browser to answer with your voice.</div>
      )}
      <button className="exit" onClick={onExit} aria-label="Close story">✕</button>
    </div>
  );
}
