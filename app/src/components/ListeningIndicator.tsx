interface Props {
  heard: string;
  showHeard: boolean;
  text: string;
}

/** A friendly pulsing ear while the app waits for the child's answer. */
export function ListeningIndicator({ heard, showHeard, text }: Props) {
  return (
    <div className="listening" aria-live="polite">
      <div className="ear">
        <span className="pulse" />
        <span className="icon" role="img" aria-label="listening">👂</span>
      </div>
      <div className="listening-text">{text}</div>
      {showHeard && heard && <div className="heard">“{heard}”</div>}
    </div>
  );
}
