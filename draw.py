"""Draw the 19 November 2026 world-news poster (1024x1024 PNG).

Pure PIL, deterministic: same input, same bytes, every run. No network,
no clock, no randomness. Fonts are bundled in assets/ so the program
renders identically in any sandbox.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

W = H = 1024

PAPER = (247, 243, 234)
INK = (22, 22, 26)
NAVY = (27, 42, 65)
NAVY2 = (18, 30, 48)
GOLD = (201, 162, 39)
RED = (166, 38, 57)
MUTED = (96, 92, 84)
BODY = (56, 54, 50)
CARD_BG = (255, 255, 255)
TEAL = (31, 111, 107)
SKY = (52, 84, 120)


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = os.path.join(ASSETS, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, lines, fnt, fill, leading):
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def flag(d, x, y, w, h, kind):
    """A small national flag: usa, china or russia."""
    if kind == "usa":
        for i in range(7):
            col = (178, 34, 52) if i % 2 == 0 else (255, 255, 255)
            d.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7], fill=col)
        d.rectangle([x, y, x + w * 2 // 5, y + h * 4 // 7], fill=(60, 59, 110))
        for r in range(3):
            for c in range(3):
                d.ellipse([x + 5 + c * 11, y + 5 + r * 11, x + 9 + c * 11, y + 9 + r * 11],
                          fill=(255, 255, 255))
    elif kind == "china":
        d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
        d.ellipse([x + 8, y + 8, x + 22, y + 22], fill=(255, 222, 0))
        for sx, sy in [(34, 10), (42, 18), (42, 28), (34, 34)]:
            d.ellipse([x + sx, y + sy, x + sx + 6, y + sy + 6], fill=(255, 222, 0))
    else:  # russia
        d.rectangle([x, y, x + w, y + h // 3], fill=(255, 255, 255))
        d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=(0, 57, 166))
        d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(213, 0, 50))


def draw_summit(d, x0, y0, x1, y1):
    """Three flags over a conference table, Shenzhen dusk."""
    d.rectangle([x0, y0, x1, y1], fill=NAVY2)
    # stars
    for sx, sy in [(x0 + 30, y0 + 26), (x0 + 90, y0 + 52), (x0 + 180, y0 + 22),
                   (x0 + 250, y0 + 58), (x0 + 320, y0 + 30)]:
        d.ellipse([sx, sy, sx + 4, sy + 4], fill=GOLD)
    # flag poles
    fw, fh = 84, 56
    for i, kind in enumerate(["usa", "china", "russia"]):
        fx = x0 + 36 + i * 118
        d.rectangle([fx + fw // 2 - 2, y0 + 30, fx + fw // 2 + 2, y0 + 30 + fh + 74], fill=(200, 190, 160))
        flag(d, fx, y0 + 36, fw, fh, kind)
    # skyline silhouette
    base = y1 - 62
    for tx, th, tw in [(x0 + 8, 44, 34), (x0 + 52, 70, 30), (x0 + 92, 50, 38),
                       (x0 + 140, 82, 32), (x0 + 182, 56, 36), (x0 + 228, 74, 30),
                       (x0 + 268, 48, 34), (x0 + 312, 66, 30)]:
        d.rectangle([tx, base - th, tx + tw, base], fill=(38, 54, 78))
        for wy in range(base - th + 10, base - 8, 16):
            d.rectangle([tx + 6, wy, tx + 12, wy + 6], fill=GOLD)
    # table
    d.rectangle([x0, base, x1, y1], fill=(24, 38, 58))
    d.ellipse([x0 + 52, base - 14, x1 - 52, base + 26], fill=(120, 92, 52))
    d.ellipse([x0 + 62, base - 10, x1 - 62, base + 18], fill=(150, 118, 66))


def icon(d, x, y, kind):
    """A small square glyph for a story card."""
    d.rectangle([x, y, x + 84, y + 84], fill=NAVY)
    if kind == "gta":
        # skyline + big VI
        for tx, th, tw in [(x + 10, 20, 12), (x + 28, 28, 12), (x + 46, 16, 12), (x + 64, 24, 10)]:
            d.rectangle([tx, y + 78 - th, tx + tw, y + 78], fill=GOLD)
        d.text((x + 14, y + 4), "VI", font=font(30, bold=True), fill=(255, 255, 255))
    elif kind == "voyager":
        for sx, sy in [(x + 12, y + 14), (x + 30, y + 8), (x + 58, y + 16), (x + 70, y + 34), (x + 20, y + 30)]:
            d.ellipse([sx, sy, sx + 3, sy + 3], fill=(255, 255, 255))
        d.polygon([(x + 20, y + 70), (x + 46, y + 38), (x + 64, y + 66)], outline=GOLD, width=3)
        d.line([x + 42, y + 52, x + 42, y + 76], fill=GOLD, width=3)
        d.line([x + 42, y + 52, x + 70, y + 20], fill=(255, 255, 255), width=2)
    elif kind == "cyclone":
        cx, cy = x + 42, y + 42
        for r in (30, 22, 14):
            d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=(255, 255, 255), width=4)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=GOLD)
        for rx in (x + 14, x + 34, x + 54):
            d.line([rx, y + 72, rx - 4, y + 80], fill=(140, 190, 220), width=3)
    else:  # gulf: radar rings + signal
        cx, cy = x + 42, y + 42
        for r in (30, 20, 10):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=2)
        d.line([cx, cy, cx + 24, cy - 18], fill=GOLD, width=3)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)


def draw_card(d, x, y, w, h, kicker, headline, body, glyph):
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=(208, 202, 188), width=2)
    d.rectangle([x, y, x + w, y + 6], fill=TEAL)
    icon(d, x + 16, y + 20, glyph)
    tx = x + 116
    tw = w - 132
    d.text((tx, y + 16), kicker, font=font(17, bold=True), fill=RED)
    hl = wrap(d, headline, font(24, bold=True), tw)
    yy = text_block(d, tx, y + 40, hl[:2], font(24, bold=True), INK, 29)
    bl = wrap(d, body, font(18), tw)
    text_block(d, tx, yy + 6, bl[:3], font(18), BODY, 23)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 140], fill=NAVY)
    d.text((40, 24), "T H E   W O R L D   I N   O N E   D A Y", font=font(21, bold=True), fill=GOLD)
    d.text((40, 56), "THURSDAY, 19 NOVEMBER 2026", font=font(50, bold=True), fill=(255, 255, 255))
    d.rectangle([0, 136, W, 140], fill=GOLD)

    # ---- lead story: trilateral summit in Shenzhen ----
    d.text((40, 162), "SHENZHEN  ·  APEC SUMMIT", font=font(20, bold=True), fill=RED)
    lead_head = wrap(d, "Three presidents, one table in Shenzhen", font(38, bold=True), 560)
    text_block(d, 40, 192, lead_head, font(38, bold=True), INK, 46)
    lead_body = wrap(
        d,
        "Trump, Xi and Putin meet together for the first time, with an "
        "hour set aside for nuclear arms, Ukraine, Iran and trade. "
        "No deal is expected to be announced.",
        font(22), 560)
    text_block(d, 40, 192 + len(lead_head) * 46 + 12, lead_body, font(22), BODY, 29)
    draw_summit(d, 624, 162, 984, 440)

    d.line([40, 462, 984, 462], fill=(200, 192, 176), width=2)

    # ---- four more stories ----
    cards = [
        ("GAMES  ·  CULTURE",
         "GTA VI rolls out around the world",
         "After 13 years, Rockstar's game unlocks at midnight in each "
         "market, starting in New Zealand.",
         "gta"),
        ("SPACE  ·  SCIENCE",
         "NASA confirms Voyager 1 is a light-day away",
         "Launched in 1977, it is the first human-made object 16 billion "
         "miles out. A signal takes a full day.",
         "voyager"),
        ("WEATHER  ·  INDIA",
         "Cyclone Akvan bears down on India's east coast",
         "A very severe cyclone nears India's coast, winds of 120-130 "
         "km/h at landfall due Friday.",
         "cyclone"),
        ("MIDDLE EAST  ·  GULF WAR",
         "Iran widens its attacks on US bases in the Gulf",
         "Tehran's drones hit a US base in Kuwait and sites in Bahrain. "
         "No US staff hurt.",
         "gulf"),
    ]
    cw, ch = 462, 182
    positions = [(40, 482), (522, 482), (40, 676), (522, 676)]
    for (kicker, head, body, glyph), (cx, cy) in zip(cards, positions):
        draw_card(d, cx, cy, cw, ch, kicker, head, body, glyph)

    # ---- also today ----
    d.rectangle([40, 878, 984, 972], fill=NAVY)
    d.text((60, 890), "ALSO TODAY", font=font(20, bold=True), fill=GOLD)
    also_left = [
        "Pew: Islam to be the largest faith by 2035",
        "Earth's missing billion years may be solved",
    ]
    also_right = [
        "Canada's Carney recalibrates China ties",
        "US senators warn on AI cyber threats",
    ]
    yy = 922
    for line in also_left:
        d.text((60, yy), "·  " + line, font=font(17), fill=(235, 232, 224))
        yy += 26
    yy = 922
    for line in also_right:
        d.text((522, yy), "·  " + line, font=font(17), fill=(235, 232, 224))
        yy += 26

    d.text((40, 986), "All stories as reported on 19 November 2026  ·  Sources: Reuters, AP, NASA, IMD, Pew, Space.com",
           font=font(15), fill=MUTED)
    return img


def main():
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = render()
    img.save(out, "PNG")
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
