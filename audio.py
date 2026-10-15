"""Music, sound effects and the final mix -- all generated in code.

Music is a small procedural band (pad, bass, plucked melody, light drums)
whose mood changes per scene. It ducks under speech. Sound effects are
synthesised from noise and oscillators and placed where the script says.
"""
import wave

import numpy as np

import film as story
from timeline import SR

TAU = 2 * np.pi


def _n():
    # length of the current film in samples (films may set their own FILM_SECONDS)
    return int(round(story.FILM_SECONDS * SR))


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env_adsr(n, a, r, sustain_decay=0.0):
    """Attack/release envelope over n samples; optional exponential decay."""
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / max(a, 1e-4))
    e *= np.minimum(1.0, (n / SR - t) / max(r, 1e-4))
    if sustain_decay:
        e *= np.exp(-t * sustain_decay)
    return e


def place(buf, start, x, gain=1.0):
    i = int(round(start * SR))
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    if i < 0:
        x, i = x[-i:], 0
    buf[i:j] += gain * x[:j - i]


def band(noise, lo, hi):
    """Band-limit a noise burst with an FFT mask."""
    f = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(len(noise), 1 / SR)
    f[(freqs < lo) | (freqs > hi)] = 0
    return np.fft.irfft(f, len(noise))


# ------------------------------------------------------------------- music

# chords as (root midi, quality); progressions are one chord per bar
MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    "title":   dict(bpm=78, prog=[(60, MAJ), (57, MIN), (53, MAJ), (55, MAJ)], drums=False, mel=0.5, oct=72, vol=0.8),
    "morning": dict(bpm=100, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=True, mel=0.6, oct=77, vol=0.8),
    "legend":  dict(bpm=68, prog=[(57, MIN), (53, MAJ), (55, MAJ), (52, MIN)], drums=False, mel=0.35, oct=81, vol=0.75),
    "garden":  dict(bpm=120, prog=[(60, MAJ), (65, MAJ), (57, MIN), (55, MAJ)], drums=True, mel=0.75, oct=72, vol=0.85),
    "meadow":  dict(bpm=104, prog=[(55, MAJ), (52, MIN), (60, MAJ), (62, MAJ)], drums=True, mel=0.6, oct=79, vol=0.8),
    "pond":    dict(bpm=64, prog=[(62, MIN), (58, MAJ), (60, MAJ), (57, MIN)], drums=False, mel=0.3, oct=74, vol=0.7),
    "realize": dict(bpm=64, prog=[(62, MIN), (58, MAJ), (60, MAJ), (57, MAJ)], drums=False, mel=0.25, oct=74, vol=0.6),
    "laugh":   dict(bpm=112, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.7, oct=72, vol=0.85),
    "home":    dict(bpm=62, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}
PENTA = [0, 2, 4, 7, 9]


def tone(freq, dur, harmonics=((1, 1.0),), decay=0.0, a=0.01, r=0.05):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = sum(g * np.sin(TAU * freq * h * t) for h, g in harmonics)
    return x * env_adsr(n, a, r, decay)


def mood_table():
    return {**MOODS, **story.MOODS}


def music_section(dur, mood, seed):
    m = mood_table().get(mood, MOODS["garden"])
    rng = np.random.default_rng(seed)
    out = np.zeros(int(dur * SR) + SR * 3, np.float32)
    beat = 60.0 / m["bpm"]
    bar = 4 * beat
    nbars = int(np.ceil(dur / bar))
    for b in range(nbars):
        root, q = m["prog"][b % len(m["prog"])]
        t0 = b * bar
        # pad: chord tones, soft and wide
        for k, iv in enumerate(q):
            place(out, t0, tone(midi(root + iv), bar + 0.4, ((1, 1), (2, 0.25)), a=0.35, r=0.6), 0.045)
        # bass on 1 and 3
        for bt in (0, 2):
            place(out, t0 + bt * beat, tone(midi(root - 24), beat * 1.6, ((1, 1), (2, 0.3), (3, 0.1)),
                                            decay=2.0, a=0.01, r=0.15), 0.16)
        # melody: plucked pentatonic notes in eighths
        tonic = m["prog"][0][0] % 12
        for e in range(8):
            if rng.random() > m["mel"] * (1.0 if e % 2 == 0 else 0.55):
                continue
            if rng.random() < 0.5:
                pc = q[rng.integers(3)] + root % 12
            else:
                pc = PENTA[rng.integers(5)] + tonic
            note = m["oct"] + (pc % 12) - 12 * (rng.random() < 0.3)
            place(out, t0 + e * beat / 2,
                  tone(midi(note), 0.9, ((1, 1), (2, 0.35), (4, 0.12)), decay=4.5, a=0.004, r=0.1), 0.07)
        if m["drums"]:
            for bt in range(4):
                tt = t0 + bt * beat
                if bt in (0, 2):
                    n = int(0.25 * SR)
                    t = np.arange(n) / SR
                    kick = np.sin(TAU * np.cumsum(55 + 90 * np.exp(-t * 30)) / SR) * np.exp(-t * 14)
                    place(out, tt, kick, 0.22)
                for half in (0, 0.5):
                    n = int(0.06 * SR)
                    hat = band(rng.standard_normal(n), 6000, 14000) * env_adsr(n, 0.002, 0.04)
                    place(out, tt + half * beat, hat, 0.035 if half else 0.05)
    return out[:int(dur * SR)] * m["vol"]


def music(tl):
    """Whole-film music track: one section per scene, crossfaded."""
    sections = [(tl.scenes[s][0], story.MUSIC.get(s, s)) for s in story.SCENES]
    for event_id, frac, mood in story.MUSIC_CUES:
        sections.append((tl.t(event_id, frac), mood))
    sections.sort()
    track = np.zeros(_n(), np.float32)
    fade = 0.8
    for k, (start, mood) in enumerate(sections):
        end = sections[k + 1][0] if k + 1 < len(sections) else story.FILM_SECONDS
        a = max(0.0, start - fade / 2)
        x = music_section(end + fade / 2 - a, mood, seed=k * 7 + 3)
        n = len(x)
        f = int(fade * SR)
        ramp = np.ones(n, np.float32)
        ramp[:f] = np.linspace(0, 1, f) if k else 1
        ramp[-f:] *= np.linspace(1, 0, f)
        place(track, a, x * ramp)
    # gentle overall fade-in and fade-out at film edges
    if story.EDGE_FADES:
        track[:SR] *= np.linspace(0, 1, SR)
        track[-4 * SR:] *= np.linspace(1, 0, 4 * SR)
    return track


# ----------------------------------------------------------- sound effects

def sfx_meow(rng):
    d = 0.75
    n = int(d * SR)
    t = np.arange(n) / SR
    u = t / d
    f0 = 520 + 260 * np.sin(np.pi * np.minimum(1, u * 1.4)) - 140 * u + 12 * np.sin(TAU * 6 * t)
    ph = TAU * np.cumsum(f0) / SR
    bright = np.sin(np.pi * np.minimum(1, u * 1.3))      # "mee-OW" opening
    x = sum((1.0 / h) * (0.3 + 0.7 * bright * (h > 1)) * np.sin(h * ph) for h in range(1, 7))
    return x * env_adsr(n, 0.04, 0.25) * 0.5


def sfx_splash(rng):
    d = 1.4
    n = int(d * SR)
    t = np.arange(n) / SR
    body = band(rng.standard_normal(n), 200, 5000) * np.exp(-t * 4.5) * np.minimum(1, t / 0.01)
    x = body * 0.6
    for _ in range(14):
        dt = rng.uniform(0.15, 1.2)
        m = int(0.07 * SR)
        tt = np.arange(m) / SR
        f = rng.uniform(700, 1400) * (1 + 1.5 * tt / 0.07)
        drop = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-tt * 60)
        place(x, dt, drop, rng.uniform(0.15, 0.35))
    return x


def sfx_clink(rng):
    d = 0.8
    t = np.arange(int(d * SR)) / SR
    x = sum(g * np.sin(TAU * f * t) * np.exp(-t * k)
            for f, g, k in ((2093, 0.5, 6), (3390, 0.35, 9), (5230, 0.25, 14), (6800, 0.1, 20)))
    return x * np.minimum(1, t / 0.002) * 0.6


def sfx_whoosh(rng):
    d = 0.7
    n = int(d * SR)
    out = np.zeros(n)
    noise = rng.standard_normal(n)
    chunks = 14
    step = n // chunks
    for c in range(chunks):
        u = c / chunks
        lo = 300 + 1600 * np.sin(np.pi * u)
        seg = band(noise[c * step:(c + 1) * step + step], lo, lo * 2.2)
        w = np.hanning(len(seg))
        out[c * step:c * step + len(seg)] += (seg * w)[:n - c * step]
    t = np.arange(n) / SR
    return out * np.sin(np.pi * t / d) ** 2 * 0.5


def sfx_ribbit(rng):
    base = rng.uniform(170, 260)
    out = np.zeros(int(0.5 * SR))
    for k, start in enumerate((0.0, 0.2)):
        d = 0.14
        n = int(d * SR)
        t = np.arange(n) / SR
        carrier = np.sign(np.sin(TAU * base * (1 + 0.15 * k) * t)) * 0.5 + np.sin(TAU * base * 2 * t) * 0.3
        pulses = (np.sin(TAU * 42 * t) > 0).astype(float)
        x = band(carrier * pulses, 100, 2500) * env_adsr(n, 0.01, 0.04)
        place(out, start, x)
    return out * 0.6


def sfx_purr(rng):
    d = 3.0
    n = int(d * SR)
    t = np.arange(n) / SR
    rumble = band(rng.standard_normal(n), 40, 400)
    pulse = 0.5 + 0.5 * np.sin(TAU * 26 * t)
    breath = 0.35 + 0.65 * np.abs(np.sin(np.pi * t / 1.5))
    x = rumble * pulse ** 2 * breath * env_adsr(n, 0.3, 0.6)
    return x / (np.abs(x).max() + 1e-9) * 0.5


SFX = {"meow": sfx_meow, "splash": sfx_splash, "clink": sfx_clink,
       "whoosh": sfx_whoosh, "ribbit": sfx_ribbit, "purr": sfx_purr}
SFX_GAIN = {"meow": 0.7, "splash": 0.9, "clink": 0.5, "whoosh": 0.45, "ribbit": 0.5, "purr": 0.55}


def effects(tl):
    track = np.zeros(_n(), np.float32)
    rng = np.random.default_rng(11)
    table = {k: (fn, SFX_GAIN[k]) for k, fn in SFX.items()}
    table.update(story.EXTRA_SFX)
    for e in tl.events:
        for name, frac in e.sfx or []:
            fn, gain = table[name]
            place(track, e.start + e.dur * frac, fn(rng), gain)
    return track


# -------------------------------------------------------------------- mix

def mix(tl, path):
    N = _n()
    voice = np.zeros(N, np.float32)
    talking = np.zeros(N, np.float32)
    for start, x in tl.voices:
        place(voice, start, x)
        i = int(start * SR)
        talking[i:i + len(x)] = 1
    # duck the music under speech with smooth 0.3 s ramps
    k = int(0.3 * SR)
    c = np.cumsum(np.concatenate([np.zeros(k), talking, np.zeros(k)]))
    smooth = (c[2 * k:] - c[:-2 * k])[:N] / (2 * k)
    smooth = np.pad(smooth, (0, N - len(smooth)))
    duck = 1.0 - 0.6 * np.clip(smooth * 1.5, 0, 1)

    out = 0.95 * voice / (np.abs(voice).max() + 1e-9) + 0.42 * music(tl) * duck + 0.8 * effects(tl)
    out = np.tanh(out * 1.1) / np.tanh(1.1)          # soft limiter
    out = out / (np.abs(out).max() + 1e-9) * 0.93
    pcm = (out * 32767).astype(np.int16)
    stereo = np.repeat(pcm[:, None], 2, axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(stereo.tobytes())
    return len(pcm) / SR
