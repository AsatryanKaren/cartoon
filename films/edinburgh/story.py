"""Film: "Whiskers and the Loch Ness Secret" -- Whiskers and Luna go to Edinburgh and the Highlands.

One spring morning Whiskers eats the very last shortbread in a tartan tin --
and inside the empty lid Luna finds a contest: "Photograph the Loch Ness
Monster and win shortbread for life!" Pip lends them his little camera, and
when a skein of wild geese honks past the window, flying north to Scotland,
the cats hitch a ride on their backs (Whiskers' goose sags a little). They come
down on Arthur's Seat in the thick sea fog called the haar; when it lifts,
there is Edinburgh Castle on its great rock. On the Royal Mile, past a badger
piper in a kilt, Dougal the Skye terrier pops out of a narrow close and becomes
their guide. Whiskers eats a whole slab of Scottish tablet and zooms up the
street on a sugar rush. Up at the castle, which sits on an old volcano, Dougal
promises it is perfectly quiet -- and the One O'Clock Gun goes BOOM. Whiskers
shoots into the sky and lands on the cannon: "on purpose, for the view." At
Greyfriars, Dougal shows them the statue of Bobby, the little dog who stayed
by his master for fourteen years, and tells them Nessie only shows herself to
those who wait. The geese take them north over purple heather, past red deer
and a castle on a loch, to Hamish, a Highland cow who can't see through his
fringe, who carries them -- slowly, wobbling -- to Loch Ness. Whiskers can't
wait and falls asleep; Luna waits all night, like Bobby. In the moonlight a
gentle, shy Nessie rises. She is frightened of the camera: a photo would bring
boats and nets and she would never have peace again. Whiskers thinks of a
mountain of shortbread... and puts the camera away. "A friend is better than
shortbread." Nessie gives them a moonlit ride past the old castle ruin, and the
geese fly them home. On the windowsill Pip sees their only photo: two cats and
"a funny rock" behind them. Moral: a loyal friend keeps your secret safe --
even for all the shortbread in Scotland.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.edinburgh import sounds

TITLE = "Whiskers and the Loch Ness Secret"
PLACE = "Edinburgh"         # folder in the catcute library
SCENES = ["title", "tin", "geese", "mile", "castle", "bobby", "highlands", "loch", "nessie", "home"]

CAST = {
    **CAST,
    # Dougal: a scruffy, perky little Skye terrier in a tartan bonnet, Edinburgh's self-appointed guide
    "dougal": Voice("bm_lewis", 1.08, 2, ["Daniel"], 184, "en-gb+m4", 56, 168),
    # Hamish: a big, slow, kind Highland cow; his ginger fringe hangs right over his eyes
    "hamish": Voice("am_onyx", 0.88, -2, ["Ralph"], 150, "en-us+m1", 24, 138),
    # Nessie: the shy, gentle creature of Loch Ness, soft-spoken
    "nessie": Voice("bf_alice", 0.9, -1, ["Kate"], 166, "en-gb+f2", 46, 150),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "dougal": (240, 220, 160),
    "hamish": (255, 176, 120),
    "nessie": (160, 240, 210),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
# Scottish flavour: mixolydian I - bVII swings (A - G, D - C), minor laments, jig tempos.
MOODS = {
    "e_title":  dict(bpm=72, prog=[(57, MAJ), (55, MAJ), (57, MAJ), (62, MAJ)], drums=False, mel=0.5, oct=81, vol=0.75),
    "e_tin":    dict(bpm=96, prog=[(62, MAJ), (60, MAJ), (62, MAJ), (67, MAJ)], drums=False, mel=0.55, oct=79, vol=0.7),
    "e_lid":    dict(bpm=112, prog=[(62, MAJ), (67, MAJ), (69, MAJ), (62, MAJ)], drums=True, mel=0.65, oct=79, vol=0.75),
    "e_fly":    dict(bpm=100, prog=[(64, MAJ), (62, MAJ), (64, MAJ), (69, MAJ)], drums=True, mel=0.6, oct=76, vol=0.75),
    "e_haar":   dict(bpm=62, prog=[(57, MIN), (55, MAJ), (53, MAJ), (55, MAJ)], drums=False, mel=0.3, oct=76, vol=0.6),
    "e_reveal": dict(bpm=70, prog=[(57, MAJ), (62, MAJ), (55, MAJ), (57, MAJ)], drums=False, mel=0.5, oct=81, vol=0.8),
    # reel: a quick fiddle-ish bounce
    "e_reel":   dict(bpm=138, prog=[(57, MAJ), (55, MAJ), (57, MAJ), (64, MAJ)], drums=True, mel=0.85, oct=81, vol=0.8),
    "e_zoom":   dict(bpm=160, prog=[(62, MAJ), (60, MAJ), (62, MAJ), (69, MAJ)], drums=True, mel=0.9, oct=81, vol=0.82),
    "e_castle": dict(bpm=88, prog=[(57, MAJ), (62, MAJ), (64, MAJ), (57, MAJ)], drums=True, mel=0.55, oct=76, vol=0.72),
    "e_boom":   dict(bpm=120, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.7, oct=72, vol=0.8),
    # lament: slow minor air for Bobby's story
    "e_bobby":  dict(bpm=60, prog=[(57, MIN), (53, MAJ), (55, MAJ), (57, MIN)], drums=False, mel=0.3, oct=76, vol=0.6),
    "e_heather": dict(bpm=84, prog=[(62, MAJ), (60, MAJ), (57, MIN), (62, MAJ)], drums=False, mel=0.5, oct=79, vol=0.75),
    "e_coo":    dict(bpm=96, prog=[(55, MAJ), (53, MAJ), (55, MAJ), (60, MAJ)], drums=True, mel=0.55, oct=74, vol=0.72),
    "e_loch":   dict(bpm=58, prog=[(62, MIN), (60, MAJ), (58, MAJ), (57, MAJ)], drums=False, mel=0.25, oct=74, vol=0.55),
    "e_night":  dict(bpm=54, prog=[(57, MIN), (55, MAJ), (53, MAJ), (52, MIN)], drums=False, mel=0.2, oct=76, vol=0.5),
    "e_nessie": dict(bpm=60, prog=[(62, MAJ), (59, MIN), (55, MAJ), (57, MAJ)], drums=False, mel=0.45, oct=81, vol=0.75),
    "e_choice": dict(bpm=56, prog=[(57, MIN), (53, MAJ), (60, MAJ), (55, MAJ)], drums=False, mel=0.2, oct=74, vol=0.5),
    "e_ride":   dict(bpm=76, prog=[(62, MAJ), (67, MAJ), (64, MIN), (69, MAJ)], drums=False, mel=0.6, oct=81, vol=0.8),
    "e_home":   dict(bpm=66, prog=[(62, MAJ), (60, MAJ), (55, MAJ), (57, MAJ)], drums=False, mel=0.4, oct=79, vol=0.7),
}
MUSIC = {"title": "e_title", "tin": "e_tin", "geese": "e_fly", "mile": "e_reel", "castle": "e_castle",
         "bobby": "e_bobby", "highlands": "e_heather", "loch": "e_loch", "nessie": "e_choice", "home": "e_home"}
MUSIC_CUES = [("i_lid", 0.0, "e_lid"),
              ("g_haar", 0.0, "e_haar"), ("g_reveal", 0.0, "e_reveal"),
              ("m_zoom", 0.0, "e_zoom"), ("m_run", 0.5, "e_reel"),
              ("c_gun", 0.0, "e_boom"), ("c_end", 0.0, "e_castle"),
              ("h_bump", 0.0, "e_coo"),
              ("l_wait2", 0.0, "e_night"), ("l_rise", 0.0, "e_nessie"),
              ("n_yes", 0.0, "e_nessie"), ("n_ride", 0.0, "e_ride")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.0, "t_open", [("pipes", 0.0)]),
    S("narrator", "Whiskers and the Loch Ness Secret.", "title", "t_name"),
    A("title", 0.9, "t_hold"),

    # ------------------------------------------------------------------ tin
    A("tin", 0.8, "i_open", [("crunch", 0.3), ("crunch", 0.7)]),
    S("narrator", "One spring morning, Whiskers ate the very last shortbread in the tin.",
      "tin", "i_narr", [("crunch", 0.2)]),
    A("tin", 0.6, "i_empty", [("tinclang", 0.3)]),
    S("whiskers", "Gone. All gone. Life is over.", "tin", "i_gone"),
    S("luna", "Wait! There's writing inside the lid!", "tin", "i_lid", [("jingle", 0.0)]),
    S("luna", "Photograph the Loch Ness Monster, and win shortbread for life!", "tin", "i_read"),
    S("whiskers", "Shortbread. For. Life.", "tin", "i_life"),
    S("pip", "Loch Ness is in Scotland. Far away, in the north.", "tin", "i_north"),
    A("tin", 0.9, "i_geese", [("geese", 0.1)]),
    S("luna", "The wild geese are flying north! Pip, can we borrow your camera?", "tin", "i_camera"),
    S("pip", "Take good care of it. And of each other!", "tin", "i_care", [("shutter", 0.9)]),
    A("tin", 0.7, "i_end", [("geese", 0.2)]),

    # ---------------------------------------------------------------- geese
    A("geese", 1.2, "g_fly", [("wings", 0.0), ("geese", 0.5)]),
    S("narrator", "So the cats hitched a ride with the wild geese, all the way to Scotland.",
      "geese", "g_narr", [("wings", 0.2)]),
    S("whiskers", "Could we fly a little lower? Or a little slower? Or not at all?", "geese", "g_low"),
    A("geese", 0.9, "g_dip", [("honk", 0.2), ("whoosh", 0.4)]),
    S("narrator", "At dawn, a thick sea fog called the haar rolled over Edinburgh.", "geese", "g_haar"),
    A("geese", 1.0, "g_land", [("wings", 0.0), ("thud", 0.75)]),
    A("geese", 1.4, "g_reveal", [("pipes", 0.3)]),
    S("luna", "Look! A castle, on top of a giant rock!", "geese", "g_wow"),
    A("geese", 0.5, "g_end"),

    # ----------------------------------------------------------------- mile
    A("mile", 1.0, "m_open", [("pipes", 0.0)]),
    S("dougal", "Och, hello! Ye look lost. I'm Dougal. Welcome to the Royal Mile!", "mile", "m_hello",
      [("yip", 0.0)]),
    S("luna", "We're looking for the Loch Ness Monster!", "mile", "m_look"),
    S("dougal", "Nessie? Everybody looks. Nobody finds her. She's awfully shy.", "mile", "m_shy"),
    S("whiskers", "Shy is fine. I just need one photo. And a snack.", "mile", "m_snack"),
    S("dougal", "Then try some tablet. Pure Scottish sugar!", "mile", "m_tablet"),
    A("mile", 0.9, "m_eat", [("crunch", 0.2), ("crunch", 0.45), ("gulp", 0.75)]),
    A("mile", 1.5, "m_zoom", [("zip", 0.05), ("zip", 0.35), ("zip", 0.65), ("boing", 0.92)]),
    S("whiskers", "I'm fine! I'm perfectly calm! Race you to the castle!", "mile", "m_calm"),
    A("mile", 0.8, "m_run", [("zip", 0.1)]),

    # --------------------------------------------------------------- castle
    A("castle", 1.0, "c_open", [("pipes", 0.1)]),
    S("dougal", "Edinburgh Castle! It sits on an old volcano.", "castle", "c_volcano"),
    S("whiskers", "A volcano? Does it ever go boom?", "castle", "c_boom"),
    S("dougal", "No, no. It's perfectly quiet up here.", "castle", "c_quiet"),
    A("castle", 1.6, "c_gun", [("gun", 0.12), ("yowl", 0.16), ("boing", 0.86)]),
    S("dougal", "Except for the One O'Clock Gun. It fires every single day.", "castle", "c_daily"),
    S("whiskers", "I jumped on purpose. For a better view.", "castle", "c_purpose"),
    A("castle", 0.7, "c_end", [("yip", 0.3)]),

    # ---------------------------------------------------------------- bobby
    A("bobby", 1.0, "b_open", [("bell", 0.2)]),
    S("dougal", "This is Greyfriars Bobby. A wee dog, just like me.", "bobby", "b_bobby"),
    S("dougal", "When his master died, Bobby stayed by his side for fourteen years.", "bobby", "b_story"),
    S("luna", "Fourteen years. That's what a true friend does.", "bobby", "b_friend"),
    S("whiskers", "I can't even wait fourteen minutes for lunch.", "bobby", "b_lunch"),
    S("dougal", "Then learn! Nessie only shows herself to those who wait.", "bobby", "b_wait",
      [("sparkle", 0.5)]),
    A("bobby", 1.0, "b_go", [("geese", 0.2), ("wings", 0.5)]),

    # ------------------------------------------------------------ highlands
    A("highlands", 1.3, "h_fly", [("wings", 0.0), ("geese", 0.3)]),
    S("narrator", "In the Highlands, the hills were purple with heather, and misty, and very big.",
      "highlands", "h_narr", [("stag", 0.85)]),
    A("highlands", 0.9, "h_bump", [("clonk", 0.55), ("moo", 0.75)]),
    S("hamish", "Who's there? Sorry. I can't see a thing through my fringe.", "highlands", "h_fringe"),
    S("luna", "Are you Hamish? We're going to Loch Ness!", "highlands", "h_hamish"),
    S("hamish", "Hop on, wee ones. It's a slow ride, but a sure one.", "highlands", "h_hop"),
    A("highlands", 1.4, "h_ride", [("clomp", 0.0), ("clonk", 0.42), ("clomp", 0.5)]),
    S("whiskers", "Hamish, left! No, your other left!", "highlands", "h_left", [("clonk", 0.95)]),
    A("highlands", 0.6, "h_end", [("moo", 0.3)]),

    # ----------------------------------------------------------------- loch
    A("loch", 1.2, "l_open", [("lap", 0.0)]),
    S("narrator", "At last they reached Loch Ness. Deep, and dark, and very still.", "loch", "l_narr",
      [("lap", 0.3)]),
    S("whiskers", "Right, monster. Come out. Smile for the camera.", "loch", "l_smile"),
    A("loch", 1.2, "l_wait1", [("lap", 0.2)]),
    S("whiskers", "This is taking forever. I'm having a little nap.", "loch", "l_nap"),
    A("loch", 1.2, "l_wait2", [("owl", 0.3), ("lap", 0.6)]),
    S("luna", "Bobby waited fourteen years. I can wait one night.", "loch", "l_luna"),
    A("loch", 2.0, "l_rise", [("bubbles", 0.05), ("bubbles", 0.3), ("rise", 0.5)]),
    S("nessie", "Hello? Are you the ones who waited for me?", "loch", "l_hello"),
    S("luna", "Whiskers! Wake up! It's her!", "loch", "l_wake", [("jingle", 0.1)]),
    A("loch", 0.8, "l_grab", [("shutter", 0.2)]),

    # --------------------------------------------------------------- nessie
    S("nessie", "Oh! A camera! Please don't. If people see me, they'll come with boats and nets.",
      "nessie", "n_please"),
    S("nessie", "I would never have peace again.", "nessie", "n_peace"),
    A("nessie", 1.4, "n_think", [("sparkle", 0.15)]),
    S("whiskers", "Shortbread for life...", "nessie", "n_life"),
    A("nessie", 0.8, "n_pause"),
    S("whiskers", "No. A friend is better than shortbread. Your secret is safe with us.", "nessie", "n_safe"),
    S("nessie", "You would do that for me? Then climb aboard!", "nessie", "n_yes", [("splash", 0.9)]),
    A("nessie", 2.0, "n_ride", [("lap", 0.0), ("lap", 0.5)]),
    S("luna", "We're riding the Loch Ness Monster!", "nessie", "n_riding"),
    S("whiskers", "And nobody will ever know.", "nessie", "n_know", [("purr", 0.6)]),
    A("nessie", 1.4, "n_end", [("geese", 0.5)]),

    # ----------------------------------------------------------------- home
    A("home", 1.0, "o_open", [("wings", 0.0), ("thud", 0.6), ("thud", 0.75)]),
    S("pip", "You're home! Did you find the Loch Ness Monster?", "home", "o_pip"),
    S("whiskers", "Monster? What monster? There's no monster.", "home", "o_none"),
    S("luna", "We only took one picture.", "home", "o_photo", [("shutter", 0.0)]),
    A("home", 0.8, "o_look"),
    S("pip", "That's just a funny rock behind you.", "home", "o_rock"),
    S("whiskers", "Exactly. Just a rock.", "home", "o_just"),
    A("home", 0.7, "o_wink", [("purr", 0.2)]),
    S("narrator", "Because a loyal friend keeps your secret safe. Even for all the shortbread in Scotland.",
      "home", "o_moral"),
    A("home", 2.4, "o_end", [("pipes", 0.25)]),
]
