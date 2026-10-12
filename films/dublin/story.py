"""Film: "Whiskers and the Rainbow's End" -- Whiskers and Luna go to Dublin and the west of Ireland.

It has rained all week and the garden pond is full to the brim. Something
shiny bobs on it: Whiskers is sure it's a glass fish, pounces, and lands in the
pond -- but he comes up with a bottle. Inside is an old map of Ireland: "Follow
the rainbow to the treasure at the rainbow's end." Luna remembers the old
story of a pot of gold; Whiskers hears "a pot of goldfish". The cats sail the
Irish Sea on a big green ferry to Dublin, walk past the city's colourful
Georgian doors to the Ha'penny Bridge over the Liffey, where Fergal, a
fiddling hare in a knitted jumper, knows the map: it leads west, to the Cliffs
of Moher. That night, in a cosy pub full of jigs and reels, Whiskers eats a
whole loaf of soda bread and tries Irish dancing, ending up head-first in a
drum ("on purpose -- a very advanced step"). Next day Fergal's painted
caravan rolls west past stone walls, sheep, a round tower and a castle ruin.
After a shower a rainbow appears, ending at the cliffs, and Whiskers finds a
four-leaf clover, which he keeps. At the cliffs the rainbow ends on a ledge --
but Bridie the sheepdog's lamb Dot is stuck there. Whiskers chooses the lamb
over the treasure, climbs down, brings her up and gives her his lucky clover;
the rainbow fades away. In Bridie's cottage the "pot of gold" turns out to be
golden fish chowder. Home again, the cats put their own map in the bottle and
send it off down the stream for someone else. Moral: luck isn't something you
keep; it's something you give away.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.dublin import sounds

TITLE = "Whiskers and the Rainbow's End"
PLACE = "Dublin"            # folder in the catcute library
SCENES = ["title", "bottle", "ferry", "dublin", "pub", "road", "cliffs", "supper", "home"]

CAST = {
    **CAST,
    # Fergal: a lively, kind fiddling hare in a cream knitted jumper
    "fergal": Voice("bm_daniel", 1.04, 1, ["Daniel"], 178, "en-gb+m4", 50, 162),
    # Bridie: a warm black-and-white sheepdog from a farm on the cliffs
    "bridie": Voice("bf_emma", 1.0, 0, ["Moira"], 176, "en-gb+f2", 52, 160),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "fergal": (190, 240, 170),
    "bridie": (255, 222, 140),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    "emerald":  dict(bpm=72, prog=[(62, MAJ), (59, MIN), (55, MAJ), (57, MAJ)], drums=False, mel=0.45, oct=74, vol=0.8),
    "rainy":    dict(bpm=70, prog=[(57, MIN), (53, MAJ), (55, MAJ), (57, MIN)], drums=False, mel=0.3, oct=72, vol=0.65),
    "mapfound": dict(bpm=100, prog=[(67, MAJ), (64, MIN), (60, MAJ), (62, MAJ)], drums=True, mel=0.6, oct=79, vol=0.75),
    "seaway":   dict(bpm=92, prog=[(62, MAJ), (67, MAJ), (69, MAJ), (62, MAJ)], drums=False, mel=0.5, oct=74, vol=0.75),
    "city":     dict(bpm=112, prog=[(67, MAJ), (60, MAJ), (62, MAJ), (67, MAJ)], drums=True, mel=0.7, oct=79, vol=0.8),
    "pubsoft":  dict(bpm=120, prog=[(67, MAJ), (62, MAJ), (67, MAJ), (62, MAJ)], drums=False, mel=0.15, oct=79, vol=0.35),
    "hills":    dict(bpm=104, prog=[(62, MAJ), (67, MAJ), (59, MIN), (69, MAJ)], drums=True, mel=0.65, oct=74, vol=0.8),
    "shower":   dict(bpm=76, prog=[(57, MIN), (62, MIN), (53, MAJ), (52, MAJ)], drums=False, mel=0.3, oct=72, vol=0.65),
    "rainbow":  dict(bpm=66, prog=[(60, MAJ), (65, MAJ), (57, MIN), (67, MAJ)], drums=False, mel=0.45, oct=79, vol=0.8),
    "cliffs":   dict(bpm=70, prog=[(62, MIN), (58, MAJ), (60, MAJ), (57, MIN)], drums=False, mel=0.3, oct=74, vol=0.75),
    "rescue":   dict(bpm=60, prog=[(57, MIN), (53, MAJ), (52, MIN), (52, MAJ)], drums=False, mel=0.2, oct=69, vol=0.7),
    "tender":   dict(bpm=64, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.35, oct=77, vol=0.7),
    "hearth":   dict(bpm=78, prog=[(58, MAJ), (55, MIN), (63, MAJ), (65, MAJ)], drums=False, mel=0.45, oct=74, vol=0.7),
    "homeward": dict(bpm=62, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}
MUSIC = {"title": "emerald", "bottle": "rainy", "ferry": "seaway", "dublin": "city", "pub": "pubsoft",
         "road": "hills", "cliffs": "cliffs", "supper": "hearth", "home": "homeward"}
MUSIC_CUES = [("b_map", 0.0, "mapfound"), ("r_rain", 0.0, "shower"), ("r_rainbow", 0.1, "rainbow"),
              ("r_clover", 0.0, "hills"), ("c_help", 0.0, "rescue"), ("c_gone", 0.0, "tender")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.3, "t_open", [("chime", 0.25)]),
    S("narrator", "Whiskers and the Rainbow's End.", "title", "t_name"),
    A("title", 1.0, "t_hold", [("whistle", 0.0)]),

    # --------------------------------------------------------------- bottle
    A("bottle", 1.0, "b_open", [("rain", 0.0)]),
    S("narrator", "It had rained all week, and the pond was brimming over.", "bottle", "b_narr",
      [("rain", 0.2)]),
    S("whiskers", "Rain, rain, rain. Even my naps are getting soggy.", "bottle", "b_soggy", [("rain", 0.3)]),
    A("bottle", 0.9, "b_spot", [("tink", 0.4)]),
    S("luna", "Whiskers, look! Something shiny is floating in the pond!", "bottle", "b_look"),
    S("whiskers", "A shiny glass fish! Leave this to me.", "bottle", "b_fish"),
    A("bottle", 2.0, "b_dive", [("whoosh", 0.25), ("splash", 0.45)]),
    S("whiskers", "Got it! Hmm. A very crunchy fish.", "bottle", "b_got"),
    A("bottle", 0.8, "b_cork", [("pop", 0.3), ("paper", 0.55)]),
    S("luna", "A map of Ireland! Follow the rainbow, to the treasure at its end.",
      "bottle", "b_map"),
    S("luna", "In the old stories, a pot of gold waits there.", "bottle", "b_gold"),
    S("whiskers", "A pot of goldfish? Luna, why are we still standing here?", "bottle", "b_goldfish",
      [("meow", 0.92)]),
    A("bottle", 0.7, "b_go"),

    # ---------------------------------------------------------------- ferry
    S("narrator", "So the cats sailed across the Irish Sea, on a big green ferry to Dublin.",
      "ferry", "f_narr", [("horn", 0.05), ("waves", 0.3)]),
    A("ferry", 2.0, "f_sail", [("gulls", 0.2), ("waves", 0.4)]),
    S("whiskers", "Is the sea supposed to go up and down this much?", "ferry", "f_wobble"),
    S("luna", "Look, Whiskers! Dublin!", "ferry", "f_look"),
    A("ferry", 1.2, "f_arrive", [("horn", 0.2), ("gulls", 0.6)]),

    # --------------------------------------------------------------- dublin
    A("dublin", 1.2, "d_doors"),
    S("narrator", "Dublin was full of doors, in every colour of the rainbow.",
      "dublin", "d_narr"),
    S("luna", "The map says: begin at the bridge that once cost half a penny.", "dublin", "d_map"),
    A("dublin", 1.6, "d_walk", [("busk", 0.15)]),
    S("fergal", "That's the Ha'penny Bridge, little cats, over the River Liffey!", "dublin", "d_fergal"),
    S("whiskers", "We haven't got a penny. We haven't even got half.", "dublin", "d_penny"),
    S("fergal", "Ha! It's free now. I'm Fergal. That map leads west, to the Cliffs of Moher. I'll take you!",
      "dublin", "d_west"),
    A("dublin", 0.7, "d_end", [("fiddle", 0.1)]),

    # ------------------------------------------------------------------ pub
    A("pub", 1.2, "p_open", [("jig", 0.0)]),
    S("narrator", "In a cosy pub, fiddles and tin whistles played jigs and reels.", "pub", "p_narr"),
    A("pub", 1.4, "p_tune", [("taps", 0.2), ("taps", 0.6)]),
    S("whiskers", "Is that bread? Warm bread? With butter?", "pub", "p_bread"),
    S("fergal", "Soda bread, fresh from the oven. Help yourself!", "pub", "p_soda"),
    A("pub", 1.4, "p_eat", [("munch", 0.1), ("munch", 0.5)]),
    S("luna", "Come on, Whiskers! Everybody's dancing!", "pub", "p_dance"),
    A("pub", 2.6, "p_jig", [("taps", 0.05), ("taps", 0.3), ("taps", 0.5), ("whoosh", 0.7), ("boom", 0.8)]),
    S("whiskers", "I did that on purpose. It's a very advanced step.", "pub", "p_purpose"),
    A("pub", 1.2, "p_laugh", [("cheer", 0.05)]),

    # ----------------------------------------------------------------- road
    S("narrator", "Next morning, Fergal's painted caravan rolled west over the green hills.",
      "road", "r_narr", [("clop", 0.0)]),
    A("road", 1.8, "r_ride", [("clop", 0.0), ("baa", 0.5)]),
    S("fergal", "See that round tower? Long ago, monks kept their books safe up there.",
      "road", "r_tower", [("clop", 0.1)]),
    A("road", 0.9, "r_rain", [("rain", 0.0)]),
    S("whiskers", "More rain? This country is one big puddle!", "road", "r_puddle", [("rain", 0.2)]),
    S("fergal", "Ah, but no rain, no rainbows.", "road", "r_norain"),
    A("road", 1.8, "r_rainbow", [("chime", 0.25)]),
    S("luna", "There it is! And look, it ends at the cliffs!", "road", "r_ends"),
    A("road", 0.7, "r_spot"),
    S("whiskers", "Ooh, a four-leaf clover. That's lucky. I'm keeping it.", "road", "r_clover", [("tink", 0.8)]),
    A("road", 0.7, "r_end", [("clop", 0.0)]),

    # --------------------------------------------------------------- cliffs
    A("cliffs", 1.3, "c_open", [("wind", 0.0), ("waves", 0.3)]),
    S("narrator", "At last, the Cliffs of Moher, high above the wild Atlantic.",
      "cliffs", "c_narr", [("gulls", 0.6)]),
    S("luna", "The rainbow ends right there, on that ledge!", "cliffs", "c_ledge"),
    S("whiskers", "My goldfish! Here I come!", "cliffs", "c_come"),
    A("cliffs", 0.8, "c_run", [("whoosh", 0.3)]),
    S("bridie", "Help! Please! My little lamb Dot is stuck!", "cliffs", "c_help", [("baa", 0.95)]),
    A("cliffs", 1.0, "c_see", [("baa", 0.4)]),
    S("luna", "Whiskers, the rainbow's fading! We'll lose the treasure!", "cliffs", "c_fading"),
    A("cliffs", 0.9, "c_think"),
    S("whiskers", "Forget the treasure. Hold on, little one! I'm coming!", "cliffs", "c_forget"),
    A("cliffs", 3.0, "c_rescue", [("scrabble", 0.15), ("pebbles", 0.35), ("scrabble", 0.55), ("baa", 0.8)]),
    S("bridie", "Dot! Oh, thank you, thank you, brave cats!", "cliffs", "c_thanks"),
    S("whiskers", "Here, little one. A lucky clover, just for you.", "cliffs", "c_give"),
    A("cliffs", 1.4, "c_gone", [("wind", 0.1)]),
    S("whiskers", "Oh. The rainbow's gone. No treasure.", "cliffs", "c_sad"),
    S("bridie", "That rainbow ended right where somebody needed you. That's real luck.",
      "cliffs", "c_luck"),
    S("bridie", "Come home with me. I've a pot of something golden on the stove.", "cliffs", "c_pot"),
    A("cliffs", 0.8, "c_end"),

    # --------------------------------------------------------------- supper
    A("supper", 1.0, "s_open", [("crackle", 0.0), ("bubble", 0.2)]),
    S("whiskers", "A pot of gold! Golden fish chowder! The legend was true!", "supper", "s_true"),
    A("supper", 1.4, "s_eat", [("munch", 0.15), ("purr", 0.5)]),
    S("luna", "You gave away your lucky clover, Whiskers.", "supper", "s_gave"),
    S("whiskers", "I know. And somehow, I feel luckier than ever.", "supper", "s_luckier"),
    A("supper", 1.2, "s_music", [("whistle", 0.1), ("crackle", 0.4)]),

    # ----------------------------------------------------------------- home
    A("home", 1.0, "h_open"),
    S("narrator", "Back home, the rain had stopped, and a rainbow shone over the garden.",
      "home", "h_narr"),
    S("pip", "So? Did you find the pot of gold?", "home", "h_pip"),
    S("whiskers", "Better, Pip. We found out what luck is for.", "home", "h_better"),
    S("luna", "Let's send our own map. Someone else might follow a rainbow too.", "home", "h_send"),
    A("home", 1.8, "h_float", [("splash", 0.3), ("tink", 0.5)]),
    S("narrator", "Because luck isn't something you keep. It's something you give away.", "home", "h_moral"),
    A("home", 2.6, "h_end", [("purr", 0.2)]),
]
