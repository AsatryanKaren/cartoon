"""Armenian clip "tree": the English clip's picture and timing, Armenian lines (see ../../lines.py)."""
from interactive.pond_or_tree.clips.tree.story import *  # noqa: F401,F403
from interactive.pond_or_tree.clips.tree import story as _en
from interactive.pond_or_tree_hy.lines import armenian

PLACE = "Interactive/pond_or_tree_hy"
LANG = "hy"
FILM_SECONDS = 44  # English clip + the extra time the Armenian lines take
SCRIPT = armenian("tree", _en.SCRIPT)
