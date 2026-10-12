"""Film: "Whiskers and the White Mountain" -- Whiskers and Luna go to Mont Blanc.

Same format as Film 1 (see films/moonfish/story.py): `Say` lines take their
speech length, weighted `Act` moments share the rest so the film is 355 s.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.montblanc import sounds

TITLE = "Whiskers and the White Mountain"
PLACE = "Chamonix"            # folder in the catcute library
SCENES = ["title", "postcard", "train", "cablecar", "snow", "storm", "chalet", "summit", "sled", "home"]

# New mountain friends
CAST = {
    **CAST,
    # Bruno: a big, old, kind Saint Bernard rescue dog -- deep, warm and jolly
    "bruno": Voice("am_santa", 0.9, -1, ["Ralph"], 160, "en-us+m1", 25, 140),
    # Margot: a quick little French marmot
    "margot": Voice("ff_siwis", 1.05, 2, ["Amelie"], 190, "fr+f2", 70, 170),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "bruno": (255, 225, 120),
    "margot": (170, 240, 190),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    "majestic": dict(bpm=66, prog=[(62, MAJ), (59, MIN), (55, MAJ), (57, MAJ)], drums=False, mel=0.4, oct=74, vol=0.8),
    "cozyhome": dict(bpm=96, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=True, mel=0.55, oct=77, vol=0.75),
    "alpine":   dict(bpm=118, prog=[(67, MAJ), (60, MAJ), (62, MAJ), (67, MAJ)], drums=True, mel=0.8, oct=79, vol=0.85),
    "lift":     dict(bpm=84, prog=[(64, MAJ), (61, MIN), (57, MAJ), (59, MAJ)], drums=False, mel=0.5, oct=76, vol=0.75),
    "snowplay": dict(bpm=124, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.7, oct=72, vol=0.8),
    "storm":    dict(bpm=60, prog=[(57, MIN), (53, MAJ), (52, MIN), (52, MAJ)], drums=False, mel=0.2, oct=69, vol=0.7),
    "rescue":   dict(bpm=72, prog=[(60, MAJ), (57, MIN), (65, MAJ), (67, MAJ)], drums=False, mel=0.35, oct=72, vol=0.7),
    "fireside": dict(bpm=76, prog=[(58, MAJ), (55, MIN), (63, MAJ), (65, MAJ)], drums=False, mel=0.45, oct=74, vol=0.7),
    "dawn":     dict(bpm=58, prog=[(62, MAJ), (67, MAJ), (59, MIN), (69, MAJ)], drums=False, mel=0.3, oct=74, vol=0.85),
    "sledding": dict(bpm=140, prog=[(62, MAJ), (67, MAJ), (69, MAJ), (62, MAJ)], drums=True, mel=0.85, oct=74, vol=0.85),
    "snowhome": dict(bpm=62, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}
MUSIC = {"title": "majestic", "postcard": "cozyhome", "train": "alpine", "cablecar": "lift", "snow": "snowplay",
         "storm": "storm", "chalet": "fireside", "summit": "dawn", "sled": "sledding", "home": "snowhome"}
MUSIC_CUES = [("st_bruno", 0.0, "rescue"), ("su_sunrise", 0.0, "majestic"), ("su_hold", 0.5, "dawn")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("wind", 0.0)]),
    S("narrator", "Whiskers and the White Mountain.", "title", "t_name"),
    A("title", 1.6, "t_hold", [("jingle", 0.3)]),

    # ------------------------------------------------------------- postcard
    A("postcard", 1.2, "pc_open", [("purr", 0.1)]),
    S("narrator", "One frosty autumn morning, Pip came running with a postcard.", "postcard", "pc_narr"),
    A("postcard", 0.8, "pc_pip"),
    S("pip", "Special delivery! All the way from the mountains!", "postcard", "pc_pip_say"),
    S("luna", "Mont Blanc! The White Mountain, the highest in all the Alps!", "postcard", "pc_mb"),
    S("luna", "They say from the top, you can watch the sun rise above the clouds.", "postcard", "pc_sun"),
    S("whiskers", "Clouds are just sky pillows.", "postcard", "pc_pillow"),
    S("pip", "It says they serve hot cheese fondue up there.", "postcard", "pc_fondue"),
    A("postcard", 0.8, "pc_ears"),
    S("whiskers", "Hot... melty... cheese? Luna, pack the bags!", "postcard", "pc_pack", [("meow", 0.85)]),
    A("postcard", 0.8, "pc_end"),

    # ---------------------------------------------------------------- train
    S("narrator", "So the two cats took the train, all the way to the Alps.", "train", "tr_narr",
      [("train", 0.0)]),
    A("train", 2.2, "tr_ride", [("cowbell", 0.35), ("cowbell", 0.5), ("whistle", 0.8)]),
    S("luna", "Look, Whiskers! Real snowy mountains!", "train", "tr_look"),
    S("whiskers", "They look like giant scoops of vanilla ice cream.", "train", "tr_ice"),
    A("train", 1.4, "tr_tunnel", [("whoosh", 0.05), ("whoosh", 0.75)]),
    S("narrator", "At last, they reached Chamonix, at the foot of Mont Blanc.", "train", "tr_cham"),
    A("train", 0.8, "tr_end", [("whistle", 0.1)]),

    # ------------------------------------------------------------- cablecar
    S("narrator", "Then a cable car carried them up, up, up into the sky.", "cablecar", "cc_narr",
      [("clunk", 0.1)]),
    A("cablecar", 2.0, "cc_rise", [("hum", 0.0)]),
    S("whiskers", "Nobody look down. Especially me.", "cablecar", "cc_down"),
    S("luna", "Open your eyes, Whiskers! We're higher than the eagles!", "cablecar", "cc_birds"),
    A("cablecar", 1.0, "cc_peek", [("hum", 0.0)]),
    S("whiskers", "Ooh. Okay. That's actually... pretty.", "cablecar", "cc_pretty"),
    A("cablecar", 1.2, "cc_arrive", [("hum", 0.0), ("clunk", 0.8)]),

    # ----------------------------------------------------------------- snow
    A("snow", 1.0, "sn_out", [("crunch", 0.3), ("crunch", 0.6)]),
    S("whiskers", "Cold! Cold! Cold! Why is the ground so cold?", "snow", "sn_cold",
      [("crunch", 0.2), ("crunch", 0.5), ("crunch", 0.8)]),
    S("luna", "It's snow, silly! Come on, it's fun!", "snow", "sn_fun"),
    A("snow", 2.0, "sn_play", [("poof", 0.15), ("crunch", 0.55), ("poof", 0.78)]),
    S("whiskers", "I'm fine! I'm measuring how deep it is. On purpose.", "snow", "sn_purpose"),
    A("snow", 1.0, "sn_pop", [("marmot", 0.15), ("poof", 0.75)]),
    S("margot", "Bonjour! Are you lost? I am Margot, the marmot.", "snow", "sn_margot"),
    S("luna", "We want to see the sunrise from the very top!", "snow", "sn_top"),
    S("margot", "Then hurry, my friends. Look! The clouds are coming.", "snow", "sn_clouds", [("wind", 0.6)]),
    A("snow", 0.8, "sn_end"),

    # ---------------------------------------------------------------- storm
    A("storm", 1.4, "st_wind", [("wind", 0.0), ("wind", 0.6)]),
    S("narrator", "The wind howled, and the snow swirled, until nobody could see a thing.",
      "storm", "st_narr", [("wind", 0.3)]),
    S("whiskers", "Luna? Luna! Where are you?", "storm", "st_where"),
    A("storm", 1.0, "st_alone", [("wind", 0.0)]),
    S("whiskers", "I'm not scared. I'm just... very, very cold.", "storm", "st_cold"),
    A("storm", 0.9, "st_bell", [("jingle", 0.2), ("jingle", 0.7)]),
    S("luna", "Whiskers! Follow the sound of my bell!", "storm", "st_follow", [("jingle", 0.95)]),
    A("storm", 1.3, "st_walk", [("jingle", 0.15), ("crunch", 0.3), ("jingle", 0.5), ("crunch", 0.65),
                                 ("jingle", 0.85)]),
    A("storm", 1.0, "st_bark", [("bark", 0.2), ("bark", 0.45)]),
    S("bruno", "Woof! Easy now, little ones. Bruno is here.", "storm", "st_bruno"),
    S("bruno", "Climb on my back. My chalet is just over the ridge.", "storm", "st_back"),
    A("storm", 1.3, "st_carry", [("crunch", 0.2), ("crunch", 0.5), ("crunch", 0.8)]),

    # --------------------------------------------------------------- chalet
    A("chalet", 1.0, "ch_in", [("crackle", 0.0)]),
    S("narrator", "In Bruno's chalet, a fire crackled, and cheese fondue bubbled.",
      "chalet", "ch_narr", [("crackle", 0.4)]),
    S("whiskers", "Is this a dream? A whole lake of cheese?", "chalet", "ch_lake"),
    A("chalet", 2.0, "ch_dip", [("crackle", 0.0)]),
    S("margot", "Careful, Whiskers! I think the cheese is winning!", "chalet", "ch_win"),
    A("chalet", 1.0, "ch_munch", [("whoosh", 0.05), ("poof", 0.14)]),
    S("luna", "I'm sorry, Whiskers. You got lost because of me.",
      "chalet", "ch_sorry"),
    S("whiskers", "Hey. I heard your bell. I'd follow that bell anywhere.", "chalet", "ch_bell"),
    S("bruno", "That is the first rule of the mountain. Nobody climbs alone.", "chalet", "ch_rule"),
    A("chalet", 1.4, "ch_zzz", [("purr", 0.1), ("crackle", 0.5)]),

    # --------------------------------------------------------------- summit
    A("summit", 1.4, "su_climb", [("crunch", 0.2), ("crunch", 0.45), ("crunch", 0.7)]),
    S("narrator", "Before dawn, the friends climbed the last ridge, together.",
      "summit", "su_narr", [("crunch", 0.3), ("crunch", 0.7)]),
    A("summit", 1.2, "su_top"),
    S("margot", "We made it! The top of Mont Blanc! The roof of Europe!", "summit", "su_made"),
    A("summit", 3.4, "su_sunrise"),
    S("luna", "Whiskers, look. We're above the clouds.", "summit", "su_above"),
    S("whiskers", "It's a whole sea of sky pillows.", "summit", "su_pillows"),
    S("whiskers", "Luna? Thank you for dragging me up here.", "summit", "su_thanks"),
    A("summit", 1.8, "su_hold", [("purr", 0.2)]),

    # ----------------------------------------------------------------- sled
    S("bruno", "And now, the fastest way down the mountain!", "sled", "sl_fast"),
    A("sled", 3.0, "sl_ride", [("whoosh", 0.05), ("swish", 0.2), ("swish", 0.5), ("whoosh", 0.75)]),
    S("whiskers", "Wheee! I am doing this on purpose!", "sled", "sl_wheee", [("swish", 0.3)]),
    A("sled", 1.3, "sl_crash", [("whoosh", 0.1), ("poof", 0.4)]),
    S("margot", "Au revoir, little cats! Come back soon!", "sled", "sl_bye", [("marmot", 0.95)]),
    A("sled", 1.0, "sl_end", [("bark", 0.2)]),

    # ----------------------------------------------------------------- home
    A("home", 1.2, "h_open"),
    S("narrator", "Back home, the first snow of winter began to fall.", "home", "h_narr"),
    S("pip", "So? Did you touch the clouds? Did you eat the fondue?", "home", "h_pip"),
    S("whiskers", "Better than that, Pip. We climbed a mountain. Together.", "home", "h_together"),
    A("home", 0.8, "h_snow"),
    S("whiskers", "Next time, though, I'm packing a lot more socks.", "home", "h_socks"),
    A("home", 1.4, "h_curl", [("purr", 0.2)]),
    S("narrator", "Because even the highest mountain feels small, when you climb it with a friend.",
      "home", "h_moral"),
    A("home", 2.8, "h_end"),
]
