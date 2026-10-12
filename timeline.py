"""Speech generation and exact-length timing.

Spoken lines take as long as their speech (plus a short pause); silent
action moments are stretched by weight so the film lands on exactly
FILM_SECONDS. The result is a Timeline that scenes and audio both read.
"""
import hashlib
import os
import platform
import shutil
import subprocess
import wave
from dataclasses import dataclass

import numpy as np

import story

SR = 48000
LINE_PAUSE = 0.35            # breath after each spoken line
MIN_ACT_PER_WEIGHT = 0.6     # an action moment never gets shorter than this x weight
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "build", "voices")
KOKORO_MODEL = os.path.join(HERE, "build", "models", "kokoro-v1.0.onnx")
KOKORO_VOICES = os.path.join(HERE, "build", "models", "voices-v1.0.bin")
_kokoro = None


# ------------------------------------------------------------------ speech

def tts_backend(requested="auto"):
    if requested != "auto":
        return requested
    if os.path.exists(KOKORO_MODEL) and os.path.exists(KOKORO_VOICES):
        try:
            import kokoro_onnx  # noqa: F401
            return "kokoro"
        except ImportError:
            pass
    if platform.system() == "Darwin" and shutil.which("say"):
        return "say"
    if shutil.which("espeak-ng"):
        return "espeak"
    raise SystemExit("No speech engine: run on macOS (say) or install espeak-ng.")


def installed_mac_voices():
    out = subprocess.run(["say", "-v", "?"], capture_output=True, text=True).stdout
    # Lines look like: "Eddy (English (US))  en_US    # Hello! ..."
    names = []
    for line in out.splitlines():
        head = line.split("#")[0].rstrip()
        parts = head.rsplit(None, 1)
        if len(parts) == 2:
            names.append(parts[0].strip())
    return names


def pick_mac_voice(voice, premium):
    if not premium:
        return voice.mac[-1]
    have = set(installed_mac_voices())
    for name in voice.mac:
        if name in have:
            return name
    return voice.mac[-1]


def read_wav(path):
    with wave.open(path, "rb") as w:
        assert w.getsampwidth() == 2 and w.getnchannels() == 1 and w.getframerate() == SR
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return data.astype(np.float32) / 32768.0


def trim_silence(x, thresh=0.01):
    loud = np.nonzero(np.abs(x) > thresh)[0]
    if len(loud) == 0:
        return x
    a = max(0, loud[0] - int(0.02 * SR))
    b = min(len(x), loud[-1] + int(0.08 * SR))
    return x[a:b]


def speak(who, text, backend, premium=False):
    """Return mono float32 speech at SR for one line (cached on disk)."""
    v = story.CAST[who]
    if backend == "kokoro":
        key = f"kokoro|{v.kokoro}|{v.k_speed}|{v.k_pitch}|{text}"
    elif backend == "say":
        name = pick_mac_voice(v, premium)
        key = f"say|{name}|{v.rate}|{text}"
    else:
        key = f"espeak|{v.espeak}|{v.pitch}|{v.speed}|{text}"
    h = hashlib.sha1(key.encode()).hexdigest()[:16]
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, f"{who}_{h}.wav")
    if not os.path.exists(out):
        raw = out + (".aiff" if backend == "say" else ".raw.wav")
        post = []
        if backend == "kokoro":
            global _kokoro
            import soundfile
            from kokoro_onnx import Kokoro
            if _kokoro is None:
                _kokoro = Kokoro(KOKORO_MODEL, KOKORO_VOICES)
            lang = "en-gb" if v.kokoro.startswith("b") else "en-us"
            samples, sr = _kokoro.create(text, voice=v.kokoro, speed=v.k_speed, lang=lang)
            soundfile.write(raw, samples, sr)
            if v.k_pitch:
                f = 2 ** (v.k_pitch / 12)
                post = ["-af", f"asetrate={sr}*{f:.5f},aresample={sr},atempo={1 / f:.5f}"]
        elif backend == "say":
            subprocess.run(["say", "-v", name, "-r", str(v.rate), "-o", raw, text], check=True)
        else:
            subprocess.run(["espeak-ng", "-v", v.espeak, "-p", str(v.pitch), "-s", str(v.speed),
                            "-w", raw, text], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, *post, "-ac", "1", "-ar", str(SR),
                        "-sample_fmt", "s16", out], check=True)
        os.remove(raw)
    return trim_silence(read_wav(out))


# ---------------------------------------------------------------- timeline

@dataclass
class Event:
    index: int
    kind: str          # "say" or "act"
    scene: str
    start: float
    end: float
    id: str = None
    who: str = None
    text: str = None
    sfx: list = None

    @property
    def dur(self):
        return self.end - self.start


class Timeline:
    def __init__(self, events, mouths, voices):
        self.events = events
        self.mouths = mouths        # who -> per-frame mouth openness 0..1
        self.voices = voices        # list of (start_seconds, samples)
        self.by_id = {e.id: e for e in events if e.id}
        self.scenes = {}
        for e in events:
            a, b = self.scenes.get(e.scene, (e.start, e.end))
            self.scenes[e.scene] = (min(a, e.start), max(b, e.end))

    def ev(self, id):
        return self.by_id[id]

    def t(self, id, frac=0.0):
        e = self.by_id[id]
        return e.start + e.dur * frac

    def prog(self, id, t, a=0.0, b=1.0):
        """0..1 progress of time t through the part [a, b] of an event."""
        t0, t1 = self.t(id, a), self.t(id, b)
        return min(1.0, max(0.0, (t - t0) / max(1e-6, t1 - t0)))

    def scene_at(self, t):
        for name in story.SCENES:
            a, b = self.scenes[name]
            if a <= t < b:
                return name
        return story.SCENES[-1]

    def line_at(self, t):
        for e in self.events:
            if e.kind == "say" and e.start <= t < e.end + 0.15:
                return e
        return None

    def mouth(self, who, t):
        m = self.mouths.get(who)
        if m is None:
            return 0.0
        i = int(round(t * story.FPS))
        return float(m[i]) if 0 <= i < len(m) else 0.0

    def talking(self, who, t):
        e = self.line_at(t)
        return e is not None and e.who == who and t < e.end


def build(backend="auto", premium=False, verbose=True):
    backend = tts_backend(backend)
    speech = {}
    for i, e in enumerate(story.SCRIPT):
        if isinstance(e, story.Say):
            speech[i] = speak(e.who, e.text, backend, premium)

    fixed = sum(len(x) / SR + LINE_PAUSE for x in speech.values())
    weights = sum(e.weight for e in story.SCRIPT if isinstance(e, story.Act))
    spare = story.FILM_SECONDS - fixed
    if spare < weights * MIN_ACT_PER_WEIGHT:
        raise SystemExit(f"Speech is {fixed:.1f}s; only {spare:.1f}s left for action moments. "
                         f"Trim the script.")
    per_weight = spare / weights

    events, t, voices = [], 0.0, []
    for i, e in enumerate(story.SCRIPT):
        if isinstance(e, story.Say):
            d = len(speech[i]) / SR
            voices.append((e.who, t, speech[i]))
            ev = Event(i, "say", e.scene, t, t + d, e.id, e.who, e.text, e.sfx)
            t += d + LINE_PAUSE
        else:
            d = e.weight * per_weight
            ev = Event(i, "act", e.scene, t, t + d, e.id, sfx=e.sfx)
            t += d
        events.append(ev)
    # Floating point: pin the last event to the exact end.
    events[-1].end = story.FILM_SECONDS

    mouths = mouth_tracks(voices)
    if verbose:
        print(f"[timeline] backend={backend}  speech={fixed:.1f}s  "
              f"action={spare:.1f}s ({per_weight:.2f}s per weight)  total={story.FILM_SECONDS}s")
    tl = Timeline(events, mouths, [(start, x) for _, start, x in voices])
    # Scene ranges must tile the film with no gaps.
    names = story.SCENES
    starts = [min(e.start for e in events if e.scene == n) for n in names]
    for k, n in enumerate(names):
        end = starts[k + 1] if k + 1 < len(names) else story.FILM_SECONDS
        tl.scenes[n] = (starts[k], end)
    return tl


def mouth_tracks(voices):
    """Per-frame mouth openness from speech loudness, per character."""
    n = story.FILM_SECONDS * story.FPS
    hop = SR // story.FPS
    tracks = {}
    for who, start, x in voices:
        m = tracks.setdefault(who, np.zeros(n, np.float32))
        f0 = int(round(start * story.FPS))
        frames = len(x) // hop + 1
        for k in range(frames):
            seg = x[k * hop:(k + 1) * hop]
            if len(seg) == 0 or f0 + k >= n:
                break
            rms = float(np.sqrt(np.mean(seg * seg)))
            m[f0 + k] = max(m[f0 + k], rms)
    for who, m in tracks.items():
        peak = np.percentile(m[m > 0], 95) if np.any(m > 0) else 1.0
        m /= max(peak, 1e-6)
        np.clip(m, 0, 1, out=m)
        m[m < 0.12] = 0
        # tiny smoothing so jaws do not flicker
        m[1:] = np.maximum(m[1:], 0.55 * m[:-1])
    return tracks


def write_srt(tl, path):
    def ts(s):
        ms = int(round(s * 1000))
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"
    n = 0
    with open(path, "w") as f:
        for e in tl.events:
            if e.kind == "say":
                n += 1
                f.write(f"{n}\n{ts(e.start)} --> {ts(e.end + 0.15)}\n{e.text}\n\n")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Generate speech and print the timing")
    p.add_argument("--tts", default="auto", choices=["auto", "kokoro", "say", "espeak"])
    p.add_argument("--premium", action="store_true")
    p.add_argument("--list-voices", action="store_true")
    a = p.parse_args()
    if a.list_voices:
        print("\n".join(installed_mac_voices()))
        raise SystemExit
    tl = build(a.tts, a.premium)
    for name in story.SCENES:
        s, e = tl.scenes[name]
        print(f"  {name:8} {s:7.2f} -> {e:7.2f}  ({e - s:5.1f}s)")
