from draw import Canvas
import film as story
def _s(tl, t):
    return Canvas()
SCENE_FUNCS = {n: _s for n in story.SCENES}
