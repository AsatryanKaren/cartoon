"""Extra synthesized sound effects for the Prague film (48 kHz float, numpy only).

Each function takes a numpy Generator and returns samples; EXTRA_SFX maps
name -> (function, gain).
"""
import numpy as np

from audio import SR, band, env_adsr, place

TAU = 2 * np.pi


def _t(d):
    return np.arange(int(d * SR)) / SR


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def _bell_note(f, d, decay=3.0, partials=((1, 1.0), (2.0, 0.5), (2.76, 0.35), (5.4, 0.15), (0.5, 0.3))):
    t = _t(d)
    x = sum(g * np.sin(TAU * f * r * t) * np.exp(-t * decay * (0.6 + 0.4 * r)) for r, g in partials)
    return x * np.minimum(1, t / 0.003)


def sfx_bells(rng):
    """Prague church bells ringing far away (a hundred spires!)."""
    out = np.zeros(int(4.0 * SR))
    notes = [62, 66, 69, 62, 74, 69]
    for k, n in enumerate(notes):
        place(out, k * 0.42 + rng.uniform(0, 0.05), _bell_note(_midi(n), 2.4, decay=1.6), 0.35)
    return band(out, 150, 6000) * 0.6


def sfx_jingle(rng):
    """Kasparek's hat bells: a quick shake of tiny bells."""
    out = np.zeros(int(0.8 * SR))
    for k in range(6):
        t = _t(0.35)
        f = rng.uniform(2600, 3600)
        x = sum(g * np.sin(TAU * f * r * t) * np.exp(-t * kk) for r, g, kk in ((1, 0.6, 12), (1.5, 0.3, 18)))
        place(out, k * 0.07 + rng.uniform(0, 0.03), x * np.minimum(1, t / 0.001), 0.5 - 0.05 * k)
    return out * 0.5


def sfx_crackle(rng):
    """A cosy fireplace: soft roar with random pops."""
    d = 3.0
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 80, 900) * 0.25
    for _ in range(40):
        i = int(rng.uniform(0, d - 0.05) * SR)
        m = int(rng.uniform(0.002, 0.008) * SR)
        x[i:i + m] += band(rng.standard_normal(m + 64), 1500, 9000)[:m] * rng.uniform(0.3, 1.0)
    return x * env_adsr(len(t), 0.4, 0.8) * 0.6


def sfx_rumble(rng):
    """Something tumbling down a brick chimney: bumpy low rumble."""
    d = 1.2
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 40, 500) * (0.6 + 0.4 * np.sin(TAU * 7 * t) ** 2)
    for k in range(5):
        tt = _t(0.2)
        place(x, k * 0.22 + rng.uniform(0, 0.05), np.sin(TAU * 80 * tt) * np.exp(-tt * 20), 0.8)
    return x * env_adsr(len(t), 0.05, 0.3) * 0.7


def sfx_poof(rng):
    """A big soft cloud of soot puffing out."""
    t = _t(0.9)
    x = band(rng.standard_normal(len(t)), 150, 2200) * np.exp(-t * 5) * np.minimum(1, t / 0.01)
    x += np.sin(TAU * np.cumsum(90 + 60 * np.exp(-t * 20)) / SR) * np.exp(-t * 10) * 0.6
    return x * 0.7


def sfx_clack(rng):
    """Wooden puppet limbs clacking: hollow knocks."""
    out = np.zeros(int(0.7 * SR))
    for k in range(4):
        t = _t(0.08)
        f = rng.uniform(700, 1100)
        x = np.sin(TAU * f * t) * np.exp(-t * 70) + 0.4 * np.sin(TAU * f * 2.3 * t) * np.exp(-t * 90)
        place(out, k * 0.12 + rng.uniform(0, 0.03), x, 0.7)
    return out


def sfx_pluck(rng):
    """A taut puppet string being plucked free: a little twang."""
    d = 0.6
    t = _t(d)
    f = rng.uniform(330, 520)
    x = sum((1 / h) * np.sin(TAU * f * h * t) * np.exp(-t * (6 + 3 * h)) for h in range(1, 6))
    return x * np.minimum(1, t / 0.002) * 0.5


def sfx_sparkle(rng):
    """Magic twinkle: a quick run of high pings."""
    out = np.zeros(int(1.0 * SR))
    for k in range(8):
        t = _t(0.3)
        f = _midi(84 + [0, 4, 7, 12, 16, 19, 24, 28][k])
        place(out, k * 0.06, np.sin(TAU * f * t) * np.exp(-t * 14), 0.35)
    return out


def sfx_ding(rng):
    """The skeleton's little bell: a bright, dry 'ding'."""
    x = _bell_note(1480 * rng.uniform(0.99, 1.01), 1.4, decay=4.0,
                   partials=((1, 1.0), (2.4, 0.4), (3.9, 0.2), (0.5, 0.1)))
    return x * 0.6


def sfx_lap(rng):
    """River water lapping against a wooden hull."""
    d = 2.2
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 150, 1200)
    sw = (0.5 + 0.5 * np.sin(TAU * 0.9 * t - 1.5)) ** 2
    return x * sw * env_adsr(len(t), 0.3, 0.6) * 0.35


def sfx_owl(rng):
    """A far-off owl in the snowy night: hoo... hoo-hoo."""
    out = np.zeros(int(1.6 * SR))
    for k, (st, d) in enumerate(((0.0, 0.45), (0.7, 0.2), (0.95, 0.45))):
        t = _t(d)
        f = 400 * (1 - 0.06 * t / d)
        x = np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 1.5
        place(out, st, x, 0.4)
    return out


def sfx_honk(rng):
    """A swan's soft trumpeting honk."""
    out = np.zeros(int(1.0 * SR))
    for k in range(2):
        d = 0.28
        t = _t(d)
        f = rng.uniform(420, 500) * (1 + 0.1 * np.sin(np.pi * t / d))
        ph = TAU * np.cumsum(f) / SR
        x = sum((1 / h) * np.sin(h * ph) for h in range(1, 8))
        x = band(x, 300, 3500) * env_adsr(len(t), 0.02, 0.08)
        place(out, k * 0.35, x, 0.5)
    return out


def sfx_accordion(rng):
    """A bouncy Czech polka on a street accordion (about 6 s)."""
    bpm = 132
    beat = 60 / bpm
    out = np.zeros(int(6.5 * SR))
    melody = [67, 71, 74, 71, 72, 69, 66, 69, 67, 71, 74, 79, 78, 74, 72, 69]
    chords = [(55, 59, 62), (50, 54, 57), (55, 59, 62), (50, 54, 57)]

    def reed(f, d):
        t = _t(d)
        x = np.zeros(len(t))
        for det in (0.996, 1.004):
            ph = TAU * f * det * t
            x += np.sign(np.sin(ph)) * 0.3 + np.sin(ph) * 0.5 + np.sin(2 * ph) * 0.2
        return band(x, 100, 5000) * env_adsr(len(t), 0.02, 0.06) * (0.85 + 0.15 * np.sin(TAU * 6 * t))

    for i, n in enumerate(melody):
        place(out, i * beat * 0.5 * 1.6, reed(_midi(n), beat * 0.7), 0.18)
    for b in range(10):
        ch = chords[b % 4]
        place(out, b * beat * 1.3, reed(_midi(ch[0] - 12), beat * 0.4), 0.16)
        for n in ch:
            place(out, b * beat * 1.3 + beat * 0.6, reed(_midi(n), beat * 0.3), 0.07)
    return out * env_adsr(len(out), 0.2, 1.0) * 0.8


def sfx_crunch(rng):
    """Footsteps on a snowy bridge."""
    out = np.zeros(int(1.4 * SR))
    for k in range(5):
        t = _t(0.14)
        x = band(rng.standard_normal(len(t)), 1500, 8000) * np.exp(-t * 30)
        place(out, k * 0.26 + rng.uniform(0, 0.04), x, 0.35)
    return out


def sfx_sniff(rng):
    """Three quick sniffs."""
    out = np.zeros(int(0.9 * SR))
    for k in range(3):
        t = _t(0.12)
        x = band(rng.standard_normal(len(t)), 1500, 6000) * np.sin(np.pi * t / 0.12)
        place(out, k * 0.2, x, 0.5)
    return out


def sfx_sizzle(rng):
    """Chimney cakes turning over hot coals: a sizzle with crackles."""
    d = 2.0
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 3000, 11000) * (0.6 + 0.4 * rng.random(len(t)) ** 8)
    return x * env_adsr(len(t), 0.2, 0.5) * 0.3


def sfx_munch(rng):
    """Crunchy, sugary munching."""
    out = np.zeros(int(1.0 * SR))
    for k in range(4):
        t = _t(0.12)
        x = band(rng.standard_normal(len(t)), 500, 6000) * np.exp(-t * 35)
        x += np.sin(TAU * 140 * t) * np.exp(-t * 40) * 0.5
        place(out, k * 0.21 + rng.uniform(0, 0.03), x, 0.6)
    return out


def sfx_pop(rng):
    """A cartoon 'pop' (a head going into a cake)."""
    t = _t(0.3)
    f = 300 + 900 * np.exp(-t * 25)
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 18)
    return x * 0.6


def sfx_yowl(rng):
    """A startled cat's 'MRAOW!'."""
    d = 0.6
    t = _t(d)
    u = t / d
    f = 600 + 500 * np.sin(np.pi * np.minimum(1, u * 1.6)) + 30 * np.sin(TAU * 9 * t)
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 8))
    return band(x, 200, 6000) * env_adsr(len(t), 0.02, 0.15) * 0.55


def sfx_tick(rng):
    """Old clockwork ticking: tick... tock... tick... tock."""
    out = np.zeros(int(2.4 * SR))
    for k in range(6):
        t = _t(0.05)
        f = 2400 if k % 2 == 0 else 1800
        x = np.sin(TAU * f * t) * np.exp(-t * 120) + band(rng.standard_normal(len(t)), 2000, 8000) * np.exp(-t * 150)
        place(out, k * 0.4, x, 0.5)
    return out


def sfx_clank(rng):
    """Gears jamming / unjamming: a heavy metal clank."""
    t = _t(0.8)
    x = sum(g * np.sin(TAU * f * t) * np.exp(-t * k)
            for f, g, k in ((180, 0.8, 8), (437, 0.5, 10), (1130, 0.3, 14), (2210, 0.2, 18)))
    x += band(rng.standard_normal(len(t)), 500, 5000) * np.exp(-t * 30) * 0.5
    return x * np.minimum(1, t / 0.002) * 0.6


def sfx_creak(rng):
    """A creaky old wooden door / wheel."""
    d = 0.9
    t = _t(d)
    f = 180 + 60 * np.sin(TAU * 1.3 * t)
    pulses = (np.sin(TAU * np.cumsum(f) / SR) > 0.85).astype(float)
    x = band(pulses * rng.standard_normal(len(t)) + pulses, 300, 3000)
    return x * env_adsr(len(t), 0.05, 0.2) * 0.4


def sfx_scrabble(rng):
    """Little claws scrabbling up stone."""
    out = np.zeros(int(0.8 * SR))
    for k in range(9):
        t = _t(0.03)
        x = band(rng.standard_normal(len(t)), 2500, 9000) * np.exp(-t * 120)
        place(out, k * 0.08 + rng.uniform(0, 0.02), x, 0.5)
    return out


def sfx_whirr(rng):
    """Gears spinning up: a rising whirr with ratchet clicks."""
    d = 1.5
    t = _t(d)
    f = 60 + 140 * (t / d)
    ph = TAU * np.cumsum(f) / SR
    clicks = (np.sin(ph) > 0.97).astype(float)
    x = band(clicks * 1.0, 1000, 8000) * 0.8 + np.sin(ph * 3) * 0.15
    return x * env_adsr(len(t), 0.1, 0.3) * 0.6


def sfx_chimes(rng):
    """Music-box chime of the clock's apostle parade."""
    out = np.zeros(int(2.4 * SR))
    tune = [79, 83, 86, 91, 86, 83, 81, 79]
    for k, n in enumerate(tune):
        t = _t(0.8)
        x = np.sin(TAU * _midi(n) * t) * np.exp(-t * 5) + 0.3 * np.sin(TAU * _midi(n) * 3 * t) * np.exp(-t * 9)
        place(out, k * 0.24, x, 0.3)
    return out


def sfx_crow(rng):
    """The golden rooster on the clock: cock-a-doodle-doo!"""
    out = np.zeros(int(1.6 * SR))
    for st, d, f0, f1 in ((0.0, 0.15, 700, 800), (0.18, 0.15, 800, 900), (0.36, 0.2, 900, 1000), (0.6, 0.6, 1000, 700)):
        t = _t(d)
        f = f0 + (f1 - f0) * t / d + 20 * np.sin(TAU * 30 * t)
        ph = TAU * np.cumsum(f) / SR
        x = sum((1 / h) * np.sin(h * ph) for h in range(1, 6))
        place(out, st, band(x, 400, 5000) * env_adsr(len(t), 0.02, 0.06), 0.5)
    return out


def sfx_cheer(rng):
    """A happy 'hooray' from the crowd."""
    d = 1.6
    t = _t(d)
    out = np.zeros(len(t))
    for k in range(12):
        f = rng.uniform(250, 600) * (1 + 0.2 * np.sin(np.pi * t / d))
        ph = TAU * np.cumsum(f) / SR
        out += band(np.sign(np.sin(ph)) * 0.5, 300, 3000) * rng.uniform(0.5, 1)
    out += band(rng.standard_normal(len(t)), 800, 4000) * 0.6
    return out / 12 * env_adsr(len(t), 0.15, 0.6) * 1.5


def sfx_laugh(rng):
    """Children giggling: quick bouncy 'ha-ha-ha' bursts."""
    out = np.zeros(int(1.6 * SR))
    for v in range(4):
        base = rng.uniform(350, 650)
        for k in range(5):
            t = _t(0.1)
            ph = TAU * np.cumsum(base * (1 - 0.15 * t / 0.1)) / SR
            x = band(np.sign(np.sin(ph)) * 0.5 + rng.standard_normal(len(t)) * 0.2, 300, 4000)
            place(out, v * 0.12 + k * 0.17 + rng.uniform(0, 0.03), x * np.sin(np.pi * t / 0.1), 0.25)
    return out


def sfx_applause(rng):
    """Many small paws clapping, swelling and fading."""
    d = 2.6
    out = np.zeros(int(d * SR))
    for _ in range(300):
        t = _t(0.02)
        x = band(rng.standard_normal(len(t)), 800, 6000) * np.exp(-t * 200)
        place(out, rng.uniform(0, d - 0.05), x, rng.uniform(0.1, 0.3))
    tt = _t(d)
    return out * np.sin(np.pi * tt / d) ** 0.7 * 0.8


def sfx_xylo(rng):
    """A wooden puppet-theatre fanfare on a xylophone."""
    out = np.zeros(int(2.0 * SR))
    for k, n in enumerate((72, 76, 79, 84, 79, 84)):
        t = _t(0.4)
        x = np.sin(TAU * _midi(n) * t) * np.exp(-t * 18) + 0.4 * np.sin(TAU * _midi(n) * 4 * t) * np.exp(-t * 40)
        place(out, k * 0.15 + (0.15 if k >= 4 else 0), x, 0.45)
    return out


EXTRA_SFX = {
    "bells": (sfx_bells, 0.4), "jingle": (sfx_jingle, 0.4), "crackle": (sfx_crackle, 0.4),
    "rumble": (sfx_rumble, 0.6), "poof": (sfx_poof, 0.6), "clack": (sfx_clack, 0.45), "pluck": (sfx_pluck, 0.4),
    "sparkle": (sfx_sparkle, 0.4), "ding": (sfx_ding, 0.45), "lap": (sfx_lap, 0.45), "owl": (sfx_owl, 0.35),
    "honk": (sfx_honk, 0.4), "accordion": (sfx_accordion, 0.7), "crunch": (sfx_crunch, 0.35),
    "sniff": (sfx_sniff, 0.45), "sizzle": (sfx_sizzle, 0.35), "munch": (sfx_munch, 0.5), "pop": (sfx_pop, 0.5),
    "yowl": (sfx_yowl, 0.6), "tick": (sfx_tick, 0.4), "clank": (sfx_clank, 0.55), "creak": (sfx_creak, 0.4),
    "scrabble": (sfx_scrabble, 0.4), "whirr": (sfx_whirr, 0.45), "chimes": (sfx_chimes, 0.5),
    "crow": (sfx_crow, 0.45), "cheer": (sfx_cheer, 0.5), "laugh": (sfx_laugh, 0.5),
    "applause": (sfx_applause, 0.6), "xylo": (sfx_xylo, 0.45),
}
