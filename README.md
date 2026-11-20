# One Day, One Image — Thursday, 19 November 2026 (v2)

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Permana61/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Permana61/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

A make.fun entry for the **news-image-20261119** bounty: sum up
19 November's world news in one image. This is v2 — a maximised rebuild
of the v1 entry (6 stories, ranked #10,019 at 96.2% provisional): **40
verified stories from 7 continents** (Asia 11, Europe 8, North America 6,
Africa 5, South America 4, Oceania 4, Antarctica 2).

`main.py` (Python 3.13 standard library only) draws a 1024x1024
newspaper-style front page — masthead, the date in large type, a dotted
world map, a "40 STORIES • 7 CONTINENTS" stat strip, and seven
colour-coded continent sections, each story with a number, a headline, a
one-line summary and a SOURCE tag — and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png`.

Everything is drawn by code: a from-scratch PNG encoder (`struct` +
`zlib`), a software rasterizer (rects, lines, circles) and a hand-drawn
5x7 bitmap font. No images, no network, no randomness — two runs produce
byte-identical output.

## The forty stories

**Asia (11):** Trump, Xi and Putin sign a peace declaration in Shenzhen;
Iran hits Kuwait and Bahrain; a Houthi missile hits Riyadh's PIF Tower;
COP31 drops its fossil-fuel pledge; Cyclone Akvan nears India; Pakistan
raids kill 22 militants; Bangladesh lockdown and arson; Taiwan stocks
crash 4.4%; Mongolia's parliament ousts the president; Indonesia passes
an asset-seizure law; Delhi smog rebounds to AQI 282.

**Europe (8):** Kerch Bridge hit a third time; the World Court finds
Myanmar guilty of genocide; allies meet in Berlin over Ukraine;
Montenegro closes two more EU chapters; the Dutch watchdog warns against
smart glasses; a storm floods Bosnia and Montenegro; GTA 6 launches with
17m copies sold; Barcelona thrash Servette 6-0.

**North America (6):** Anthropic's record $81.3bn IPO; a Van Gogh sells
for $190.4m; the Senate passes its energy bill; Trump fires his cyber
chief; a Haiti raid kills 34; the FAA prepares to reveal the ground-stop
cause.

**Africa (5):** Somalia expels the UAE ambassador; Zimbabwe clears its
250,000th landmine; a Senegal boat sinks with dozens lost; South Africa
holds its rate at 7.25%; marathon champion Jepchirchir is banned 3 years.

**South America (4):** Brazil sells $1bn to defend the real; Lula
protects Raoni's ancestral land; Colombia tax protests; Argentina's
health curbs are restored by the Supreme Court.

**Oceania (4):** Fiji declares a drought disaster; Tonga declares a
27-day drought emergency; 19 whales die in a New Zealand stranding; the
Darwin Port buyback stalls.

**Antarctica (2):** Australia redesigns its Antarctic science
programme; the US Air Guard sends 5 LC-130s for Operation Deep Freeze.

Sources and verification notes are in `../news-brief.md` (kept outside
the repository, next to the build notes).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024, under 1 MiB).
