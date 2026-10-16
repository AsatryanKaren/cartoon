"""Armenian clip "q1_auto": the English clip's picture and timing, Armenian lines (see ../../lines.py)."""
from interactive.pond_or_tree.clips.q1_auto.story import *  # noqa: F401,F403
from interactive.pond_or_tree.clips.q1_auto import story as _en
from interactive.pond_or_tree_hy.lines import armenian

PLACE = "Interactive/pond_or_tree_hy"
LANG = "hy"
FILM_SECONDS = 5
SCRIPT = armenian("q1_auto", _en.SCRIPT)
