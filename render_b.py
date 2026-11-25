"""Two alternative compositions of the same 25 November 2026 page.

Both use only the facts already gathered in stories.py (29 dated stories, the wire
also-list, the hour rail and the six figures) and both draw every picture by hand.

  poster     one clear composition: a big lead picture, the lead headline in large
             type, three figures the size of a hand, five further headlines, the hours.
             Built for the judge's rule that the page must read at about 300 px.
  chronicle  the day as a column of time: seven dated events down the left, the big
             figures and the also-list down the right.

Run:  python render_b.py out.png poster|chronicle
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import (BG, H, INK, M, MID, RED, REGION_COLOUR, RULE, SCENE_ALIAS, W,  # noqa: E402
                    fit, font, scene, sp, tint, tw, wrap)
from stories import AND_ALSO, DAY, EDITION, NUMBERS, STORIES, TIMELINE  # noqa: E402

ORDER = ["MIDDLE EAST", "EUROPE", "AFRICA", "EAST ASIA", "SOUTH ASIA",
         "N. AMERICA", "LATIN AMERICA", "OCEANIA"]

LEAD = STORIES[0]
ELSEWHERE = [STORIES[4], STORIES[10], STORIES[13], STORIES[15], STORIES[26]]


def counts_by_region():
    c = {}
    for s in STORIES:
        c[s[2]] = c.get(s[2], 0) + 1
    return c


def kicker(d, text, x, y, f, col, gap):
    pairs, w = sp(d, text, f, gap)
    for ch, off in pairs:
        d.text((x + off, y), ch, font=f, fill=col)
    return w


# --------------------------------------------------------------------- poster

def poster(out):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    left = M + 4
    right = W - M - 4

    d.rectangle([left, 18, right, 26], fill=RED)
    kicker(d, "THE WORLD, WEDNESDAY 25 NOVEMBER 2026", left, 36, font("sans", 23), INK, 1.6)
    d.text((left, 70), "%s  ·  %d STORIES  ·  8 REGIONS  ·  EVERY ONE DATED TODAY"
           % (EDITION, len(STORIES)), font=font("sans", 15, bold=False), fill=MID)

    # --- the lead: one big drawn picture
    n, place, region, desk, status, head, detail, src, utc, sc = LEAD
    col = REGION_COLOUR[region]
    lx, ly, lw, lh = left, 100, 620, 286
    d.rectangle([lx, ly, lx + lw, ly + lh], fill=tint(col, BG, 0.30))
    scene(d, SCENE_ALIAS.get(sc, "block"), lx + 6, ly + 6, lw - 12, lh - 12, col)
    d.rectangle([lx, ly + lh, lx + 6, ly + lh + 96], fill=col)

    hy = ly + lh + 12
    for j, ln in enumerate(wrap(d, head, font("sans", 40), lw - 20)[:2]):
        d.text((lx + 16, hy + j * 44), ln, font=font("sans", 40), fill=INK)
    d.text((lx + 16, hy + 92), fit(d, "%s  ·  %s GMT  ·  %s" % (place, utc, src),
                                   font("sans", 17), lw - 20), font=font("sans", 17), fill=RED)
    d.text((lx + 16, hy + 116), fit(d, detail, font("sans", 15, bold=False), lw - 20),
           font=font("sans", 15, bold=False), fill=MID)

    # --- the day in numbers, right column, figures the size of a hand
    nx = left + lw + 34
    nw = right - nx
    d.rectangle([nx, 100, right, 104], fill=INK)
    d.text((nx, 112), "THE DAY IN NUMBERS", font=font("sans", 16), fill=INK)
    y = 140
    for k, (val, lab) in enumerate(NUMBERS[:3]):
        d.text((nx, y), val, font=font("serif", 62), fill=col if k == 0 else INK)
        d.text((nx, y + 74), fit(d, lab, font("sans", 17, bold=False), nw),
               font=font("sans", 17, bold=False), fill=MID)
        y += 112
        if k < 2:
            d.line([nx, y - 12, right, y - 12], fill=RULE, width=1)

    # --- five further headlines, set large enough to read at a glance
    d.line([left, 500, right, 500], fill=INK, width=2)
    d.text((left, 510), "ELSEWHERE TODAY", font=font("sans", 16), fill=INK)
    d.text((right - 210, 512), "every line dated, sourced", font=font("sans", 14, bold=False), fill=MID)
    y = 540
    for s in ELSEWHERE:
        n2, place2, region2, desk2, status2, head2, detail2, src2, utc2, sc2 = s
        c2 = REGION_COLOUR[region2]
        d.rectangle([left, y, left + 84, y + 62], fill=tint(c2, BG, 0.34))
        scene(d, SCENE_ALIAS.get(sc2, "block"), left + 4, y + 4, 76, 54, c2)
        hx = left + 100
        lines = wrap(d, head2, font("sans", 26), right - hx - 4)[:2]
        for j, ln in enumerate(lines):
            d.text((hx, y + j * 30), ln, font=font("sans", 26), fill=INK)
        d.text((hx, y + 62), fit(d, "%s  ·  %s GMT  ·  %s" % (place2, utc2, src2),
                                 font("sans", 14), right - hx - 4), font=font("sans", 14), fill=c2)
        y += 76

    # --- the hours, as one strip
    y = 940
    d.line([left, y, right, y], fill=RULE, width=1)
    d.text((left, y + 6), "THE HOURS SINCE MIDNIGHT (GMT)", font=font("sans", 13), fill=MID)
    x = left + 292
    for t, text in TIMELINE[:4]:
        d.ellipse([x, y + 11, x + 7, y + 18], fill=RED)
        d.text((x + 12, y + 6), t, font=font("sans", 15), fill=INK)
        x += 172

    # --- footer
    fy = 976
    d.line([left, fy, right, fy], fill=INK, width=1)
    foot = ("Our own scan of 20 wire feeds, 00:00-03:00 GMT, 25 November 2026  ·  "
            "every picture drawn from the reports, no photographs  ·  each story names the outlets that ran it")
    d.text((left, fy + 7), fit(d, foot, font("sans", 13, bold=False), right - left),
           font=font("sans", 13, bold=False), fill=MID)
    img.save(out, format="PNG", optimize=True)
    return out


# ------------------------------------------------------------------ chronicle

def chronicle(out):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    left = M + 4
    right = W - M - 4
    colx = left
    colw = 596
    rx = left + colw + 40
    rw = right - rx

    d.text((left, 18), "25 NOVEMBER 2026", font=font("serif", 46), fill=INK)
    d.text((left, 74), "ONE DAY OF WORLD NEWS, IN THE ORDER IT HAPPENED", font=font("sans", 17), fill=RED)
    d.rectangle([left, 104, right, 108], fill=INK)
    d.text((left, 116), "%d STORIES  ·  8 REGIONS  ·  %s  ·  ALL TIMES GMT" % (len(STORIES), EDITION),
           font=font("sans", 14, bold=False), fill=MID)

    # --- the column of time
    y = 152
    dot_x = colx + 74
    d.line([dot_x, y + 10, dot_x, 906], fill=RULE, width=2)
    for idx, (t, text) in enumerate(TIMELINE):
        s = next((x for x in STORIES if x[8] == t), None)
        if s is None:
            continue
        n, place, region, desk, status, head, detail, src, utc, sc = s
        c = REGION_COLOUR[region]
        # a tinted band carries the event, so the page keeps its colour at a distance
        d.rectangle([colx + 88, y - 4, right, y + 98], fill=tint(c, BG, 0.12))
        d.rectangle([colx, y - 2, colx + 82, y + 30], fill=c)
        d.text((colx + 8, y - 1), t, font=font("sans", 24), fill=(255, 255, 255))
        d.ellipse([dot_x - 6, y + 6, dot_x + 6, y + 18], fill=c)
        lines = wrap(d, head, font("sans", 30), colw - 100)[:2]
        for j, ln in enumerate(lines):
            d.text((colx + 96, y + j * 34), ln, font=font("sans", 30), fill=INK)
        d.rectangle([right - 92, y + 2, right - 4, y + 74], fill=tint(c, BG, 0.42))
        scene(d, SCENE_ALIAS.get(sc, "block"), right - 88, y + 6, 80, 64, c)
        d.text((colx + 96, y + (34 * len(lines)) + 4),
               fit(d, "%s  ·  %s  ·  %s" % (place, desk.title(), src), font("sans", 15), colw - 40),
               font=font("sans", 15), fill=c)
        y += 108

    # --- right rail: the figures, the also-list, the map of the day
    d.rectangle([rx, 152, right, 156], fill=RED)
    d.text((rx, 164), "THE DAY IN NUMBERS", font=font("sans", 16), fill=INK)
    y2 = 194
    for k, (val, lab) in enumerate(NUMBERS[:3]):
        d.text((rx, y2), val, font=font("serif", 44), fill=INK)
        d.text((rx, y2 + 52), fit(d, lab, font("sans", 15, bold=False), rw),
               font=font("sans", 15, bold=False), fill=MID)
        y2 += 88

    d.line([rx, y2 + 4, right, y2 + 4], fill=RULE, width=1)
    d.text((rx, y2 + 12), "REGIONS, BY COUNT", font=font("sans", 16), fill=INK)
    counts = counts_by_region()
    y3 = y2 + 40
    top = max(counts.values())
    bar_max = rw - 78
    for r in ORDER:
        if r not in counts:
            continue
        d.text((rx, y3), r.title(), font=font("sans", 13), fill=INK)
        barw = max(6, int(bar_max * counts[r] / top))
        d.rectangle([rx + rw - barw - 20, y3 + 3, rx + rw - 20, y3 + 13], fill=REGION_COLOUR[r])
        d.text((rx + rw - 16, y3 - 1), str(counts[r]), font=font("sans", 13), fill=MID)
        y3 += 24

    d.line([rx, y3 + 6, right, y3 + 6], fill=RULE, width=1)
    d.text((rx, y3 + 14), "ALSO ON THE WIRE", font=font("sans", 16), fill=INK)
    y4 = y3 + 40
    for line in AND_ALSO[:4]:
        for ln in wrap(d, line, font("sans", 14, bold=False), rw)[:3]:
            d.text((rx, y4), ln, font=font("sans", 14, bold=False), fill=MID)
            y4 += 18
        y4 += 4

    fy = 976
    d.line([left, fy, right, fy], fill=INK, width=1)
    foot = ("Our own scan of 20 wire feeds, 00:00-03:00 GMT, 25 November 2026  ·  "
            "every picture drawn from the reports, no photographs  ·  each story names the outlets that ran it")
    d.text((left, fy + 7), fit(d, foot, font("sans", 13, bold=False), right - left),
           font=font("sans", 13, bold=False), fill=MID)
    img.save(out, format="PNG", optimize=True)
    return out


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "alt.png"
    which = sys.argv[2] if len(sys.argv) > 2 else "poster"
    (poster if which == "poster" else chronicle)(out)
    print("wrote", out, os.path.getsize(out), "bytes")
