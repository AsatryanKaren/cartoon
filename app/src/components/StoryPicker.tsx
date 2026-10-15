import { useEffect, useState } from "react";
import type { StorySummary } from "../types/story";

interface Props {
  onPick: (story: StorySummary) => void;
}

const BASE = import.meta.env.BASE_URL + "stories/";

export function StoryPicker({ onPick }: Props) {
  const [stories, setStories] = useState<StorySummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(BASE + "index.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setStories)
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="picker">
      <h1>Whiskers &amp; Luna</h1>
      <p className="subtitle">Pick a story. You help choose what happens!</p>
      {error && <p className="error">Could not load stories: {error}</p>}
      <div className="cards">
        {stories?.map((s) => (
          <button key={s.id} className="card" onClick={() => onPick(s)}>
            {s.cover && <img src={`${BASE}${s.id}/${s.cover}`} alt="" />}
            <span>{s.title}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
