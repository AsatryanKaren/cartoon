"""Athens sound effects, synthesised with numpy (48 kHz mono float).

Each function takes a numpy Generator and returns samples; EXTRA_SFX maps
names to (function, gain). The bouzouki is a doubled, slightly detuned
Karplus-Strong string playing a little tremolo riff in a Greek (hijaz) mode.
The theatre echoes re-use the film's own cached speech.
"""
import numpy as np

SR = 48000
TAU = 2 * np.pi


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a, r, decay=0.0):
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / max(a, 1e-4)) * np.minimum(1.0, (n / SR - t) / max(r, 1e-4))
    if decay:
        e *= np.exp(-t * decay)
    return e


def _band(x, lo, hi):
    f = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, len(x))


def _place(buf, start, x, gain=1.0):
    i = int(start * SR)
    j = min(len(buf), i + len(x))
    if 0 <= i < len(buf):
        buf[i:j] += gain * x[:j - i]


def _norm(x, peak=0.6):
    return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ------------------------------------------------------------- bouzouki

def _string(rng, freq, dur, damp=0.997):
    """Karplus-Strong plucked string (vectorised one period at a time)."""
    n = int(dur * SR)
    p = max(2, int(round(SR / freq)))
    y = np.zeros(n + p + 1)
    y[:p] = rng.uniform(-1, 1, p)
    k = p
    while k < n + p:
        m = min(p, n + p - k)
        y[k:k + m] = damp * 0.5 * (y[k - p:k - p + m] + y[k - p + 1:k - p + m + 1])
        k += m
    return y[p:p + n]


def _bouzouki_note(rng, note, dur):
    f = _midi(note)
    x = _string(rng, f, dur, 0.996) + 0.8 * _string(rng, f * 1.004, dur, 0.996)   # doubled course
    x += 0.35 * _string(rng, f * 2.002, dur, 0.993)                                 # octave string
    return _band(x, 180, 9000) * _env(len(x), 0.002, 0.06)


def sfx_bouzouki(rng):
    """A bright tremolo riff: D hijaz (D Eb F# G A Bb C D)."""
    scale = [62, 63, 66, 67, 69, 70, 72, 74]
    riff = [(4, 0.25), (5, 0.25), (4, 0.25), (3, 0.25), (2, 0.25), (3, 0.25), (1, 0.25), (0, 0.6),
            (2, 0.25), (3, 0.25), (4, 0.5), (7, 0.9)]
    out = np.zeros(int(4.6 * SR))
    t0 = 0.0
    for deg, d in riff:
        note = scale[deg] + 12
        if d >= 0.5:                              # long notes are tremolo-picked
            k = 0
            while k * 0.07 < d:
                _place(out, t0 + k * 0.07, _bouzouki_note(rng, note, 0.25), 0.5 if k else 0.8)
                k += 1
        else:
            _place(out, t0, _bouzouki_note(rng, note, d + 0.3), 0.8)
        t0 += d
    return _norm(out, 0.6)


# ------------------------------------------------------------------ owls

def _hoo(f0, d):
    t = _t(d)
    u = t / d
    f = f0 * (1 + 0.08 * np.sin(np.pi * u) - 0.06 * u)
    ph = TAU * np.cumsum(f) / SR
    x = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    return x * _env(len(t), 0.05, 0.12) * (0.6 + 0.4 * np.sin(np.pi * u))


def sfx_hoot(rng):
    """Soft owl call: hoo... hoo-hoo."""
    out = np.zeros(int(1.6 * SR))
    f = rng.uniform(560, 640)
    _place(out, 0.0, _hoo(f, 0.42), 0.8)
    _place(out, 0.62, _hoo(f * 1.03, 0.2), 0.6)
    _place(out, 0.86, _hoo(f, 0.5), 0.7)
    return _norm(out, 0.5)


def sfx_flap(rng):
    """Wing beats: soft feathery thumps."""
    out = np.zeros(int(1.0 * SR))
    for k in range(4):
        n = int(0.12 * SR)
        x = _band(rng.standard_normal(n), 150, 2500) * _env(n, 0.01, 0.08, 18)
        _place(out, k * 0.2, x, 1.0 - 0.15 * k)
    return _norm(out, 0.5)


# --------------------------------------------------------------- weather

def sfx_rain(rng):
    d = 6.0
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 1200, 9000) * 0.4
    for _ in range(260):                          # individual drops on the glass
        m = int(0.02 * SR)
        drop = _band(rng.standard_normal(m), 2000, 8000) * np.exp(-np.arange(m) / SR * 220)
        _place(x, rng.uniform(0, d - 0.05), drop, rng.uniform(0.3, 1.0))
    return _norm(x * _env(len(t), 0.8, 1.6), 0.45)


def sfx_thunder(rng):
    d = 3.2
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 25, 300)
    crack = _band(rng.standard_normal(len(t)), 300, 4000) * np.exp(-t * 9)
    rumble = x * (np.exp(-t * 1.1) * (0.6 + 0.4 * np.sin(TAU * 1.7 * t) ** 2))
    return _norm(rumble + 0.5 * crack, 0.75)


def sfx_thump(rng):
    """A small soft body bumping the window glass, then a rattle."""
    d = 0.6
    t = _t(d)
    x = np.sin(TAU * 90 * t) * np.exp(-t * 22) + 0.4 * _band(rng.standard_normal(len(t)), 300, 3000) * np.exp(-t * 30)
    rattle = sum(np.sin(TAU * f * t) * np.exp(-t * 25) for f in (1900, 2700, 3400)) * 0.15
    return _norm(x + rattle, 0.7)


def sfx_page(rng):
    """A page turning."""
    d = 0.45
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 1500, 9000) * np.sin(np.pi * t / d) ** 2
    return _norm(x * (0.6 + 0.4 * np.sin(TAU * 11 * t)), 0.35)


def sfx_sparkle(rng):
    out = np.zeros(int(1.6 * SR))
    for k in range(9):
        f = _midi(rng.choice([86, 88, 91, 93, 98]))
        tt = _t(0.6)
        _place(out, k * 0.11 + rng.uniform(0, 0.04), np.sin(TAU * f * tt) * np.exp(-tt * 9), 0.5)
    return _norm(out, 0.4)


# --------------------------------------------------------------- travel

def sfx_hum(rng):
    """Airship engines: a low propeller drone with a gentle throb."""
    d = 3.0
    t = _t(d)
    x = sum(g * np.sin(TAU * f * t) for f, g in ((62, 1.0), (124, 0.5), (186, 0.25)))
    x *= 0.7 + 0.3 * np.sin(TAU * 7 * t)
    x += 0.3 * _band(rng.standard_normal(len(t)), 80, 700)
    return _norm(x * _env(len(t), 0.6, 0.9), 0.4)


def _gull(rng, f0, d):
    t = _t(d)
    u = t / d
    f = f0 * (1 + 0.35 * np.sin(np.pi * u)) * (1 - 0.25 * u)
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 6))
    return _band(x, 500, 6000) * _env(len(t), 0.02, 0.1)


def sfx_gulls(rng):
    out = np.zeros(int(2.4 * SR))
    for _ in range(4):
        _place(out, rng.uniform(0, 1.9), _gull(rng, rng.uniform(1100, 1600), rng.uniform(0.2, 0.35)),
               rng.uniform(0.3, 0.7))
    return _norm(out, 0.4)


def sfx_cicada(rng):
    """Summer cicadas buzzing in the trees."""
    d = 4.0
    t = _t(d)
    buzz = np.sin(TAU * 4200 * t) * (0.5 + 0.5 * np.sign(np.sin(TAU * 38 * t)))
    buzz = _band(buzz + 0.3 * rng.standard_normal(len(t)), 3000, 7000)
    swell = 0.4 + 0.6 * np.sin(np.pi * t / d)
    return _norm(buzz * swell * _env(len(t), 0.5, 1.0), 0.18)


def sfx_crickets(rng):
    d = 4.0
    out = np.zeros(int(d * SR))
    for k in range(10):
        n = int(0.18 * SR)
        tt = np.arange(n) / SR
        chirp = np.sin(TAU * 4600 * tt) * (np.sin(TAU * 30 * tt) > 0) * _env(n, 0.01, 0.03)
        _place(out, k * 0.38 + rng.uniform(0, 0.05), chirp, rng.uniform(0.5, 1.0))
    return _norm(out, 0.2)


def sfx_chime(rng):
    """Magic moonrise shimmer."""
    out = np.zeros(int(2.6 * SR))
    for k, n in enumerate((74, 78, 81, 86)):
        tt = _t(1.8)
        x = np.sin(TAU * _midi(n) * tt) * np.exp(-tt * 2.5) + 0.3 * np.sin(TAU * _midi(n) * 2.76 * tt) * np.exp(-tt * 5)
        _place(out, k * 0.22, x, 0.5)
    return _norm(out, 0.45)


# ----------------------------------------------------------------- food

def sfx_sniff(rng):
    out = np.zeros(int(1.0 * SR))
    for k in range(3):
        n = int(0.14 * SR)
        x = _band(rng.standard_normal(n), 1200, 6000) * np.sin(np.pi * np.arange(n) / n) ** 2
        _place(out, k * 0.22, x, 1.0)
    return _norm(out, 0.35)


def sfx_splat(rng):
    """Face-first into a bowl of thick yogurt."""
    d = 0.7
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 80, 1500) * np.exp(-t * 12)
    x += np.sin(TAU * np.cumsum(180 - 120 * t) / SR) * np.exp(-t * 10) * 0.8
    for _ in range(6):                             # sticky little blobs
        m = int(0.05 * SR)
        tt = np.arange(m) / SR
        blob = np.sin(TAU * np.cumsum(rng.uniform(300, 700) * (1 + 3 * tt)) / SR) * np.exp(-tt * 70)
        _place(x, rng.uniform(0.08, 0.5), blob, 0.3)
    return _norm(x, 0.7)


def sfx_lick(rng):
    d = 0.25
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 600, 4000) * np.sin(np.pi * t / d) ** 3
    return _norm(x, 0.3)


# ---------------------------------------------------------------- echoes

def _speech(who, text):
    import timeline
    return timeline.speak(who, text, timeline.tts_backend("auto")).astype(np.float64)


def _echo(x, delays, gains, lo=200, hi=3200, tail=0.0):
    x = _band(np.concatenate([x, np.zeros(int(0.2 * SR))]), lo, hi)
    if tail:
        x = x[int(len(x) * tail):]
    n = int((delays[-1] + 0.3) * SR) + len(x)
    out = np.zeros(n)
    for d, g in zip(delays, gains):
        _place(out, d, x, g)
    return out.astype(np.float32)


def sfx_echo_hello(rng):
    """The theatre throws Whiskers' 'Hello!' back three times."""
    return _norm(_echo(_speech("whiskers", "Hello!"), (0.0, 0.45, 0.9), (0.8, 0.45, 0.22)), 0.6)


def sfx_echo_dont(rng):
    """'...don't... don't' rolling around the stone seats."""
    return _norm(_echo(_speech("socrates", "No, you don't."), (0.0, 0.42, 0.84), (0.75, 0.4, 0.2),
                       tail=0.45), 0.55)


EXTRA_SFX = {
    "bouzouki": (sfx_bouzouki, 0.55),
    "hoot": (sfx_hoot, 0.55),
    "flap": (sfx_flap, 0.5),
    "rain": (sfx_rain, 0.55),
    "thunder": (sfx_thunder, 0.7),
    "thump": (sfx_thump, 0.7),
    "page": (sfx_page, 0.5),
    "sparkle": (sfx_sparkle, 0.45),
    "hum": (sfx_hum, 0.5),
    "gulls": (sfx_gulls, 0.45),
    "cicada": (sfx_cicada, 0.4),
    "crickets": (sfx_crickets, 0.4),
    "chime": (sfx_chime, 0.5),
    "sniff": (sfx_sniff, 0.5),
    "splat": (sfx_splat, 0.7),
    "lick": (sfx_lick, 0.5),
    "echo_hello": (sfx_echo_hello, 0.75),
    "echo_dont": (sfx_echo_dont, 0.75),
}
