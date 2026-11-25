"""Quality check of a candidate page: the gate's numeric caps plus what our own OCR can read."""
import os
import re
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rapidocr_onnxruntime import RapidOCR  # noqa: E402
from stories import AND_ALSO, NUMBERS, STORIES, TIMELINE  # noqa: E402
from render_b import ELSEWHERE  # noqa: E402

PNG = sys.argv[1]
ocr = RapidOCR()


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def covers(text, hay):
    words = [norm(w) for w in text.split() if norm(w)]
    return sum(1 for w in words if w in hay) / max(1, len(words))


im = Image.open(PNG).convert("RGB")
w, h = im.size
px = im.load()
print("size", w, h, "bytes", os.path.getsize(PNG), "| gate 1024x1024 & <=1MiB:",
      (w, h) == (1024, 1024) and os.path.getsize(PNG) <= 1048576)

border = 12
ink = sum(1 for y in range(h) for x in range(w)
          if (x < border or y < border or x >= w - border or y >= h - border) and max(px[x, y]) < 232)
print("ink in 12px border", ink, "(0 = clear margins)")

light = colour = tot = 0
for y in range(0, h, 3):
    for x in range(0, w, 3):
        r, g, b = px[x, y]
        mx, mn = max(r, g, b), min(r, g, b)
        tot += 1
        if mx > 225 and mx - mn < 22:
            light += 1
        elif mx - mn > 30:
            colour += 1
print("light %.1f%% (65-90)  colour %.1f%% (8-25)" % (100 * light / tot, 100 * colour / tot))

res, _ = ocr(PNG)
full = " ".join(t[1] for t in (res or []))
nf = norm(full)
print("ocr runs", len(res or []))
print("  date:", "25november2026" in nf)
lead = STORIES[0][5]
print("  lead headline cover %.2f" % covers(lead, nf))
for s in ELSEWHERE:
    print("  else %.2f  %s" % (covers(s[5], nf), s[5][:46]))
miss_place = [s[1] for s in [STORIES[0]] + ELSEWHERE if norm(s[1]) not in nf]
print("  places missing:", miss_place)
miss_num = [v for v, _ in NUMBERS[:3] if norm(v) not in nf]
print("  numbers missing:", miss_num)
miss_t = [t for t, _ in TIMELINE[:4] if norm(t) not in nf]
print("  hours missing:", miss_t)

small = "/tmp/_qc300.png"
im.resize((300, 300), Image.LANCZOS).save(small)
res2, _ = ocr(small)
ns = norm(" ".join(t[1] for t in (res2 or [])))
hits = sum(1 for s in [STORIES[0]] + ELSEWHERE if covers(s[5], ns) >= 0.9)
print("AT 300px: runs %d | whole headlines %d/%d | date reads %s | numbers %s"
      % (len(res2 or []), hits, 1 + len(ELSEWHERE), "25november2026" in ns,
         [v for v, _ in NUMBERS[:3] if norm(v) in ns]))
