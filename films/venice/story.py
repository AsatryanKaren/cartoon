"""Film: "Whiskers and the Singing Glass" -- the two cats travel to Venice.

Whiskers rolls off the windowsill in his sleep and squashes Luna's little
silver bell flat -- and doesn't own up ("a big, heavy mouse did it").  A radio
show tells of Murano, where glass sings like a bell, so guilty Whiskers (who
never wants to go anywhere) insists they fly to Venice at once, in the basket
of a striped balloon.  In St Mark's Square a sugary carnival doughnut sets off
a pigeon stampede and Whiskers ends up in a canal (again!).  Bepi, a singing
egret gondolier, fishes him out and rows them under the Rialto Bridge to
Nonna Vetra's glass furnace on Murano, where Whiskers finally says sorry and
helps blow a new bell.  High water floods the square at sunset -- so the
gondola sails right across it to the balloon.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act
from films.venice.sounds import EXTRA_SFX  # noqa: F401

TITLE = "Whiskers and the Singing Glass"
PLACE = "Venice"            # folder in the catcute library
SCENES = ["title", "bell", "balloon", "square", "canal", "murano", "flood", "home"]

CAST = {
    **CAST,
    "bepi": Voice("im_nicola", 0.95, -3, ["Luca"], 176, "it+m3", 40, 160),
    "vetra": Voice("if_sara", 0.9, -2, ["Alice"], 166, "it+f4", 48, 150),
    "radio": Voice("bm_lewis", 1.0, 0, ["Daniel"], 180, "en-gb+m2", 45, 165),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "bepi": (175, 235, 255),
    "vetra": (255, 225, 150),
    "radio": (210, 240, 190),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    # a lilting barcarolle in 6/8 feel (slow bpm, lots of melody) for the canals
    "v_title": dict(bpm=70, prog=[(57, MIN), (62, MIN), (64, MAJ), (57, MIN)], drums=False, mel=0.55, oct=76, vol=0.8),
    "v_morning": dict(bpm=100, prog=[(67, MAJ), (64, MIN), (60, MAJ), (62, MAJ)], drums=True, mel=0.6, oct=79, vol=0.75),
    "v_guilty": dict(bpm=66, prog=[(62, MIN), (58, MAJ), (57, MAJ), (62, MIN)], drums=False, mel=0.3, oct=74, vol=0.6),
    "v_radio": dict(bpm=76, prog=[(65, MAJ), (62, MIN), (70, MAJ), (72, MAJ)], drums=False, mel=0.5, oct=81, vol=0.65),
    "v_sky": dict(bpm=84, prog=[(65, MAJ), (69, MIN), (70, MAJ), (72, MAJ)], drums=False, mel=0.55, oct=84, vol=0.75),
    "v_square": dict(bpm=116, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.7, oct=76, vol=0.8),
    "v_chase": dict(bpm=156, prog=[(62, MIN), (58, MAJ), (60, MAJ), (57, MAJ)], drums=True, mel=0.85, oct=74, vol=0.85),
    "v_barca": dict(bpm=72, prog=[(62, MIN), (57, MAJ), (62, MIN), (55, MIN), (57, MAJ), (62, MIN)], drums=False,
                    mel=0.7, oct=74, vol=0.75),
    "v_furnace": dict(bpm=80, prog=[(57, MIN), (53, MAJ), (55, MAJ), (57, MIN)], drums=False, mel=0.35, oct=74, vol=0.65),
    "v_sorry": dict(bpm=62, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.3, oct=77, vol=0.55),
    "v_glass": dict(bpm=96, prog=[(65, MAJ), (70, MAJ), (72, MAJ), (65, MAJ)], drums=False, mel=0.7, oct=86, vol=0.7),
    "v_hurry": dict(bpm=138, prog=[(57, MIN), (53, MAJ), (55, MAJ), (52, MAJ)], drums=True, mel=0.75, oct=76, vol=0.85),
    "v_triumph": dict(bpm=110, prog=[(62, MAJ), (67, MAJ), (69, MAJ), (62, MAJ)], drums=True, mel=0.7, oct=78, vol=0.85),
    "v_night": dict(bpm=62, prog=[(65, MAJ), (58, MAJ), (65, MAJ), (60, MAJ)], drums=False, mel=0.3, oct=77, vol=0.6),
}
MUSIC = {"title": "v_title", "bell": "v_morning", "balloon": "v_sky", "square": "v_square", "canal": "v_barca",
         "murano": "v_furnace", "flood": "v_hurry", "home": "v_night"}
MUSIC_CUES = [("b_pop", 0.5, "v_guilty"), ("b_radio", 0.0, "v_radio"), ("b_window", 0.0, "v_morning"),
              ("q_shoo", 0.6, "v_chase"), ("c_hook", 0.0, "v_barca"),
              ("m_pause", 0.0, "v_sorry"), ("m_help", 0.5, "v_glass"),
              ("f_gondola", 0.5, "v_triumph"), ("f_lift", 0.3, "v_sky"), ("h_sill", 0.0, "v_morning")]

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.1, "t_open", [("chime", 0.3)]),
    S("narrator", "Whiskers and the Singing Glass.", "title", "t_name"),
    A("title", 0.9, "t_hold", [("gull", 0.3)]),

    # ----------------------------------------------------------------- bell
    A("bell", 1.2, "b_play", [("jingle", 0.15), ("jingle", 0.55)]),
    S("narrator", "Luna loved her little golden bell.", "bell", "b_narr",
      [("jingle", 0.5)]),
    A("bell", 1.8, "b_pop", [("jingle", 0.08), ("ting", 0.2), ("whoosh", 0.62), ("crunch", 0.78)]),
    S("whiskers", "Oof. There's something under my bottom.", "bell", "b_oof"),
    A("bell", 0.9, "b_look"),
    S("luna", "Whiskers! My bell fell off! Have you seen it?", "bell", "b_seen"),
    S("whiskers", "Your bell? Um... it was like that already.", "bell", "b_like"),
    S("luna", "It's squashed flat. It doesn't ring anymore.", "bell", "b_squash", [("clunk", 0.75)]),
    S("whiskers", "Probably a mouse did it. A big, heavy mouse.", "bell", "b_mouse"),
    S("pip", "Hey! I heard that!", "bell", "b_pip"),
    A("bell", 0.7, "b_sad", [("click", 0.5)]),
    S("radio", "Venice! Where the glassmakers of Murano make glass that sings like a bell.",
      "bell", "b_radio"),
    S("whiskers", "Then we go to Venice. Right now.", "bell", "b_go"),
    S("luna", "You? Whiskers, you never want to go anywhere!", "bell", "b_you"),
    S("whiskers", "I... suddenly love travelling.", "bell", "b_love"),
    A("bell", 0.8, "b_window", [("burner", 0.3)]),
    S("pip", "Look! A balloon to Venice! Bring me a present!", "bell", "b_ball"),
    A("bell", 1.2, "b_run", [("whoosh", 0.2), ("whoosh", 0.45)]),

    # -------------------------------------------------------------- balloon
    A("balloon", 1.4, "v_lift", [("burner", 0.1), ("burner", 0.6)]),
    S("narrator", "So two cats hid in a striped balloon, and floated over the mountains.",
      "balloon", "v_narr"),
    A("balloon", 1.4, "v_alps", [("wind", 0.0), ("burner", 0.6)]),
    S("whiskers", "Don't look down. Don't look down.", "balloon", "v_down"),
    S("luna", "Whiskers, look down! There it is!", "balloon", "v_look"),
    A("balloon", 1.6, "v_venice", [("gull", 0.3), ("gull", 0.7)]),
    S("whiskers", "Wait. The whole city is sitting in the water?", "balloon", "v_water"),
    S("narrator", "Venice has canals for streets, and boats for buses.", "balloon", "v_canals"),
    A("balloon", 1.4, "v_land", [("burner", 0.2), ("thump", 0.92)]),

    # --------------------------------------------------------------- square
    A("square", 1.0, "q_arrive", [("coo", 0.3), ("flutter", 0.5)]),
    S("narrator", "They landed in Saint Mark's Square, by the golden church and the tall bell tower.",
      "square", "q_narr", [("coo", 0.8)]),
    S("narrator", "Lots and lots of pigeons.", "square", "q_lots", [("coo", 0.2), ("coo", 0.6)]),
    S("luna", "We fly home when the big bell rings at sunset!",
      "square", "q_late"),
    A("square", 0.8, "q_smell"),
    S("whiskers", "Sniff, sniff. Is that... a doughnut?", "square", "q_sniff"),
    S("narrator", "A sugary doughnut rolled to his paws. But the pigeons saw it too.",
      "square", "q_roll", [("coo", 0.7)]),
    S("whiskers", "Shoo! This doughnut is for cats!", "square", "q_shoo", [("flutter", 0.85)]),
    A("square", 1.8, "q_swarm", [("flutter", 0.0), ("coo", 0.2), ("flutter", 0.4), ("coo", 0.6), ("flutter", 0.8)]),
    A("square", 1.0, "q_run", [("whoosh", 0.4)]),

    # ---------------------------------------------------------------- canal
    A("canal", 1.2, "c_leap", [("whoosh", 0.1), ("splash", 0.55)]),
    S("whiskers", "Blub! Not the water again!", "canal", "c_blub", [("bubbles", 0.0)]),
    A("canal", 0.9, "c_hook", [("splash", 0.4)]),
    S("bepi", "Ha! I have caught a fish with whiskers!", "canal", "c_fish"),
    S("whiskers", "I meant to do that. I needed a bath.", "canal", "c_bath"),
    S("bepi", "I am Bepi, the singing gondolier. Hop in!", "canal", "c_bepi"),
    S("luna", "We're looking for glass that sings!", "canal", "c_glass"),
    S("bepi", "Then to Murano, to Nonna Vetra! Andiamo!", "canal", "c_andiamo"),
    A("canal", 1.2, "g_row", [("song", 0.0), ("lap", 0.5)]),
    S("bepi", "La la laaa! The Rialto Bridge!", "canal", "g_rialto"),
    A("canal", 1.4, "g_bridge", [("song", 0.1), ("lap", 0.6)]),
    S("luna", "Whiskers, you're very quiet.", "canal", "g_quiet"),
    S("whiskers", "Just thinking. About... bells.", "canal", "g_think"),
    S("bepi", "Sing with me!", "canal", "g_sing"),
    S("whiskers", "Meeeow la laaa!", "canal", "g_meow"),
    A("canal", 1.2, "g_lagoon", [("gull", 0.4), ("lap", 0.7)]),

    # --------------------------------------------------------------- murano
    A("murano", 1.0, "m_arrive", [("roar", 0.0)]),
    S("narrator", "Murano: the island of glassmakers.",
      "murano", "m_narr", [("roar", 0.5)]),
    S("vetra", "Welcome! What can Nonna Vetra make for you?", "murano", "m_welcome"),
    S("luna", "A new bell, please. Mine got squashed.", "murano", "m_please"),
    S("vetra", "Squashed? How?", "murano", "m_what"),
    A("murano", 1.0, "m_pause"),
    S("whiskers", "It was me. I rolled on it in my sleep.", "murano", "m_me"),
    S("whiskers", "Not on purpose. I'm sorry I didn't tell you, Luna.",
      "murano", "m_sorry"),
    S("luna", "Oh, Whiskers. So that's why you came all this way.", "murano", "m_oh"),
    S("luna", "Thank you for telling me the truth.", "murano", "m_truth", [("purr", 0.3)]),
    S("vetra", "A brave sorry! Now, help me blow the glass.", "murano", "m_help"),
    A("murano", 1.4, "m_blow", [("blow", 0.05), ("blow", 0.45)]),
    S("vetra", "Gently! It's a bell, not a balloon!", "murano", "m_gently"),
    A("murano", 1.4, "m_shape", [("roar", 0.1), ("chime", 0.85)]),
    S("vetra", "A bell made with a friend sings the sweetest.", "murano", "m_there"),
    A("murano", 0.8, "m_ring", [("glassbell", 0.2), ("glassbell", 0.6)]),
    S("luna", "Listen! It sings!", "murano", "m_sings", [("glassbell", 0.9)]),
    S("bepi", "The sunset bell! Quick, to the gondola!", "murano", "m_quick",
      [("bong", 0.0), ("bong", 0.6)]),

    # ---------------------------------------------------------------- flood
    A("flood", 1.2, "f_row", [("bong", 0.1), ("lap", 0.3), ("bong", 0.6)]),
    S("narrator", "But the tide had come in. Acqua alta! The square was flooded.",
      "flood", "f_narr", [("lap", 0.5)]),
    A("flood", 0.8, "f_flood", [("bong", 0.2)]),
    S("whiskers", "The square is a swimming pool!", "flood", "f_never"),
    S("bepi", "In Venice, where there is water, there is a gondola!", "flood", "f_gondola"),
    A("flood", 1.8, "f_across", [("song", 0.0), ("splash", 0.3), ("lap", 0.5), ("bong", 0.7)]),
    S("luna", "Grazie, Bepi!", "flood", "f_grazie"),
    S("bepi", "Ciao, little cats!", "flood", "f_ciao", [("burner", 0.8)]),
    A("flood", 1.4, "f_lift", [("burner", 0.2), ("glassbell", 0.6)]),

    # ----------------------------------------------------------------- home
    A("home", 1.4, "h_fly", [("wind", 0.1)]),
    S("narrator", "The balloon carried them home through the night.",
      "home", "h_narr"),
    A("home", 1.0, "h_sill", [("chime", 0.2)]),
    S("pip", "Did you find the singing glass?", "home", "h_pip"),
    S("luna", "Listen.", "home", "h_listen"),
    A("home", 0.9, "h_ring", [("glassbell", 0.1), ("glassbell", 0.45), ("chime", 0.6)]),
    S("whiskers", "And for you, Pip: a glass mouse.", "home", "h_gift"),
    S("whiskers", "Now, a nap. Far away from all bells.", "home", "h_nap", [("purr", 0.6)]),
    S("narrator", "Because saying sorry is the first step to fixing what is broken. And friends help with the rest.",
      "home", "h_moral"),
    A("home", 3.6, "h_end", [("glassbell", 0.1), ("purr", 0.4)]),
]
