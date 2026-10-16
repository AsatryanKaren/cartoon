import { useEffect, useMemo, useRef, useState } from "react";
import type { SpeechRecognizer } from "./types";
import { WebSpeechRecognizer } from "./webSpeech";

/**
 * Listens while `active` is true and calls `onText` with what was heard.
 * `lang` is the language to recognise ("en-US", "hy-AM" ...).
 * The recognizer can be swapped (e.g. for an on-device one) by passing it in.
 */
export function useSpeechRecognition(
  active: boolean,
  onText: (text: string, isFinal: boolean) => void,
  lang = "en-US",
  recognizer?: SpeechRecognizer,
) {
  const rec = useMemo(() => recognizer ?? new WebSpeechRecognizer(lang), [recognizer, lang]);
  const [heard, setHeard] = useState("");
  const [error, setError] = useState<string | null>(null);
  const cb = useRef(onText);
  cb.current = onText;

  useEffect(() => {
    if (!active || !rec.supported) return;
    setHeard("");
    rec.start(
      (text, isFinal) => {
        setHeard(text);
        cb.current(text, isFinal);
      },
      (e) => setError(e),
    );
    return () => rec.stop();
  }, [active, rec]);

  return { supported: rec.supported, heard, error };
}
