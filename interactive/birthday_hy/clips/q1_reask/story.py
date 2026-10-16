"""Armenian clip "q1_reask": the English clip's picture and timing, Armenian lines (see ../../lines.py)."""
from interactive.birthday.clips.q1_reask.story import *  # noqa: F401,F403
from interactive.birthday.clips.q1_reask import story as _en
from interactive.birthday_hy.lines import armenian

PLACE = "Interactive/birthday_hy"
LANG = "hy"
FILM_SECONDS = 5
SCRIPT = armenian("q1_reask", _en.SCRIPT)
