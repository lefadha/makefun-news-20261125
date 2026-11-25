"""Local mirror of the competition gate, run before any submission.

Checks the file the judge will see (PNG wholeness, the 1024x1024 and 1 MiB caps), that the
render is deterministic and the committed image is the one this code draws, that the sandbox
program ships the same bytes twice, that the page has no ink in its margins, and -- with our
own OCR -- that every place tag, headline, chip, time and figure is actually readable in it.
"""
import hashlib
import os
import re
import struct
import subprocess
import sys
import tempfile
import zlib

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "entry.png")
sys.path.insert(0, HERE)
from stories import AND_ALSO, NUMBERS, STORIES, TIMELINE  # noqa: E402

PASS, FAIL = [], []


def check(name, ok, note=""):
    (PASS if ok else FAIL).append((name, note))
    print("%s  %-42s %s" % ("pass" if ok else "FAIL", name, note))


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def png_chunks(data):
    at = 8
    out = []
    while at + 12 <= len(data):
        (ln,) = struct.unpack(">I", data[at:at + 4])
        typ = data[at + 4:at + 8].decode("latin1")
        body = data[at + 8:at + 8 + ln]
        (crc,) = struct.unpack(">I", data[at + 8 + ln:at + 12 + ln])
        out.append((typ, body, crc, zlib.crc32(data[at + 4:at + 8 + ln]) & 0xFFFFFFFF))
        at += 12 + ln
        if typ == "IEND":
            break
    return out


def render(path):
    subprocess.run([sys.executable, os.path.join(HERE, "render.py"), path], check=True,
                   stdout=subprocess.DEVNULL, cwd=HERE)


def main():
    data = open(PNG, "rb").read()
    check("png: signature", data[:8] == b"\x89PNG\r\n\x1a\n")
    chunks = png_chunks(data)
    check("png: chunk CRCs", all(c[2] == c[3] for c in chunks), "%d chunks" % len(chunks))
    check("png: ends with IEND", chunks[-1][0] == "IEND" and data.endswith(chunks[-1][1]))
    ihdr = chunks[0][1]
    w, h, depth, ctype = struct.unpack(">IIBB", ihdr[:10])
    check("gate: 1024x1024", (w, h) == (1024, 1024), "%dx%d" % (w, h))
    check("gate: at most 1 MiB", len(data) <= 1048576, "%d bytes" % len(data))
    idat = b"".join(c[1] for c in chunks if c[0] == "IDAT")
    raw = zlib.decompress(idat)
    check("png: IDAT length matches header", len(raw) == h * (1 + w * 3), "%d bytes" % len(raw))

    tmp = tempfile.mkdtemp()
    a, b = os.path.join(tmp, "a.png"), os.path.join(tmp, "b.png")
    render(a)
    render(b)
    da, db = open(a, "rb").read(), open(b, "rb").read()
    check("render: two runs identical", da == db, hashlib.sha256(da).hexdigest()[:12])
    check("render: committed is the fresh render", da == data, "%d bytes" % len(da))

    outs = [os.path.join(tmp, "o%d" % i) for i in (1, 2)]
    for o in outs:
        env = dict(os.environ, MAKEFUN_OUTPUT_DIR=o)
        subprocess.run(["node", os.path.join(HERE, "main.ts")], check=True, env=env,
                       stdout=subprocess.DEVNULL, cwd=HERE)
    sob = [open(os.path.join(o, "entry.png"), "rb").read() for o in outs]
    check("program: ships the committed bytes twice", sob[0] == sob[1] == data)

    im = Image.open(PNG).convert("RGB")
    px = im.load()
    border = 12
    ink = 0
    for y in range(1024):
        for x in range(1024):
            if x < border or y < border or x >= 1024 - border or y >= 1024 - border:
                r, g, bl = px[x, y]
                if max(r, g, bl) < 232:
                    ink += 1
    check("page: clear margins", ink == 0, "%d ink pixels in the %dpx border" % (ink, border))

    light = colour = tot = 0
    for y in range(0, 1024, 3):
        for x in range(0, 1024, 3):
            r, g, bl = px[x, y]
            mx, mn = max(r, g, bl), min(r, g, bl)
            tot += 1
            if mx > 225 and mx - mn < 22:
                light += 1
            elif mx - mn > 30:
                colour += 1
    lp, cp = 100 * light / tot, 100 * colour / tot
    check("page: light share 65-90%", 65 <= lp <= 90, "%.1f%%" % lp)
    check("page: colour share 8-25%", 8 <= cp <= 25, "%.1f%%" % cp)

    # every card carries a drawn scene (ink inside its 56x42 box, away from the frame)
    x0 = 5 + 3
    scenes_bad = []
    for idx in range(len(STORIES)):
        col, row = idx % 5, idx // 5
        bx = 18 + col * (cw() + 5) + 6
        by = 246 + row * (ch() + 5) + 19
        n = 0
        for y in range(by + 2, by + 40):
            for x in range(bx + 2, bx + 54):
                r, g, bl = px[x, y]
                if abs(r - g) + abs(g - bl) + abs(r - bl) > 40 or max(r, g, bl) < 180:
                    n += 1
        if n < 40:
            scenes_bad.append(idx + 1)
    check("page: a drawn picture in every card", not scenes_bad, "empty: %s" % scenes_bad[:6])

    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    res, _ = ocr(PNG)
    full = " ".join(t[1] for t in (res or []))
    nfull = norm(full)
    check("ocr: date in the masthead", "25november2026" in nfull)
    chips = {}
    for s in STORIES:
        chips[s[2]] = chips.get(s[2], 0) + 1
    miss_chip = [r for r in chips if norm("%s %d" % (r, chips[r])) not in nfull]
    check("ocr: all region chips", not miss_chip, "missing %s" % miss_chip)
    miss_tag = [s[1] for s in STORIES if norm(s[1]) not in nfull]
    check("ocr: all %d place tags" % len(STORIES), len(miss_tag) <= 1, "missing %s" % miss_tag[:5])

    def covers(text, hay):
        words = [norm(w) for w in text.split() if norm(w)]
        got = sum(1 for w in words if w in hay)
        return got / max(1, len(words))

    miss_head = [(s[5], round(covers(s[5], nfull), 2)) for s in STORIES if covers(s[5], nfull) < 0.9]
    check("ocr: all %d headlines" % len(STORIES), len(miss_head) <= 2, "weak %s" % miss_head[:4])
    miss_t = [t for t, _ in TIMELINE if norm(t) not in nfull]
    check("ocr: timeline times", not miss_t, "missing %s" % miss_t)
    miss_n = [v for v, _ in NUMBERS if norm(v) not in nfull]
    check("ocr: numbers strip", len(miss_n) <= 1, "missing %s" % miss_n)
    foot_ink = sum(1 for y in range(996, 1016) for x in range(18, 1006, 2)
                   if max(px[x, y]) < 200)
    check("page: footer credit line is set", foot_ink > 40, "%d dark px on the footer rule row" % foot_ink)

    small = os.path.join(tmp, "s.png")
    Image.open(PNG).resize((300, 300), Image.LANCZOS).save(small)
    res2, _ = ocr(small)
    ns = norm(" ".join(t[1] for t in (res2 or [])))
    hits = sum(1 for s in STORIES if norm(s[5]) in ns)
    runs300 = len(res2 or [])
    check("ocr@300px: date still reads", "25november2026" in ns)
    print("note  ocr@300px                            %d runs, %d whole headlines at 300 px" % (runs300, hits))

    print("\n%d pass, %d fail" % (len(PASS), len(FAIL)))
    if FAIL:
        for name, note in FAIL:
            print("  FAILED:", name, note)
        return 1
    return 0


def cw():
    return (1024 - 2 * 18 - 4 * 5) // 5


def ch():
    return (1024 - 246 - 34 - 5 * 5) // 6


if __name__ == "__main__":
    sys.exit(main())
