interface Props {
  heard: string;
  showHeard: boolean;
}

/** A friendly pulsing ear while the app waits for the child's answer. */
export function ListeningIndicator({ heard, showHeard }: Props) {
  return (
    <div className="listening" aria-live="polite">
      <div className="ear">
        <span className="pulse" />
        <span className="icon" role="img" aria-label="listening">👂</span>
      </div>
      <div className="listening-text">I'm listening…</div>
      {showHeard && heard && <div className="heard">“{heard}”</div>}
    </div>
  );
}
