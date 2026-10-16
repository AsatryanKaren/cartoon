"""Armenian clip "honey": the English clip's picture and timing, Armenian lines (see ../../lines.py)."""
from interactive.birthday.clips.honey.story import *  # noqa: F401,F403
from interactive.birthday.clips.honey import story as _en
from interactive.birthday_hy.lines import armenian

PLACE = "Interactive/birthday_hy"
LANG = "hy"
FILM_SECONDS = 40
SCRIPT = armenian("honey", _en.SCRIPT)
