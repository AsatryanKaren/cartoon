"""Film: "Whiskers and the Owl of Athens" -- Whiskers and Luna go to Athens.

On a stormy night, while Luna reads her book of Greek myths (how Athena won
Athens with an olive tree), a soaked little owl crashes onto the windowsill.
Sophia was blown all the way from Athens and her wing hurts; her family waits
for her on the Parthenon at the full moon. Whiskers, who "knows everything",
promises to take her home. A silver honey airship carries them over the blue
Aegean. In the maze of the Plaka Whiskers refuses to ask the way, walks in
circles, and dives face-first into a bowl of yogurt and honey (a philosopher's
beard!). In the old stone theatre his echo talks back -- it is Socrates, an
old street cat. As the sun sets, Whiskers finally admits he doesn't know the
way, and asks. The cats of Athens lead them up a secret path, past the
Caryatids, to the moonlit Parthenon and Sophia's grandmother. Moral: nobody
knows everything -- the wise thing is to ask.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.athens import sounds

TITLE = "Whiskers and the Owl of Athens"
PLACE = "Athens"            # folder in the catcute library
SCENES = ["title", "storm", "airship", "plaka", "yogurt", "theatre", "agora", "acropolis", "home"]

CAST = {
    **CAST,
    # Sophia: a small, bright little owl from the Parthenon, with a hurt wing
    "sophia": Voice("bf_alice", 1.05, 3, ["Kate"], 186, "en-gb+f4", 74, 172),
    # Socrates: an old, white-chinned Athens street cat who answers questions with questions
    "socrates": Voice("am_onyx", 0.88, -1, ["Ralph"], 150, "en-us+m1", 26, 140),
    # Yaya Glafki: Sophia's grandmother, the old owl of the Parthenon
    "yaya": Voice("bf_isabella", 0.9, -2, ["Moira"], 160, "en-gb+f2", 40, 150),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "sophia": (255, 214, 140),
    "socrates": (205, 240, 190),
    "yaya": (225, 200, 255),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
# Greek colour: minor keys leaning on the major dominant (Dm Gm A Dm), sirtaki-style speed-ups
SIRTAKI = [(62, MIN), (55, MIN), (57, MAJ), (62, MIN)]
MOODS = {
    "g_title":  dict(bpm=76, prog=[(62, MIN), (60, MAJ), (58, MAJ), (57, MAJ)], drums=False, mel=0.5, oct=74, vol=0.8),
    "g_storm":  dict(bpm=66, prog=[(57, MIN), (53, MAJ), (52, MAJ), (57, MIN)], drums=False, mel=0.3, oct=74, vol=0.6),
    "g_myth":   dict(bpm=72, prog=[(62, MIN), (58, MAJ), (60, MAJ), (57, MAJ)], drums=False, mel=0.55, oct=79, vol=0.7),
    "g_owl":    dict(bpm=84, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.45, oct=77, vol=0.7),
    "g_sky":    dict(bpm=92, prog=[(62, MAJ), (67, MAJ), (59, MIN), (57, MAJ)], drums=True, mel=0.6, oct=78, vol=0.78),
    "g_plaka":  dict(bpm=126, prog=SIRTAKI, drums=True, mel=0.75, oct=74, vol=0.8),
    "g_lost":   dict(bpm=144, prog=SIRTAKI, drums=True, mel=0.85, oct=76, vol=0.82),
    "g_yogurt": dict(bpm=112, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.7, oct=76, vol=0.8),
    "g_echo":   dict(bpm=70, prog=[(57, MIN), (62, MIN), (64, MAJ), (57, MIN)], drums=False, mel=0.35, oct=74, vol=0.65),
    "g_sunset": dict(bpm=60, prog=[(62, MIN), (58, MAJ), (55, MIN), (57, MAJ)], drums=False, mel=0.25, oct=74, vol=0.58),
    "g_hope":   dict(bpm=76, prog=[(60, MAJ), (57, MIN), (65, MAJ), (67, MAJ)], drums=False, mel=0.45, oct=79, vol=0.7),
    "g_climb":  dict(bpm=104, prog=[(62, MIN), (60, MAJ), (58, MAJ), (57, MAJ)], drums=True, mel=0.6, oct=76, vol=0.78),
    "g_moon":   dict(bpm=64, prog=[(62, MAJ), (67, MAJ), (59, MIN), (69, MAJ)], drums=False, mel=0.45, oct=81, vol=0.85),
    "g_dance":  dict(bpm=138, prog=[(62, MAJ), (67, MAJ), (69, MAJ), (62, MAJ)], drums=True, mel=0.8, oct=78, vol=0.85),
    "g_home":   dict(bpm=64, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}
MUSIC = {"title": "g_title", "storm": "g_storm", "airship": "g_sky", "plaka": "g_plaka", "yogurt": "g_yogurt",
         "theatre": "g_echo", "agora": "g_sunset", "acropolis": "g_climb", "home": "g_home"}
MUSIC_CUES = [("s_myth", 0.0, "g_myth"), ("s_thump", 0.2, "g_owl"), ("a_tale", 0.0, "g_myth"),
              ("a_land", 0.0, "g_sky"), ("p_maze", 0.0, "g_lost"), ("p_sniff", 0.0, "g_plaka"),
              ("ag_ask", 0.0, "g_hope"), ("ac_top", 0.0, "g_moon"), ("ac_dance", 0.0, "g_dance")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.3, "t_open", [("bouzouki", 0.05)]),
    S("narrator", "Whiskers and the Owl of Athens.", "title", "t_name"),
    A("title", 1.0, "t_hold", [("hoot", 0.3)]),

    # ---------------------------------------------------------------- storm
    A("storm", 1.0, "s_open", [("rain", 0.0), ("thunder", 0.4)]),
    S("narrator", "One stormy night, Luna was reading Greek myths.",
      "storm", "s_narr", [("rain", 0.3)]),
    S("luna", "Long ago, Athena and Poseidon both wanted the same city.", "storm", "s_myth",
      [("page", 0.0)]),
    A("storm", 0.9, "s_rock", [("thunder", 0.1), ("splash", 0.35)]),
    S("luna", "Poseidon gave it a spring. But the water was salty. Yuck!",
      "storm", "s_salt"),
    S("luna", "Athena gave it an olive tree. So the city chose her name: Athens!",
      "storm", "s_olive", [("sparkle", 0.3)]),
    A("storm", 0.9, "s_tree", [("sparkle", 0.1)]),
    S("whiskers", "Is there a myth about dinner?", "storm", "s_dinner", [("page", 0.85)]),
    A("storm", 1.0, "s_thump", [("thunder", 0.05), ("thump", 0.45)]),
    S("sophia", "Hoo! The storm blew me all the way from Athens!",
      "storm", "s_sophia", [("rain", 0.2)]),
    S("sophia", "I'm Sophia. My family waits for me on the Parthenon at the full moon.",
      "storm", "s_home"),
    S("whiskers", "Easy. I know everything.", "storm", "s_know"),
    S("luna", "Then where is Athens?", "storm", "s_where"),
    S("whiskers", "South. Mostly. Trust me.", "storm", "s_south"),
    A("storm", 1.0, "s_night", [("rain", 0.0)]),

    # -------------------------------------------------------------- airship
    A("airship", 0.8, "a_open", [("hum", 0.0)]),
    S("narrator", "Next morning, a silver airship came humming by, carrying honey to Athens.",
      "airship", "a_narr", [("hum", 0.3)]),
    S("sophia", "Quick! Grab the rope!", "airship", "a_rope"),
    A("airship", 1.4, "a_climb", [("whoosh", 0.15), ("whoosh", 0.55), ("hum", 0.8)]),
    S("whiskers", "Jars of honey? Best. Trip. Ever.", "airship", "a_honey",
      [("clink", 0.9)]),
    A("airship", 1.4, "a_sea", [("hum", 0.2), ("gulls", 0.6)]),
    S("sophia", "Grandma says Athena's owl was the wisest bird. Not because she knew everything, but because she asked.",
      "airship", "a_tale"),
    S("whiskers", "Asking is for kittens.", "airship", "a_kittens"),
    A("airship", 1.2, "a_land", [("hum", 0.1), ("gulls", 0.5)]),
    S("luna", "Look! The Acropolis!", "airship", "a_look"),
    A("airship", 0.9, "a_down", [("whoosh", 0.4)]),

    # ---------------------------------------------------------------- plaka
    S("narrator", "But first they had to cross the Plaka: a maze of twisty little streets.",
      "plaka", "p_narr", [("cicada", 0.0)]),
    S("sophia", "Should we ask somebody the way?", "plaka", "p_ask"),
    S("whiskers", "Ask? Never. Follow me.", "plaka", "p_never"),
    A("plaka", 2.6, "p_maze", [("bouzouki", 0.1), ("bouzouki", 0.55)]),
    S("luna", "We've passed this souvlaki stand three times!", "plaka", "p_three"),
    S("whiskers", "On purpose. I like the smell.", "plaka", "p_purpose"),
    A("plaka", 0.8, "p_sniff", [("sniff", 0.2)]),

    # --------------------------------------------------------------- yogurt
    S("narrator", "Then Whiskers smelled yogurt. Thick white yogurt, with golden honey.",
      "yogurt", "y_narr"),
    A("yogurt", 1.2, "y_dive", [("whoosh", 0.3), ("splat", 0.55)]),
    S("sophia", "Hoo hoo hoo! He's got a big white beard!", "yogurt", "y_beard", [("hoot", 0.9)]),
    S("whiskers", "I am a great Greek thinker. And I think... more honey.", "yogurt", "y_think"),
    A("yogurt", 1.0, "y_lick", [("lick", 0.2), ("lick", 0.5)]),
    S("luna", "Which way now?", "yogurt", "y_which"),
    S("whiskers", "Up. Obviously.", "yogurt", "y_up"),
    A("yogurt", 0.8, "y_go"),

    # -------------------------------------------------------------- theatre
    S("narrator", "Whiskers led them into an ancient stone theatre.",
      "theatre", "th_narr"),
    S("whiskers", "Hello!", "theatre", "th_hello"),
    A("theatre", 0.6, "th_echo1", [("echo_hello", 0.0)]),
    S("whiskers", "I know the way!", "theatre", "th_way"),
    A("theatre", 0.4, "th_wait"),
    S("socrates", "No, you don't.", "theatre", "th_dont"),
    A("theatre", 0.6, "th_echo2", [("echo_dont", 0.0)]),
    S("whiskers", "Hey! Echoes aren't supposed to argue!", "theatre", "th_argue"),
    A("theatre", 0.9, "th_reveal", [("meow", 0.3)]),
    S("socrates", "I'm not an echo. I'm Socrates. And you are lost.", "theatre", "th_lost"),
    S("whiskers", "Lost? Us? We're exploring.", "theatre", "th_explore"),
    A("theatre", 0.6, "th_end"),

    # ---------------------------------------------------------------- agora
    S("narrator", "The sun was setting. Soon the moon would rise.", "agora", "ag_narr",
      [("cicada", 0.0)]),
    S("sophia", "My family will be waiting. And I can't fly that high.", "agora", "ag_sad"),
    A("agora", 1.0, "ag_quiet"),
    S("whiskers", "Sophia... I don't know the way. I never did. I just wanted to look clever.",
      "agora", "ag_admit"),
    S("socrates", "The only thing I know is that I know nothing. So I ask.",
      "agora", "ag_nothing"),
    S("sophia", "Like owls! That's why we always say: hoo? Hoo?", "agora", "ag_hoo", [("hoot", 0.75)]),
    A("agora", 0.6, "ag_think"),
    S("whiskers", "Please, Socrates, how do we get to the top?", "agora", "ag_ask"),
    S("socrates", "A wise question! Follow the cats of Athens!", "agora", "ag_follow",
      [("meow", 0.95)]),
    A("agora", 1.4, "ag_cats", [("meow", 0.2), ("meow", 0.5)]),

    # ------------------------------------------------------------ acropolis
    S("narrator", "Up a secret cat path they climbed, through the olive trees.",
      "acropolis", "ac_narr", [("crickets", 0.0)]),
    A("acropolis", 1.0, "ac_maidens"),
    S("whiskers", "Those stone ladies have held up that roof for two thousand years. And I complain about carrying my bowl.",
      "acropolis", "ac_ladies"),
    A("acropolis", 1.4, "ac_top", [("chime", 0.2)]),
    S("sophia", "Grandma! I'm home!", "acropolis", "ac_home", [("flap", 0.6)]),
    A("acropolis", 1.2, "ac_fly", [("flap", 0.1), ("flap", 0.4), ("hoot", 0.8)]),
    S("yaya", "Sophia! Thank you, wise cats.", "acropolis", "ac_thanks"),
    S("whiskers", "Wise? Me? I didn't know a thing. I just asked.", "acropolis", "ac_asked"),
    S("yaya", "Little cat, that is how all wisdom begins.", "acropolis", "ac_begins", [("hoot", 0.9)]),
    A("acropolis", 1.8, "ac_dance", [("bouzouki", 0.05), ("hoot", 0.4), ("hoot", 0.7)]),

    # ----------------------------------------------------------------- home
    A("home", 1.2, "h_fly", [("hum", 0.1)]),
    S("narrator", "The honey airship carried them home.", "home", "h_narr"),
    A("home", 0.8, "h_sill", [("purr", 0.2)]),
    S("pip", "An olive tree! And honey! Where have you been?", "home", "h_pip"),
    S("whiskers", "Athens, Pip! Ask me anything. If I don't know, we'll ask together.",
      "home", "h_together"),
    A("home", 1.0, "h_owl", [("hoot", 0.3)]),
    S("narrator", "Because nobody knows everything. And the wisest words of all are: let's ask!",
      "home", "h_moral"),
    A("home", 1.7, "h_end", [("hoot", 0.4)]),
]
