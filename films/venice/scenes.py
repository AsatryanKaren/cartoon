import draw as D
def _blank(tl, t):
    return D.Canvas()
SCENE_FUNCS = {k: _blank for k in ["title", "bell", "balloon", "square", "canal", "murano", "flood", "home"]}
