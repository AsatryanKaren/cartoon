import { useState } from "react";
import { Player } from "./components/Player";
import { StoryPicker } from "./components/StoryPicker";
import { warmUpMicrophone } from "./speech/webSpeech";
import type { StorySummary } from "./types/story";

export default function App() {
  const [story, setStory] = useState<StorySummary | null>(null);

  const pick = async (s: StorySummary) => {
    // Ask for the microphone now (a parent is tapping), so the prompt never interrupts the story.
    await warmUpMicrophone();
    setStory(s);
  };

  return story ? <Player storyId={story.id} onExit={() => setStory(null)} /> : <StoryPicker onPick={pick} />;
}
