import math
import wave

import numpy as np

from timeline import DURATION, SR, tts

N = int(DURATION * SR)
NOTE = {'C': 261.63, 'D': 293.66, 'E': 329.63, 'F': 349.23, 'G': 392.0, 'A': 440.0, 'B': 493.88}
CHORDS = {
    'C': ('C', 'E', 'G'), 'G': ('G', 'B', 'D'), 'Am': ('A', 'C', 'E'), 'F': ('F', 'A', 'C'),
    'Dm': ('D', 'F', 'A'), 'Em': ('E', 'G', 'B'),
}
MOODS = {
    'title': (['F', 'C', 'G', 'Am'], 3.2, 0.4, 0.8),
    'day': (['C', 'G', 'Am', 'F'], 2.4, 0.3, 1.0),
    'play': (['C', 'F', 'G', 'C'], 2.0, 0.25, 1.0),
    'dusk': (['Am', 'F', 'C', 'G'], 2.8, 0.35, 0.9),
    'night': (['Am', 'Em', 'F', 'C'], 3.4, 0.425, 0.7),
    'warm': (['F', 'C', 'Dm', 'G'], 3.2, 0.4, 0.8),
}
SCENE_MOOD = {'title': 'title', 'morning': 'day', 'legend': 'day', 'garden': 'play',
              'meadow': 'dusk', 'pond': 'night', 'realize': 'night', 'home': 'warm'}


def tone(f, n, harm=((1, 1.0), (2, 0.25), (3, 0.1))):
    t = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * k * t) for k, a in harm)


def music_segment(n, mood):
    prog, chord_len, step, oct_ = MOODS[mood]
    out = np.zeros(n, np.float32)
    cl = int(chord_len * SR)
    i = 0
    for pos in range(0, n, cl):
        ln = min(cl, n - pos)
        names = CHORDS[prog[i % len(prog)]]
        freqs = [NOTE[x] * oct_ for x in names]
        t = np.arange(ln) / SR
        env = np.minimum(1, t / 0.4) * np.minimum(1, (ln / SR - t) / 0.6 + 0.05)
        pad = sum(tone(f * 0.5, ln, ((1, 1), (2, 0.12))) for f in freqs) * env * 0.09
        bass = tone(freqs[0] * 0.25, ln, ((1, 1), (2, 0.3))) * np.exp(-t * 1.2) * 0.22
        out[pos:pos + ln] += pad + bass
        seq = freqs + [f * 2 for f in freqs]
        st = int(step * SR)
        for j, p in enumerate(range(0, ln, st)):
            m = min(st * 3, ln - p)
            tt = np.arange(m) / SR
            f = seq[(j * 2 + (j // 3)) % len(seq)] * (2 if j % 4 == 3 else 1)
            out[pos + p:pos + p + m] += tone(f, m, ((1, 1), (2, 0.3), (4, 0.05))) * np.exp(-tt * 5) * 0.07
        i += 1
    fade = int(0.6 * SR)
    out[:fade] *= np.linspace(0, 1, fade)
    out[-fade:] *= np.linspace(1, 0, fade)
    return out


def meow(f0=600, dur=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.35 * np.sin(np.pi * t / dur)) * (1 + 0.012 * np.sin(2 * np.pi * 6 * t))
    ph = np.cumsum(f) / SR
    s = sum(np.sin(2 * np.pi * k * ph) / k ** 1.1 * (1.6 if k in (2, 3) else 1) for k in range(1, 7))
    env = np.sin(np.pi * t / dur) ** 0.7
    return (s * env * 0.18).astype(np.float32)


def noise_lp(n, k, seed=0):
    rnd = np.random.default_rng(seed)
    x = rnd.standard_normal(n + k).astype(np.float32)
    c = np.cumsum(x)
    return (c[k:] - c[:-k]) / k


def splash():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    s = noise_lp(n, 6, 1) * np.exp(-t * 3) * 0.9
    rnd = np.random.default_rng(2)
    for _ in range(10):
        p = int(rnd.uniform(0.1, 1.3) * SR)
        m = int(0.06 * SR)
        tt = np.arange(m) / SR
        f = np.linspace(400, 1300, m)
        s[p:p + m] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 40) * 0.25
    return s.astype(np.float32)


def clink():
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * 2100 * t) + 0.6 * np.sin(2 * np.pi * 3170 * t)) * np.exp(-t * 9) * 0.15
    s[int(0.18 * SR):] += s[:n - int(0.18 * SR)] * 0.6
    return s.astype(np.float32)


def whoosh():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    return (noise_lp(n, 18, 3) * np.sin(np.pi * t / 0.45) ** 2 * 0.5).astype(np.float32)


def pop():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = np.linspace(300, 1000, n)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 25) * 0.3).astype(np.float32)


def ding():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    return ((np.sin(2 * np.pi * 1320 * t) + 0.4 * np.sin(2 * np.pi * 1980 * t)) * np.exp(-t * 3) * 0.1).astype(np.float32)


def ribbit():
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    buzz = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.5 + np.sin(2 * np.pi * 330 * t)
    gate = ((t < 0.13) | ((t > 0.2) & (t < 0.36))).astype(np.float32)
    s = buzz * gate
    k = 12
    c = np.cumsum(np.concatenate([np.zeros(k), s]))
    return ((c[k:] - c[:-k]) / k * 0.12).astype(np.float32)


def purr(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    am = (0.5 + 0.5 * np.sin(2 * np.pi * 24 * t)) ** 2
    s = noise_lp(n, 60, 5) * am * 1.6
    env = np.minimum(1, t / 2) * np.minimum(1, (dur - t) / 2)
    return (s * env * 0.25).astype(np.float32)


def sfx_for(sc):
    out = []
    if sc.id == 'morning':
        out += [(sc.s('stretch') + 0.1, meow(430, 0.9), 0.8),
                (sc.s('stretch') + (sc.e('stretch') - sc.s('stretch')) * 0.45, whoosh(), 0.6),
                (sc.e('bowl') - 0.4, clink(), 1.0)]
    elif sc.id == 'legend':
        out += [(sc.s('think') + 0.2, ding(), 1.0), (sc.s('meow') + 0.2, meow(540, 0.7), 1.0),
                (sc.s('meow') + 0.75, meow(720, 0.6), 1.0)]
    elif sc.id == 'garden':
        out.append((sc.s('chase') + 0.1, whoosh(), 0.7))
        s, e = sc.marks['fence']
        for x in (600, 420):
            k = (1450 - x) / 1700
            out.append((s + k * (e - s) - 0.35, whoosh(), 0.6))
    elif sc.id == 'meadow':
        out.append((0.35, pop(), 1.0))
    elif sc.id == 'pond':
        s, e = sc.marks['pounce']
        out += [(s + (e - s) * 0.35, whoosh(), 0.8), (e - 0.05, splash(), 1.0)]
    elif sc.id == 'realize':
        s = sc.s('laugh')
        for i, ch in enumerate(('W', 'L', 'P')):
            out.append((s + 0.6 + i * 0.35, tts(ch, 'Ha ha ha ha!'), 0.75))
        out += [(s + 1.2, ribbit(), 1.0), (s + 2.6, ribbit(), 0.8), (sc.e('laugh') + 0.3, ribbit(), 0.9)]
    elif sc.id == 'home':
        st = sc.e('walkhome') + 1.5
        out.append((st, purr(sc.dur - st - 1), 1.0))
    return out


def place(buf, start_s, sig, gain=1.0):
    p = int(round(start_s * SR))
    if p >= len(buf):
        return
    m = min(len(sig), len(buf) - p)
    buf[p:p + m] += sig[:m] * gain


def build_audio(scenes, path):
    speech = np.zeros(N, np.float32)
    music = np.zeros(N, np.float32)
    fx = np.zeros(N, np.float32)
    active = np.zeros(N, np.float32)
    for sc in scenes:
        a = int(round(sc.start * SR))
        b = min(N, int(round(sc.end * SR)) + int(0.3 * SR))
        seg = music_segment(b - a, SCENE_MOOD[sc.id])
        music[a:b] += seg
        for ln in sc.lines:
            place(speech, sc.start + ln['s'], ln['audio'])
            p0 = int((sc.start + ln['s'] - 0.15) * SR)
            active[max(0, p0):p0 + len(ln['audio']) + int(0.4 * SR)] = 1
        for t, sig, g in sfx_for(sc):
            place(fx, sc.start + t, sig, g)
    k = int(0.35 * SR)
    c = np.cumsum(np.concatenate([np.zeros(k, np.float32), active]))
    duck = (c[k:] - c[:-k]) / k
    mix = speech * 0.9 + music * (0.55 - 0.33 * duck) + fx
    mix = np.tanh(mix * 1.1) / math.tanh(1.1)
    mix *= 0.92 / max(1e-6, np.abs(mix).max())
    end = int(1.5 * SR)
    mix[-end:] *= np.linspace(1, 0, end)
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
