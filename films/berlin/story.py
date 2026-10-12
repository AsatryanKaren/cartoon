"""Film: "Whiskers and the Painted Wall" -- Whiskers and Luna go to Berlin.

One sunny morning there is only one warm sunbeam on the windowsill, and the
two cats quarrel over it. Whiskers builds a wall of cushions down the middle:
"My side, your side." When a big moving van bound for Berlin stops outside,
each cat climbs aboard -- separately, and Pip goes along to keep them talking.
All night a wall of boxes stands between them. In Berlin, Berti the Berlin
bear shows them the Brandenburg Gate and the Reichstag's glass dome; at Oma
Hilde's snack stand Whiskers gets his head stuck through a giant pretzel and
squirts doughnut jam all over Luna. Luna storms onto a yellow U-Bahn train and
the doors close between them. Walking along the river, Berti shows Whiskers
the East Side Gallery: a piece of the old Wall that once kept friends apart,
now covered in happy paintings. Whiskers paints his own picture -- two cats
sharing one sunbeam -- and Luna finds him there. They say sorry, and watch the
city lights from the TV Tower: one Berlin, no wall. At home the cushion wall
becomes a bed for two. Moral: walls keep friends apart; a sorry brings them
down.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.berlin import sounds

TITLE = "Whiskers and the Painted Wall"
PLACE = "Berlin"            # folder in the catcute library
SCENES = ["title", "sill", "van", "gate", "imbiss", "ubahn", "gallery", "tower", "home"]

CAST = {
    **CAST,
    # Berti: a young, cheerful brown Berlin bear with a little gold crown; a proud city guide
    "berti": Voice("am_echo", 1.0, 1, ["Fred"], 182, "en-us+m4", 52, 165),
    # Oma Hilde: a jolly old dachshund who runs a snack stand (pretzels, currywurst, doughnuts)
    "hilde": Voice("bf_isabella", 0.95, -1, ["Moira"], 168, "en-gb+f2", 42, 155),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "berti": (255, 214, 150),
    "hilde": (190, 240, 200),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    "b_title":  dict(bpm=84, prog=[(60, MAJ), (64, MIN), (65, MAJ), (67, MAJ)], drums=False, mel=0.5, oct=76, vol=0.8),
    "b_sunny":  dict(bpm=100, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=True, mel=0.55, oct=77, vol=0.75),
    "b_sulk":   dict(bpm=92, prog=[(57, MIN), (53, MAJ), (57, MIN), (52, MAJ)], drums=True, mel=0.45, oct=76, vol=0.72),
    "b_road":   dict(bpm=70, prog=[(62, MIN), (58, MAJ), (60, MAJ), (57, MIN)], drums=False, mel=0.35, oct=74, vol=0.62),
    # a jaunty little Berlin march (oom-pah)
    "b_city":   dict(bpm=116, prog=[(58, MAJ), (63, MAJ), (65, MAJ), (58, MAJ)], drums=True, mel=0.7, oct=74, vol=0.82),
    "b_story":  dict(bpm=70, prog=[(57, MIN), (53, MAJ), (48, MAJ), (55, MAJ)], drums=False, mel=0.35, oct=76, vol=0.62),
    # cabaret-ish snack stand swing
    "b_snack":  dict(bpm=128, prog=[(60, MAJ), (57, MIN), (62, MIN), (55, MAJ)], drums=True, mel=0.8, oct=76, vol=0.84),
    # rattling U-Bahn: steady electronic four-on-the-floor
    "b_train":  dict(bpm=124, prog=[(57, MIN), (57, MIN), (53, MAJ), (55, MAJ)], drums=True, mel=0.6, oct=81, vol=0.8),
    "b_alone":  dict(bpm=62, prog=[(62, MIN), (58, MAJ), (55, MIN), (57, MAJ)], drums=False, mel=0.3, oct=74, vol=0.6),
    "b_paint":  dict(bpm=88, prog=[(60, MAJ), (65, MAJ), (57, MIN), (67, MAJ)], drums=False, mel=0.6, oct=79, vol=0.72),
    "b_hug":    dict(bpm=76, prog=[(65, MAJ), (60, MAJ), (62, MIN), (58, MAJ)], drums=False, mel=0.5, oct=77, vol=0.78),
    "b_lights": dict(bpm=72, prog=[(62, MAJ), (67, MAJ), (59, MIN), (69, MAJ)], drums=False, mel=0.45, oct=81, vol=0.8),
    "b_home":   dict(bpm=64, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}
MUSIC = {"title": "b_title", "sill": "b_sunny", "van": "b_road", "gate": "b_city", "imbiss": "b_snack",
         "ubahn": "b_train", "gallery": "b_alone", "tower": "b_lights", "home": "b_home"}
MUSIC_CUES = [("s_mine", 0.0, "b_sulk"), ("s_van", 0.0, "b_city"), ("g_wall", 0.0, "b_story"),
              ("g_dome", 0.0, "b_city"), ("u_gone", 0.0, "b_alone"), ("ga_paint", 0.0, "b_paint"),
              ("ga_luna", 0.0, "b_hug"), ("ga_down", 0.0, "b_city")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.3, "t_open", [("bells", 0.05)]),
    S("narrator", "Whiskers and the Painted Wall.", "title", "t_name"),
    A("title", 1.0, "t_hold", [("jingle", 0.4)]),

    # ----------------------------------------------------------------- sill
    A("sill", 0.7, "s_open", [("sparrows", 0.1)]),
    S("narrator", "One sunny morning, there was only one warm sunbeam on the windowsill.", "sill", "s_narr"),
    A("sill", 1.1, "s_bump", [("thump", 0.55), ("meow", 0.65)]),
    S("whiskers", "My sunbeam! I was here first.", "sill", "s_mine"),
    S("luna", "You were snoring on the rug! I was here first!", "sill", "s_first"),
    A("sill", 1.3, "s_build", [("cushion", 0.2), ("cushion", 0.45), ("cushion", 0.7)]),
    S("whiskers", "There. A wall. My side. Your side.", "sill", "s_wall"),
    S("luna", "Fine! I'm not talking to you anyway.", "sill", "s_fine"),
    S("pip", "Oh dear. A wall between best friends.", "sill", "s_pip"),
    A("sill", 1.0, "s_van", [("engine", 0.0), ("honk", 0.55)]),
    S("pip", "Look! That moving van is going all the way to Berlin!", "sill", "s_berlin"),
    S("luna", "Then I'm going to Berlin. Alone!", "sill", "s_alone"),
    S("whiskers", "Then I'm going to Berlin too. Also alone!", "sill", "s_also"),
    A("sill", 1.3, "s_jump", [("whoosh", 0.1), ("thump", 0.3), ("whoosh", 0.45), ("thump", 0.62)]),
    S("pip", "Wait for me! Somebody has to keep an eye on you two.", "sill", "s_wait"),
    A("sill", 1.0, "s_drive", [("vandoor", 0.1), ("engine", 0.3), ("honk", 0.7)]),

    # ------------------------------------------------------------------ van
    S("narrator", "All night the van rumbled along. And between the two cats stood a wall of boxes.",
      "van", "v_narr", [("engine", 0.0)]),
    A("van", 1.0, "v_ride", [("engine", 0.1)]),
    S("whiskers", "Pip. Tell Luna it's cold on my side.", "van", "v_cold"),
    A("van", 0.8, "v_run1", [("scurry", 0.1)]),
    S("pip", "Luna, Whiskers says it's cold on his side.", "van", "v_says"),
    S("luna", "Tell him it's cold on my side too.", "van", "v_too"),
    A("van", 0.8, "v_run2", [("scurry", 0.1)]),
    S("pip", "You know, you could just sit together. It's warmer.", "van", "v_together"),
    S("luna", "Never!", "van", "v_never1"),
    S("whiskers", "Never!", "van", "v_never2"),
    A("van", 1.2, "v_sleep", [("engine", 0.0), ("purr", 0.5)]),

    # ----------------------------------------------------------------- gate
    A("gate", 0.8, "g_open", [("vandoor", 0.05), ("thump", 0.5), ("thump", 0.62)]),
    S("narrator", "In the morning, the doors swung open. Berlin!", "gate", "g_narr", [("bells", 0.2)]),
    S("berti", "Hallo! Willkommen in Berlin! I'm Berti, the Berlin bear.", "gate", "g_hallo"),
    S("luna", "A real bear? In the middle of the city?", "gate", "g_bear"),
    S("berti", "Of course! The bear is on every flag in Berlin. Come, I'll show you my city!",
      "gate", "g_flag"),
    A("gate", 1.4, "g_look", [("clop", 0.2), ("clop", 0.5)]),
    S("berti", "This is the Brandenburg Gate. On top, the goddess of victory drives four horses.",
      "gate", "g_horses"),
    S("whiskers", "Do the horses ever get a day off?", "gate", "g_dayoff"),
    S("berti", "Long ago, a wall stood right here. Nobody could walk through this gate.", "gate", "g_wall"),
    A("gate", 0.8, "g_glance"),
    S("berti", "And over there is the Reichstag, with a glass dome you can walk up inside!",
      "gate", "g_dome"),
    S("whiskers", "Very nice. Is there any food in the dome?", "gate", "g_food", [("rumble", 0.6)]),
    A("gate", 0.8, "g_sniff", [("sniff", 0.2)]),

    # --------------------------------------------------------------- imbiss
    S("narrator", "Whiskers' nose led him straight to a little snack stand.", "imbiss", "i_narr",
      [("sizzle", 0.0)]),
    S("hilde", "Guten Tag! Pretzels, currywurst, and fresh Berliner doughnuts!", "imbiss", "i_hilde"),
    S("whiskers", "One of everything, please. For me. Only me.", "imbiss", "i_order"),
    A("imbiss", 1.4, "i_pretzel", [("crunch", 0.25), ("crunch", 0.4), ("boing", 0.62)]),
    S("pip", "He's wearing it like a necklace!", "imbiss", "i_necklace"),
    S("whiskers", "I did that on purpose. It's a travel snack.", "imbiss", "i_purpose"),
    A("imbiss", 1.2, "i_donut", [("squish", 0.45), ("splat", 0.58)]),
    S("luna", "Whiskers!", "imbiss", "i_jam"),
    S("whiskers", "That one was not on purpose. Really!", "imbiss", "i_notpurpose"),
    S("luna", "Come on, Pip. We're taking the yellow train. Without him.", "imbiss", "i_train"),
    A("imbiss", 0.8, "i_off"),

    # ---------------------------------------------------------------- ubahn
    S("narrator", "In Berlin, the yellow U-Bahn trains even ride over the river, on a bridge with two red towers.",
      "ubahn", "u_narr", [("rattle", 0.1)]),
    A("ubahn", 1.3, "u_board", [("chime", 0.1), ("hiss", 0.6)]),
    S("whiskers", "Luna! Wait!", "ubahn", "u_wait", [("hiss", 0.4)]),
    A("ubahn", 1.3, "u_gone", [("rattle", 0.05), ("rattle", 0.45)]),
    S("berti", "Don't worry. That train goes to the East Side Gallery. We'll walk along the river.",
      "ubahn", "u_walk"),
    A("ubahn", 1.0, "u_river", [("boat", 0.3)]),

    # -------------------------------------------------------------- gallery
    S("narrator", "So they came to a very long wall, covered in colourful paintings.", "gallery", "ga_narr"),
    S("whiskers", "Who painted all this?", "gallery", "ga_who"),
    S("berti", "Artists from everywhere. It's a piece of the old Berlin Wall.", "gallery", "ga_piece"),
    S("berti", "For years it kept friends apart. When it came down, people hugged and danced.",
      "gallery", "ga_apart"),
    S("berti", "Then they painted it, so now it only makes people smile.", "gallery", "ga_smile"),
    A("gallery", 1.6, "ga_walk", [("sparrows", 0.3)]),
    S("whiskers", "I built a wall this morning. Out of cushions. Over a sunbeam.", "gallery", "ga_cushions"),
    S("berti", "And how is it, on your side of the wall?", "gallery", "ga_how"),
    S("whiskers", "Lonely. Very lonely.", "gallery", "ga_lonely"),
    A("gallery", 0.6, "ga_think"),
    S("berti", "Then paint something. Right here.", "gallery", "ga_brush"),
    A("gallery", 1.8, "ga_paint", [("brush", 0.1), ("brush", 0.35), ("brush", 0.6), ("brush", 0.8)]),
    S("luna", "Whiskers? Is that us?", "gallery", "ga_luna", [("jingle", 0.0)]),
    S("whiskers", "Luna! I'm sorry. The sunbeam is big enough for two.", "gallery", "ga_sorry"),
    S("luna", "I'm sorry too. I missed you, you big furry grump.", "gallery", "ga_missed"),
    A("gallery", 1.2, "ga_hug", [("purr", 0.1)]),
    S("pip", "Hooray! The wall is down!", "gallery", "ga_down", [("clap", 0.2)]),
    A("gallery", 0.6, "ga_end"),

    # ---------------------------------------------------------------- tower
    S("narrator", "That evening, Berti took them up the TV Tower, high above the whole city.",
      "tower", "tw_narr"),
    A("tower", 1.3, "tw_up", [("lift", 0.05)]),
    S("pip", "Whee! My ears went pop!", "tower", "tw_pop", [("pop", 0.5)]),
    A("tower", 0.8, "tw_view", [("sparkle", 0.3)]),
    S("luna", "Look! The Gate, the glass dome, and the river, all lit up!", "tower", "tw_look"),
    S("berti", "Long ago, you could see the wall from up here, cutting the city in two.", "tower", "tw_wall"),
    S("berti", "Now there's just one Berlin. And lots of friends.", "tower", "tw_one"),
    S("whiskers", "One Berlin. And one sunbeam, for two.", "tower", "tw_two"),
    A("tower", 1.6, "tw_lights", [("sparkle", 0.2), ("sparkle", 0.6)]),

    # ----------------------------------------------------------------- home
    A("home", 1.0, "h_back", [("engine", 0.0), ("honk", 0.6)]),
    S("narrator", "And the moving van, empty now, carried them home.", "home", "h_narr"),
    A("home", 0.8, "h_sill", [("sparrows", 0.2)]),
    S("pip", "Whiskers! What happened to your wall?", "home", "h_pip"),
    S("whiskers", "I knocked it down. Now it's a bed. For two.", "home", "h_bed", [("cushion", 0.3)]),
    S("luna", "And I brought one pretzel from Berlin. For sharing.", "home", "h_pretzel"),
    S("whiskers", "Then I'll share. On purpose.", "home", "h_share", [("crunch", 0.9)]),
    A("home", 0.8, "h_munch", [("purr", 0.2)]),
    S("narrator", "Because walls keep friends apart. But one little sorry can bring any wall down.",
      "home", "h_moral"),
    A("home", 1.7, "h_end", [("jingle", 0.4)]),
]
