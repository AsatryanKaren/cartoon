"""Armenian clip "q2_reask": the English clip's picture and timing, Armenian lines (see ../../lines.py)."""
from interactive.birthday.clips.q2_reask.story import *  # noqa: F401,F403
from interactive.birthday.clips.q2_reask import story as _en
from interactive.birthday_hy.lines import armenian

PLACE = "Interactive/birthday_hy"
LANG = "hy"
FILM_SECONDS = 5
SCRIPT = armenian("q2_reask", _en.SCRIPT)
