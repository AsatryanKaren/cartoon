def _f(tl,t):
    from draw import Canvas
    return Canvas()
import films.santorini.story as s
SCENE_FUNCS={n:_f for n in s.SCENES}
