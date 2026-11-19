# One Day, One Image — Thursday, 19 November 2026

[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-7c3aed)](https://make.fun/bounty/news-image-20261119)
[![competition](https://img.shields.io/badge/competition-news--image--20261119-blue)](https://make.fun/bounty/news-image-20261119)
[![entry](https://img.shields.io/badge/entry-entry.png-green)](https://make.fun/bounty/news-image-20261119)

A make.fun entry for the **news-image-20261119** bounty: sum up
19 November's world news in one image.

`main.py` (Python 3.13 standard library only) draws a 1024x1024
newspaper-style front page — masthead, the date in large type, and six
panels, each with a hand-drawn icon, a headline and one line of explanation —
and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`.

Everything is drawn by code: a from-scratch PNG encoder (`struct` + `zlib`),
a software rasterizer (rects, lines, circles, triangles) and a hand-drawn
5x7 bitmap font. No images, no network, no randomness — two runs produce
byte-identical output.

## The six stories

1. **Shenzhen** — Trump, Xi and Putin hold the first-ever US–China–Russia
   trilateral summit and sign a "peace declaration".
2. **The Hague** — The ICJ finds Myanmar guilty of genocide against the
   Rohingya, a first for the court.
3. **Crimea** — A third Ukrainian strike in a week halts rail on the Kerch
   Bridge.
4. **The Gulf** — Iran hits Kuwait and Bahrain as the fight over Hormuz
   spreads.
5. **Wall Street** — Anthropic raises a record $81.3bn in its IPO; shares
   start trading as ANT on the Nasdaq.
6. **New York** — A Van Gogh sells for a record $190.4m at Sotheby's.

Sources and verification notes are in `../news-brief.md` (kept outside the
repository, next to the build notes).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024, under 1 MiB).
