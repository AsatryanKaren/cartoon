"""Film: "Whiskers and the Chimney Cake" -- the two cats travel to Prague.

One snowy winter night something tumbles down the chimney in a cloud of soot:
Kasparek, a little wooden marionette from Prague, blown away by the winter wind
with his strings in knots. Pip untangles him. He must be home for the Christmas
puppet show, which starts when the old Astronomical Clock strikes twelve -- and
Prague has chimney cakes, so Whiskers (who wanted no part of the clock's
skeleton) is suddenly ready to go. They float down the river all night on a
barge full of Christmas trees, past swans, to the city of a hundred spires,
cross the Charles Bridge and reach the Christmas market. Whiskers gets his head
stuck in a chimney cake, the skeleton's bell gives him such a fright that the
cake flies into the clock and jams it a minute before noon. Mr Bones, the
skeleton, turns out to be the gentlest soul in Prague; Whiskers climbs into the
clockwork and eats his way through the problem. The apostles march, the show
goes on (starring a puppet Whiskers), and the barge carries them home, where
Whiskers has saved one chimney cake for Pip.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act
from films.prague.sounds import EXTRA_SFX  # noqa: F401

TITLE = "Whiskers and the Chimney Cake"
PLACE = "Prague"            # folder in the catcute library
SCENES = ["title", "chimney", "barge", "bridge", "market", "clock", "gears", "noon", "home"]

CAST = {
    **CAST,
    "kaspar": Voice("am_puck", 1.05, 2, ["Fred"], 186, "en-us+m4", 70, 170),
    "bones": Voice("bm_lewis", 0.9, -2, ["Ralph"], 160, "en-gb+m2", 30, 145),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "kaspar": (175, 240, 160),
    "bones": (240, 222, 170),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    # Bohemian flavour: polka bounce for the city, a slow carol for the snow, music-box for the clock
    "p_title": dict(bpm=72, prog=[(62, MAJ), (59, MIN), (67, MAJ), (69, MAJ)], drums=False, mel=0.5, oct=79, vol=0.8),
    "p_fire": dict(bpm=66, prog=[(65, MAJ), (62, MIN), (70, MAJ), (72, MAJ)], drums=False, mel=0.35, oct=77, vol=0.6),
    "p_puppet": dict(bpm=124, prog=[(67, MAJ), (62, MAJ), (67, MAJ), (62, MAJ)], drums=True, mel=0.7, oct=79, vol=0.75),
    "p_river": dict(bpm=64, prog=[(57, MIN), (53, MAJ), (60, MAJ), (55, MAJ)], drums=False, mel=0.35, oct=76, vol=0.65),
    "p_dawn": dict(bpm=76, prog=[(62, MAJ), (67, MAJ), (59, MIN), (69, MAJ)], drums=False, mel=0.55, oct=81, vol=0.75),
    "p_polka": dict(bpm=132, prog=[(60, MAJ), (67, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.75, oct=76, vol=0.8),
    "p_market": dict(bpm=112, prog=[(65, MAJ), (70, MAJ), (72, MAJ), (65, MAJ)], drums=True, mel=0.7, oct=77, vol=0.75),
    "p_spooky": dict(bpm=70, prog=[(57, MIN), (53, MAJ), (52, MAJ), (57, MIN)], drums=False, mel=0.3, oct=72, vol=0.6),
    "p_brave": dict(bpm=84, prog=[(62, MIN), (58, MAJ), (60, MAJ), (57, MAJ)], drums=False, mel=0.4, oct=74, vol=0.6),
    "p_gears": dict(bpm=96, prog=[(57, MIN), (62, MIN), (64, MAJ), (57, MIN)], drums=True, mel=0.55, oct=81, vol=0.6),
    "p_triumph": dict(bpm=116, prog=[(62, MAJ), (67, MAJ), (69, MAJ), (62, MAJ)], drums=True, mel=0.75, oct=78, vol=0.85),
    "p_show": dict(bpm=128, prog=[(67, MAJ), (60, MAJ), (62, MAJ), (67, MAJ)], drums=True, mel=0.75, oct=79, vol=0.75),
    "p_night": dict(bpm=60, prog=[(65, MAJ), (58, MAJ), (62, MIN), (60, MAJ)], drums=False, mel=0.3, oct=77, vol=0.6),
}
MUSIC = {"title": "p_title", "chimney": "p_fire", "barge": "p_river", "bridge": "p_polka", "market": "p_market",
         "clock": "p_spooky", "gears": "p_gears", "noon": "p_triumph", "home": "p_night"}
MUSIC_CUES = [("c_soot", 0.5, "p_puppet"), ("c_think", 0.0, "p_fire"),
              ("b_dawn", 0.0, "p_dawn"), ("m_bong", 0.0, "p_spooky"),
              ("k_brave", 0.0, "p_brave"), ("g_turn", 0.3, "p_triumph"),
              ("n_show", 0.0, "p_show"), ("h_sill", 0.0, "p_night")]

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.3, "t_open", [("bells", 0.05)]),
    S("narrator", "Whiskers and the Chimney Cake.", "title", "t_name"),
    A("title", 1.0, "t_hold", [("jingle", 0.3)]),

    # -------------------------------------------------------------- chimney
    A("chimney", 1.0, "c_open", [("crackle", 0.0), ("purr", 0.3)]),
    S("narrator", "One snowy winter night, the two cats were warming their paws by the fire.",
      "chimney", "c_narr", [("crackle", 0.4)]),
    A("chimney", 1.3, "c_rumble", [("rumble", 0.05), ("rumble", 0.4), ("poof", 0.78)]),
    S("whiskers", "Hey! Who is throwing logs down the chimney?", "chimney", "c_hey"),
    A("chimney", 0.9, "c_soot", [("jingle", 0.3), ("clack", 0.6)]),
    S("kaspar", "Ahoj! Sorry! I'm Kasparek, a puppet from Prague!", "chimney", "c_ahoj", [("jingle", 0.1)]),
    S("kaspar", "The winter wind blew me off a bridge, and all the way to your chimney!", "chimney", "c_wind"),
    S("luna", "A puppet? But who is pulling your strings?", "chimney", "c_strings"),
    S("kaspar", "Nobody! At Christmas, a little magic lets us walk on our own. But look. Knots!",
      "chimney", "c_knots"),
    A("chimney", 0.7, "c_pip"),
    S("pip", "Tiny knots need tiny paws. Hold still!", "chimney", "c_paws"),
    A("chimney", 1.1, "c_untie", [("pluck", 0.2), ("pluck", 0.5), ("pluck", 0.8)]),
    S("kaspar", "Thank you! Now I must hurry home. Tomorrow at noon, the old clock strikes twelve,",
      "chimney", "c_noon", [("jingle", 0.0)]),
    S("kaspar", "and our Christmas puppet show begins!", "chimney", "c_show"),
    S("luna", "The Astronomical Clock! Where little figures come out every hour!", "chimney", "c_clock",
      [("sparkle", 0.3)]),
    S("kaspar", "And a skeleton rings the bell. Ding, ding!", "chimney", "c_skel", [("ding", 0.75)]),
    S("whiskers", "A skeleton? No, thank you. I'm staying right here.", "chimney", "c_no"),
    S("kaspar", "Pity. Prague has chimney cakes. Warm, sweet, and rolled in sugar.", "chimney", "c_cake"),
    A("chimney", 0.7, "c_think"),
    S("whiskers", "Which way is Prague?", "chimney", "c_which", [("meow", 0.85)]),
    A("chimney", 0.6, "c_end"),

    # ---------------------------------------------------------------- barge
    S("narrator", "So the three friends hid on a barge full of Christmas trees, and floated down the river "
      "all night long.", "barge", "b_narr", [("lap", 0.2)]),
    A("barge", 1.5, "b_float", [("lap", 0.1), ("lap", 0.55), ("owl", 0.7)]),
    S("whiskers", "It smells like a forest. A forest with no snacks.", "barge", "b_forest"),
    A("barge", 1.4, "b_dawn", [("lap", 0.2), ("bells", 0.6)]),
    S("kaspar", "Wake up! Look! Prague, the city of a hundred spires!", "barge", "b_look"),
    S("luna", "And the castle, high up on the hill!", "barge", "b_castle"),
    S("whiskers", "One spire, two spires... ninety-nine spires...", "barge", "b_count"),
    A("barge", 1.4, "b_swans", [("honk", 0.2), ("lap", 0.5), ("honk", 0.7)]),

    # --------------------------------------------------------------- bridge
    S("narrator", "They hopped off at the Charles Bridge, where stone saints stand guard, and musicians play "
      "all day.", "bridge", "br_narr", [("accordion", 0.2)]),
    A("bridge", 1.6, "br_walk", [("accordion", 0.0), ("crunch", 0.4)]),
    S("luna", "Everybody is so happy here!", "bridge", "br_happy"),
    S("kaspar", "Hurry! The clock is just across the square.", "bridge", "br_hurry"),
    A("bridge", 0.8, "br_sniff", [("sniff", 0.2)]),
    S("whiskers", "Sniff, sniff. Cinnamon!", "bridge", "br_cinn"),
    A("bridge", 1.0, "br_run", [("whoosh", 0.2), ("whoosh", 0.6)]),

    # --------------------------------------------------------------- market
    S("narrator", "In the Old Town Square, the Christmas market glowed with lights.", "market", "m_narr",
      [("sizzle", 0.4)]),
    A("market", 1.0, "m_stall", [("sizzle", 0.1)]),
    S("kaspar", "A chimney cake, for my rescuers!", "market", "m_gift", [("sparkle", 0.5)]),
    A("market", 1.6, "m_eat", [("munch", 0.1), ("munch", 0.4), ("pop", 0.75)]),
    S("whiskers", "Mmf! Who turned off the lights?", "market", "m_dark"),
    S("luna", "Whiskers! You've got your head stuck in a chimney cake!", "market", "m_stuck"),
    S("whiskers", "I did that on purpose. It's a hat.", "market", "m_hat"),
    A("market", 1.2, "m_bong", [("ding", 0.1), ("ding", 0.35), ("yowl", 0.45), ("whoosh", 0.6)]),
    S("whiskers", "Aaah! The skeleton! It looked at me!", "market", "m_aah"),
    A("market", 0.6, "m_hide"),

    # ---------------------------------------------------------------- clock
    S("narrator", "It was one minute to noon. And then, the clock stopped.", "clock", "k_narr",
      [("tick", 0.0), ("clank", 0.85)]),
    A("clock", 1.0, "k_stop", [("creak", 0.2)]),
    S("bones", "Oh dear, oh dear. Something is stuck in my gears.", "clock", "k_dear"),
    S("bones", "If I can't ring my bell, the clock can't strike twelve. And there will be no puppet show.",
      "clock", "k_noshow"),
    S("kaspar", "No show? But all the children are waiting!", "clock", "k_kids"),
    S("luna", "Whiskers... where is your chimney cake?", "clock", "k_where"),
    S("whiskers", "Oh no. It flew right into the clock.", "clock", "k_flew"),
    S("bones", "Then someone small must climb inside. Through that little door, up here.", "clock", "k_door"),
    S("whiskers", "Up there? Right next to you?", "clock", "k_next"),
    S("bones", "Don't be afraid, little cat. I'm only bones. Bones and a big smile.", "clock", "k_smile"),
    A("clock", 0.8, "k_brave"),
    S("whiskers", "That cake is my mess. I'll fix it.", "clock", "k_fix"),
    A("clock", 1.5, "k_climb", [("whoosh", 0.1), ("scrabble", 0.3), ("scrabble", 0.6), ("creak", 0.9)]),

    # ---------------------------------------------------------------- gears
    S("narrator", "Inside, the clock was a giant maze of golden wheels.", "gears", "g_narr", [("tick", 0.2)]),
    A("gears", 1.0, "g_look", [("tick", 0.0)]),
    S("whiskers", "There it is. Stuck in the biggest wheel.", "gears", "g_there"),
    S("whiskers", "Don't worry. This is the job I was born for.", "gears", "g_born"),
    A("gears", 1.8, "g_munch", [("munch", 0.05), ("munch", 0.3), ("munch", 0.55), ("munch", 0.8)]),
    A("gears", 1.1, "g_turn", [("clank", 0.1), ("whirr", 0.3), ("tick", 0.6)]),
    S("whiskers", "Delicious. And the clock is free!", "gears", "g_free"),

    # ----------------------------------------------------------------- noon
    A("noon", 1.0, "n_strike", [("ding", 0.1), ("ding", 0.4), ("ding", 0.7)]),
    S("narrator", "Ding, ding! The skeleton rang his bell, and the little apostles marched past the windows.",
      "noon", "n_narr", [("chimes", 0.3)]),
    A("noon", 1.6, "n_parade", [("chimes", 0.0), ("chimes", 0.4), ("crow", 0.85)]),
    S("bones", "Thank you, brave cat. You saved twelve o'clock!", "noon", "n_thanks", [("cheer", 0.1)]),
    S("whiskers", "You're not scary at all, Mister Bones. Just a bit thin.", "noon", "n_thin"),
    S("bones", "And you're not a scaredy cat at all. Just a bit round.", "noon", "n_round"),
    A("noon", 0.8, "n_laugh", [("laugh", 0.1)]),
    S("narrator", "And at last, the Christmas puppet show began.", "noon", "n_show", [("applause", 0.4)]),
    A("noon", 1.3, "n_curtain", [("xylo", 0.1)]),
    S("kaspar", "The story of a brave orange cat, who ate his way into a clock!", "noon", "n_story"),
    A("noon", 1.5, "n_play", [("xylo", 0.0), ("laugh", 0.5), ("applause", 0.75)]),
    S("whiskers", "I did that on purpose too.", "noon", "n_too"),
    S("kaspar", "Come back soon, my friends! Na shledanou!", "noon", "n_bye", [("jingle", 0.2)]),
    A("noon", 0.8, "n_end", [("applause", 0.1)]),

    # ----------------------------------------------------------------- home
    A("home", 1.3, "h_float", [("lap", 0.1), ("lap", 0.6)]),
    S("narrator", "That night, the empty barge carried them home, under the winter stars.", "home", "h_narr"),
    A("home", 1.0, "h_sill", [("crackle", 0.1)]),
    S("pip", "You're back! Did you bring me anything?", "home", "h_pip"),
    S("whiskers", "One chimney cake. I saved it just for you.", "home", "h_gift", [("sparkle", 0.4)]),
    S("whiskers", "I only licked it a little.", "home", "h_lick"),
    S("luna", "Merry Christmas, Whiskers.", "home", "h_merry", [("jingle", 0.4)]),
    S("whiskers", "Merry Christmas. Don't wake me before noon.", "home", "h_noon", [("purr", 0.6)]),
    S("narrator", "A friend can be wooden, or tiny, or made of bones. What matters is the kind heart inside.",
      "home", "h_moral"),
    A("home", 3.4, "h_end", [("bells", 0.1), ("purr", 0.4)]),
]
