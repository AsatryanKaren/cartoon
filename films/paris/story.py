"""Film: "Whiskers and the City of Lights" -- the two cats go to Paris.

A postcard of the sparkling Eiffel Tower blows onto Whiskers' nose. The cats
(and a stowaway Pip) ride a picnic basket on the train to Paris, meet Colette,
cause croissant chaos in Monsieur Gaston's bakery, float down the Seine past
the Louvre -- and, thanks to one nap too many, get lost at dusk in Montmartre.
Lazy Whiskers leads the climb up the steps of the Sacre-Coeur, the tower
sparkles, and he shares the croissant he saved all day.
"""
from common import *  # noqa: F401,F403
from films.paris.sounds import EXTRA_SFX  # noqa: F401

TITLE = "Whiskers and the City of Lights"
SCENES = ["title", "postcard", "train", "arrival", "bakery", "seine", "montmartre", "sparkle", "home"]

CAST = {
    **CAST,
    "colette": Voice("ff_siwis", 0.95, 0, ["Amelie"], 178, "fr+f2", 58, 158),
    "gaston": Voice("am_onyx", 0.95, -2, ["Thomas"], 160, "fr+m3", 25, 140),
    "pierre": Voice("am_puck", 1.0, 2, ["Thomas"], 184, "fr+m1", 60, 168),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "colette": (255, 235, 140),
    "gaston": (200, 235, 180),
    "pierre": (190, 240, 240),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    # A-minor musette feel for the city at night
    "p_title": dict(bpm=76, prog=[(57, MIN), (62, MIN), (64, MAJ), (57, MIN)], drums=False, mel=0.5, oct=76, vol=0.8),
    "p_train": dict(bpm=132, prog=[(60, MAJ), (67, MAJ), (65, MAJ), (67, MAJ)], drums=True, mel=0.7, oct=72, vol=0.8),
    "p_paris": dict(bpm=112, prog=[(60, MAJ), (57, MIN), (62, MIN), (55, MAJ)], drums=True, mel=0.7, oct=79, vol=0.8),
    "p_bakery": dict(bpm=92, prog=[(62, MIN), (57, MAJ), (62, MIN), (57, MAJ)], drums=True, mel=0.45, oct=74, vol=0.75),
    "p_chase": dict(bpm=152, prog=[(62, MIN), (58, MAJ), (60, MAJ), (57, MAJ)], drums=True, mel=0.8, oct=74, vol=0.85),
    "p_seine": dict(bpm=84, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.5, oct=77, vol=0.75),
    "p_nap": dict(bpm=60, prog=[(65, MAJ), (58, MAJ), (65, MAJ), (60, MAJ)], drums=False, mel=0.25, oct=77, vol=0.6),
    "p_lost": dict(bpm=68, prog=[(57, MIN), (53, MAJ), (52, MIN), (57, MIN)], drums=False, mel=0.3, oct=76, vol=0.65),
    "p_climb": dict(bpm=104, prog=[(57, MIN), (53, MAJ), (60, MAJ), (55, MAJ)], drums=True, mel=0.6, oct=76, vol=0.8),
    "p_sparkle": dict(bpm=72, prog=[(65, MAJ), (69, MIN), (70, MAJ), (72, MAJ)], drums=False, mel=0.5, oct=84, vol=0.75),
}
MUSIC = {"title": "p_title", "postcard": "morning", "train": "p_train", "arrival": "p_paris",
         "bakery": "p_bakery", "seine": "p_chase", "montmartre": "p_lost", "sparkle": "p_lost",
         "home": "home"}
MUSIC_CUES = [("b_hey", 0.0, "p_chase"), ("s_purpose", 0.0, "p_seine"), ("s_sleepy", 0.2, "p_nap"),
              ("m_come", 0.6, "p_climb"), ("x_sparkle", 0.0, "p_sparkle")]

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("sparkle", 0.3)]),
    S("narrator", "Whiskers and the City of Lights.", "title", "t_name"),
    A("title", 1.6, "t_hold", [("sparkle", 0.2)]),

    # ------------------------------------------------------------- postcard
    A("postcard", 1.4, "p_sleep", [("purr", 0.1)]),
    S("narrator", "Ever since the Moon Fish, Whiskers had napped on the windowsill every day.",
      "postcard", "p_narr"),
    A("postcard", 1.2, "p_wind", [("whoosh", 0.15)]),
    S("whiskers", "Mmf! Who is throwing paper at a sleeping cat?", "postcard", "p_mmf"),
    S("luna", "A postcard from Paris! Look, the Eiffel Tower!", "postcard", "p_card",
      [("sparkle", 0.3)]),
    S("luna", "Every night, it sparkles like a thousand stars. Let's go and see it!", "postcard", "p_says"),
    S("whiskers", "Paris... isn't that where croissants come from?", "postcard", "p_crois"),
    S("whiskers", "Paris is very far. And my legs are very short.", "postcard", "p_far"),
    A("postcard", 1.0, "p_basket"),
    S("luna", "Then we'll ride in that basket. It's going to Paris on the train!",
      "postcard", "p_plan"),
    A("postcard", 1.6, "p_jump", [("whoosh", 0.1), ("whoosh", 0.45), ("clink", 0.85)]),

    # ---------------------------------------------------------------- train
    S("narrator", "So two cats hid in a picnic basket, and rode the train to Paris.",
      "train", "tr_narr", [("chug", 0.0)]),
    A("train", 1.6, "tr_ride", [("whistle", 0.2), ("chug", 0.5)]),
    A("train", 0.9, "tr_inside", [("chug", 0.1)]),
    S("whiskers", "This basket smells like cheese. I love it.", "train", "tr_cheese"),
    A("train", 0.8, "tr_rustle", [("clink", 0.4)]),
    S("pip", "Psst! Save some cheese for me!", "train", "tr_pip"),
    S("luna", "Pip! What are you doing here?", "train", "tr_what"),
    S("pip", "Every big adventure needs a brave mouse!", "train", "tr_brave"),
    A("train", 2.0, "tr_arrive", [("whistle", 0.1), ("chug", 0.3)]),

    # -------------------------------------------------------------- arrival
    A("arrival", 1.4, "a_out", [("accordion", 0.05), ("whoosh", 0.45)]),
    S("narrator", "Paris! The City of Lights. Rooftops, bridges, and fresh bread everywhere.",
      "arrival", "a_narr"),
    A("arrival", 0.8, "a_walk"),
    S("colette", "Bonjour, little travellers! You look a little bit lost.", "arrival", "a_bonjour"),
    S("luna", "We came to see the Eiffel Tower sparkle!", "arrival", "a_luna"),
    S("colette", "I am Colette. The tower sparkles at nine tonight. Until then, I show you Paris!",
      "arrival", "a_colette"),
    S("whiskers", "Does your city have croissants?", "arrival", "a_crois"),
    S("colette", "Mon ami, it has the best croissants in the world.", "arrival", "a_best", [("accordion", 0.9)]),
    A("arrival", 1.4, "a_go"),

    # --------------------------------------------------------------- bakery
    A("bakery", 1.0, "b_arrive", [("bell", 0.15)]),
    S("narrator", "Whiskers followed his nose into the bakery of Monsieur Gaston.", "bakery", "b_narr"),
    A("bakery", 1.5, "b_sneak"),
    S("whiskers", "One for me... one for me... and one more for me.", "bakery", "b_stack"),
    A("bakery", 1.2, "b_wobble"),
    S("gaston", "Hey! Who is stealing my croissants?", "bakery", "b_hey"),
    A("bakery", 1.6, "b_poof", [("whoosh", 0.05), ("poof", 0.3)]),
    S("gaston", "Since when do I have a cat statue?", "bakery", "b_statue"),
    A("bakery", 1.2, "b_still"),
    S("whiskers", "Ah... ah... ACHOO!", "bakery", "b_achoo", [("poof", 0.85)]),
    S("gaston", "Come back here, you flour monster!", "bakery", "b_monster"),
    A("bakery", 1.8, "b_chase", [("whoosh", 0.1), ("bell", 0.25), ("whoosh", 0.55)]),

    # ---------------------------------------------------------------- seine
    S("colette", "Vite! To the river! Jump on the boat!", "seine", "s_vite"),
    A("seine", 1.6, "s_jump", [("whoosh", 0.15), ("whoosh", 0.35), ("horn", 0.7)]),
    S("whiskers", "We escaped. I planned that. Completely on purpose.", "seine", "s_purpose"),
    S("luna", "Whiskers, you are covered in flour!", "seine", "s_flour"),
    A("seine", 1.6, "s_float", [("accordion", 0.1)]),
    S("colette", "Look! The Louvre, the biggest museum in the world. And its glass pyramid.", "seine", "s_louvre"),
    S("pip", "It looks like a giant piece of cheese!", "seine", "s_cheese"),
    S("colette", "I must go home now. Nine o'clock at the tower. Don't be late!", "seine", "s_bye"),
    A("seine", 1.0, "s_wave", [("whoosh", 0.3)]),
    S("narrator", "But the sun was warm, and a full cat is a sleepy cat.",
      "seine", "s_sleepy", [("purr", 0.4)]),
    A("seine", 2.2, "s_nap", [("purr", 0.2)]),
    S("luna", "Whiskers! Wake up! The sun is going down! Where are we?", "seine", "s_wake", [("horn", 0.9)]),

    # ----------------------------------------------------------- montmartre
    A("montmartre", 1.4, "m_lost"),
    S("whiskers", "The tower is this way. Or maybe that way.", "montmartre", "m_way"),
    S("luna", "We're lost, Whiskers. We came all this way, and now we'll miss it.", "montmartre", "m_lostline"),
    A("montmartre", 1.0, "m_sad"),
    S("pierre", "Lost, mes amis? Then go up, not around!", "montmartre", "m_pierre"),
    S("pierre", "From the top of the steps, you can see all of Paris.", "montmartre", "m_steps"),
    A("montmartre", 1.3, "m_look_up", [("bell", 0.5)]),
    S("luna", "So many steps. I'm too tired, Whiskers.", "montmartre", "m_tired"),
    S("whiskers", "Come on, Luna. If a lazy cat can climb them, so can you.", "montmartre", "m_come"),
    A("montmartre", 2.6, "m_climb", [("meow", 0.05)]),

    # -------------------------------------------------------------- sparkle
    A("sparkle", 1.0, "x_top"),
    S("pip", "Is it nine o'clock yet?", "sparkle", "x_nine"),
    A("sparkle", 1.2, "x_bong", [("bell", 0.0), ("bell", 0.3), ("bell", 0.6)]),
    A("sparkle", 2.6, "x_sparkle", [("sparkle", 0.0), ("sparkle", 0.35), ("sparkle", 0.7)]),
    S("luna", "Oh, Whiskers. It's the most beautiful thing I have ever seen.", "sparkle", "x_beautiful"),
    S("whiskers", "I saved something too. The best croissant in Paris. For you.", "sparkle", "x_saved"),
    S("luna", "You saved a croissant? You?", "sparkle", "x_you"),
    S("whiskers", "Completely on purpose.", "sparkle", "x_purpose"),
    A("sparkle", 1.4, "x_share", [("sparkle", 0.5)]),
    S("narrator", "High above Paris, three friends shared one croissant. It tasted better than a hundred.",
      "sparkle", "x_narr"),
    A("sparkle", 1.0, "x_end", [("sparkle", 0.2)]),

    # ----------------------------------------------------------------- home
    A("home", 1.6, "h_train", [("whistle", 0.2), ("chug", 0.4)]),
    S("narrator", "The picnic basket brought them home again.", "home", "h_narr"),
    A("home", 1.4, "h_sill", [("purr", 0.2)]),
    S("luna", "Where shall we go next, Whiskers?", "home", "h_next"),
    S("whiskers", "Somewhere with a nap. And croissants.", "home", "h_nap"),
    A("home", 1.0, "h_purr", [("purr", 0.1)]),
    S("narrator", "Because the most beautiful sights in the world are even more beautiful when you share them.",
      "home", "h_moral"),
    A("home", 4.0, "h_end"),
]
