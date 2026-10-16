import { describe, expect, it } from "vitest";
import { allSources, initialState, matchChoice, reduce, type EngineState } from "./storyEngine";
import type { Story } from "../types/story";

const story: Story = {
  id: "t",
  title: "Test",
  start: "intro",
  nodes: {
    intro: { type: "clip", src: "intro.mp4", next: "q1" },
    q1: {
      type: "question",
      listen: "q1_listen.mp4",
      reask: "q1_reask.mp4",
      auto: "q1_auto.mp4",
      timeoutSec: 7,
      maxReasks: 1,
      default: "pond",
      choices: [
        { id: "pond", keywords: ["pond", "water", "frog"], next: "pond" },
        { id: "tree", keywords: ["tree", "climb", "up"], next: "tree" },
      ],
    },
    pond: { type: "clip", src: "pond.mp4", next: "end" },
    tree: { type: "clip", src: "tree.mp4", next: "end" },
    end: { type: "clip", src: "end.mp4", next: null },
  },
};

const run = (s: EngineState, ...events: Parameters<typeof reduce>[2][]) =>
  events.reduce((st, e) => reduce(story, st, e), s);

describe("matchChoice", () => {
  const choices = (story.nodes.q1 as Extract<Story["nodes"][string], { type: "question" }>).choices;
  it("finds keywords in a sentence", () => {
    expect(matchChoice("Let's go to the POND!", choices)?.id).toBe("pond");
    expect(matchChoice("climb the trees", choices)?.id).toBe("tree");
  });
  it("ignores partial words", () => {
    expect(matchChoice("upset", choices)).toBeNull();
  });
  it("returns null on a tie or nothing", () => {
    expect(matchChoice("pond or tree", choices)).toBeNull();
    expect(matchChoice("banana", choices)).toBeNull();
  });
});

describe("story engine", () => {
  it("plays the intro, then listens", () => {
    const s0 = initialState(story);
    expect(s0).toMatchObject({ kind: "clip", src: "intro.mp4" });
    expect(run(s0, { type: "CLIP_ENDED" })).toMatchObject({ kind: "listening", src: "q1_listen.mp4", reasks: 0 });
  });
  it("branches on the spoken answer", () => {
    const s = run(initialState(story), { type: "CLIP_ENDED" }, { type: "HEARD", text: "the tree please" });
    expect(s).toMatchObject({ kind: "clip", src: "tree.mp4" });
  });
  it("keeps listening when the answer is unclear", () => {
    const s = run(initialState(story), { type: "CLIP_ENDED" }, { type: "HEARD", text: "hmm" });
    expect(s).toMatchObject({ kind: "listening" });
  });
  it("re-asks once, then chooses the default by itself", () => {
    let s = run(initialState(story), { type: "CLIP_ENDED" }, { type: "TIMEOUT" });
    expect(s).toMatchObject({ kind: "reasking", src: "q1_reask.mp4", reasks: 1 });
    s = run(s, { type: "CLIP_ENDED" });
    expect(s).toMatchObject({ kind: "listening", reasks: 1 });
    s = run(s, { type: "TIMEOUT" });
    expect(s).toMatchObject({ kind: "auto", src: "q1_auto.mp4" });
    s = run(s, { type: "CLIP_ENDED" });
    expect(s).toMatchObject({ kind: "clip", src: "pond.mp4" });
  });
  it("finishes after the last clip", () => {
    const s = run(initialState(story), { type: "CLIP_ENDED" }, { type: "HEARD", text: "pond" }, { type: "CLIP_ENDED" }, { type: "CLIP_ENDED" });
    expect(s).toEqual({ kind: "finished" });
  });
  it("lists every clip for preloading", () => {
    expect(allSources(story).sort()).toEqual(
      ["end.mp4", "intro.mp4", "pond.mp4", "q1_auto.mp4", "q1_listen.mp4", "q1_reask.mp4", "tree.mp4"].sort(),
    );
  });
});

describe("matchChoice in Armenian (stems)", () => {
  const choices = [
    { id: "pond", keywords: ["լճ*", "լիճ*", "ջր*", "գորտ*", "pond"], next: "pond" },
    { id: "tree", keywords: ["ծառ*", "վերև*", "թռչուն*", "tree"], next: "tree" },
  ];
  it("matches a word with an ending", () => {
    expect(matchChoice("Լճակի մոտ", choices)?.id).toBe("pond");
    expect(matchChoice("ծառի վրա", choices)?.id).toBe("tree");
    expect(matchChoice("Ծառը", choices)?.id).toBe("tree");
  });
  it("ignores Armenian stress and question marks inside a word", () => {
    expect(matchChoice("լճա՞կը", choices)?.id).toBe("pond");
    expect(matchChoice("ծա՛ռ", choices)?.id).toBe("tree");
  });
  it("only matches at the start of a word", () => {
    expect(matchChoice("բարեծառ", choices)).toBeNull();
  });
  it("still returns null on a tie", () => {
    expect(matchChoice("լճակ, թե՞ ծառ", choices)).toBeNull();
  });
});
