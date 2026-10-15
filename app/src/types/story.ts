/** A story is a graph of nodes: plain clips, and questions that branch on the child's spoken answer. */

export interface ClipNode {
  type: "clip";
  /** Video file, relative to the story folder. */
  src: string;
  /** Node to go to when the clip ends; null ends the story. */
  next: string | null;
}

export interface Choice {
  id: string;
  /** Words that select this choice when heard in the child's answer. */
  keywords: string[];
  next: string;
}

export interface QuestionNode {
  type: "question";
  /** Seamless loop played while listening. */
  listen: string;
  /** Short clip asking the question again after silence. */
  reask: string;
  /** Clip where the character picks the default choice himself. */
  auto: string;
  /** Seconds of silence before re-asking. */
  timeoutSec: number;
  /** How many times to re-ask before choosing automatically. */
  maxReasks: number;
  /** Choice id used when nobody answers. */
  default: string;
  choices: Choice[];
}

export type StoryNode = ClipNode | QuestionNode;

export interface Story {
  id: string;
  title: string;
  cover?: string;
  start: string;
  nodes: Record<string, StoryNode>;
}

export interface StorySummary {
  id: string;
  title: string;
  cover?: string;
}
