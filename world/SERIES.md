# Whiskers & Luna's World: geography series

An educational cartoon where children learn geography with Whiskers, Luna, Pip and the narrator
(the same characters and voices as the travel films). Each episode is exactly 5:55.

- **Code:** `world/s<season>e<episode>_<slug>/` (for example `world/s1e01_our_planet/`), rendered with
  `python3 render.py --film world/s1e01_our_planet`
- **Shared series kit:** `world/kit.py` holds the globe, magic map, "Remember!" fact cards, quiz cards and
  the intro/outro, so every episode looks the same. Episodes import it; only change it for the whole series.
- **Videos:** `catcute/World/Season <n>/<NN> - <Topic>.mp4` (+ `.srt`), on GitHub and in `~/Desktop/catcute/`.
  In `story.py`: `PLACE = "World/Season 1"`, `TITLE = "01 - Our Planet"`.

## Episode format (every episode)

1. **Windowsill start:** Luna spins her old globe at home and Whiskers asks a lazy question.
2. **Magic map:** the globe glows and the friends fly into a big friendly map; arrows show where they go.
3. **Adventure:** they travel there and meet one local animal guide. Three easy facts are learned through
   the story, not lectured.
4. **Whiskers' mistake:** something funny he gets wrong ("on purpose"), which shows a fact.
5. **"Remember!":** the 3 facts appear as big, simple words on screen.
6. **Quiz:** the narrator asks 1–2 questions, pauses about 3 seconds for the child to answer, then reveals the answer.
7. **Home again** on the windowsill.

Facts must be correct and simple for ages 4–8. Use simple diagrams (arrows, labels) where they help.

## Season 1

- [x] 01 - Our Planet: the Earth is round, land and water, globe and map, north/south/east/west (guide: wise old turtle)
- [x] 02 - The Seven Continents: a flying tour, one famous animal or place each (guide: albatross)
- [x] 03 - The Five Oceans: the Pacific is the biggest, why the sea is salty, waves and tides (guide: whale)
- [x] 04 - Mountains and Volcanoes: how mountains grow, Everest the tallest, a volcano erupts (guide: snow leopard)
- [ ] 05 - Rivers and Lakes: from a raindrop to the sea, the Nile and the Amazon, the water cycle (guide: otter)
- [ ] 06 - Deserts: the hot Sahara, why it rarely rains, oases, the camel's secrets (guides: camel, fennec fox)
- [ ] 07 - Rainforests: the Amazon, layers from floor to treetops, so many animals (guides: toucan, sloth)
- [ ] 08 - The Frozen Poles: Arctic and Antarctica, penguins vs polar bears, ice, northern lights (guide: penguin)
- [ ] 09 - Weather and Seasons: summer and winter, the Earth's tilt, rain, wind, rainbows (guide: weather-vane rooster)
- [ ] 10 - Day and Night, Earth and Sun: the Earth spins, time zones, the Moon (Moon Fish callback!) (guide: owl)

## Season 2 (ideas for later)

Countries and flags, famous landmarks of the world, islands, caves, coral reefs, maps and compasses,
volcano islands (Iceland, Hawaii), the biggest cities, the night sky and stars.
