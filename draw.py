"""Poster painter for the 19 November 2026 world-news sheet.

Everything on the page comes from the EDITION table below: one lead item,
four card items, a strip of shorter items and a footer line. The painter
only knows geometry; the words live in the table, so swapping a day's news
means editing data, not drawing code.

Layout (1024 x 1024, all coordinates in pixels):
    masthead band, lead row (words left, picture right),
    a 2 x 2 grid of cards, an "also today" band, a footer line.
"""

from PIL import Image, ImageDraw, ImageFont

CANVAS = (1024, 1024)
MARGIN = 40
GUTTER = 24

INK = (22, 28, 44)          # near-black navy for text
NAVY = (23, 35, 61)         # masthead / strip background
NAVY_DEEP = (16, 26, 48)    # picture panel background
PAPER = (247, 243, 232)     # page background
CARD = (255, 255, 255)
CARD_EDGE = (203, 196, 178)
RULE = (201, 194, 176)
GOLD = (212, 175, 55)
GOLD_SOFT = (226, 196, 110)
CRIMSON = (178, 34, 52)
TEAL = (15, 118, 110)
MUTED = (96, 96, 92)
BODY = (52, 52, 50)

EDITION = {
    "kicker": "THE WORLD IN ONE DAY",
    "dateline": "THURSDAY, 19 NOVEMBER 2026",
    "lead": {
        "tag": "SHENZHEN  \u00b7  APEC SUMMIT",
        "headline": "Three presidents, one table in Shenzhen",
        "body": (
            "Trump, Xi and Putin meet together for the first time, with an "
            "hour set aside for nuclear arms, Ukraine, Iran and trade. "
            "No deal is expected."
        ),
    },
    "cards": [
        {
            "tag": "GAMES  \u00b7  CULTURE",
            "headline": "GTA VI rolls out around the world",
            "body": (
                "After 13 years, it unlocks at midnight in each market. "
                "99 on Metacritic."
            ),
            "glyph": "bars",
        },
        {
            "tag": "SPACE  \u00b7  SCIENCE",
            "headline": "NASA confirms Voyager 1 is a light-day away",
            "body": (
                "Launched in 1977, now the first human-made object "
                "16 billion miles out. Signals take a day."
            ),
            "glyph": "dish",
        },
        {
            "tag": "WEATHER  \u00b7  INDIA",
            "headline": "Cyclone Akvan bears down on India's east",
            "body": (
                "A very severe cyclone nears India's coast, winds of "
                "120-130 km/h at landfall due Friday."
            ),
            "glyph": "swirl",
        },
        {
            "tag": "MIDDLE EAST  \u00b7  GULF WAR",
            "headline": "Iran widens its attacks on US bases in the Gulf",
            "body": (
                "Tehran's drones hit a US base in Kuwait and sites in "
                "Bahrain. No US staff hurt."
            ),
            "glyph": "target",
        },
    ],
    "also": [
        "Pew: Islam to be the largest faith by 2035",
        "Earth's missing billion years may be solved",
        "Canada's Carney recalibrates China ties",
        "US senators warn on AI cyber threats",
    ],
    "footer": (
        "All stories as reported on 19 November 2026  \u00b7  "
        "Sources: Reuters, AP, NASA, IMD"
    ),
}


class Typefaces:
    """Loads the bundled DejaVu faces once and hands out sizes."""

    def __init__(self, folder):
        self.regular = folder + "/DejaVuSans.ttf"
        self.bold = folder + "/DejaVuSans-Bold.ttf"
        self._cache = {}

    def at(self, size, heavy=False):
        key = (size, heavy)
        if key not in self._cache:
            path = self.bold if heavy else self.regular
            self._cache[key] = ImageFont.truetype(path, size)
        return self._cache[key]


def fold(draw, text, font, width):
    """Split text into lines that fit `width`, word by word."""
    lines, current = [], ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def tracked(draw, xy, text, font, fill, step):
    """Draw text with extra space between letters (masthead kicker)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + step
    return x


def _stars(draw, cx, cy, count, spread, colour):
    for i in range(count):
        ox = (i % 4) * spread - spread * 1.5
        oy = (i // 4) * spread - spread
        draw.ellipse([cx + ox - 2, cy + oy - 2, cx + ox + 2, cy + oy + 2],
                     fill=colour)


def _flag_us(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(178, 34, 52))
    for i in range(1, 7, 2):
        draw.rectangle([x, y + h * i / 7, x + w, y + h * (i + 1) / 7],
                       fill=(255, 255, 255))
    draw.rectangle([x, y, x + w * 0.42, y + h * 4 / 7], fill=(30, 58, 138))
    _stars(draw, x + w * 0.21, y + h * 2 / 7, 8, 11, (255, 255, 255))


def _flag_cn(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    draw.ellipse([x + w * 0.14, y + h * 0.16, x + w * 0.34, y + h * 0.48],
                 fill=(255, 222, 0))
    for dx, dy in ((0.55, 0.18), (0.68, 0.32), (0.66, 0.55), (0.5, 0.62)):
        draw.ellipse([x + w * dx - 3, y + h * dy - 3,
                      x + w * dx + 3, y + h * dy + 3], fill=(255, 222, 0))


def _flag_ru(draw, x, y, w, h):
    for i, colour in enumerate(((255, 255, 255), (0, 57, 166), (213, 0, 50))):
        draw.rectangle([x, y + h * i / 3, x + w, y + h * (i + 1) / 3],
                       fill=colour)


def paint_lead_art(draw, box):
    """Night skyline, three flags on poles, one round table."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=NAVY_DEEP)
    for sx, sy in ((30, 26), (120, 52), (210, 20), (300, 60), (360, 30),
                   (70, 90), (250, 100), (330, 110), (170, 70)):
        draw.ellipse([x0 + sx - 2, y0 + sy - 2, x0 + sx + 2, y0 + sy + 2],
                     fill=GOLD_SOFT)
    blocks = [(8, 150, 62, 96), (78, 128, 58, 118), (150, 158, 66, 88),
              (232, 120, 60, 126), (306, 150, 58, 96), (340, 138, 52, 108)]
    for bx, by, bw, bh in blocks:
        draw.rectangle([x0 + bx, y0 + by, x0 + bx + bw, y1 - 62],
                       fill=(38, 54, 92))
        for wy in range(by + 14, by + bh - 16, 26):
            for wx in (bx + 12, bx + bw - 20):
                draw.rectangle([x0 + wx, y0 + wy, x0 + wx + 8, y0 + wy + 10],
                               fill=GOLD_SOFT)
    draw.ellipse([x0 + 60, y1 - 72, x1 - 60, y1 - 28], fill=(146, 110, 52))
    draw.ellipse([x0 + 60, y1 - 72, x1 - 60, y1 - 48], fill=(176, 138, 72))
    flags = ((_flag_us, 36), (_flag_cn, 168), (_flag_ru, 300))
    for painter, fx in flags:
        draw.rectangle([x0 + fx + 34, y0 + 22, x0 + fx + 38, y1 - 62],
                       fill=(214, 205, 180))
        painter(draw, x0 + fx - 28, y0 + 26, 96, 58)


def paint_glyph(draw, box, kind, faces):
    """Small square emblem drawn from primitives, per card."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=NAVY)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if kind == "bars":
        draw.text((cx, y0 + 6), "VI", font=faces.at(22, heavy=True),
                  fill=(255, 255, 255), anchor="ma")
        tops = (34, 26, 30, 20)
        for i, top in enumerate(tops):
            bx = x0 + 10 + i * 15
            draw.rectangle([bx, y1 - 10 - top, bx + 11, y1 - 10],
                           fill=GOLD)
    elif kind == "dish":
        for sx, sy in ((14, 12), (34, 22), (58, 10), (70, 28)):
            draw.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1],
                         fill=(255, 255, 255))
        draw.line([cx - 6, cy + 26, cx + 26, cy - 22], fill=(255, 255, 255),
                  width=3)
        draw.polygon([(cx - 26, cy + 26), (cx + 6, cy + 26), (cx - 10, cy - 2)],
                     outline=GOLD, width=3)
    elif kind == "swirl":
        for r in (30, 22, 14):
            draw.arc([cx - r, cy - r, cx + r, cy + r], 20, 300,
                     fill=(255, 255, 255), width=3)
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=GOLD)
        for rx in (18, 40, 62):
            draw.line([x0 + rx, y1 - 16, x0 + rx - 5, y1 - 6],
                      fill=(140, 190, 220), width=2)
    elif kind == "target":
        for r in (30, 21, 12):
            draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                         outline=(255, 255, 255), width=3)
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=CRIMSON)
        draw.line([cx + 4, cy - 4, cx + 26, cy - 26], fill=GOLD, width=3)


def paint_masthead(draw, faces):
    draw.rectangle([0, 0, CANVAS[0], 148], fill=NAVY)
    tracked(draw, (MARGIN, 26), EDITION["kicker"], faces.at(26, heavy=True),
            GOLD, 7)
    draw.text((MARGIN, 58), EDITION["dateline"],
              font=faces.at(52, heavy=True), fill=(255, 255, 255))
    draw.rectangle([0, 148, CANVAS[0], 154], fill=GOLD)


def paint_lead(draw, faces):
    top = 182
    art = (584, top, CANVAS[0] - MARGIN, top + 268)
    paint_lead_art(draw, art)
    text_w = 584 - MARGIN - 28
    draw.text((MARGIN, top), EDITION["lead"]["tag"],
              font=faces.at(21, heavy=True), fill=CRIMSON)
    y = top + 38
    for line in fold(draw, EDITION["lead"]["headline"],
                     faces.at(40, heavy=True), text_w):
        draw.text((MARGIN, y), line, font=faces.at(40, heavy=True), fill=INK)
        y += 48
    y += 8
    for line in fold(draw, EDITION["lead"]["body"], faces.at(21), text_w):
        draw.text((MARGIN, y), line, font=faces.at(21), fill=BODY)
        y += 29
    draw.line([MARGIN, 486, CANVAS[0] - MARGIN, 486], fill=RULE, width=2)


def paint_card(draw, faces, item, box):
    """Icon + tag + headline up top, body text full-width underneath."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=CARD, outline=CARD_EDGE, width=2)
    draw.rectangle([x0, y0, x1, y0 + 7], fill=TEAL)
    icon = (x0 + 16, y0 + 16, x0 + 92, y0 + 92)
    paint_glyph(draw, icon, item["glyph"], faces)
    tx = x0 + 108
    tw = x1 - tx - 16
    draw.text((tx, y0 + 18), item["tag"], font=faces.at(17, heavy=True),
              fill=CRIMSON)
    y = y0 + 42
    for line in fold(draw, item["headline"], faces.at(24, heavy=True), tw):
        draw.text((tx, y), line, font=faces.at(24, heavy=True), fill=INK)
        y += 29
    by = y0 + 104
    for line in fold(draw, item["body"], faces.at(18),
                     x1 - x0 - 32):
        draw.text((x0 + 16, by), line, font=faces.at(18), fill=BODY)
        by += 24


def paint_grid(draw, faces):
    cw = (CANVAS[0] - 2 * MARGIN - GUTTER) // 2
    ch = 168
    top = 500
    for i, item in enumerate(EDITION["cards"]):
        col, row = i % 2, i // 2
        x0 = MARGIN + col * (cw + GUTTER)
        y0 = top + row * (ch + 14)
        paint_card(draw, faces, item, (x0, y0, x0 + cw, y0 + ch))


def paint_also(draw, faces):
    y0, y1 = 862, 960
    draw.rectangle([MARGIN, y0, CANVAS[0] - MARGIN, y1], fill=NAVY)
    draw.text((MARGIN + 18, y0 + 12), "ALSO TODAY",
              font=faces.at(22, heavy=True), fill=GOLD)
    col_w = (CANVAS[0] - 2 * MARGIN - 36 - GUTTER) // 2
    for i, entry in enumerate(EDITION["also"]):
        col, row = i % 2, i // 2
        x = MARGIN + 18 + col * (col_w + GUTTER)
        y = y0 + 46 + row * 28
        draw.text((x, y), "\u00b7", font=faces.at(19, heavy=True),
                  fill=GOLD_SOFT)
        draw.text((x + 16, y), entry, font=faces.at(18), fill=(255, 255, 255))


def paint_footer(draw, faces):
    draw.text((MARGIN, 974), EDITION["footer"], font=faces.at(17),
              fill=MUTED)


def compose(assets_dir):
    """Build the whole poster and hand back a PIL image."""
    faces = Typefaces(assets_dir)
    sheet = Image.new("RGB", CANVAS, PAPER)
    draw = ImageDraw.Draw(sheet)
    paint_masthead(draw, faces)
    paint_lead(draw, faces)
    paint_grid(draw, faces)
    paint_also(draw, faces)
    paint_footer(draw, faces)
    return sheet
