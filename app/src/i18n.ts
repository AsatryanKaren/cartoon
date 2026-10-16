/** The few words the player shows on screen, per story language (the cartoon itself speaks the rest). */
export interface UiText {
  listening: string;
  theEnd: string;
  thanks: string;
  playAgain: string;
  otherStories: string;
  noSpeech: string;
  micBlocked: string;
}

const EN: UiText = {
  listening: "I'm listening…",
  theEnd: "The End",
  thanks: "Thank you for helping Whiskers and Luna!",
  playAgain: "Play again",
  otherStories: "Other stories",
  noSpeech: "Voice answers need Chrome, Edge or Safari. The story will choose by itself.",
  micBlocked: "The microphone is blocked. Allow it in the browser to answer with your voice.",
};

const HY: UiText = {
  listening: "Լսում եմ…",
  theEnd: "Վերջ",
  thanks: "Շնորհակալություն, որ օգնեցիր Վիսկերսին և Լունային։",
  playAgain: "Նորից խաղալ",
  otherStories: "Այլ պատմություններ",
  noSpeech: "Ձայնով պատասխանելու համար բացեք Chrome-ում։ Պատմությունն ինքը կընտրի։",
  micBlocked: "Խոսափողն արգելափակված է։ Թույլատրեք այն դիտարկիչում՝ ձայնով պատասխանելու համար։",
};

export function uiText(lang = "en-US"): UiText {
  return lang.toLowerCase().startsWith("hy") ? HY : EN;
}
