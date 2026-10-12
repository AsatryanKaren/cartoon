import hashlib
import os
import subprocess
import wave

import numpy as np

from story import SCRIPT, VOICES

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, 'build')
TTS_DIR = os.path.join(BUILD, 'tts')
FPS = 24
DURATION = 355.0
SR = 48000
LEAD, TAIL, GAP = 0.8, 0.8, 0.45


def read_wav(path):
    with wave.open(path) as w:
        n = w.getnframes()
        sr = w.getframerate()
        ch = w.getnchannels()
        data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1:
        data = data.reshape(-1, ch).mean(axis=1)
    assert sr == SR, (path, sr)
    return data


def tts(ch, text):
    voice, rate = VOICES[ch]
    os.makedirs(TTS_DIR, exist_ok=True)
    key = hashlib.md5(f'{voice}|{rate}|{text}'.encode()).hexdigest()[:16]
    path = os.path.join(TTS_DIR, f'{ch}_{key}.wav')
    if not os.path.exists(path):
        subprocess.run(['say', '-v', voice, '-r', str(rate), '--file-format=WAVE',
                        f'--data-format=LEI16@{SR}', '-o', path, text], check=True)
    a = read_wav(path)
    # trim silence so mouths do not move during pauses
    idx = np.nonzero(np.abs(a) > 0.01)[0]
    if len(idx):
        a = a[max(0, idx[0] - 200): idx[-1] + 2000]
    peak = np.abs(a).max() or 1
    return a * (0.85 / peak)


def envelope(a):
    hop = SR // FPS
    n = int(np.ceil(len(a) / hop))
    pad = np.zeros(n * hop, dtype=np.float32)
    pad[:len(a)] = a
    rms = np.sqrt((pad.reshape(n, hop) ** 2).mean(axis=1))
    ref = np.percentile(rms, 90) or 1
    return np.clip(rms / ref, 0, 1)


class Scene:
    def __init__(self, sid, start, dur, lines, marks):
        self.id, self.start, self.dur, self.lines, self.marks = sid, start, dur, lines, marks

    @property
    def end(self):
        return self.start + self.dur

    def s(self, name):
        return self.marks[name][0]

    def e(self, name):
        return self.marks[name][1]

    def p(self, name, t):
        s, e = self.marks[name]
        if e <= s:
            return float(t >= s)
        return min(1.0, max(0.0, (t - s) / (e - s)))

    def inside(self, name, t):
        s, e = self.marks[name]
        return s <= t < e

    def mouth(self, ch, t):
        for ln in self.lines:
            if ln['ch'] == ch and ln['s'] <= t < ln['s'] + ln['dur']:
                env = ln['env']
                return float(env[min(len(env) - 1, int((t - ln['s']) * FPS))])
        return 0.0

    def line_at(self, t):
        for ln in self.lines:
            if ln['s'] - 0.1 <= t < ln['s'] + ln['dur'] + 0.3:
                return ln
        return None

    def time_in(self, names, t):
        total = 0.0
        for n in names:
            s, e = self.marks[n]
            total += min(max(t - s, 0.0), e - s)
        return total


def build():
    audio = {}
    fixed, weights = 0.0, 0.0
    for sc in SCRIPT:
        fixed += LEAD + TAIL
        for it in sc['items']:
            if it[0] == 'act':
                weights += it[2]
            else:
                a = tts(it[0], it[1])
                audio[(it[0], it[1])] = a
                fixed += len(a) / SR + GAP
    rem = DURATION - fixed
    if rem <= 0:
        raise SystemExit(f'speech is {fixed:.1f}s, longer than {DURATION}s')
    unit = rem / weights

    scenes, t0 = [], 0.0
    for sc in SCRIPT:
        t = LEAD
        lines, marks = [], {}
        for it in sc['items']:
            if it[0] == 'act':
                d = it[2] * unit
                marks[it[1]] = (t, t + d)
                t += d
            else:
                a = audio[(it[0], it[1])]
                d = len(a) / SR
                lines.append({'ch': it[0], 'text': it[1], 's': t, 'dur': d,
                              'audio': a, 'env': envelope(a)})
                if len(it) > 2:
                    marks[it[2]] = (t, t + d + GAP)
                t += d + GAP
        t += TAIL
        scenes.append(Scene(sc['id'], t0, t, lines, marks))
        t0 += t
    # absorb rounding so the total is exactly DURATION
    scenes[-1].dur += DURATION - t0
    return scenes, unit, fixed
