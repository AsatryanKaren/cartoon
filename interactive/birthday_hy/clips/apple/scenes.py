"""Armenian clip "apple": same scenes as the English clip, with the on-screen words and word cues in Armenian."""
import draw
from interactive.birthday import shared
from interactive.birthday.clips.apple.scenes import *  # noqa: F401,F403
from interactive.birthday_hy.lines import TEXTS, WORDS

draw.TEXTS.update(TEXTS)
shared.WORDS.update(WORDS)
