"""Armenian speech for films whose story.py sets LANG = "hy".

Engine: Kyutai Pocket TTS fine-tuned for Eastern Armenian (huggingface.co/mnjoyan/pocket-tts-armenian,
CC-BY-4.0), run on the CPU. It clones a voice from a short reference clip, so every character keeps
his own voice: the reference is the character's usual English (Kokoro) voice from common.CAST.

    build/models/pocket_hy/            <- the model folder (see download_model())
        configs/english_2026-09_24l.yaml, configs/hy_text.py, configs/hy_itn.py
        run4_60k/model.safetensors, run4_60k/tokenizer_hy.model
"""
import hashlib
import importlib.util
import os
import subprocess

import numpy as np

import film as story

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(HERE, "build", "models", "pocket_hy")
REPO = "https://huggingface.co/mnjoyan/pocket-tts-armenian/resolve/main"
FILES = ["configs/english_2026-09_24l.yaml", "configs/hy_text.py", "configs/hy_itn.py",
         "run4_60k/model.safetensors", "run4_60k/tokenizer_hy.model"]
CACHE = os.path.join(HERE, "build", "voices")
SR_MODEL = 24000

# What each character says (in English, with his usual voice) to give the Armenian model his voice.
REFERENCE = {
    "narrator": "Once upon a time, in a little house with a green garden, there lived two cats and one brave mouse.",
    "whiskers": "Watch this, Luna. My super-duper mega kick! Uh oh. Where did my ball go?",
    "luna": "It flew far, far away! Maybe it landed by the pond. Or maybe up in the big tree!",
    "pip": "Hello, friends! Need some help? Leave it to me! I'm the bravest mouse in the meadow!",
    "frog": "Ribbit! Are you looking for a big red ball? It bounced on my lily pad. Boing!",
    "bird": "Tweet! Hello! I saw it from up here! It bounced down the hill, all the way to the river!",
}

_model = None
_states = {}
_text = None


def download_model():
    for f in FILES:
        path = os.path.join(MODEL_DIR, f)
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            subprocess.run(["curl", "-sSfL", "-o", path + ".part", f"{REPO}/{f}"], check=True)
            os.replace(path + ".part", path)


def _load():
    global _model, _text
    if _model is not None:
        return
    download_model()
    import yaml
    from pocket_tts import TTSModel
    cfg = yaml.safe_load(open(os.path.join(MODEL_DIR, FILES[0])))
    cfg["weights_path"] = os.path.join(MODEL_DIR, "run4_60k/model.safetensors")
    cfg["flow_lm"]["lookup_table"]["tokenizer"] = "sentencepiece"
    cfg["flow_lm"]["lookup_table"]["tokenizer_path"] = os.path.join(MODEL_DIR, "run4_60k/tokenizer_hy.model")
    cfg.pop("weights_path_without_voice_cloning", None)
    path = os.path.join(MODEL_DIR, "cfg_hy.yaml")
    with open(path, "w") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)
    _model = TTSModel.load_model(config=path)
    spec = importlib.util.spec_from_file_location("hy_text", os.path.join(MODEL_DIR, "configs/hy_text.py"))
    _text = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_text)


def normalise(text):
    """Armenian text the way the model was trained on it."""
    _load()
    return _text.normalise(text)


def _reference(who, english_speak):
    """24 kHz wav of the character's English voice (made once with the film's usual TTS)."""
    os.makedirs(CACHE, exist_ok=True)
    v = story.CAST[who]
    key = hashlib.sha1(f"{who}|{v}|{REFERENCE[who]}".encode()).hexdigest()[:12]
    path = os.path.join(CACHE, f"ref_{who}_{key}.wav")
    if not os.path.exists(path):
        import soundfile
        x = english_speak(who, REFERENCE[who])
        soundfile.write(path + ".48k.wav", x, 48000)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path + ".48k.wav", "-ac", "1",
                        "-ar", str(SR_MODEL), path], check=True)
        os.remove(path + ".48k.wav")
    return path


MAX_CHARS_PER_SEC = 20     # faster than this means the model stopped early: try again
PAUSE = {".": 0.28, "?": 0.3, "!": 0.28}


def sentences(text):
    """Split a line after . ? ! (the model drops words at the end of long multi-sentence input)."""
    t = normalise(text)
    out, cur = [], ""
    for ch in t:
        cur += ch
        if ch in ".?!":
            out.append(cur.strip())
            cur = ""
    if cur.strip():
        out.append(cur.strip())
    return [s for s in out if any(c.isalpha() for c in s)]


def _one(who, s, seed, tries=8):
    """One sentence; regenerate (new seed) while it is too short to contain every word."""
    import torch
    best = None
    for k in range(tries):
        torch.manual_seed(seed + 7919 * k)
        chunks = [np.asarray(c, dtype=np.float32).reshape(-1)
                  for c in _model.generate_audio_stream(_states[who], s)]
        x = np.concatenate(chunks) if chunks else np.zeros(1, np.float32)
        if best is None or len(x) > len(best):
            best = x
        letters = sum(c.isalpha() for c in s)
        if len(x) / SR_MODEL >= letters / MAX_CHARS_PER_SEC:
            return x
    return best


def synth(who, text, english_speak, seed=0):
    """Mono float32 Armenian speech at 24 kHz."""
    _load()
    if who not in _states:
        _states[who] = _model.get_state_for_audio_prompt(_reference(who, english_speak))
    parts = []
    for k, s in enumerate(sentences(text)):
        if parts:
            parts.append(np.zeros(int(PAUSE.get(prev[-1], 0.25) * SR_MODEL), np.float32))
        x = _one(who, s, seed + 101 * k)
        parts.append(_trim(x))
        prev = s
    return np.concatenate(parts) if parts else np.zeros(1, np.float32)


def _trim(x, thresh=0.01):
    loud = np.nonzero(np.abs(x) > thresh)[0]
    if len(loud) == 0:
        return x
    return x[max(0, loud[0] - int(0.02 * SR_MODEL)):min(len(x), loud[-1] + int(0.06 * SR_MODEL))]
