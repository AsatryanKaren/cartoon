import type { SpeechRecognizer } from "./types";

// Minimal typings: the Web Speech API is not in TypeScript's DOM lib yet.
interface SRAlternative { transcript: string }
interface SRResult { isFinal: boolean; 0: SRAlternative; length: number }
interface SREvent { resultIndex: number; results: ArrayLike<SRResult> }
interface SRErrorEvent { error: string }
interface SRInstance {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  onresult: ((e: SREvent) => void) | null;
  onerror: ((e: SRErrorEvent) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}
type SRConstructor = new () => SRInstance;

function ctor(): SRConstructor | undefined {
  const w = window as unknown as { SpeechRecognition?: SRConstructor; webkitSpeechRecognition?: SRConstructor };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition;
}

/** Browser speech recognition (Chrome, Edge, Safari). Restarts itself if the browser stops on silence. */
export class WebSpeechRecognizer implements SpeechRecognizer {
  readonly supported = !!ctor();
  private rec: SRInstance | null = null;
  private active = false;
  private readonly lang: string;

  constructor(lang = "en-US") {
    this.lang = lang;
  }

  start(onText: (text: string, isFinal: boolean) => void, onError?: (error: string) => void): void {
    const C = ctor();
    if (!C) {
      onError?.("not-supported");
      return;
    }
    this.stop();
    const rec = new C();
    rec.lang = this.lang;
    rec.continuous = true;
    rec.interimResults = true;
    rec.maxAlternatives = 1;
    rec.onresult = (e) => {
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const r = e.results[i];
        onText(r[0].transcript, r.isFinal);
      }
    };
    rec.onerror = (e) => {
      // "no-speech" and "aborted" are normal while waiting; report the rest
      if (e.error !== "no-speech" && e.error !== "aborted") onError?.(e.error);
      if (e.error === "not-allowed" || e.error === "service-not-allowed") this.active = false;
    };
    rec.onend = () => {
      if (this.active && this.rec === rec) {
        try {
          rec.start();
        } catch {
          /* already started */
        }
      }
    };
    this.rec = rec;
    this.active = true;
    try {
      rec.start();
    } catch {
      /* start() throws if called twice; harmless */
    }
  }

  stop(): void {
    this.active = false;
    if (this.rec) {
      this.rec.onend = null;
      try {
        this.rec.abort();
      } catch {
        /* ignore */
      }
      this.rec = null;
    }
  }
}

/** Ask for the microphone once up front, so the permission prompt doesn't interrupt the story. */
export async function warmUpMicrophone(): Promise<boolean> {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach((t) => t.stop());
    return true;
  } catch {
    return false;
  }
}
