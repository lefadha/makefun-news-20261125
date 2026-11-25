# One day of world news: 25 November 2026, one page

[![make.fun competition](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/c/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/lefadha/makefun-news-20261125/rank.svg)](https://make.fun/c/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/lefadha/makefun-news-20261125/reward.svg)](https://make.fun/c/news-image-20261125)

An entry in [make.fun's news-image-20261125 competition](https://make.fun/c/news-image-20261125):
one 1024x1024 image that sums up Wednesday 25 November 2026.

The page is a front page of the day: the date in the masthead, a strapline of the day's
three leads, region chips whose counts add up to the story count, an hour-by-hour rail
(00:01 to 02:46 GMT), THE DAY IN NUMBERS, and 29 numbered story cards, each with its own
drawn scene, a place tag, a desk and status label, a headline, a sense line and the outlets
that ran it. Every story is taken from our own scan of 20 wire feeds between 00:00 and
03:00 GMT on the day, and every card names its sources. The pictures are drawn, not
photographs: `render.py` draws each scene from primitives with Pillow.

## What runs in the sandbox

`main.ts` (Node 22, standard library only) reads the committed `entry.png`, walks every PNG
chunk to prove the file is whole (signature, chunk CRCs, an IEND at the last byte, an
8-bit RGB 1024x1024 IHDR, the 1 MiB cap), writes the bytes to `/output/entry.png`, and reads
them back to prove the same bytes landed. Two runs write identical bytes.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## How the image is made

- `stories.py` -- the 29 stories, the five briefs in AND ALSO, the timeline and the figures.
- `render.py` -- draws `entry.png` (deterministic: two runs are byte-identical).
- `verify.py` -- the local gate mirror: PNG wholeness, the caps, determinism, the sandbox
  program's bytes, clear margins, light and colour shares, a drawn picture in every card,
  and our own OCR at 1024 and at 300 px across (the date, all 29 place tags, every headline,
  the chips, the rail times and the figures).

```sh
python3 render.py entry.png
python3 verify.py
```

## License

MIT, see [LICENSE](LICENSE).
