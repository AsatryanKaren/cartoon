"""Film: "Whiskers and the Mosaic Bowl" -- Whiskers and Luna go to Barcelona.

Whiskers breaks his beloved blue breakfast bowl chasing a butterfly. Marina, a
Spanish seagull resting on the windowsill, tells him that in Barcelona nobody
throws broken pieces away. The cats sail to Barcelona on a big white ship,
meet Paco the flamenco guitar cat on La Rambla, survive spicy patatas bravas
(churros to the rescue), marvel at the unfinished Sagrada Familia -- and lose
the bowl pieces to a wave on the beach. At Park Guell, the mosaic lizard shows
them Gaudi's secret: broken pieces can become something even more beautiful.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.barcelona import sounds

TITLE = "Whiskers and the Mosaic Bowl"
PLACE = "Barcelona"            # folder in the catcute library
SCENES = ["title", "bowl", "ship", "rambla", "tapas", "sagrada", "beach", "park", "home"]

CAST = {
    **CAST,
    # Marina: a cheerful, chatty Barcelona seagull
    "marina": Voice("ef_dora", 1.0, 1, ["Monica"], 182, "es+f2", 62, 165),
    # Paco: a tuxedo street-musician cat with a flamenco guitar
    "paco": Voice("em_alex", 0.95, 0, ["Jorge"], 172, "es+m3", 40, 155),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "marina": (175, 235, 255),
    "paco": (255, 225, 110),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
# Andalusian cadence (Am G F E) gives the flamenco colour
ANDALUZ = [(57, MIN), (55, MAJ), (53, MAJ), (52, MAJ)]
MOODS = {
    "b_title":   dict(bpm=80, prog=ANDALUZ, drums=False, mel=0.5, oct=76, vol=0.8),
    "b_morning": dict(bpm=100, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=True, mel=0.6, oct=77, vol=0.75),
    "b_sad":     dict(bpm=62, prog=[(62, MIN), (58, MAJ), (55, MIN), (57, MAJ)], drums=False, mel=0.3, oct=74, vol=0.6),
    "b_sea":     dict(bpm=96, prog=[(62, MAJ), (67, MAJ), (59, MIN), (57, MAJ)], drums=True, mel=0.55, oct=74, vol=0.75),
    "b_rambla":  dict(bpm=126, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.7, oct=76, vol=0.8),
    "b_flamenco": dict(bpm=144, prog=ANDALUZ, drums=True, mel=0.85, oct=76, vol=0.85),
    "b_tapas":   dict(bpm=112, prog=[(57, MIN), (62, MIN), (64, MAJ), (57, MIN)], drums=True, mel=0.6, oct=76, vol=0.75),
    "b_grand":   dict(bpm=70, prog=[(62, MAJ), (59, MIN), (67, MAJ), (69, MAJ)], drums=False, mel=0.4, oct=79, vol=0.75),
    "b_beach":   dict(bpm=88, prog=[(65, MAJ), (62, MIN), (70, MAJ), (72, MAJ)], drums=False, mel=0.45, oct=77, vol=0.7),
    "b_hope":    dict(bpm=76, prog=[(60, MAJ), (57, MIN), (65, MAJ), (67, MAJ)], drums=False, mel=0.45, oct=79, vol=0.7),
    "b_home":    dict(bpm=66, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}
MUSIC = {"title": "b_title", "bowl": "b_morning", "ship": "b_sea", "rambla": "b_rambla", "tapas": "b_tapas",
         "sagrada": "b_grand", "beach": "b_beach", "park": "b_hope", "home": "b_home"}
MUSIC_CUES = [("b_crash", 0.5, "b_sad"), ("b_gull", 0.0, "b_morning"), ("r_guitar", 0.0, "b_flamenco"),
              ("r_vamos", 1.0, "b_rambla"), ("ta_spicy", 0.0, "b_flamenco"), ("ta_churro", 0.0, "b_tapas"),
              ("be_wave", 0.3, "b_sad"), ("be_look", 0.0, "b_hope"), ("pa_ole", 0.0, "b_flamenco")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.3, "t_open", [("strum", 0.05), ("gull", 0.6)]),
    S("narrator", "Whiskers and the Mosaic Bowl.", "title", "t_name"),
    A("title", 1.0, "t_hold", [("waves", 0.0)]),

    # ----------------------------------------------------------------- bowl
    A("bowl", 1.0, "b_open", [("purr", 0.1)]),
    S("narrator", "Whiskers loved his big blue breakfast bowl more than anything.",
      "bowl", "b_narr"),
    S("whiskers", "Good morning, bowl. You look delicious today.", "bowl", "b_hello"),
    A("bowl", 0.9, "b_fly"),
    S("luna", "Whiskers, look! A butterfly!", "bowl", "b_look"),
    A("bowl", 1.2, "b_crash", [("whoosh", 0.05), ("crash", 0.42)]),
    S("whiskers", "Oh no. My bowl. My beautiful bowl.", "bowl", "b_oh"),
    A("bowl", 0.7, "b_sad"),
    A("bowl", 0.9, "b_gull", [("flap", 0.1), ("gull", 0.55)]),
    S("marina", "Hola, gatitos! Why such sad faces?", "bowl", "b_hola"),
    S("luna", "Whiskers broke his favourite bowl.", "bowl", "b_broke"),
    S("marina", "Broken? Ay! In Barcelona, we never throw broken pieces away.", "bowl", "b_never"),
    S("marina", "Come with me, and I will show you a secret.", "bowl", "b_secret"),
    S("whiskers", "Does the secret have food in it?", "bowl", "b_food"),
    A("bowl", 1.0, "b_pack", [("clink", 0.2), ("clink", 0.45), ("clink", 0.7)]),

    # ----------------------------------------------------------------- ship
    S("narrator", "So they sailed away on a big white ship, across the sparkling blue sea.", "ship", "s_narr",
      [("horn", 0.0)]),
    A("ship", 1.6, "s_sail", [("waves", 0.0), ("gull", 0.6)]),
    S("luna", "Dolphins! Whiskers, look, real dolphins!", "ship", "s_dolph", [("splash", 0.6)]),
    S("whiskers", "I'm not looking. I'm keeping my breakfast where it belongs.", "ship", "s_sick"),
    A("ship", 1.8, "s_land", [("waves", 0.0), ("splash", 0.2)]),
    S("marina", "Mira! There it is. Barcelona!", "ship", "s_mira", [("gull", 0.9)]),
    A("ship", 0.8, "s_end", [("horn", 0.1)]),

    # --------------------------------------------------------------- rambla
    S("narrator", "La Rambla was full of flowers, music, and street performers.", "rambla", "r_narr"),
    A("rambla", 1.5, "r_walk"),
    S("whiskers", "Luna. That golden statue just winked at me.", "rambla", "r_wink"),
    A("rambla", 1.0, "r_statue", [("ding", 0.35)]),
    A("rambla", 1.2, "r_guitar", [("flamenco", 0.0)]),
    S("paco", "Ole! Welcome, little friends! I am Paco, and this is my guitar.", "rambla", "r_paco",
      [("strum", 0.0)]),
    S("paco", "And you look hungry, amigo. Vamos, to the tapas!", "rambla", "r_vamos"),
    S("whiskers", "Finally, somebody who understands me.", "rambla", "r_finally"),

    # ---------------------------------------------------------------- tapas
    A("tapas", 0.9, "ta_open", [("clink", 0.4)]),
    S("narrator", "Tapas are little plates, so you can taste a bit of everything.", "tapas", "ta_narr"),
    S("whiskers", "Little plates? Then I will need a lot of them.", "tapas", "ta_lot"),
    A("tapas", 1.5, "ta_eat", [("munch", 0.1), ("clink", 0.35), ("munch", 0.55), ("clink", 0.8)]),
    S("paco", "Careful, amigo! The patatas bravas are a little bit spicy.", "tapas", "ta_careful"),
    A("tapas", 1.3, "ta_spicy", [("munch", 0.05), ("boing", 0.3), ("steam", 0.4)]),
    S("whiskers", "A little spicy? My whiskers are on fire!", "tapas", "ta_fire", [("steam", 0.2)]),
    S("paco", "Quick! Churros with hot chocolate. That will fix it.", "tapas", "ta_churros"),
    A("tapas", 1.4, "ta_churro", [("munch", 0.2), ("gulp", 0.5), ("munch", 0.7)]),
    S("luna", "Whiskers, you have a chocolate moustache.", "tapas", "ta_moust"),
    S("whiskers", "I did that on purpose. It's very fashionable.", "tapas", "ta_purpose"),
    A("tapas", 0.6, "ta_end"),

    # -------------------------------------------------------------- sagrada
    A("sagrada", 1.4, "sa_tilt", [("bells", 0.1)]),
    S("narrator", "Next, they visited the Sagrada Familia, with towers like giant sandcastles.",
      "sagrada", "sa_narr"),
    S("luna", "Why are there cranes everywhere?", "sagrada", "sa_why", [("clank", 0.9)]),
    S("paco", "They have been building it for over a hundred years. It is still not finished.",
      "sagrada", "sa_build"),
    S("whiskers", "Not finished? But it's already so beautiful.", "sagrada", "sa_beauty"),
    S("paco", "Exacto. Beautiful things take time.", "sagrada", "sa_time"),
    A("sagrada", 0.9, "sa_end", [("clank", 0.3)]),

    # ---------------------------------------------------------------- beach
    A("beach", 1.0, "be_open", [("waves", 0.0)]),
    S("narrator", "At the beach, full and happy, Whiskers fell asleep on the warm sand.",
      "beach", "be_narr", [("waves", 0.3)]),
    A("beach", 1.6, "be_nap", [("purr", 0.1), ("waves", 0.4)]),
    A("beach", 1.1, "be_wave", [("bigwave", 0.0)]),
    S("luna", "Whiskers! Wake up! Your bowl!", "beach", "be_wake"),
    A("beach", 1.1, "be_gone", [("waves", 0.0)]),
    S("whiskers", "It's gone. All I have left is one little piece.", "beach", "be_left"),
    A("beach", 0.9, "be_sad"),
    S("luna", "Don't give up, Whiskers. Look what the sea brought us instead.", "beach", "be_look",
      [("sparkle", 0.8)]),
    A("beach", 1.3, "be_glass", [("sparkle", 0.1), ("sparkle", 0.5), ("sparkle", 0.85)]),
    S("marina", "Sea glass, polished by the waves! And a pretty shell, from me.", "beach", "be_shell"),

    # ----------------------------------------------------------------- park
    S("narrator", "Then Paco led them up the hill, to Park Guell.", "park", "pa_narr", [("strum", 0.1)]),
    A("park", 1.3, "pa_up"),
    S("luna", "Whiskers, look! A giant lizard, made of colourful tiles!", "park", "pa_lizard"),
    S("paco", "Every tile was once broken. Gaudi turned the pieces into art.", "park", "pa_gaudi"),
    S("whiskers", "Broken pieces? Like my bowl?", "park", "pa_like"),
    S("marina", "Just like your bowl. That is my secret.", "park", "pa_secret"),
    A("park", 2.4, "pa_build", [("clink", 0.12), ("clink", 0.3), ("clink", 0.48), ("clink", 0.66),
                                ("sparkle", 0.9)]),
    S("whiskers", "It's even better than before. It has a piece of everybody in it.", "park", "pa_better"),
    S("paco", "Then tonight, we celebrate! Ole!", "park", "pa_ole", [("strum", 0.9)]),
    A("park", 2.2, "pa_dance", [("flamenco", 0.0), ("castanets", 0.3), ("castanets", 0.65)]),

    # ----------------------------------------------------------------- home
    A("home", 1.0, "h_open", [("gull", 0.5)]),
    S("narrator", "Back home, Whiskers ate breakfast from the most beautiful bowl in the world.", "home", "h_narr"),
    S("pip", "Wow! Where did you get that?", "home", "h_pip"),
    S("whiskers", "Every piece is from a friend, Pip. The blue one is my old bowl.", "home",
      "h_piece"),
    S("pip", "Can I add a piece too?", "home", "h_add"),
    S("whiskers", "There's always room for one more.", "home", "h_room", [("clink", 0.9)]),
    A("home", 1.3, "h_curl", [("purr", 0.2), ("gull", 0.6)]),
    S("narrator", "Because broken things can shine again, when friends help put the pieces together.",
      "home", "h_moral"),
    A("home", 2.2, "h_end"),
]
