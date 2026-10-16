/**
 * Story engine: a pure state machine. It knows nothing about video or microphones;
 * the Player feeds it events and plays whatever `state.src` says.
 */
import type { Choice, QuestionNode, Story, StoryNode } from "../types/story";

export type EngineState =
  | { kind: "clip"; nodeId: string; src: string }
  | { kind: "listening"; nodeId: string; src: string; reasks: number }
  | { kind: "reasking"; nodeId: string; src: string; reasks: number }
  | { kind: "auto"; nodeId: string; src: string }
  | { kind: "finished" };

export type EngineEvent =
  | { type: "CLIP_ENDED" }
  | { type: "HEARD"; text: string }
  | { type: "TIMEOUT" };

function node(story: Story, id: string): StoryNode {
  const n = story.nodes[id];
  if (!n) throw new Error(`Story "${story.id}" has no node "${id}"`);
  return n;
}

/** State for arriving at a node (a clip plays; a question starts listening). */
export function enter(story: Story, id: string | null): EngineState {
  if (id === null) return { kind: "finished" };
  const n = node(story, id);
  if (n.type === "clip") return { kind: "clip", nodeId: id, src: n.src };
  return { kind: "listening", nodeId: id, src: n.listen, reasks: 0 };
}

export function initialState(story: Story): EngineState {
  return enter(story, story.start);
}

/** Normalise speech text into lowercase words. */
export function words(text: string): string[] {
  return text
    .toLowerCase()
    // Armenian stress/question/exclamation marks sit inside a word (լճա՞կ): drop them, don't split there
    .replace(/[\u055b\u055c\u055e]/gu, "")
    .replace(/[^\p{L}\p{N}\s']/gu, " ")
    .split(/\s+/)
    .filter(Boolean);
}

/**
 * Pick the choice whose keywords appear in what was heard.
 * Returns null when nothing matches or two choices match equally (ask again rather than guess).
 */
export function matchChoice(text: string, choices: Choice[]): Choice | null {
  const heard = words(text);
  const joined = " " + heard.join(" ") + " ";
  let best: Choice | null = null;
  let bestScore = 0;
  let tie = false;
  for (const c of choices) {
    let score = 0;
    for (const k of c.keywords) {
      const kw = words(k).join(" ");
      if (!kw) continue;
      if (k.trim().endsWith("*")) {
        // stem: any word that starts with it ("ծառ*" matches ծառը, ծառի, ծառին), for languages with endings
        if (joined.includes(` ${kw}`)) score += 1;
      } else if (joined.includes(` ${kw} `) || joined.includes(` ${kw}s `)) {
        // whole-word match; also accept simple plurals ("trees", "boats")
        score += 1;
      }
    }
    if (score > bestScore) {
      best = c;
      bestScore = score;
      tie = false;
    } else if (score > 0 && score === bestScore) {
      tie = true;
    }
  }
  return tie ? null : best;
}

function question(story: Story, id: string): QuestionNode {
  const n = node(story, id);
  if (n.type !== "question") throw new Error(`Node "${id}" is not a question`);
  return n;
}

export function reduce(story: Story, state: EngineState, event: EngineEvent): EngineState {
  switch (state.kind) {
    case "clip":
      if (event.type !== "CLIP_ENDED") return state;
      return enter(story, (node(story, state.nodeId) as { next: string | null }).next);

    case "listening":
    case "reasking": {
      const q = question(story, state.nodeId);
      if (event.type === "HEARD") {
        const c = matchChoice(event.text, q.choices);
        return c ? enter(story, c.next) : state;
      }
      if (state.kind === "listening" && event.type === "TIMEOUT") {
        if (state.reasks < q.maxReasks) {
          return { kind: "reasking", nodeId: state.nodeId, src: q.reask, reasks: state.reasks + 1 };
        }
        return { kind: "auto", nodeId: state.nodeId, src: q.auto };
      }
      if (state.kind === "reasking" && event.type === "CLIP_ENDED") {
        return { kind: "listening", nodeId: state.nodeId, src: q.listen, reasks: state.reasks };
      }
      return state;
    }

    case "auto": {
      if (event.type !== "CLIP_ENDED") return state;
      const q = question(story, state.nodeId);
      const c = q.choices.find((x) => x.id === q.default) ?? q.choices[0];
      return enter(story, c.next);
    }

    case "finished":
      return state;
  }
}

/** Every video file a story uses (for preloading). */
export function allSources(story: Story): string[] {
  const out = new Set<string>();
  for (const n of Object.values(story.nodes)) {
    if (n.type === "clip") out.add(n.src);
    else [n.listen, n.reask, n.auto].forEach((s) => out.add(s));
  }
  return [...out];
}
