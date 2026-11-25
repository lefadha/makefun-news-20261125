"""Draw the one-page picture of 25 November 2026 (1024x1024, deterministic).

Layout, top to bottom: kicker rule, masthead with the date, a three-lead strapline,
region chips whose counts sum to the story count, an hour-by-hour rail, THE DAY IN
NUMBERS, then a 5x7 grid of numbered cards -- each with its own drawn scene, a place
tag, a desk and status label, a headline, a sense line and the outlets that ran it --
and a footer naming the scan.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

from stories import AND_ALSO, DAY, EDITION, NUMBERS, STORIES, TIMELINE

W = H = 1024
M = 18  # page margin
BG = (246, 243, 236)
INK = (24, 26, 31)
MID = (86, 92, 103)
RULE = (198, 194, 184)
RED = (176, 38, 42)

REGION_COLOUR = {
    "MIDDLE EAST": (176, 38, 42),
    "EAST ASIA": (28, 92, 132),
    "SOUTH ASIA": (166, 105, 20),
    "EUROPE": (54, 76, 128),
    "AFRICA": (32, 112, 74),
    "N. AMERICA": (108, 58, 118),
    "LATIN AMERICA": (168, 78, 32),
    "OCEANIA": (26, 118, 116),
}

FONT_DIR = {"serif": "/usr/share/fonts/truetype/liberation/LiberationSerif-%s.ttf",
            "sans": "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf"}
_cache = {}


def font(kind, size, bold=True):
    key = (kind, size, bold)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FONT_DIR[kind] % ("Bold" if bold else "Regular"), size)
    return _cache[key]


def tw(d, text, f):
    return d.textbbox((0, 0), text, font=f)[2]


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w0 in words:
        t = (cur + " " + w0).strip()
        if tw(d, t, f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w0
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, f, maxw):
    if tw(d, text, f) <= maxw:
        return text
    while text and tw(d, text + "...", f) > maxw:
        text = text[:-1]
    return text.rstrip() + "..."


def sp(d, text, f, gap):
    """letter-spaced small caps-ish label for kickers"""
    x = 0
    out = []
    for ch in text:
        out.append((ch, x))
        x += tw(d, ch, f) + gap
    return out, x


# ---------------------------------------------------------------- drawn scenes

def scene(d, kind, x, y, w, h, col):
    """A small vector picture, drawn inside the box (x, y, w, h)."""
    pad = 1
    x2, y2 = x + w, y + h
    d.rectangle([x, y, x2, y2], outline=RULE, width=1)
    cx, cy = (x + x2) / 2, (y + y2) / 2
    dark = tuple(max(0, c - 40) for c in col)
    light = tuple(min(255, int(c + (255 - c) * 0.55)) for c in col)

    if kind == "ship":  # hull, containers, smoke
        d.rectangle([x + 4, y + h - 14, x + w - 6, y + h - 9], fill=dark)
        d.polygon([(x + 2, y + h - 9), (x + w - 4, y + h - 9), (x + w - 10, y + h - 4), (x + 8, y + h - 4)], fill=col)
        for i in range(3):
            d.rectangle([x + 8 + i * (w - 22) / 3, y + h - 20, x + 8 + i * (w - 22) / 3 + 8, y + h - 14], fill=light)
        d.rectangle([x + w - 18, y + h - 26, x + w - 10, y + h - 14], fill=dark)
        for i, r in enumerate((4, 6, 8)):
            d.arc([x + w - 22 - r, y + h - 32 - r, x + w - 18 + r, y + h - 28 + r], 200, 340, fill=RED, width=2)
    elif kind == "cross":  # clinic
        d.rectangle([x + w * 0.25, y + h * 0.35, x + w * 0.75, y + h - 4], fill=light)
        d.rectangle([x + w * 0.4, y + h * 0.12, x + w * 0.6, y + h * 0.32], fill=light)
        d.rectangle([cx - 2, y + h * 0.42, cx + 2, y + h * 0.68], fill=RED)
        d.rectangle([cx - 7, y + h * 0.49, cx + 7, y + h * 0.56], fill=RED)
    elif kind == "dome":  # parliament
        d.rectangle([x + 5, y + h * 0.45, x + w - 5, y + h - 5], fill=light)
        d.pieslice([x + w * 0.2, y + h * 0.3, x + w * 0.8, y + h * 0.62], 180, 360, fill=col)
        d.rectangle([cx - 1, y + h * 0.2, cx + 1, y + h * 0.32], fill=dark)
        for i in range(4):
            xx = x + 10 + i * (w - 24) / 3
            d.rectangle([xx, y + h * 0.55, xx + 3, y + h - 8], fill=dark)
    elif kind == "whip":  # lash marks
        for i in range(4):
            d.line([x + 6 + i * 3, y + 8, x + w - 8, y + h - 10 - i * 4], fill=RED, width=2)
        d.line([x + 8, y + h - 10, x + w - 8, y + 8], fill=dark, width=1)
    elif kind == "soldier":  # helmet and rifle
        d.pieslice([x + w * 0.25, y + h * 0.2, x + w * 0.75, y + h * 0.8], 180, 360, fill=dark)
        d.rectangle([x + w * 0.22, y + h * 0.5, x + w * 0.78, y + h * 0.56], fill=dark)
        d.line([x + w * 0.7, y + h * 0.2, x + w * 0.5, y + h - 6], fill=col, width=2)
    elif kind == "rocket":
        d.polygon([(cx, y + 4), (cx + 7, y + h * 0.55), (cx, y + h * 0.66), (cx - 7, y + h * 0.55)], fill=light)
        d.polygon([(cx, y + 4), (cx + 7, y + h * 0.55), (cx, y + h * 0.55)], fill=col)
        d.polygon([(cx - 9, y + h * 0.5), (cx - 5, y + h * 0.62), (cx - 5, y + h * 0.5)], fill=RED)
        d.polygon([(cx + 9, y + h * 0.5), (cx + 5, y + h * 0.62), (cx + 5, y + h * 0.5)], fill=RED)
        d.polygon([(cx - 4, y + h * 0.7), (cx + 4, y + h * 0.7), (cx, y + h - 2)], fill=(230, 150, 40))
    elif kind == "chip":
        d.rectangle([x + w * 0.28, y + h * 0.25, x + w * 0.72, y + h * 0.75], outline=dark, width=2)
        d.rectangle([x + w * 0.38, y + h * 0.36, x + w * 0.62, y + h * 0.64], fill=col)
        for i in range(4):
            yy = y + h * 0.3 + i * h * 0.13
            d.line([x + w * 0.18, yy, x + w * 0.28, yy], fill=dark, width=1)
            d.line([x + w * 0.72, yy, x + w * 0.82, yy], fill=dark, width=1)
    elif kind == "tower":  # a tower block, windows lit
        d.rectangle([x + w * 0.3, y + h * 0.1, x + w * 0.7, y + h - 4], fill=light)
        for r in range(4):
            for c in range(2):
                d.rectangle([x + w * 0.36 + c * w * 0.14, y + h * 0.18 + r * h * 0.18,
                             x + w * 0.44 + c * w * 0.14, y + h * 0.26 + r * h * 0.18], fill=dark)
        d.polygon([(x + w * 0.25, y + h * 0.1), (x + w * 0.75, y + h * 0.1), (x + w * 0.7, y + h * 0.16), (x + w * 0.3, y + h * 0.16)], fill=col)
    elif kind == "locker":
        for r in range(2):
            for c in range(4):
                d.rectangle([x + 6 + c * (w - 14) / 4, y + 8 + r * (h - 16) / 2,
                             x + 6 + (c + 1) * (w - 14) / 4 - 2, y + 8 + (r + 1) * (h - 16) / 2 - 2],
                            outline=dark, width=1)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=col)
    elif kind == "runway":
        d.polygon([(x + 4, y + h - 4), (x + w * 0.55, y + 6), (x + w * 0.75, y + 6), (x + w - 4, y + h - 4)], fill=(210, 208, 200))
        d.line([cx, y + h * 0.55, cx, y + h - 6], fill=INK, width=2)
        d.line([cx - 6, y + h * 0.72, cx + 6, y + h * 0.72], fill=INK, width=1)
        d.polygon([(x + w * 0.7, y + h * 0.3), (x + w * 0.85, y + h * 0.42), (x + w * 0.62, y + h * 0.42)], fill=dark)
    elif kind == "bars":  # rising bars + arrow
        for i, hh in enumerate((0.3, 0.45, 0.62, 0.8)):
            bx = x + 8 + i * (w - 22) / 4
            d.rectangle([bx, y + h * (1 - hh) - 4, bx + (w - 26) / 4, y + h - 6], fill=col if i == 3 else light)
        d.line([x + 10, y + h * 0.62, x + w - 10, y + h * 0.2], fill=RED, width=2)
    elif kind == "waves":
        for i in range(3):
            yy = y + h * 0.62 + i * h * 0.1
            d.arc([x + 4, yy - 6, x + w * 0.6, yy + 6], 200, 340, fill=col, width=2)
            d.arc([x + w * 0.45, yy - 6, x + w - 4, yy + 6], 200, 340, fill=col, width=2)
        d.polygon([(x + w * 0.35, y + h * 0.3), (x + w * 0.6, y + h * 0.3), (x + w * 0.6, y + h * 0.6), (x + w * 0.35, y + h * 0.6)], fill=light)
        d.polygon([(x + w * 0.31, y + h * 0.3), (x + w * 0.475, y + h * 0.14), (x + w * 0.64, y + h * 0.3)], fill=dark)
    elif kind == "scale":  # balance
        d.line([cx, y + 8, cx, y + h - 8], fill=dark, width=2)
        d.line([x + 8, y + h * 0.3, x + w - 8, y + h * 0.3], fill=dark, width=2)
        d.arc([x + 4, y + h * 0.3, x + w * 0.45, y + h * 0.66], 0, 180, fill=col, width=2)
        d.arc([x + w * 0.55, y + h * 0.3, x + w - 4, y + h * 0.66], 0, 180, fill=col, width=2)
        d.rectangle([x + w * 0.3, y + h - 8, x + w * 0.7, y + h - 4], fill=dark)
    elif kind == "flagpole":
        d.line([x + w * 0.3, y + 4, x + w * 0.3, y + h - 4], fill=dark, width=2)
        d.polygon([(x + w * 0.3, y + 6), (x + w * 0.8, y + h * 0.2), (x + w * 0.3, y + h * 0.34)], fill=col)
        d.rectangle([x + w * 0.2, y + h - 5, x + w * 0.4, y + h - 3], fill=dark)
    elif kind == "knife":
        d.polygon([(x + 8, y + h * 0.62), (x + w - 12, y + h * 0.22), (x + w - 8, y + h * 0.3), (x + 12, y + h * 0.72)], fill=(196, 200, 208))
        d.rectangle([x + 4, y + h * 0.6, x + 14, y + h * 0.76], fill=dark)
        d.line([x + 8, y + h * 0.86, x + w - 8, y + h * 0.86], fill=RED, width=2)
    elif kind == "shield":
        d.polygon([(cx, y + 5), (x + w - 10, y + h * 0.22), (cx, y + h - 5), (x + 10, y + h * 0.22)], fill=light)
        d.line([cx, y + h * 0.3, cx, y + h * 0.66], fill=col, width=2)
        d.line([cx - 8, y + h * 0.46, cx + 8, y + h * 0.46], fill=col, width=2)
    elif kind == "cup":
        d.arc([x + w * 0.25, y + 6, x + w * 0.75, y + h * 0.7], 0, 180, fill=col, width=3)
        d.line([x + w * 0.25, y + h * 0.36, x + w * 0.75, y + h * 0.36], fill=col, width=2)
        d.line([cx, y + h * 0.7, cx, y + h - 8], fill=dark, width=3)
        d.rectangle([x + w * 0.35, y + h - 8, x + w * 0.65, y + h - 4], fill=dark)
    elif kind == "hands":
        d.line([x + 6, y + h - 12, cx - 2, y + h * 0.45], fill=col, width=4)
        d.line([x + w - 6, y + h - 12, cx + 2, y + h * 0.45], fill=dark, width=4)
        d.ellipse([cx - 7, y + h * 0.34, cx + 7, y + h * 0.5], fill=light)
    elif kind == "tent":
        d.polygon([(x + 6, y + h - 6), (cx, y + 8), (x + w - 6, y + h - 6)], fill=light)
        d.polygon([(cx, y + 8), (cx + 9, y + h - 6), (cx - 2, y + h - 6)], fill=col)
        d.line([x + 4, y + h - 5, x + w - 4, y + h - 5], fill=dark, width=2)
    elif kind == "wheat":
        d.line([cx, y + h - 6, cx, y + 10], fill=dark, width=2)
        for i in range(4):
            yy = y + 12 + i * h * 0.15
            d.ellipse([cx - 10, yy, cx - 3, yy + 7], fill=col)
            d.ellipse([cx + 3, yy + 3, cx + 10, yy + 10], fill=light)
    elif kind == "ballotbox":
        d.rectangle([x + w * 0.22, y + h * 0.42, x + w * 0.78, y + h - 5], fill=light)
        d.rectangle([x + w * 0.35, y + h * 0.44, x + w * 0.65, y + h * 0.5], fill=INK)
        d.rectangle([x + w * 0.34, y + 8, x + w * 0.66, y + h * 0.42], fill=(255, 255, 255), outline=dark)
        d.line([x + w * 0.38, y + h * 0.2, x + w * 0.46, y + h * 0.28], fill=RED, width=2)
        d.line([x + w * 0.46, y + h * 0.28, x + w * 0.62, y + h * 0.12], fill=RED, width=2)
    elif kind == "gavel":
        d.rectangle([x + w * 0.2, y + h * 0.22, x + w * 0.62, y + h * 0.42], fill=dark)
        d.line([x + w * 0.55, y + h * 0.4, x + w * 0.3, y + h - 8], fill=col, width=4)
        d.rectangle([x + w * 0.15, y + h - 12, x + w * 0.75, y + h - 6], fill=dark)
    elif kind == "bed":
        d.rectangle([x + 4, y + h * 0.45, x + w - 4, y + h * 0.62], fill=light)
        d.line([x + 6, y + h * 0.62, x + 6, y + h - 5], fill=dark, width=2)
        d.line([x + w - 6, y + h * 0.62, x + w - 6, y + h - 5], fill=dark, width=2)
        d.rectangle([x + 8, y + h * 0.36, x + w * 0.34, y + h * 0.47], fill=(255, 255, 255), outline=dark)
    elif kind == "drum":
        d.rectangle([x + 10, y + h * 0.3, x + w - 10, y + h - 6], fill=light, outline=dark)
        d.line([x + 10, y + h * 0.52, x + w - 10, y + h * 0.52], fill=dark, width=1)
        d.ellipse([x + 14, y + h * 0.24, x + w - 14, y + h * 0.4], fill=col)
        d.polygon([(cx, y + 4), (cx + 5, y + h * 0.14), (cx, y + h * 0.2), (cx - 5, y + h * 0.14)], fill=RED)
    elif kind == "plane":
        d.line([x + 6, y + h - 8, x + w - 6, y + h - 8], fill=col, width=2)
        d.arc([x + 4, y + h * 0.5, x + w - 4, y + h * 0.9], 180, 360, fill=col, width=2)
        d.polygon([(x + w * 0.3, y + h * 0.35), (x + w * 0.78, y + h * 0.18), (x + w * 0.62, y + h * 0.42), (x + w * 0.34, y + h * 0.5)], fill=dark)
        d.line([x + w * 0.3, y + h * 0.4, x + w * 0.45, y + h * 0.28], fill=dark, width=2)
    elif kind == "shop":
        d.rectangle([x + 8, y + h * 0.35, x + w - 8, y + h - 5], fill=light)
        for i in range(3):
            d.rectangle([x + 8 + i * (w - 16) / 3, y + h * 0.28, x + 8 + (i + 1) * (w - 16) / 3 - 2, y + h * 0.37], fill=col)
        d.rectangle([cx - 5, y + h * 0.55, cx + 5, y + h - 5], fill=dark)
        d.ellipse([x + w * 0.72, y + h * 0.1, x + w * 0.88, y + h * 0.24], fill=RED)
    elif kind == "roundtable":
        d.ellipse([x + 6, y + h * 0.35, x + w - 6, y + h * 0.85], fill=light, outline=dark)
        for i in range(5):
            ang = -150 + i * 60
            import math
            px = cx + 0.38 * w * math.cos(math.radians(ang))
            py = cy + 0.32 * h * math.sin(math.radians(ang))
            d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=col)
    elif kind == "palm":
        d.arc([x + w * 0.2, y + h * 0.55, x + w - 4, y + h + 4], 180, 360, fill=col, width=2)
        d.line([cx, y + h * 0.62, cx - 2, y + h * 0.28], fill=dark, width=2)
        for a in (-40, -10, 20, 50):
            import math
            d.line([cx - 2, y + h * 0.3, cx - 2 + 16 * math.cos(math.radians(a)), y + h * 0.3 - 14 * math.sin(math.radians(a))], fill=dark, width=2)
    elif kind == "line":  # a rising line chart
        pts = [(x + 8, y + h * 0.72), (x + w * 0.35, y + h * 0.6), (x + w * 0.6, y + h * 0.66), (x + w - 8, y + h * 0.28)]
        d.line(pts, fill=col, width=2)
        for px, py in pts:
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        d.line([x + 6, y + h - 4, x + w - 6, y + h - 4], fill=RULE)
    else:  # fall back: a bold block with the region colour
        d.rectangle([x + 8, y + 8, x + w - 8, y + h - 8], outline=dark, width=2)
        d.rectangle([x + 14, y + 14, x + w * 0.5, y + h * 0.5], fill=col)


SCENE_ALIAS = {
    "port": "ship", "clinic": "cross", "knesset": "dome", "whip": "whip", "soldier": "soldier",
    "rocket": "rocket", "chip": "chip", "party": "dome", "tower": "tower", "locker": "locker",
    "runway": "runway", "money": "bars", "flood": "waves", "scale": "scale", "flag": "flagpole",
    "knife": "knife", "badge": "shield", "trophy": "cup", "handshake": "hands", "tent": "tent",
    "wheat": "wheat", "tariff": "bars", "ballot": "ballotbox", "gavel": "gavel",
    "boardroom": "tower", "gurney": "bed", "barrel": "drum", "wreck": "plane",
    "hostage": "shop", "fuel": "drum", "table": "roundtable", "chart": "line", "island": "palm",
}


def tint(col, bg, k):
    return tuple(int(col[i] * k + bg[i] * (1 - k)) for i in range(3))


def main(out_path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f_kick = font("sans", 12)
    f_mast = font("serif", 41)
    f_lead = font("sans", 13)
    f_small = font("sans", 9)
    f_chip = font("sans", 11)
    f_rail_h = font("sans", 9)
    f_rail_t = font("sans", 9, bold=False)
    f_num = font("serif", 26)
    f_num_l = font("sans", 8, bold=False)

    # ---- kicker
    d.rectangle([M, 13, W - M, 30], fill=INK)
    d.text((M + 8, 16), "ONE DAY OF WORLD NEWS", font=f_kick, fill=(255, 255, 255))
    right = "WEDNESDAY EDITION  ·  03:00 GMT  ·  %d STORIES" % len(STORIES)
    d.text((W - M - 8 - tw(d, right, f_kick), 16), right, font=f_kick, fill=(255, 255, 255))

    # ---- masthead
    d.text((M, 36), "THE WORLD, 25 NOVEMBER 2026", font=f_mast, fill=INK)
    # lead scene at the top right
    lx, ly, lw, lh = W - M - 252, 36, 252, 56
    d.rectangle([lx, ly, lx + lw, ly + lh], fill=tint(REGION_COLOUR["MIDDLE EAST"], BG, 0.34))
    scene(d, "ship", lx + 2, ly + 2, lw - 4, lh - 4, REGION_COLOUR["MIDDLE EAST"])
    d.text((lx, ly + lh + 2), "HODEIDAH: YEMEN'S PORT UNDER STRIKE", font=f_small, fill=RED)
    d.text((M, 80), fit(d, "Coalition strikes Yemen's port  ·  Shenzhou-24 lifts a Pakistani astronaut  ·  "
                            "Ukraine asks €115bn for 2027  ·  Senegal handed back its AFCON title",
                        f_lead, 690), font=f_lead, fill=MID)

    # ---- region chips
    counts = {}
    for s in STORIES:
        counts[s[2]] = counts.get(s[2], 0) + 1
    order = ["MIDDLE EAST", "EUROPE", "AFRICA", "EAST ASIA", "SOUTH ASIA", "N. AMERICA",
             "LATIN AMERICA", "OCEANIA"]
    x = M
    y = 100
    for r in order:
        if r not in counts:
            continue
        label = "%s %d" % (r, counts[r])
        wch = tw(d, label, f_chip) + 12
        d.rounded_rectangle([x, y, x + wch, y + 17], radius=3, fill=REGION_COLOUR[r])
        d.text((x + 6, y + 3), label, font=f_chip, fill=(255, 255, 255))
        x += wch + 5
    d.text((M, y + 21), "%d stories in 8 regions, every one dated 25 November 2026" % len(STORIES),
           font=f_small, fill=MID)

    # ---- hour-by-hour rail
    y = 144
    d.line([M, y, W - M, y], fill=RULE, width=1)
    d.text((M, y + 4), "THE DAY, HOUR BY HOUR (GMT)", font=f_rail_h, fill=INK)
    colw = (W - 2 * M) / len(TIMELINE)
    for i, (t, text) in enumerate(TIMELINE):
        cx0 = M + i * colw
        d.text((cx0 + 2, y + 18), t, font=font("sans", 10), fill=RED)
        lines = wrap(d, text, f_rail_t, colw - 10)[:2]
        for j, ln in enumerate(lines):
            d.text((cx0 + 2, y + 31 + j * 10), ln, font=f_rail_t, fill=MID)

    # ---- numbers strip
    y = 192
    d.line([M, y, W - M, y], fill=RULE, width=1)
    d.text((M, y + 4), "THE DAY IN NUMBERS", font=f_rail_h, fill=INK)
    nw = (W - 2 * M) / len(NUMBERS)
    for i, (val, lab) in enumerate(NUMBERS):
        cx0 = M + i * nw
        d.rectangle([cx0, y + 15, cx0 + 3, y + 52], fill=RED)
        d.text((cx0 + 8, y + 14), val, font=f_num, fill=INK)
        d.text((cx0 + 8, y + 44), fit(d, lab, f_num_l, nw - 14), font=f_num_l, fill=MID)

    # ---- story grid
    TOP = 246
    COLS, ROWS = 5, 6
    GAP = 5
    cw = (W - 2 * M - (COLS - 1) * GAP) // COLS
    ch = (H - TOP - 34 - (ROWS - 1) * GAP) // ROWS
    d.line([M, TOP - 6, W - M, TOP - 6], fill=INK, width=2)

    cells = list(STORIES) + [None]
    for idx, s in enumerate(cells):
        r, c = divmod(idx, COLS)
        x0 = M + c * (cw + GAP)
        y0 = TOP + r * (ch + GAP)
        if s is None:
            d.rectangle([x0, y0, x0 + cw, y0 + ch], fill=tint(INK, BG, 0.05), outline=RULE)
            d.rectangle([x0, y0, x0 + cw, y0 + 13], fill=INK)
            d.text((x0 + 5, y0 + 3), "AND ALSO", font=font("sans", 8), fill=(255, 255, 255))
            yy = y0 + 18
            for line in AND_ALSO:
                for ln in wrap(d, line, font("sans", 7, bold=False), cw - 10)[:2]:
                    d.text((x0 + 5, yy), ln, font=font("sans", 7, bold=False), fill=MID)
                    yy += 8
                yy += 3
            continue
        n, place, region, desk, status, head, detail, src, utc, sc = s
        col = REGION_COLOUR[region]
        d.rectangle([x0, y0, x0 + cw, y0 + ch], fill=tint(col, BG, 0.03), outline=RULE)
        d.rectangle([x0, y0, x0 + cw, y0 + 14], fill=tint(col, BG, 0.40))
        d.text((x0 + 5, y0 + 2), "%02d" % n, font=font("sans", 10), fill=col)
        pl = fit(d, place, font("sans", 8, bold=False), cw - 74)
        d.text((x0 + 23, y0 + 3), pl, font=font("sans", 8, bold=False), fill=INK)
        st = fit(d, status, font("sans", 7, bold=False), 48)
        d.text((x0 + cw - 4 - tw(d, st, font("sans", 7, bold=False)), y0 + 3), st,
               font=font("sans", 7, bold=False), fill=RED)
        # scene, tinted, then headline beside it
        d.rectangle([x0 + 5, y0 + 18, x0 + 63, y0 + 62], fill=tint(col, BG, 0.52))
        scene(d, SCENE_ALIAS.get(sc, "block"), x0 + 6, y0 + 19, 56, 42, col)
        hl = wrap(d, head, font("sans", 11), cw - 74)[:3]
        for j, ln in enumerate(hl):
            d.text((x0 + 68, y0 + 19 + j * 13), ln, font=font("sans", 11), fill=INK)
        # sense line, then source and time
        dl = wrap(d, detail, font("sans", 8, bold=False), cw - 10)[:2]
        for j, ln in enumerate(dl):
            d.text((x0 + 5, y0 + 68 + j * 10), ln, font=font("sans", 8, bold=False), fill=MID)
        d.text((x0 + 5, y0 + 92), fit(d, "%s · %s GMT" % (desk.title(), utc), font("sans", 7, bold=False), cw - 10),
               font=font("sans", 7, bold=False), fill=INK)
        d.text((x0 + 5, y0 + 103), fit(d, src, font("sans", 7, bold=False), cw - 10),
               font=font("sans", 7, bold=False), fill=(150, 58, 52))

    # ---- footer
    fy = H - 26
    d.line([M, fy, W - M, fy], fill=INK, width=1)
    foot = ("Sources: our own scan of 20 wire feeds, 00:00-03:00 GMT, 25 November 2026  ·  "
            "pictures drawn from the reports, not photographs  ·  every story carries the outlets that ran it")
    d.text((M, fy + 5), fit(d, foot, font("sans", 7, bold=False), W - 2 * M), font=font("sans", 7, bold=False), fill=MID)

    img.save(out_path, format="PNG", optimize=True)
    return out_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    main(out)
    print("wrote", out, os.path.getsize(out), "bytes")
