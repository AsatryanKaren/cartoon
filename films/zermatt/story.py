"""Film: "Whiskers and the Chocolate Mountain" -- Whiskers and Luna go to Zermatt and the Matterhorn.

A fluffy black-nosed Valais sheep turns up stuck in the garden hedge: she
is lost on her way home from the fair. Whiskers hears that her mountain
"glows like a mountain of chocolate" and is very keen to help. Same format
as Film 1: `Say` lines take their speech length, weighted `Act` moments
share the rest so the film is exactly 355 s.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.zermatt import sounds

TITLE = "Whiskers and the Chocolate Mountain"
PLACE = "Zermatt"            # folder in the catcute library
SCENES = ["title", "hedge", "trailer", "village", "chocolate", "cogtrain", "meadow", "alpenglow", "home"]

# New Swiss friends
CAST = {
    **CAST,
    # Wolli: a young Valais black-nosed sheep, very fluffy, sweet and a little shy
    "wolli": Voice("bf_lily", 1.02, 2, ["Kate"], 180, "en-gb+f4", 70, 165),
    # Berta: a big, jolly brown cow who makes chocolate, with an enormous bell
    "berta": Voice("bf_isabella", 0.94, -2, ["Moira"], 165, "en-gb+f1", 40, 150),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "wolli": (200, 245, 200),
    "berta": (240, 200, 150),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    "alpenhorn": dict(bpm=70, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=False, mel=0.45, oct=72, vol=0.8),
    "summer":    dict(bpm=108, prog=[(62, MAJ), (67, MAJ), (69, MAJ), (62, MAJ)], drums=True, mel=0.65, oct=74, vol=0.8),
    "lullroad":  dict(bpm=72, prog=[(57, MAJ), (62, MAJ), (64, MAJ), (57, MAJ)], drums=False, mel=0.35, oct=76, vol=0.7),
    "laendler":  dict(bpm=132, prog=[(65, MAJ), (60, MAJ), (60, MAJ), (65, MAJ)], drums=True, mel=0.8, oct=77, vol=0.85),
    "choco":     dict(bpm=116, prog=[(58, MAJ), (63, MAJ), (65, MAJ), (58, MAJ)], drums=True, mel=0.7, oct=74, vol=0.8),
    "climb":     dict(bpm=96, prog=[(64, MAJ), (69, MAJ), (71, MAJ), (64, MAJ)], drums=True, mel=0.55, oct=76, vol=0.75),
    "dusk":      dict(bpm=62, prog=[(57, MIN), (53, MAJ), (60, MAJ), (55, MAJ)], drums=False, mel=0.25, oct=72, vol=0.65),
    "reunion":   dict(bpm=84, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=False, mel=0.5, oct=72, vol=0.8),
    "glow":      dict(bpm=58, prog=[(62, MAJ), (67, MAJ), (59, MIN), (69, MAJ)], drums=False, mel=0.3, oct=74, vol=0.85),
    "homesill":  dict(bpm=66, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}
MUSIC = {"title": "alpenhorn", "hedge": "summer", "trailer": "lullroad", "village": "laendler", "chocolate": "choco",
         "cogtrain": "climb", "meadow": "dusk", "alpenglow": "glow", "home": "homesill"}
MUSIC_CUES = [("tr_taxi", 0.0, "laendler"), ("m_bwoo", 0.6, "reunion")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("cowbell", 0.2), ("alphorn", 0.35)]),
    S("narrator", "Whiskers and the Chocolate Mountain.", "title", "t_name"),
    A("title", 1.4, "t_hold", [("cowbell", 0.4)]),

    # ---------------------------------------------------------------- hedge
    A("hedge", 0.9, "g_open", [("birds", 0.0)]),
    S("narrator", "One sunny summer morning, the hedge in the garden said: baa.", "hedge", "g_narr",
      [("baa", 0.92)]),
    A("hedge", 0.8, "g_shake", [("rustle", 0.0), ("rustle", 0.45)]),
    S("pip", "Whiskers! Luna! There's a cloud stuck in the hedge!", "hedge", "g_pip"),
    A("hedge", 0.8, "g_pop", [("rustle", 0.0), ("pop", 0.55), ("baa", 0.7)]),
    S("wolli", "Hello! I'm Wolli. I fell off the trailer, on the way home from the fair.", "hedge", "g_wolli"),
    S("luna", "Oh, you poor thing! Where is home, Wolli?", "hedge", "g_where"),
    S("wolli", "Zermatt! Under the Matterhorn, the pointiest mountain in the world.", "hedge", "g_zermatt"),
    S("wolli", "At sunrise, it glows like a mountain of chocolate.", "hedge", "g_glow"),
    A("hedge", 0.6, "g_ears"),
    S("whiskers", "A mountain... of chocolate?", "hedge", "g_choc"),
    A("hedge", 1.0, "g_dream", [("sparkle", 0.1)]),
    S("luna", "Don't worry, Wolli. We'll take you home!", "hedge", "g_home"),
    S("whiskers", "To the chocolate mountain! I'll bring a big spoon.", "hedge", "g_spoon", [("meow", 0.9)]),
    A("hedge", 0.6, "g_end"),

    # -------------------------------------------------------------- trailer
    S("narrator", "That evening, the last sheep trailer from the fair rumbled off towards Zermatt.",
      "trailer", "tr_narr", [("engine", 0.0)]),
    A("trailer", 1.0, "tr_ride", [("engine", 0.0), ("baa", 0.6)]),
    S("narrator", "Three stowaways were snuggled inside.", "trailer", "tr_three", [("engine", 0.0)]),
    S("whiskers", "Fluffiest. Bed. Ever.", "trailer", "tr_bed", [("purr", 0.5)]),
    A("trailer", 1.6, "tr_night", [("engine", 0.0), ("engine", 0.5)]),
    S("narrator", "At the end of the road, they hopped into a tiny electric taxi. No cars are allowed in Zermatt!",
      "trailer", "tr_taxi", [("hum", 0.1)]),
    A("trailer", 1.2, "tr_zoom", [("hum", 0.0), ("toot", 0.55)]),

    # -------------------------------------------------------------- village
    A("village", 0.8, "v_open", [("cowbell", 0.3)]),
    S("narrator", "Zermatt was a village of dark wooden chalets, with red flowers at every window.",
      "village", "v_narr", [("clop", 0.2), ("clop", 0.5)]),
    S("luna", "Look, Whiskers! There it is! The Matterhorn!", "village", "v_look"),
    A("village", 0.9, "v_see"),
    S("whiskers", "Hmm. It looks very... rocky. Where's the chocolate?", "village", "v_rocky"),
    A("village", 0.9, "v_cuckoo", [("cuckoo", 0.3)]),
    S("whiskers", "Waah! I jumped on purpose. To stretch.", "village", "v_stretch"),
    S("wolli", "My family is high up on the summer meadow. We must find them before dark.", "village", "v_family"),
    A("village", 0.7, "v_sniff", [("sniff", 0.1), ("sniff", 0.5)]),
    S("whiskers", "Wait. Do you smell that?", "village", "v_smell"),
    A("village", 0.7, "v_follow"),

    # ------------------------------------------------------------ chocolate
    A("chocolate", 0.7, "c_open", [("bell", 0.3)]),
    S("berta", "Grüezi, little ones! Welcome to Berta's chocolate kitchen!", "chocolate", "c_berta",
      [("bigbell", 0.9)]),
    S("whiskers", "A river of chocolate. I'll just have a tiny taste.", "chocolate", "c_taste"),
    A("chocolate", 1.4, "c_lean", [("slip", 0.55), ("splosh", 0.72)]),
    A("chocolate", 0.9, "c_out", [("bubble", 0.0), ("pop", 0.35)]),
    S("whiskers", "I fell in on purpose. I'm a chocolate cat now.", "chocolate", "c_purpose"),
    A("chocolate", 0.8, "c_laugh", [("munch", 0.3)]),
    S("berta", "Ha ha! Here, a little chocolate Matterhorn for each of you.", "chocolate", "c_gift",
      [("sparkle", 0.6)]),
    S("whiskers", "I'm saving mine. For something very special.", "chocolate", "c_save"),
    S("berta", "And take my alphorn. When the sheep hear it, they always come home.", "chocolate", "c_horn"),
    A("chocolate", 0.6, "c_end"),

    # ------------------------------------------------------------- cogtrain
    S("narrator", "So up they went on the little cog train, climbing towards the sky.", "cogtrain", "ct_narr",
      [("cog", 0.0)]),
    A("cogtrain", 1.6, "ct_climb", [("cog", 0.0), ("cog", 0.5), ("cowbell", 0.7)]),
    S("wolli", "Look how tiny the village is now!", "cogtrain", "ct_tiny", [("cog", 0.0)]),
    A("cogtrain", 1.2, "ct_top", [("cog", 0.0), ("ding", 0.85)]),

    # --------------------------------------------------------------- meadow
    A("meadow", 0.8, "m_open", [("wind", 0.0)]),
    S("wolli", "Mama! Mama! Where are you?", "meadow", "m_mama"),
    A("meadow", 0.8, "m_echo", [("echo", 0.05)]),
    S("luna", "Quick, Whiskers! Blow the alphorn!", "meadow", "m_quick"),
    A("meadow", 1.0, "m_blow1", [("pfft", 0.35)]),
    A("meadow", 0.9, "m_blow2", [("squawk", 0.25), ("flap", 0.45)]),
    S("whiskers", "It's broken. I did that on purpose.", "meadow", "m_broken"),
    S("narrator", "The sun sank lower, and Wolli began to cry.", "meadow", "m_sank"),
    S("wolli", "What if I never find my family?", "meadow", "m_never"),
    A("meadow", 0.8, "m_think"),
    S("whiskers", "Here, Wolli. My chocolate Matterhorn. It's for you.", "meadow", "m_give"),
    S("wolli", "But you saved it all day!", "meadow", "m_saved"),
    S("whiskers", "I saved it for something special. And you're special.", "meadow", "m_special"),
    A("meadow", 0.7, "m_breath", [("inhale", 0.3)]),
    S("whiskers", "Okay, alphorn. This time, it's for a friend.", "meadow", "m_friend"),
    A("meadow", 2.4, "m_bwoo", [("alphorn", 0.05), ("cowbell", 0.6), ("baa", 0.7), ("cowbell", 0.8),
                                 ("baa", 0.9)]),
    A("meadow", 1.3, "m_flock", [("baa", 0.1), ("cowbell", 0.3), ("baa", 0.45), ("cowbell", 0.6)]),
    S("wolli", "Mama!", "meadow", "m_found", [("baa", 0.9)]),
    A("meadow", 1.3, "m_hug", [("purr", 0.2)]),

    # ------------------------------------------------------------ alpenglow
    S("narrator", "Next morning, the whole flock watched the sun rise over the Matterhorn.", "alpenglow", "a_narr"),
    A("alpenglow", 3.2, "a_glow", [("cowbell", 0.5)]),
    S("whiskers", "Luna, look. It IS a chocolate mountain. A golden one.", "alpenglow", "a_gold"),
    S("luna", "And you called a whole flock home. I'm proud of you.", "alpenglow", "a_proud"),
    S("wolli", "Thank you, my friends. You'll always have a home in Zermatt.", "alpenglow", "a_thanks",
      [("baa", 0.95)]),
    A("alpenglow", 1.4, "a_hold", [("alphorn", 0.1)]),

    # ----------------------------------------------------------------- home
    A("home", 1.0, "h_open", [("tick", 0.0)]),
    S("narrator", "Back home, Berta's present ticked away on the wall: a real cuckoo clock.", "home", "h_narr",
      [("tick", 0.0)]),
    S("pip", "So, Whiskers? Did you eat the chocolate mountain?", "home", "h_pip"),
    S("whiskers", "Even better, Pip. I helped a friend find her way home.", "home", "h_better"),
    A("home", 1.1, "h_cuckoo", [("cuckoo", 0.1), ("cuckoo", 0.45)]),
    S("whiskers", "But that bird and I are going to have words.", "home", "h_words"),
    A("home", 1.2, "h_curl", [("purr", 0.2)]),
    S("narrator", "Because however far you wander, the sweetest sound in the world is a friend calling you home.",
      "home", "h_moral"),
    A("home", 2.6, "h_end", [("tick", 0.2)]),
]
