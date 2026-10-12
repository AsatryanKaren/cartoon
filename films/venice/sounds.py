"""Extra synthesized sound effects for the Venice film (48 kHz float, numpy only)."""
import numpy as np

from audio import SR, band, env_adsr, place

TAU = 2 * np.pi


def _t(d):
    return np.arange(int(d * SR)) / SR


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def sfx_jingle(rng):
    """Luna's little silver bell: a few quick metallic tinkles."""
    out = np.zeros(int(0.9 * SR))
    for k in range(4):
        t = _t(0.5)
        f = 3100 * rng.uniform(0.97, 1.03)
        x = sum(g * np.sin(TAU * f * r * t) * np.exp(-t * kk)
                for r, g, kk in ((1, 0.6, 9), (1.48, 0.35, 13), (2.6, 0.2, 20)))
        place(out, k * 0.09 + rng.uniform(0, 0.03), x * np.minimum(1, t / 0.001), 0.5 - 0.08 * k)
    return out * 0.5


def sfx_ting(rng):
    """The bell pinging off the collar and rolling: tinkles getting quieter."""
    out = np.zeros(int(1.4 * SR))
    for k in range(7):
        t = _t(0.25)
        x = np.sin(TAU * 3000 * t) * np.exp(-t * 25) + 0.4 * np.sin(TAU * 4440 * t) * np.exp(-t * 35)
        place(out, 0.05 + k * (0.12 + 0.03 * k), x, 0.5 * 0.75 ** k)
    return out * 0.5


def sfx_crunch(rng):
    """Bell squashed under a cat: a short crumple."""
    d = 0.45
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 600, 7000) * np.exp(-t * 14)
    clicks = np.zeros(len(t))
    for _ in range(9):
        i = int(rng.uniform(0, 0.2) * SR)
        clicks[i:i + 40] += rng.uniform(-1, 1)
    thud = np.sin(TAU * 90 * t) * np.exp(-t * 18)
    return (x * 0.5 + band(clicks, 1000, 9000) * 0.8 + thud * 0.6) * 0.7


def sfx_clunk(rng):
    """The squashed bell: a dull, sad 'tunk'."""
    t = _t(0.4)
    x = np.sin(TAU * 420 * t) * np.exp(-t * 30) + 0.5 * np.sin(TAU * 610 * t) * np.exp(-t * 40)
    return x * np.minimum(1, t / 0.002) * 0.6


def sfx_click(rng):
    """Radio switching on: click + a little tuning whistle."""
    t = _t(0.7)
    x = np.zeros(len(t))
    x[:60] = np.hanning(60) * 0.9
    f = 900 + 1400 * np.exp(-t * 6)
    whistle = np.sin(TAU * np.cumsum(f) / SR) * 0.12 * env_adsr(len(t), 0.05, 0.3)
    hiss = band(rng.standard_normal(len(t)), 2000, 8000) * 0.08 * np.exp(-t * 5)
    return x + whistle + hiss


def sfx_burner(rng):
    """Balloon burner: a roaring whoosh of gas flame."""
    d = 1.3
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 80, 1800) + 0.4 * band(rng.standard_normal(len(t)), 1800, 5000)
    flick = 0.8 + 0.2 * np.sin(TAU * 13 * t)
    return x * flick * env_adsr(len(t), 0.05, 0.4) * 0.45


def sfx_wind(rng):
    """High-altitude wind, slow swells."""
    d = 3.5
    t = _t(d)
    out = np.zeros(len(t))
    noise = rng.standard_normal(len(t))
    for lo, hi, g in ((200, 600, 1.0), (500, 1200, 0.5)):
        out += band(noise, lo, hi) * g
    swell = 0.5 + 0.5 * np.sin(TAU * 0.4 * t - 1.2)
    return out * swell * env_adsr(len(t), 0.8, 1.2) * 0.4


def sfx_thump(rng):
    """Basket bumping onto the ground."""
    t = _t(0.4)
    x = np.sin(TAU * np.cumsum(70 + 60 * np.exp(-t * 25)) / SR) * np.exp(-t * 12)
    x += band(rng.standard_normal(len(t)), 300, 2500) * np.exp(-t * 30) * 0.4
    return x * 0.8


def sfx_coo(rng):
    """Pigeons cooing: a few soft 'roo-coo' warbles."""
    out = np.zeros(int(1.4 * SR))
    for k in range(3):
        d = 0.42
        t = _t(d)
        base = rng.uniform(320, 420)
        f = base * (1 + 0.25 * np.sin(np.pi * t / d)) * (1 + 0.03 * np.sin(TAU * 22 * t))
        ph = TAU * np.cumsum(f) / SR
        x = np.sin(ph) + 0.3 * np.sin(2 * ph)
        e = env_adsr(len(t), 0.05, 0.12) * (0.6 + 0.4 * (np.sin(TAU * t / d * 2) > 0))
        place(out, k * 0.38 + rng.uniform(0, 0.1), band(x * e, 150, 1600), 0.5)
    return out * 0.5


def sfx_flutter(rng):
    """Many wings taking off: noisy flaps."""
    d = 1.4
    out = np.zeros(int(d * SR))
    for _ in range(40):
        m = int(0.05 * SR)
        tt = np.arange(m) / SR
        flap = band(rng.standard_normal(m), 400, 4000) * np.sin(np.pi * tt / 0.05)
        place(out, rng.uniform(0, d - 0.06), flap, rng.uniform(0.2, 0.5))
    return out * env_adsr(len(out), 0.02, 0.5) * 0.7


def sfx_bubbles(rng):
    """Blub blub: rising bubble pops under water."""
    d = 1.2
    out = np.zeros(int(d * SR))
    for _ in range(10):
        m = int(0.08 * SR)
        tt = np.arange(m) / SR
        f = rng.uniform(250, 600) * (1 + 3 * tt / 0.08)
        b = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-tt * 40)
        place(out, rng.uniform(0, d - 0.1), b, rng.uniform(0.2, 0.5))
    return out * 0.7


def sfx_lap(rng):
    """Water lapping against a boat / stone."""
    d = 2.2
    out = np.zeros(int(d * SR))
    for k in range(4):
        m = int(0.5 * SR)
        tt = np.arange(m) / SR
        x = band(rng.standard_normal(m), 150, 1400) * np.sin(np.pi * tt / 0.5) ** 2
        place(out, k * 0.5 + rng.uniform(0, 0.1), x, 0.4)
    return out * 0.6


def sfx_song(rng):
    """The gondolier's song: a barcarolle phrase on a reedy voice-like tone."""
    notes = [(69, 0.45), (71, 0.15), (72, 0.3), (74, 0.3), (76, 0.9), (74, 0.3), (72, 0.3), (71, 0.3), (69, 1.0)]
    total = sum(d for _, d in notes) + 0.5
    out = np.zeros(int(total * SR))
    t0 = 0.0
    for n, d in notes:
        t = _t(d + 0.15)
        f = _midi(n - 12) * (1 + 0.012 * np.sin(TAU * 5.5 * t) * np.minimum(1, t / 0.2))
        ph = TAU * np.cumsum(f) / SR
        x = sum(g * np.sin(h * ph) for h, g in ((1, 1.0), (2, 0.5), (3, 0.35), (4, 0.15), (5, 0.1)))
        x = band(x, 150, 3000)
        place(out, t0, x * env_adsr(len(t), 0.05, 0.12), 0.35)
        t0 += d
    return out * 0.6


def sfx_roar(rng):
    """The glass furnace: a deep, steady roar of fire."""
    d = 2.8
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 40, 500) + 0.3 * band(rng.standard_normal(len(t)), 500, 2000)
    x *= 0.85 + 0.15 * np.sin(TAU * 3 * t) * np.sin(TAU * 0.7 * t)
    crack = np.zeros(len(t))
    for _ in range(8):
        i = int(rng.uniform(0, d - 0.05) * SR)
        crack[i:i + 80] += rng.uniform(-1, 1) * np.hanning(80)
    return (x * env_adsr(len(t), 0.4, 0.8) + crack * 0.4) * 0.4


def sfx_blow(rng):
    """Whiskers blowing hard into the blowpipe: puffy breath noise."""
    d = 1.0
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 300, 3500) * env_adsr(len(t), 0.15, 0.25)
    return x * (0.8 + 0.2 * np.sin(TAU * 7 * t)) * 0.5


def sfx_glassbell(rng):
    """The new Murano glass bell: pure, singing, slightly shimmering."""
    d = 2.2
    t = _t(d)
    f0 = 1568.0      # G6
    x = sum(g * np.sin(TAU * f0 * r * t + 0.3 * np.sin(TAU * 4 * t)) * np.exp(-t * k)
            for r, g, k in ((1.0, 1.0, 2.2), (2.0, 0.35, 3.0), (2.76, 0.25, 4.0), (1.003, 0.6, 2.4), (5.4, 0.1, 8)))
    return x * np.minimum(1, t / 0.002) * 0.3


def sfx_chime(rng):
    """Sparkly glass arpeggio."""
    out = np.zeros(int(1.8 * SR))
    for k, n in enumerate((84, 88, 91, 96, 100)):
        t = _t(1.0)
        x = np.sin(TAU * _midi(n) * t) * np.exp(-t * 5) + 0.3 * np.sin(TAU * _midi(n) * 2.7 * t) * np.exp(-t * 9)
        place(out, k * 0.09, x, 0.3)
    return out * 0.6


def sfx_bong(rng):
    """The big campanile bell: deep, long, inharmonic."""
    d = 3.5
    t = _t(d)
    f0 = 146.8      # D3
    x = sum(g * np.sin(TAU * f0 * r * t) * np.exp(-t * k)
            for r, g, k in ((0.5, 0.7, 0.8), (1.0, 1.0, 1.0), (1.2, 0.6, 1.4), (1.5, 0.4, 1.8), (2.0, 0.45, 2.0),
                            (2.5, 0.2, 3.0), (3.0, 0.15, 3.5)))
    x += band(rng.standard_normal(len(t)), 800, 4000) * np.exp(-t * 40) * 0.3
    return x * np.minimum(1, t / 0.004) * 0.35


def sfx_gull(rng):
    """A seagull's cry: two falling squeals."""
    out = np.zeros(int(1.1 * SR))
    for k in range(2):
        d = 0.35
        t = _t(d)
        f = (1700 - 700 * t / d) * rng.uniform(0.9, 1.1)
        ph = TAU * np.cumsum(f) / SR
        x = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sign(np.sin(ph))
        x = band(x, 600, 5000) * env_adsr(len(t), 0.03, 0.1)
        place(out, k * 0.4, x, 0.5 - 0.15 * k)
    return out * 0.4


EXTRA_SFX = {
    "jingle": (sfx_jingle, 0.5),
    "ting": (sfx_ting, 0.5),
    "crunch": (sfx_crunch, 0.8),
    "clunk": (sfx_clunk, 0.7),
    "click": (sfx_click, 0.6),
    "burner": (sfx_burner, 0.5),
    "wind": (sfx_wind, 0.45),
    "thump": (sfx_thump, 0.6),
    "coo": (sfx_coo, 0.55),
    "flutter": (sfx_flutter, 0.55),
    "bubbles": (sfx_bubbles, 0.6),
    "lap": (sfx_lap, 0.4),
    "song": (sfx_song, 0.7),
    "roar": (sfx_roar, 0.5),
    "blow": (sfx_blow, 0.55),
    "glassbell": (sfx_glassbell, 0.6),
    "chime": (sfx_chime, 0.45),
    "bong": (sfx_bong, 0.75),
    "gull": (sfx_gull, 0.4),
}
