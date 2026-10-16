"""Draw the cover (run from the repo root: python3 interactive/birthday_hy/make_cover.py)."""
import os, sys; sys.path.insert(0, os.getcwd())
from PIL import ImageFilter
import draw as D
from draw import Canvas, W, H, SS
import interactive.birthday.shared as S
img = S.party_bg(False, True).filter(ImageFilter.GaussianBlur(2 * SS))
c = Canvas(img)
for x, y, ci in ((110, 300, 0), (190, 250, 1), (150, 190, 2), (1120, 270, 3), (1190, 210, 4), (1060, 200, 5)):
    S.party_balloon(c, x, y, 50, S.BALLOON_COLS[ci], 0.3, string=260, seed=x)
S.cat_front(c, 420, 760, D.LUNA, 0.95, 0, eyes="happy", tilt=-4)
S.cat_front(c, 860, 750, D.WHISKERS, 1.0, 0, eyes="open", look=(-0.3, 0.3), tilt=4)
S.cake(c, 640, 712, 1.15, 0.2, candle_on=True)
D.mouse(c, 760, 704, 2.4, -1, 0.5, proud=True, eyes="happy")
c.text(W / 2, 70, "Պիպի ծննդյան", 54, (255, 240, 200), stroke=4)
c.text(W / 2, 150, "ԱՆԱԿՆԿԱԼԸ", 92, (240, 80, 110), stroke=6)
for x, y in ((250, 150), (1030, 150), (290, 70), (990, 80)):
    S.sparkle(c, x, y, 18, (255, 230, 120))
c.finish().save("interactive/birthday_hy/cover.png")
