"""News image entry: Thursday, 19 November 2026.

Draws a 1024x1024 newspaper-style front page summing up the day's world news
and writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default "out").

Everything here is hand-written in this session, Python 3.13 standard library
only: a from-scratch PNG encoder (struct + zlib), a software rasterizer, and a
hand-drawn 5x7 bitmap font. No network, no randomness, no timestamps in the
output, so two runs produce byte-identical files.
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette ---
PAPER = (246, 241, 227)   # warm newsprint
CARD = (253, 251, 244)    # panel background
INK = (26, 26, 26)
RED = (176, 42, 48)
NAVY = (22, 50, 79)
GOLD = (200, 155, 60)
TEAL = (46, 125, 107)
ORANGE = (224, 122, 42)
BROWN = (110, 72, 32)
GREEN = (74, 124, 64)
GREY = (120, 116, 104)
BLUE = (52, 96, 158)
WHITE = (255, 255, 255)

# ------------------------------------------------------------- bitmap font --
# Hand-drawn 5x7 glyphs, '1' = ink, '0' = empty. Uppercase + digits + marks.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", "01100", "01100"),
    ',': (".....", ".....", ".....", ".....", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", ".....", ".....", ".....", "....."),
    ':': (".....", "01100", "01100", ".....", "01100", "01100", "....."),
    ';': (".....", "01100", "01100", ".....", "01100", "00100", "01000"),
    '-': (".....", ".....", ".....", "01110", ".....", ".....", "....."),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '!': ("00100", "00100", "00100", "00100", "00100", ".....", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", ".....", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': (".....", "00100", "00100", "11111", "00100", "00100", "....."),
    '=': (".....", ".....", "11111", ".....", "11111", ".....", "....."),
    '"': ("01010", "01010", "01010", ".....", ".....", ".....", "....."),
    '*': (".....", "10101", "01110", "10101", ".....", ".....", "....."),
}

# -------------------------------------------------------------- rasterizer --
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bytes(bg) * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, yy, dx * 2 + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            dy = yy - cy
            if ry == 0:
                continue
            dx = int(rx * (1 - (dy * dy) / (ry * ry)) ** 0.5)
            self.fill_rect(cx - dx, yy, dx * 2 + 1, 1, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx_, cy_) = pts
        for y in range(ay, cy_ + 1):
            if y < by:
                xa = ax + (bx - ax) * (y - ay) / (by - ay) if by != ay else ax
                xb = ax + (cx_ - ax) * (y - ay) / (cy_ - ay) if cy_ != ay else ax
            else:
                xa = bx + (cx_ - bx) * (y - by) / (cy_ - by) if cy_ != by else bx
                xb = ax + (cx_ - ax) * (y - ay) / (cy_ - ay) if cy_ != ay else ax
            lo, hi = int(min(xa, xb)), int(max(xa, xb))
            self.fill_rect(lo, y, hi - lo + 1, 1, c)

    # ---------------------------------------------------------------- text --
    def draw_char(self, x, y, ch, scale, c):
        glyph = FONT.get(ch.upper(), FONT[' '])
        for r, row in enumerate(glyph):
            for col, bit in enumerate(row):
                if bit == '1':
                    self.fill_rect(x + col * scale, y + r * scale,
                                   scale, scale, c)

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def draw_text(self, x, y, s, scale, c):
        for i, ch in enumerate(s):
            self.draw_char(x + i * 6 * scale, y, ch, scale, c)

    def draw_text_center(self, cx, y, s, scale, c):
        self.draw_text(cx - self.text_width(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, max_w, scale):
        lines, cur = [], ""
        for word in s.split(" "):
            trial = (cur + " " + word).strip()
            if self.text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# ------------------------------------------------------------------ icons --
def icon_flags(cv, cx, sy):
    """Three flags: USA, China, Russia."""
    fw, fh = 64, 40
    y = sy + 12
    # USA
    x = cx - 112
    for i in range(7):
        cv.fill_rect(x, y + i * 6, fw, 6, RED if i % 2 == 0 else WHITE)
    cv.fill_rect(x, y, 26, 22, NAVY)
    for r in range(3):
        for cc in range(4):
            cv.px(x + 3 + cc * 6, y + 4 + r * 6, WHITE)
    cv.rect(x, y, fw, fh, INK)
    # China
    x = cx - 32
    cv.fill_rect(x, y, fw, fh, RED)
    cv.circle(x + 12, y + 10, 4, GOLD)
    for dx, dy in ((26, 6), (32, 12), (32, 20), (26, 24)):
        cv.circle(x + dx, y + dy, 2, GOLD)
    cv.rect(x, y, fw, fh, INK)
    # Russia
    x = cx + 48
    cv.fill_rect(x, y, fw, 14, WHITE)
    cv.fill_rect(x, y + 14, fw, 13, BLUE)
    cv.fill_rect(x, y + 27, fw, 13, RED)
    cv.rect(x, y, fw, fh, INK)
    cv.fill_rect(cx - 112, y + fh + 6, 288, 3, GOLD)


def icon_scales(cv, cx, sy):
    """Scales of justice."""
    cy = sy + 32
    cv.line(cx, cy - 26, cx, cy + 24, NAVY, 3)
    cv.line(cx - 58, cy - 22, cx + 58, cy - 22, NAVY, 3)
    cv.circle(cx, cy - 26, 4, GOLD)
    for sgn in (-1, 1):
        bx = cx + sgn * 58
        cv.line(bx, cy - 22, bx, cy + 2, INK, 2)
        cv.triangle(bx - 18, cy + 2, bx + 18, cy + 2, bx, cy + 20, GOLD)
        cv.line(bx - 18, cy + 2, bx + 18, cy + 2, INK, 2)
    cv.line(cx - 30, cy + 24, cx + 30, cy + 24, NAVY, 3)
    cv.line(cx - 20, cy + 28, cx + 20, cy + 28, NAVY, 2)


def icon_bridge(cv, cx, sy):
    """A bridge with a crack in the middle."""
    deck = sy + 42
    cv.line(cx - 200, deck, cx - 8, deck, NAVY, 4)
    cv.line(cx + 8, deck, cx + 200, deck, NAVY, 4)
    for tx in (cx - 110, cx + 110):
        cv.line(tx, sy + 6, tx, deck, NAVY, 4)
        cv.line(tx - 4, sy + 6, tx + 4, sy + 6, NAVY, 4)
    cv.line(cx - 110, sy + 6, cx - 8, deck, GREY, 2)
    cv.line(cx + 110, sy + 6, cx + 8, deck, GREY, 2)
    cv.line(cx - 110, sy + 6, cx, deck - 2, GREY, 2)
    cv.line(cx + 110, sy + 6, cx, deck - 2, GREY, 2)
    # crack zigzag across the gap
    pts = [(cx - 8, deck - 2), (cx - 3, deck + 6), (cx + 2, deck - 4),
           (cx + 6, deck + 5), (cx + 8, deck - 2)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, 2)
    cv.line(cx - 200, deck + 10, cx + 200, deck + 10, BLUE, 2)


def icon_derrick(cv, cx, sy):
    """Oil derrick with a flame."""
    base = sy + 58
    cv.line(cx - 58, base, cx, sy + 16, INK, 3)
    cv.line(cx + 58, base, cx, sy + 16, INK, 3)
    cv.line(cx - 58, base, cx + 58, base, INK, 3)
    for yy, half in ((sy + 30, 38), (sy + 42, 24), (sy + 52, 10)):
        cv.line(cx - half, yy, cx + half, yy, INK, 2)
    # flame above the derrick
    cv.ellipse(cx, sy + 12, 13, 17, ORANGE)
    cv.ellipse(cx, sy + 14, 7, 10, GOLD)
    cv.triangle(cx - 7, sy + 2, cx + 7, sy + 2, cx, sy - 8, ORANGE)


def icon_chart(cv, cx, sy):
    """Rising bars and an arrow."""
    base = sy + 56
    cv.line(cx - 180, sy + 6, cx - 180, base, INK, 2)
    cv.line(cx - 180, base, cx + 190, base, INK, 2)
    bars = [(cx - 150, 18, TEAL), (cx - 90, 28, GOLD),
            (cx - 30, 38, NAVY), (cx + 30, 46, TEAL)]
    for bx, bh, col in bars:
        cv.fill_rect(bx, base - bh, 42, bh, col)
    cv.line(cx - 140, base - 22, cx + 150, sy + 2, RED, 4)
    cv.triangle(cx + 154, sy + 2, cx + 128, sy - 5, cx + 131, sy + 15, RED)


def icon_sunflower(cv, cx, sy):
    """A sunflower."""
    cv.line(cx, sy + 58, cx, sy + 34, GREEN, 3)
    cv.ellipse(cx - 16, sy + 48, 14, 6, GREEN)
    import math
    for k in range(8):
        ang = k * math.pi / 4
        px = cx + int(21 * math.cos(ang))
        py = sy + 22 + int(21 * math.sin(ang))
        cv.circle(px, py, 8, GOLD)
    cv.circle(cx, sy + 22, 14, BROWN)
    for dx, dy in ((-5, -4), (5, -4), (-5, 5), (5, 5), (0, 0)):
        cv.px(cx + dx, sy + 22 + dy, GOLD)


ICONS = {
    "flags": icon_flags,
    "scales": icon_scales,
    "bridge": icon_bridge,
    "derrick": icon_derrick,
    "chart": icon_chart,
    "sunflower": icon_sunflower,
}

STORIES = [
    ("SHENZHEN - CHINA", "THREE POWERS MEET",
     "TRUMP, XI AND PUTIN HOLD FIRST-EVER SUMMIT, SIGN A 'PEACE DECLARATION'.",
     "flags", NAVY),
    ("THE HAGUE", "MYANMAR GUILTY",
     "WORLD COURT FINDS MYANMAR GUILTY OF GENOCIDE AGAINST THE ROHINGYA.",
     "scales", RED),
    ("CRIMEA", "BRIDGE HIT AGAIN",
     "THIRD UKRAINIAN STRIKE IN A WEEK HALTS RAIL ON THE CRIMEA BRIDGE.",
     "bridge", NAVY),
    ("THE GULF", "GULF ATTACKS WIDEN",
     "IRAN HITS KUWAIT AND BAHRAIN AS THE FIGHT OVER HORMUZ SPREADS.",
     "derrick", RED),
    ("WALL STREET", "RECORD $81.3BN IPO",
     "ANTHROPIC RAISES A RECORD $81.3BN; SHARES START TRADING AS ANT ON NASDAQ.",
     "chart", TEAL),
    ("NEW YORK", "VAN GOGH: $190.4M",
     "VAN GOGH SELLS FOR A RECORD $190.4M AT SOTHEBY'S IN NEW YORK.",
     "sunflower", GOLD),
]


def draw_panel(cv, x, y, w, h, tag, headline, body, icon, accent):
    cv.fill_rect(x, y, w, h, CARD)
    cv.rect(x, y, w, h, INK, 2)
    cv.fill_rect(x, y, w, 6, accent)
    cv.draw_text(x + 16, y + 16, tag, 2, RED)
    ICONS[icon](cv, x + w // 2, y + 40)
    cv.draw_text(x + 16, y + 116, headline, 4, INK)
    by = y + 160
    for i, line in enumerate(cv.wrap(body, w - 32, 3)):
        cv.draw_text(x + 16, by + i * 24, line, 3, INK)


def draw():
    cv = Canvas(W, H, PAPER)
    cv.rect(8, 8, W - 16, H - 16, INK, 3)
    # header
    cv.draw_text_center(W // 2, 30, "THE WORLD IN ONE IMAGE", 2, RED)
    cv.draw_text_center(W // 2, 56, "THURSDAY, 19 NOVEMBER 2026", 6, INK)
    cv.fill_rect(120, 116, W - 240, 3, RED)
    cv.draw_text_center(W // 2, 130, "SIX STORIES THAT DEFINED THE DAY", 2, NAVY)
    # grid: 2 columns x 3 rows
    pw, ph, gap = 484, 257, 16
    gx, gy = 20, 164
    for i, (tag, head, body, icon, accent) in enumerate(STORIES):
        px = gx + (i % 2) * (pw + gap)
        py = gy + (i // 2) * (ph + gap)
        draw_panel(cv, px, py, pw, ph, tag, head, body, icon, accent)
    # footer
    cv.draw_text_center(W // 2, 980,
                        "SOURCES: REUTERS - AP - USA TODAY - THE TIMES - WSJ - NYT",
                        2, GREY)
    return cv


# ------------------------------------------------------------ PNG encoder --
def chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    out += struct.pack(">I", binascii.crc32(ctype + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        start = y * cv.w * 3
        raw += cv.buf[start:start + cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(draw())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()
