"""Armenian clip "pond": same scenes as the English clip, with the on-screen words in Armenian."""
import draw
from interactive.pond_or_tree.clips.pond.scenes import *  # noqa: F401,F403
from interactive.pond_or_tree_hy.lines import TEXTS

draw.TEXTS.update(TEXTS)
