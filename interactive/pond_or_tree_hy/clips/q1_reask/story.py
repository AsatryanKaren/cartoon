"""Armenian clip "q1_reask": the English clip's picture and timing, Armenian lines (see ../../lines.py)."""
from interactive.pond_or_tree.clips.q1_reask.story import *  # noqa: F401,F403
from interactive.pond_or_tree.clips.q1_reask import story as _en
from interactive.pond_or_tree_hy.lines import armenian

PLACE = "Interactive/pond_or_tree_hy"
LANG = "hy"
FILM_SECONDS = 6
SCRIPT = armenian("q1_reask", _en.SCRIPT)
