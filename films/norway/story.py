"""Film: "Whiskers and the Dancing Lights" -- Whiskers and Luna go to Norway.

A fish van from Norway stops outside the cats' window. Luna dreams of the
northern lights; Whiskers just smells fish -- and, never one to wait, he dives
into a crate. Luna jumps in after him, the lid slams, and a cargo plane flies
them north. In Bergen's harbour of wooden houses they meet Tuva the puffin,
and Whiskers burns his tongue on a waffle he could not wait for (brown cheese
makes everything better). Tuva sails them up a fjord in a Viking longship,
under a waterfall, to a snowy forest where Whiskers mistakes a moose for a
troll. Magnus the moose takes them up Troll Hill: "the lights come to those
who wait". But the sky stays cloudy, and Luna wants to give up -- until
Whiskers, who never waits for anything, says: we'll wait together. The clouds
part and the sky dances green and purple. Back home, Whiskers waits patiently
for a waffle to cool.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.norway import sounds

TITLE = "Whiskers and the Dancing Lights"
PLACE = "Norway"            # folder in the catcute library
SCENES = ["title", "van", "plane", "harbour", "fjord", "forest", "hill", "aurora", "home"]

CAST = {
    **CAST,
    # Tuva: a chatty, bouncy puffin from Bergen harbour
    "tuva": Voice("af_nova", 1.08, 2, ["Samantha"], 188, "en-us+f4", 72, 172),
    # Magnus: a huge, slow, gentle moose of the snowy forest
    "magnus": Voice("am_fenrir", 0.86, -2, ["Ralph"], 150, "en-us+m1", 22, 135),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "tuva": (255, 190, 120),
    "magnus": (190, 240, 200),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    "n_title":  dict(bpm=66, prog=[(62, MIN), (58, MAJ), (65, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=74, vol=0.8),
    "n_street": dict(bpm=104, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=True, mel=0.6, oct=77, vol=0.78),
    "n_sneak":  dict(bpm=126, prog=[(62, MIN), (60, MAJ), (58, MAJ), (57, MAJ)], drums=True, mel=0.7, oct=74, vol=0.8),
    "n_fly":    dict(bpm=86, prog=[(60, MAJ), (67, MAJ), (57, MIN), (65, MAJ)], drums=False, mel=0.55, oct=76, vol=0.8),
    "n_harbour": dict(bpm=116, prog=[(67, MAJ), (62, MAJ), (64, MIN), (60, MAJ)], drums=True, mel=0.75, oct=79, vol=0.82),
    "n_waffle": dict(bpm=132, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.8, oct=76, vol=0.82),
    "n_viking": dict(bpm=92, prog=[(62, MIN), (60, MAJ), (58, MAJ), (62, MIN)], drums=True, mel=0.55, oct=74, vol=0.85),
    "n_forest": dict(bpm=70, prog=[(57, MIN), (53, MAJ), (55, MAJ), (52, MIN)], drums=False, mel=0.3, oct=76, vol=0.7),
    "n_troll":  dict(bpm=140, prog=[(57, MIN), (56, MAJ), (57, MIN), (52, MAJ)], drums=True, mel=0.8, oct=72, vol=0.8),
    "n_moose":  dict(bpm=80, prog=[(55, MAJ), (60, MAJ), (52, MIN), (62, MAJ)], drums=False, mel=0.45, oct=74, vol=0.75),
    "n_wait":   dict(bpm=58, prog=[(57, MIN), (53, MAJ), (60, MAJ), (55, MAJ)], drums=False, mel=0.25, oct=74, vol=0.62),
    "n_hope":   dict(bpm=64, prog=[(60, MAJ), (57, MIN), (53, MAJ), (55, MAJ)], drums=False, mel=0.35, oct=76, vol=0.7),
    "n_aurora": dict(bpm=60, prog=[(62, MAJ), (67, MAJ), (59, MIN), (69, MAJ)], drums=False, mel=0.45, oct=79, vol=0.88),
    "n_home":   dict(bpm=66, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.72),
}
MUSIC = {"title": "n_title", "van": "n_street", "plane": "n_fly", "harbour": "n_harbour", "fjord": "n_viking",
         "forest": "n_forest", "hill": "n_wait", "aurora": "n_aurora", "home": "n_home"}
MUSIC_CUES = [("v_sneak", 0.0, "n_sneak"), ("pl_narr", 0.0, "n_fly"), ("hb_ten", 0.0, "n_waffle"),
              ("hb_end", 0.0, "n_harbour"), ("fo_troll", 0.0, "n_troll"), ("fo_magnus", 0.0, "n_moose"),
              ("hi_waffles", 0.0, "n_hope")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.2, "t_open", [("wind", 0.0), ("shimmer", 0.3)]),
    S("narrator", "Whiskers and the Dancing Lights.", "title", "t_name"),
    A("title", 1.0, "t_hold", [("shimmer", 0.2)]),

    # ------------------------------------------------------------------ van
    A("van", 1.0, "v_open", [("engine", 0.0)]),
    S("narrator", "One chilly morning, a fish van stopped right outside the cats' window.", "van", "v_narr",
      [("brakes", 0.7)]),
    S("luna", "Whiskers, look! Those crates came all the way from Norway!", "van", "v_look"),
    S("luna", "Up there, the night sky dances, green and purple. I wish I could see it.", "van", "v_dance"),
    S("whiskers", "Dancing skies are nice. Dancing fish are nicer.", "van", "v_fish", [("sniff", 0.7)]),
    S("narrator", "Now, Whiskers was very bad at waiting.", "van", "v_wait"),
    A("van", 1.3, "v_sneak", [("whoosh", 0.1), ("thump", 0.5)]),
    S("luna", "Whiskers, wait! That crate is going to the airport!", "van", "v_stop"),
    A("van", 0.9, "v_jump", [("whoosh", 0.1), ("thump", 0.45), ("slam", 0.75)]),
    S("pip", "Hey! Come back! Oh, bring me a souvenir!", "van", "v_pip", [("engine", 0.3)]),
    A("van", 1.1, "v_drive", [("engine", 0.0)]),

    # ---------------------------------------------------------------- plane
    S("narrator", "So two cats flew north, in a crate of fish, inside a big cargo plane.", "plane", "pl_narr",
      [("plane", 0.0)]),
    A("plane", 1.6, "pl_fly", [("plane", 0.0), ("plane", 0.6)]),
    S("whiskers", "Breakfast, lunch and dinner, all in one box!", "plane", "pl_munch", [("plane", 0.0)]),
    S("luna", "Whiskers, look! Mountains, and snow, and the sea, all tangled together!", "plane", "pl_look",
      [("plane", 0.3)]),
    A("plane", 1.4, "pl_land", [("plane", 0.0), ("thump", 0.85)]),

    # -------------------------------------------------------------- harbour
    S("narrator", "They landed in Bergen, a harbour town of little wooden houses.", "harbour", "hb_narr",
      [("bell", 0.2)]),
    A("harbour", 0.9, "hb_pop", [("creak", 0.2), ("puffin", 0.75)]),
    S("tuva", "Hallo, stowaways! I'm Tuva the puffin. Welcome to Norway!", "harbour", "hb_tuva"),
    S("luna", "Tuva, where can we see the northern lights?", "harbour", "hb_where"),
    S("tuva", "Far up the fjord, on Troll Hill. But first, you must try our waffles!", "harbour", "hb_waffle"),
    A("harbour", 1.1, "hb_walk", [("puffin", 0.6)]),
    S("whiskers", "Waffles? I'll have ten. Right now!", "harbour", "hb_ten", [("sizzle", 0.4)]),
    S("tuva", "Wait, wait! They're still too hot!", "harbour", "hb_hot"),
    A("harbour", 1.2, "hb_burn", [("sizzle", 0.05), ("yowl", 0.25), ("boing", 0.5), ("boing", 0.75)]),
    S("whiskers", "Hot! Hot! I did that on purpose. To test them.", "harbour", "hb_purpose"),
    S("tuva", "Here. With brown cheese on top. Norwegian magic.", "harbour", "hb_brown"),
    A("harbour", 0.8, "hb_taste", [("munch", 0.2), ("munch", 0.55)]),
    S("whiskers", "It's cheese, but it tastes like caramel! I love this country!", "harbour", "hb_love"),
    A("harbour", 0.8, "hb_end", [("puffin", 0.4)]),

    # ---------------------------------------------------------------- fjord
    S("narrator", "So Tuva took them up the fjord, in a real Viking longship with a dragon head.", "fjord",
      "fj_narr", [("waves", 0.0)]),
    A("fjord", 1.9, "fj_sail", [("waves", 0.0), ("oars", 0.2), ("oars", 0.55), ("horn", 0.8)]),
    S("luna", "Look at the cliffs! They go all the way up to the clouds!", "fjord", "fj_cliffs", [("waves", 0.2)]),
    S("tuva", "And here are the Seven Sisters. The prettiest waterfalls in Norway!", "fjord", "fj_sisters",
      [("falls", 0.3)]),
    A("fjord", 1.4, "fj_splash", [("falls", 0.0), ("splash", 0.4), ("splash", 0.6)]),
    S("whiskers", "Nobody. Say. Anything.", "fjord", "fj_wet"),
    A("fjord", 1.0, "fj_end", [("waves", 0.0), ("oars", 0.3)]),

    # --------------------------------------------------------------- forest
    A("forest", 0.9, "fo_open", [("crunch", 0.2), ("crunch", 0.5), ("crunch", 0.8)]),
    S("narrator", "At the end of the fjord, the snowy forest grew dark and quiet.", "forest", "fo_narr",
      [("crunch", 0.3), ("crunch", 0.7)]),
    A("forest", 1.2, "fo_shadow", [("stomp", 0.2), ("stomp", 0.5), ("snap", 0.75)]),
    S("whiskers", "T-T-Troll! A real troll! Everybody run!", "forest", "fo_troll", [("yowl", 0.9)]),
    A("forest", 1.1, "fo_reveal", [("stomp", 0.15), ("stomp", 0.45), ("bellow", 0.7)]),
    S("magnus", "A troll? Ho ho. No, little one. I am only Magnus, the moose.", "forest", "fo_magnus"),
    S("luna", "Magnus, will the northern lights dance tonight?", "forest", "fo_tonight"),
    S("magnus", "Maybe. The lights come to those who wait. Climb on, I'll carry you up Troll Hill.",
      "forest", "fo_wait"),
    A("forest", 1.4, "fo_ride", [("stomp", 0.2), ("stomp", 0.5), ("stomp", 0.8)]),

    # ----------------------------------------------------------------- hill
    A("hill", 1.1, "hi_open", [("wind", 0.0)]),
    S("narrator", "On top of Troll Hill, they waited, and waited. But the sky stayed full of clouds.",
      "hill", "hi_narr", [("wind", 0.5)]),
    S("luna", "It's no use. We came all this way, and there's nothing.", "hill", "hi_nothing"),
    S("whiskers", "Hey. Remember the waffles? The best things need a little waiting.", "hill", "hi_waffles"),
    S("whiskers", "I'm not going anywhere, Luna. We'll wait together.", "hill", "hi_together"),
    A("hill", 1.7, "hi_snuggle", [("purr", 0.1), ("wind", 0.5)]),
    S("magnus", "Look up, little ones. The wind is changing.", "hill", "hi_change", [("wind", 0.4)]),
    A("hill", 1.3, "hi_part", [("shimmer", 0.5)]),

    # --------------------------------------------------------------- aurora
    A("aurora", 2.0, "au_glow", [("shimmer", 0.0), ("shimmer", 0.5)]),
    S("luna", "Whiskers... the sky is dancing!", "aurora", "au_dance"),
    S("tuva", "Green and purple! The northern lights!", "aurora", "au_green", [("puffin", 0.95)]),
    A("aurora", 1.4, "au_reindeer", [("shimmer", 0.2), ("bells", 0.4)]),
    S("whiskers", "Luna? This was worth every single minute.", "aurora", "au_worth"),
    S("luna", "Thank you for waiting with me.", "aurora", "au_thanks"),
    A("aurora", 3.0, "au_hold", [("shimmer", 0.1), ("purr", 0.4), ("shimmer", 0.6)]),

    # ----------------------------------------------------------------- home
    A("home", 1.0, "h_open"),
    S("narrator", "A few days later, the fish van brought two happy cats back home.", "home", "h_narr",
      [("engine", 0.0)]),
    S("pip", "You're back! Did you see the sky dance?", "home", "h_pip"),
    S("luna", "We did, Pip. Because Whiskers waited with me, all night long.", "home", "h_luna"),
    S("pip", "Whiskers? Waiting? For something that isn't food?", "home", "h_pip2"),
    A("home", 0.8, "h_waffle", [("clink", 0.4)]),
    S("whiskers", "This one's too hot. So I'll wait. One... two... three...", "home", "h_count"),
    S("whiskers", "Perfect!", "home", "h_perfect", [("munch", 0.6)]),
    A("home", 1.2, "h_eat", [("munch", 0.1), ("purr", 0.4)]),
    S("narrator", "Because the most wonderful things are worth the wait, when you wait with a friend.",
      "home", "h_moral"),
    A("home", 2.0, "h_end"),
]
