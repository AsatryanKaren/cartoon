/**
 * Anything that turns the child's voice into text. The browser's Web Speech API is the first
 * implementation; an on-device model (e.g. Whisper) or a native mobile recognizer can replace it later
 * without changing the Player.
 */
export interface SpeechRecognizer {
  readonly supported: boolean;
  /** Start listening; `onText` receives partial and final transcripts. */
  start(onText: (text: string, isFinal: boolean) => void, onError?: (error: string) => void): void;
  stop(): void;
}
