"""Record and check every line of a translated (LANG = "hy") story, keeping the best take of each.

    python3 tools/voice_check/check_voices.py interactive/pond_or_tree_hy      # all clips
    python3 tools/voice_check/check_voices.py interactive/pond_or_tree_hy --clips boat ending --tries 12

1. Each line is spoken with the film's voice engine (timeline.speak -> armenian_tts, cached in build/voices/).
2. Whisper (openai/whisper-large-v3-turbo, from huggingface.co) writes down what it hears; the letter error
   against the script is printed (0.00 = perfect; Whisper's own Armenian spelling makes ~0.05-0.15 normal).
3. Lines worse than --good are re-recorded with other seeds; the best take replaces the cached one.
4. out/<story>_all_lines.mp3 has every line in story order, for a native speaker to listen to.

Very short lines (one word) often score badly even when they sound fine: let a person listen to them.
Needs: pip install pocket-tts sentencepiece transformers (torch comes with pocket-tts).
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
import soundfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import armenian_tts as A  # noqa: E402
import film  # noqa: E402
import timeline  # noqa: E402


def letters(s):
    s = s.lower().replace("եւ", "և")
    return "".join(c for c in s if "ա" <= c <= "և")


def lev(a, b):
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (ca != cb))
    return d[-1]


_asr = None


def score(path, text):
    global _asr
    if _asr is None:
        import torch
        from transformers import pipeline
        _asr = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3-turbo",
                        torch_dtype=torch.float32, device="cpu")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    out = _asr({"raw": np.frombuffer(raw, np.float32), "sampling_rate": 16000},
               generate_kwargs={"language": "armenian", "task": "transcribe", "no_repeat_ngram_size": 4,
                                "repetition_penalty": 1.3, "num_beams": 3, "max_new_tokens": 120})["text"].strip()
    return lev(letters(text), letters(out)) / max(1, len(letters(text))), out


def cache_path(who, text):
    h = hashlib.sha1(f"pocket_hy|{film.CAST[who]}|{A.REFERENCE[who]}|{text}".encode()).hexdigest()[:16]
    return os.path.join(timeline.CACHE, f"hy_{who}_{h}.wav")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("story", help="e.g. interactive/pond_or_tree_hy")
    p.add_argument("--good", type=float, default=0.15, help="letter error that counts as good")
    p.add_argument("--tries", type=int, default=6, help="extra takes for a weak line")
    p.add_argument("--clips", nargs="*", help="only these clips (default: all)")
    a = p.parse_args()
    clips_dir = os.path.join(a.story, "clips")
    clips = sorted(c for c in os.listdir(clips_dir) if os.path.exists(os.path.join(clips_dir, c, "story.py")))
    order = json.load(open(os.path.join(a.story, "story.json")))["nodes"]
    clips.sort(key=lambda c: list(order).index(c) if c in order else 999)
    if a.clips:
        clips = [c for c in clips if c in a.clips]
    done, parts, scratch = set(), [], os.path.join(ROOT, "build", "voice_check")
    os.makedirs(scratch, exist_ok=True)
    for clip in clips:
        film.load(f"{a.story}/clips/{clip}")
        for e in film.SCRIPT:
            if not isinstance(e, film.Say) or (e.who, e.text) in done:
                continue
            done.add((e.who, e.text))
            timeline.speak(e.who, e.text, "kokoro")
            path = cache_path(e.who, e.text)
            first, heard = score(path, e.text)
            best = (first, path, heard)
            for k in range(1, a.tries + 1):
                if best[0] <= a.good:
                    break
                x = A.synth(e.who, e.text, lambda w, t: timeline.speak_english(w, t, "kokoro"),
                            seed=1000003 * k + len(e.text))
                alt = os.path.join(scratch, f"take{k}.wav")
                soundfile.write(alt + ".24k.wav", x, A.SR_MODEL)
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", alt + ".24k.wav", "-ac", "1", "-ar",
                                str(timeline.SR), "-sample_fmt", "s16", alt], check=True)
                c2, h2 = score(alt, e.text)
                if c2 < best[0]:
                    keep = os.path.join(scratch, f"best{k}.wav")
                    os.replace(alt, keep)
                    best = (c2, keep, h2)
            if best[1] != path:
                os.replace(best[1], path)
            flag = "" if best[0] <= a.good else "   <-- listen to this one"
            print(f"{clip:9} {e.who:9} {first:.2f}->{best[0]:.2f} | {e.text} | heard: {best[2]}{flag}", flush=True)
            parts += [timeline.trim_silence(timeline.read_wav(path)), np.zeros(int(0.7 * timeline.SR), np.float32)]
    name = a.story.strip("/").replace("/", "_")
    wav = os.path.join(scratch, f"{name}_all_lines.wav")
    soundfile.write(wav, np.concatenate(parts), timeline.SR)
    os.makedirs("out", exist_ok=True)
    mp3 = os.path.join("out", f"{name}_all_lines.mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-b:a", "128k", mp3], check=True)
    print("all lines:", mp3)


if __name__ == "__main__":
    main()
