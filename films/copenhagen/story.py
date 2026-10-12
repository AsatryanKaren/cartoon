"""Film: "Whiskers and the Flying Trunk" -- Whiskers and Luna go to Copenhagen.

One grey, rainy evening nobody at home feels cosy -- Whiskers' blanket is in
the wash. Pip drags in an old storybook: fairy tales by Hans Christian
Andersen of Copenhagen. Luna reads "The Flying Trunk": whoever clicked its
lock flew away over the rooftops. "Fairy tales aren't real," says Whiskers,
sitting on the old trunk under the window -- click! -- and the trunk floats.
It flies them through the night, across the sea, to Copenhagen. In Nyhavn,
among painted houses and wooden ships, two ducks are laughing at Saga, a
scruffy grey bird who thinks she is the ugliest duckling in Denmark. Luna --
grey herself -- thinks grey is the best colour. Saga takes them to Bodil the
seal's bakery boat: Whiskers looks for the lid of his open sandwich and
unrolls a giant cinnamon snail into a "cinnamon blanket". Meanwhile the ducks
peck the trunk's lock and it flies away. The chase passes the palace, where a
low-flying trunk drops a guard's bearskin hat on Whiskers, and the Little
Mermaid, who never quite fit in on land either. At night the trunk is stuck
on top of Tivoli's old wooden roller coaster. Whiskers rides the coaster and
misses ("on purpose"). Only Saga could reach it -- but ducklings like her
can't fly. Luna and Whiskers believe in her; she spreads her wings, flies
into the lantern light, brings the trunk down -- and everyone sees she is a
young swan. Bodil teaches them "hygge" with candles, blankets and cocoa, and
Saga flies beside the trunk all the way home, where the cats make hygge on
the windowsill. Moral: being different isn't being wrong, and a kind friend
can help anyone find their wings.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.copenhagen import sounds

TITLE = "Whiskers and the Flying Trunk"
PLACE = "Copenhagen"        # folder in the catcute library
SCENES = ["title", "rain", "flight", "nyhavn", "bakery", "palace", "tivoli", "hygge", "home"]

CAST = {
    **CAST,
    # Saga: a scruffy grey cygnet who thinks she is an ugly duckling; shy, kind, hopeful
    "saga": Voice("af_bella", 1.02, 2, ["Samantha"], 186, "en-us+f2", 70, 170),
    # Bodil: a round, jolly grandmother seal who runs a bakery boat in Nyhavn
    "bodil": Voice("af_alloy", 0.92, -2, ["Karen"], 166, "en-gb+f4", 40, 150),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "saga": (215, 240, 255),
    "bodil": (255, 225, 160),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    # a music-box waltz feel for the fairy-tale title
    "c_title":  dict(bpm=80, prog=[(62, MAJ), (59, MIN), (55, MAJ), (57, MAJ)], drums=False, mel=0.55, oct=79, vol=0.8),
    "c_rain":   dict(bpm=66, prog=[(57, MIN), (53, MAJ), (55, MAJ), (52, MIN)], drums=False, mel=0.3, oct=76, vol=0.62),
    "c_story":  dict(bpm=72, prog=[(60, MAJ), (57, MIN), (65, MAJ), (67, MAJ)], drums=False, mel=0.5, oct=81, vol=0.7),
    "c_magic":  dict(bpm=92, prog=[(62, MAJ), (66, MIN), (67, MAJ), (69, MAJ)], drums=False, mel=0.75, oct=81, vol=0.78),
    "c_night":  dict(bpm=70, prog=[(62, MIN), (58, MAJ), (65, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=79, vol=0.66),
    # bright harbour morning, a sea-shanty bounce
    "c_harbour": dict(bpm=112, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.7, oct=74, vol=0.8),
    "c_shy":    dict(bpm=76, prog=[(64, MIN), (60, MAJ), (67, MAJ), (62, MAJ)], drums=False, mel=0.4, oct=79, vol=0.64),
    "c_bakery": dict(bpm=126, prog=[(65, MAJ), (62, MIN), (70, MAJ), (72, MAJ)], drums=True, mel=0.8, oct=77, vol=0.84),
    "c_chase":  dict(bpm=138, prog=[(57, MIN), (53, MAJ), (55, MAJ), (57, MIN)], drums=True, mel=0.75, oct=76, vol=0.84),
    # a little royal march
    "c_march":  dict(bpm=108, prog=[(60, MAJ), (67, MAJ), (65, MAJ), (67, MAJ)], drums=True, mel=0.6, oct=72, vol=0.78),
    "c_mermaid": dict(bpm=62, prog=[(62, MIN), (58, MAJ), (60, MAJ), (57, MAJ)], drums=False, mel=0.3, oct=79, vol=0.6),
    # Tivoli: a carousel organ whirl
    "c_tivoli": dict(bpm=132, prog=[(67, MAJ), (64, MIN), (60, MAJ), (62, MAJ)], drums=True, mel=0.85, oct=79, vol=0.84),
    "c_hope":   dict(bpm=70, prog=[(60, MAJ), (64, MIN), (65, MAJ), (67, MAJ)], drums=False, mel=0.45, oct=79, vol=0.68),
    "c_soar":   dict(bpm=96, prog=[(65, MAJ), (69, MIN), (70, MAJ), (72, MAJ)], drums=False, mel=0.8, oct=81, vol=0.85),
    "c_hygge":  dict(bpm=64, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.66),
    "c_home":   dict(bpm=66, prog=[(62, MAJ), (59, MIN), (55, MAJ), (57, MAJ)], drums=False, mel=0.45, oct=79, vol=0.7),
}
MUSIC = {"title": "c_title", "rain": "c_rain", "flight": "c_night", "nyhavn": "c_harbour", "bakery": "c_bakery",
         "palace": "c_march", "tivoli": "c_tivoli", "hygge": "c_hygge", "home": "c_home"}
MUSIC_CUES = [("r_book", 0.0, "c_story"), ("r_click", 0.0, "c_magic"), ("f_dawn", 0.0, "c_harbour"),
              ("n_ducks", 0.0, "c_shy"), ("n_hungry", 0.0, "c_harbour"), ("b_oh", 0.0, "c_chase"),
              ("p_mer", 0.0, "c_mermaid"), ("p_there", 0.0, "c_chase"), ("tv_high", 0.0, "c_hope"),
              ("tv_fly", 0.0, "c_soar"), ("tv_cheer", 0.0, "c_tivoli")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.0, "t_open", [("musicbox", 0.05)]),
    S("narrator", "Whiskers and the Flying Trunk.", "title", "t_name"),
    A("title", 0.7, "t_hold", [("sparkle", 0.4)]),

    # ----------------------------------------------------------------- rain
    A("rain", 0.8, "r_open", [("rain", 0.0)]),
    S("narrator", "One grey, rainy evening, nobody felt cosy at all.", "rain", "r_narr", [("rain", 0.3)]),
    S("whiskers", "Rain, rain, rain. And my blanket is in the wash.", "rain", "r_moan"),
    A("rain", 0.9, "r_pip", [("scurry", 0.1), ("thump", 0.75)]),
    S("pip", "Look! Fairy tales by Hans Christian Andersen, from Copenhagen!",
      "rain", "r_book", [("page", 0.9)]),
    S("luna", "The Flying Trunk. Click its lock, and away it flies!",
      "rain", "r_read"),
    S("whiskers", "Pah. Fairy tales aren't real. Click!", "rain", "r_pah",
      [("click", 0.92)]),
    A("rain", 1.1, "r_click", [("sparkle", 0.05), ("magic", 0.2)]),
    S("luna", "Then let's fly! To Copenhagen!", "rain", "r_fly"),
    A("rain", 1.4, "r_go", [("thump", 0.12), ("thump", 0.28), ("creak", 0.45), ("whoosh", 0.7)]),

    # --------------------------------------------------------------- flight
    S("narrator", "Over the clouds and across the sea flew the trunk.",
      "flight", "f_narr", [("wind", 0.0)]),
    A("flight", 1.1, "f_fly", [("wind", 0.2)]),
    S("whiskers", "I'm not scared. My fur is just extra fluffy.", "flight", "f_fluffy"),
    A("flight", 1.0, "f_dawn", [("gulls", 0.5)]),
    S("pip", "Copper roofs and twisty spires! Copenhagen!", "flight", "f_look"),
    A("flight", 1.0, "f_land", [("whoosh", 0.3)]),

    # --------------------------------------------------------------- nyhavn
    A("nyhavn", 0.8, "n_bump", [("thump", 0.35), ("gulls", 0.6)]),
    S("narrator", "They landed among the painted houses of the New Harbour.",
      "nyhavn", "n_narr", [("shipbell", 0.5)]),
    A("nyhavn", 1.0, "n_look", [("waves", 0.1), ("gulls", 0.5)]),
    S("narrator", "Two ducks were laughing at a scruffy grey bird.", "nyhavn", "n_ducks",
      [("quack", 0.3), ("quack", 0.7)]),
    A("nyhavn", 0.7, "n_tease", [("quack", 0.1), ("quack", 0.4)]),
    S("saga", "Yes, I know. I'm the ugliest duckling in Denmark.", "nyhavn", "n_ugly"),
    S("luna", "Ugly? I'm grey too. Grey is the best colour!", "nyhavn", "n_grey"),
    S("saga", "Really? I'm Saga. Thank you!", "nyhavn", "n_saga"),
    S("saga", "Hungry? Bodil's bakery has the best pastries in town.", "nyhavn", "n_hungry"),
    S("whiskers", "Did somebody say pastries?", "nyhavn", "n_pastry"),
    A("nyhavn", 0.9, "n_go", [("waves", 0.2)]),

    # --------------------------------------------------------------- bakery
    S("bodil", "Velkommen! Try my smørrebrød. Open sandwiches!", "bakery", "b_hello"),
    A("bakery", 1.0, "b_lid"),
    S("whiskers", "Excuse me. Somebody stole the lid.", "bakery", "b_stole"),
    S("bodil", "Ho ho! In Denmark, sandwiches don't have lids!", "bakery", "b_nolid"),
    A("bakery", 1.6, "b_snail", [("boing", 0.15), ("whirl", 0.3), ("thump", 0.85)]),
    S("pip", "He's turned into a cinnamon roll!", "bakery", "b_roll"),
    S("whiskers", "I did that on purpose. It's a cinnamon blanket.", "bakery", "b_purpose"),
    A("bakery", 0.8, "b_peck", [("quack", 0.1), ("click", 0.5), ("magic", 0.6)]),
    S("luna", "Oh no! The ducks clicked the lock!", "bakery", "b_oh", [("whoosh", 0.4)]),
    A("bakery", 0.9, "b_away", [("quack", 0.2), ("splash", 0.45)]),
    S("saga", "It's heading for the palace! Follow me!", "bakery", "b_follow"),

    # --------------------------------------------------------------- palace
    S("narrator", "At the palace, the royal guards wear tall bearskin hats.",
      "palace", "p_narr", [("drum", 0.2)]),
    A("palace", 1.5, "p_swoop", [("drum", 0.0), ("whoosh", 0.35), ("plop", 0.62)]),
    S("whiskers", "How do I look? Very royal?", "palace", "p_royal"),
    A("palace", 0.7, "p_back", [("drum", 0.2)]),
    S("narrator", "By the sea sat the Little Mermaid, from another Andersen story.",
      "palace", "p_mer", [("waves", 0.2)]),
    S("saga", "She left the sea, but never quite fit in on land. Like me.", "palace", "p_fit"),
    S("whiskers", "I don't fit in either. Too round. But Luna likes me anyway.",
      "palace", "p_round"),
    S("pip", "There! It's flying to Tivoli!", "palace", "p_there"),
    A("palace", 0.8, "p_run"),

    # --------------------------------------------------------------- tivoli
    S("narrator", "At nightfall, the lanterns of Tivoli Gardens lit up.", "tivoli", "tv_narr",
      [("sparkle", 0.3)]),
    A("tivoli", 1.2, "tv_lights", [("organ", 0.0)]),
    S("luna", "The trunk is stuck on the old roller coaster!", "tivoli", "tv_stuck"),
    S("whiskers", "Leave it to me.", "tivoli", "tv_me"),
    A("tivoli", 2.2, "tv_ride", [("coaster", 0.0), ("whoosh", 0.45), ("coaster", 0.55)]),
    S("whiskers", "I missed. On purpose. To check the view.", "tivoli", "tv_miss"),
    S("luna", "It's too high!", "tivoli", "tv_high"),
    S("saga", "I could try. But ugly ducklings can't fly.", "tivoli", "tv_cant"),
    S("luna", "Who says you're a duckling? Spread your wings, Saga!", "tivoli", "tv_spread"),
    S("whiskers", "Go on! We believe in you!", "tivoli", "tv_believe"),
    A("tivoli", 2.2, "tv_fly", [("flap", 0.05), ("flap", 0.25), ("sparkle", 0.5), ("flap", 0.6), ("thump", 0.95)]),
    S("pip", "She's not a duckling at all. She's a swan!", "tivoli", "tv_swan"),
    S("saga", "I'm a swan? I'm a swan!", "tivoli", "tv_iam"),
    A("tivoli", 1.2, "tv_cheer", [("fireworks", 0.1), ("clap", 0.2), ("fireworks", 0.55)]),

    # ---------------------------------------------------------------- hygge
    S("narrator", "That night, Bodil made hot cocoa for everyone.", "hygge", "hy_narr",
      [("pour", 0.6)]),
    S("bodil", "Cosy together? We call it hooga. Spelled H, Y, G, G, E!", "hygge", "hy_hygge"),
    S("whiskers", "Hooga. My new favourite word.", "hygge", "hy_word"),
    S("saga", "Thank you for being my friends, even when I was scruffy.", "hygge", "hy_thanks"),
    S("luna", "We'll always be your friends. Grey, white, or polka-dot.", "hygge", "hy_always"),
    A("hygge", 1.2, "hy_cosy", [("purr", 0.2)]),

    # ----------------------------------------------------------------- home
    A("home", 1.1, "h_fly", [("wind", 0.0), ("flap", 0.5)]),
    S("narrator", "Saga flew beside the trunk, all the way home.", "home", "h_narr"),
    A("home", 0.9, "h_land", [("whoosh", 0.1), ("thump", 0.5), ("sparrows", 0.7)]),
    S("pip", "Look! The Ugly Duckling story. That's Saga!", "home", "h_book", [("page", 0.1)]),
    S("whiskers", "Fairy tales aren't real. Except the ones that are.", "home", "h_real"),
    S("luna", "Let's make hooga at home!", "home", "h_home"),
    S("whiskers", "A candle, cocoa, and my best friends. Perfect.", "home", "h_perfect",
      [("purr", 0.6)]),
    S("narrator", "Being different isn't being wrong. And a kind friend can help anyone find their wings.",
      "home", "h_moral"),
    A("home", 1.8, "h_end", [("musicbox", 0.3)]),
]
