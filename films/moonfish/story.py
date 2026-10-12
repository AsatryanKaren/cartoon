"""Film 1: "Whiskers and the Moon Fish" -- the script.

The script is a flat list of entries. `Say` entries are spoken lines; their
length is fixed by the generated speech. `Act` entries are silent action
moments; they share whatever time is left so the film is exactly
FILM_SECONDS long, in proportion to their weights.

Any entry may carry an `id` so scenes can sync animation to it, and a list of
sound effects as (name, fraction-of-entry) pairs.
"""
from common import *  # noqa: F401,F403

TITLE = "Whiskers and the Moon Fish"
SCENES = ["title", "morning", "legend", "garden", "meadow", "pond", "realize", "home"]

# the playful music for the laugh, then back to the quiet pond theme
MUSIC_CUES = [("r_laugh", 0.0, "laugh"), ("r_end", 0.3, "realize")]

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.6, "t_open"),
    S("narrator", "Whiskers and the Moon Fish.", "title", "t_name"),
    A("title", 1.8, "t_hold"),

    # -------------------------------------------------------------- morning
    A("morning", 2.0, "m_sleep", [("purr", 0.1)]),
    S("narrator", "Every morning, Whiskers the orange tabby did exactly one thing. Nothing at all.", "morning"),
    A("morning", 1.5, "m_luna_in"),
    S("luna", "Whiskers! Wake up! The sun is already halfway up the sky!", "morning"),
    S("whiskers", "Five more minutes, Luna. Maybe five more hours.", "morning"),
    A("morning", 1.2, "m_bowl", [("clink", 0.45), ("clink", 0.62)]),
    S("whiskers", "Was that... my breakfast bowl?", "morning", "m_wake"),
    S("luna", "It was. And now that you're awake, I have news. Big news.", "morning"),
    A("morning", 0.8, "m_end"),

    # --------------------------------------------------------------- legend
    S("luna", "Old Tom from next door says there's a pond past the garden, beyond the meadow.", "legend", "l_tom"),
    S("luna", "And at night, a fish swims in it. A fish that glows like the moon itself.", "legend", "l_fish"),
    S("narrator", "The Moon Fish. A fish so bright, they say, it lights up the whole pond.", "legend", "l_narr"),
    A("legend", 1.5, "l_dream", [("whoosh", 0.1)]),
    S("whiskers", "A glowing fish? Is it... tasty?", "legend", "l_tasty"),
    S("luna", "Whiskers! It's a legend! Let's go and find it!", "legend"),
    S("whiskers", "Find it? That sounds like walking.", "legend"),
    S("luna", "There might be a snack at the end.", "legend"),
    A("legend", 0.8, "l_think"),
    S("whiskers", "Fine. Let's go.", "legend", "l_go", [("meow", 0.9)]),
    A("legend", 1.0, "l_out"),

    # --------------------------------------------------------------- garden
    S("narrator", "And so the two cats set off through the garden.", "garden", "g_narr"),
    A("garden", 2.0, "g_walk"),
    S("luna", "Look, Whiskers! A butterfly!", "garden", "g_look"),
    A("garden", 2.5, "g_chase", [("whoosh", 0.05)]),
    S("whiskers", "Come back here, you flappy little sandwich!", "garden", "g_shout"),
    A("garden", 2.0, "g_miss", [("whoosh", 0.3)]),
    S("luna", "You'll never catch it. It's much too fast for you.", "garden", "g_tease"),
    S("whiskers", "I let it win. On purpose.", "garden", "g_purpose"),
    A("garden", 1.0, "g_on"),
    S("narrator", "At the end of the garden stood the tall wooden fence.", "garden", "g_fence"),
    S("luna", "Up and over! Ready?", "garden", "g_ready"),
    A("garden", 1.8, "g_jump_l", [("whoosh", 0.2)]),
    S("whiskers", "Cats were made for sleeping, not for climbing.", "garden", "g_grumble"),
    A("garden", 2.6, "g_jump_w", [("whoosh", 0.15), ("meow", 0.55), ("whoosh", 0.7)]),
    S("whiskers", "Ta-da! Completely on purpose.", "garden", "g_tada"),
    A("garden", 0.8, "g_end"),

    # --------------------------------------------------------------- meadow
    S("narrator", "Beyond the fence lay a meadow of tall, whispering grass.", "meadow", "md_narr"),
    A("meadow", 2.0, "md_walk"),
    S("pip", "Halt! Who goes there?", "meadow", "md_halt"),
    A("meadow", 1.2, "md_look"),
    S("luna", "Down here, Whiskers. It's a mouse!", "meadow", "md_down"),
    S("pip", "Not just a mouse. I am Pip, the bravest mouse in the meadow!", "meadow", "md_pip"),
    S("whiskers", "Hello, Pip. Don't worry. We only eat fish today.", "meadow", "md_hello"),
    S("pip", "Fish? You don't mean... the Moon Fish?", "meadow", "md_fish"),
    S("luna", "You know about it?", "meadow"),
    S("pip", "Everybody knows! But nobody has ever caught it. I'll show you the way to the pond!", "meadow", "md_way"),
    A("meadow", 2.0, "md_walk2"),
    S("narrator", "And so, the three new friends walked on as the sun went down.", "meadow", "md_sun"),
    A("meadow", 2.5, "md_sunset"),

    # ----------------------------------------------------------------- pond
    A("pond", 2.0, "p_arrive", [("ribbit", 0.2), ("ribbit", 0.7)]),
    S("pip", "There it is. The pond.", "pond", "p_there"),
    S("luna", "Look! In the water! Something is glowing!", "pond", "p_glow"),
    S("whiskers", "The Moon Fish! It's real! And it's mine!", "pond", "p_mine"),
    A("pond", 1.5, "p_crouch"),
    S("narrator", "Whiskers wiggled. Whiskers waited. And then, Whiskers pounced!", "pond", "p_narr"),
    A("pond", 2.5, "p_pounce", [("whoosh", 0.05), ("splash", 0.38)]),

    # -------------------------------------------------------------- realize
    S("whiskers", "Blub! Where did it go? I had it! I definitely had it!", "realize", "r_blub"),
    A("realize", 1.8, "r_out", [("splash", 0.15)]),
    S("luna", "Whiskers... look up.", "realize", "r_lookup"),
    A("realize", 1.5, "r_up"),
    S("pip", "It's not a fish at all. It's the moon!", "realize", "r_moon"),
    S("narrator", "The Moon Fish was only the reflection of the moon, shining in the water.", "realize", "r_narr"),
    A("realize", 1.0, "r_down"),
    S("whiskers", "So I just tried to catch... the sky?", "realize", "r_sky"),
    A("realize", 2.8, "r_laugh", [("ribbit", 0.15), ("ribbit", 0.45), ("ribbit", 0.75)]),
    S("narrator", "And everyone laughed. Even the frogs.", "realize", "r_frogs", [("ribbit", 0.85)]),
    S("luna", "We didn't find a Moon Fish, Whiskers. But we found a new friend.", "realize", "r_friend"),
    S("pip", "And I found two!", "realize", "r_two"),
    S("whiskers", "Best adventure ever. Now can we go home and sleep?", "realize", "r_home"),
    A("realize", 1.2, "r_end"),

    # ----------------------------------------------------------------- home
    S("narrator", "So the three friends walked home under the silver moon.", "home", "h_narr"),
    A("home", 3.0, "h_walk"),
    A("home", 2.0, "h_sill", [("purr", 0.2)]),
    S("narrator", "That night, they curled up together on the windowsill, warm and dry and happy.", "home", "h_night"),
    S("whiskers", "Goodnight, moon. Sorry I jumped on you.", "home", "h_gn"),
    A("home", 2.0, "h_purr", [("purr", 0.1)]),
    S("narrator", "Because the best thing you find, is who you find along the way.", "home", "h_moral"),
    A("home", 4.5, "h_end"),
]
