"""News image entry v2: Thursday, 19 November 2026.

Draws a 1024x1024 newspaper-style front page summing up the day's world
news in one image and writes it to $MAKEFUN_OUTPUT_DIR/entry.png
(default "out").

Forty verified stories from seven continents, laid out as a four-column
story grid under colour-coded continent sections, with a dotted world map
beside the masthead.

Everything here is hand-written in this session, Python 3.13 standard
library only: a from-scratch PNG encoder (struct + zlib), a software
rasterizer (rectangles, lines, circles, triangles), and a hand-drawn 5x7
bitmap font. No images, no network, no randomness, no timestamps in the
output, so two runs produce byte-identical files.
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette ---
PAPER = (246, 241, 227)   # warm newsprint
CARD = (253, 251, 244)    # story cell background
INK = (26, 26, 26)
RED = (176, 42, 48)
NAVY = (22, 50, 79)
BLUE = (52, 96, 158)
GOLD = (200, 155, 60)
TEAL = (46, 125, 107)
ORANGE = (224, 122, 42)
GREEN = (74, 124, 64)
PURPLE = (110, 70, 150)
GREY = (120, 116, 104)
LIGHT = (232, 226, 210)   # hairline / section divider
WHITE = (255, 255, 255)

# ------------------------------------------------------------- bitmap font --
# Hand-drawn 5x7 glyphs, '1' = ink, '.' = empty. Uppercase + digits + marks.
# Every glyph is my own drawing of the letterform at this size.
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
    """An RGB pixel buffer with primitive drawing operations."""

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
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

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
            if abs(dy) > r:
                continue
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, yy, dx * 2 + 1, 1, c)

    # ---------------------------------------------------------------- text --
    def draw_char(self, x, y, ch, scale, c):
        glyph = FONT.get(ch.upper(), FONT[' '])
        for r, row in enumerate(glyph):
            for col, bit in enumerate(row):
                if bit == '1':
                    self.fill_rect(x + col * scale, y + r * scale,
                                   scale, scale, c)

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale if s else 0

    def draw_text(self, x, y, s, scale, c):
        for i, ch in enumerate(s):
            self.draw_char(x + i * 6 * scale, y, ch, scale, c)

    def draw_text_center(self, cx, y, s, scale, c):
        self.draw_text(cx - self.text_width(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, max_w, scale):
        """Greedy word wrap; returns a list of lines fitting max_w."""
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

# ------------------------------------------------------------- world map ---
# Dotted world map, drawn from a hand-sketched land grid. Each entry is
# (row, [(col_start, col_end), ...]) with inclusive column ranges on a
# 48-column by 14-row grid; a dot is drawn for every land cell.
MAP_LAND = [
    (1, [(1, 11), (13, 15), (23, 26), (30, 46)]),
    (2, [(1, 11), (13, 14), (23, 28), (29, 46)]),
    (3, [(2, 10), (24, 27), (29, 31), (32, 45)]),
    (4, [(3, 9), (23, 29), (31, 43)]),
    (5, [(4, 7), (23, 30), (32, 41)]),
    (6, [(7, 12), (24, 29), (37, 42)]),
    (7, [(7, 12), (24, 28)]),
    (8, [(8, 11), (25, 27)]),
    (9, [(8, 11), (39, 45)]),
    (10, [(9, 10), (40, 44)]),
    (11, [(9, 9), (46, 47)]),
    (12, [(46, 46)]),
    (13, [(4, 4), (10, 10), (16, 16), (22, 22),
          (28, 28), (34, 34), (40, 40), (46, 46)]),
]
MAP_COLS, MAP_ROWS = 48, 14
MAP_DX, MAP_DY = 6, 6  # dot spacing in pixels


def draw_map(cv, x0, y0, color):
    for row, spans in MAP_LAND:
        for a, b in spans:
            for col in range(a, b + 1):
                cx = x0 + col * MAP_DX + MAP_DX // 2
                cy = y0 + row * MAP_DY + MAP_DY // 2
                cv.circle(cx, cy, 2, color)


# ------------------------------------------------------------------ data ---
# Each story: (headline, summary, outlet). Headlines carry their number as a
# "NN " prefix and are kept short so they wrap to at most two lines at
# scale 2 in a 232 px cell; summaries are capped at 76 characters so they
# wrap to at most two lines at scale 1.
#
# Sections: (name, accent colour, [story indices]) — story order is global
# 01..40, grouped by continent.
SECTIONS = [
    ("ASIA", RED, 11),
    ("EUROPE", BLUE, 8),
    ("NORTH AMERICA", NAVY, 6),
    ("AFRICA", ORANGE, 5),
    ("SOUTH AMERICA", GREEN, 4),
    ("OCEANIA", TEAL, 4),
    ("ANTARCTICA", PURPLE, 2),
]

STORIES = [
    # Asia (11)
    ("01 TRUMP, XI, PUTIN SIGN PEACE", "First three-way summit in Shenzhen agrees nuclear-risk, UN-reform text.", "BBC"),
    ("02 IRAN HITS KUWAIT, BAHRAIN", "Tehran widens attacks as Hormuz fight spreads after US strikes on Qeshm.", "WALL STREET JOURNAL"),
    ("03 HOUTHI MISSILE HITS RIYADH", "Missile damages Saudi wealth-fund tower; no injuries reported.", "SKY NEWS"),
    ("04 COP31 DROPS FOSSIL PLEDGE", "COP31 draft drops fossil-fuel phase-out, keeps 35% clean target.", "UN NEWS"),
    ("05 CYCLONE AKVAN NEARS INDIA", "Storm 440 km off Andhra coast, winds 90-100 km/h; landfall due Friday.", "INDIA MET DEPT"),
    ("06 PAKISTAN RAIDS KILL 22", "Army kills 22 in 48-hour raids on hideouts in South Waziristan.", "TBS NEWS"),
    ("07 BANGLADESH LOCKDOWN, ARSON", "Awami League lockdown: 2 killed, Yunus home torched, 97 guard platoons out.", "REUTERS"),
    ("08 TAIWAN STOCKS CRASH 4.4%", "Index plunges 1,768 points to 38,427; TSMC falls 3.45% to NT$2,100.", "GLOBAL BANKING & FINANCE"),
    ("09 MONGOLIA OUSTS PRESIDENT", "Parliament votes to remove Khurelsukh over $25m railway bribe claims.", "GOGO MONGOLIA"),
    ("10 INDONESIA PASSES SEIZURE LAW", "State can now seize corruption-linked assets without a conviction.", "REUTERS"),
    ("11 DELHI SMOG REBOUNDS, AQI 282", "Delhi AQI jumps to 282, up 67 in a day; Pusa station worst at 361.", "ECONOMIC TIMES"),
    # Europe (8)
    ("12 KERCH BRIDGE HIT THIRD TIME", "Ukraine hits Crimea bridge third time in four days; rail traffic halted.", "BBC"),
    ("13 WORLD COURT: MYANMAR GUILTY", "ICJ rules 9-6 on Rohingya; first genocide verdict against a state.", "BBC"),
    ("14 ALLIES MEET IN BERLIN", "30+ leaders in Berlin, Zelenskyy joins; Europe ready for Russia talks.", "NATO"),
    ("15 MONTENEGRO CLOSES EU CHAPTERS", "EU, Montenegro close chapters 16 and 22; 25 of 33 closed, 2028 entry eyed.", "COUNCIL OF THE EU"),
    ("16 DUTCH: DON'T BUY SMART GLASSES", "Dutch watchdog studied 6 AI glasses, warns not to buy; unsafe for users.", "REUTERS"),
    ("17 STORM FLOODS BOSNIA", "Storm floods Bosnia, Montenegro; 80 l/m2 rain in Gacko, gusts 76 km/h.", "ALLATRA"),
    ("18 GTA 6 LAUNCHES, 17M SOLD", "Launches at midnight; 17m copies, $1.65bn by Thursday morning.", "STOCKTWITS"),
    ("19 BARCELONA THRASH SERVETTE 6-0", "UWCL: Barcelona beat Servette 6-0; Arsenal lose 0-2 to Lyon.", "UEFA"),
    # North America (6)
    ("20 ANTHROPIC IPO: RECORD $81.3B", "Priced $83 a share, valued near $1.5T; debuts on Nasdaq as ANT.", "BUSINESSWORLD"),
    ("21 VAN GOGH SELLS FOR $190.4M", "1890 Chataigniers en fleurs sells at Sotheby's New York, artist record.", "REUTERS"),
    ("22 SENATE PASSES ENERGY BILL", "Senate passes permitting reform 62-33, speeding energy approvals.", "USA TODAY"),
    ("23 TRUMP FIRES CYBER CHIEF", "Cyber chief Cairncross fired after US tech outages; Pentagon CIO steps in.", "CNN"),
    ("24 HAITI RAID KILLS 34", "Police kill 34 alleged gang members in Martissant, Port-au-Prince.", "REUTERS"),
    ("25 FAA TO REVEAL GROUND-STOP", "FAA to announce cause of router outage that grounded 18,000+ flights.", "REUTERS"),
    # Africa (5)
    ("26 SOMALIA EXPELS UAE ENVOY", "Mogadishu orders UAE envoy out in 72 hours, recalls own envoy.", "REUTERS"),
    ("27 ZIMBABWE CLEARS 250,000 MINES", "HALO Trust destroys 250,000 mines since 2013; 4% of land still mined.", "HALO TRUST"),
    ("28 SENEGAL BOAT SINKS, DOZENS LOST", "Migrant boat with about 100 capsizes off Yenne; 1 dead, dozens missing.", "REUTERS"),
    ("29 SOUTH AFRICA HOLDS RATE 7.25%", "Reserve Bank keeps repo at 7.25% in 4-3 vote; prime stays 10.75%.", "REUTERS"),
    ("30 MARATHON CHAMP BANNED 3 YEARS", "Kenya's Peres Jepchirchir banned 3 years for EPO; Sydney win stripped.", "REUTERS"),
    # South America (4)
    ("31 BRAZIL SELLS $1BN TO DEFEND REAL", "Central bank sells $1bn as real falls 0.95% to 5.92 per dollar.", "REUTERS"),
    ("32 LULA PROTECTS RAONI LAND", "Lula declares 362,243-ha Kapot Nhinore land for Kayapo and Yudja.", "LATINNEWS"),
    ("33 COLOMBIA TAX PROTESTS", "Unions march in Bogota, Cali, Medellin vs tax bill; threshold cut to $985.", "AFP"),
    ("34 ARGENTINA HEALTH CURBS BACK", "Supreme Court voids Milei decree; prepagas need state OK for fee rises.", "PARTICLE NEWS"),
    # Oceania (4)
    ("35 FIJI DECLARES DROUGHT DISASTER", "Fiji declares 1-month disaster state; FJ$20m for water as rain stays low.", "REUTERS"),
    ("36 TONGA DROUGHT EMERGENCY 27 DAYS", "Tonga declares 27-day drought emergency; very dry Nov-Jan likely.", "AFP"),
    ("37 19 WHALES DIE IN NZ STRANDING", "24 sperm whales strand at Ninety Mile Beach; 19 dead, 5 alive, poor health.", "RNZ"),
    ("38 DARWIN PORT BUYBACK STALLS", "Landbridge denies Darwin Port sale talks; Albanese vows buyback, no date.", "SPLASH247"),
    # Antarctica (2)
    ("39 AUSTRALIA REDESIGNS ANTARCTIC", "AAD unveils 6 new science programmes from 2028-29 under Decadal Strategy.", "AUSTRALIAN ANTARCTIC PROGRAM"),
    ("40 US AIR GUARD SENDS 5 LC-130S", "109th Wing deploys 5 ski LC-130s, 75 personnel for Operation Deep Freeze.", "THE DEFENSE WATCH"),
]

# ---------------------------------------------------------------- layout ---
MARGIN = 16
COLS = 4
COL_W = 240
COL_GUT = 10
CELL_H = 60
SEC_H = 14
SEC_GAP = 0


def draw_header(cv):
    # Masthead, left; dotted map, right.
    cv.draw_text(24, 20, "THE WORLD IN ONE DAY", 4, INK)
    cv.draw_text(24, 56, "THURSDAY 19 NOVEMBER 2026", 2, RED)
    draw_map(cv, 700, 16, NAVY)
    cv.draw_text_center(700 + MAP_COLS * MAP_DX // 2, 104,
                        "WHERE IT HAPPENED", 1, GREY)
    # Stat strip.
    cv.fill_rect(MARGIN, 114, W - 2 * MARGIN, 28, NAVY)
    t1, t2 = "40 STORIES", "7 CONTINENTS"
    w1 = cv.text_width(t1, 2)
    w2 = cv.text_width(t2, 2)
    total = w1 + 10 + 8 + 10 + w2
    x = (W - total) // 2
    cv.draw_text(x, 121, t1, 2, WHITE)
    cv.fill_rect(x + w1 + 10, 128, 8, 8, GOLD)
    cv.draw_text(x + w1 + 28, 121, t2, 2, WHITE)
    cv.hline(MARGIN, 146, W - 2 * MARGIN, INK, 2)


def draw_section_header(cv, y, name, accent, count, first, last):
    cv.fill_rect(MARGIN, y, 8, SEC_H, accent)
    cv.draw_text(MARGIN + 14, y, name, 2, accent)
    right = "%d STORIES  %02d-%02d" % (count, first, last)
    cv.draw_text(W - MARGIN - cv.text_width(right, 1), y + 3, right, 1, GREY)


def draw_story(cv, x, y, headline, summary, outlet, accent):
    cv.fill_rect(x, y, COL_W, CELL_H, CARD)
    cv.rect(x, y, COL_W, CELL_H, LIGHT, 1)
    cv.fill_rect(x, y, COL_W, 3, accent)
    # Headline, scale 2, at most two lines.
    lines = cv.wrap(headline, COL_W - 10, 2)
    for i, ln in enumerate(lines[:2]):
        cv.draw_text(x + 5, y + 5 + i * 14, ln, 2, INK)
    # Summary, scale 1, at most two lines.
    slines = cv.wrap(summary, COL_W - 10, 1)
    for i, ln in enumerate(slines[:2]):
        cv.draw_text(x + 5, y + 35 + i * 8, ln, 1, INK)
    # Source tag.
    cv.draw_text(x + 5, y + CELL_H - 8, "SOURCE: " + outlet, 1, RED)


def draw(cv):
    cv.rect(8, 8, W - 16, H - 16, INK, 3)
    draw_header(cv)
    y = 152
    idx = 0
    for name, accent, count in SECTIONS:
        first = idx + 1
        last = idx + count
        draw_section_header(cv, y, name, accent, count, first, last)
        y += SEC_H + 2
        rows = (count + COLS - 1) // COLS
        for r in range(rows):
            for c in range(COLS):
                k = idx + r * COLS + c
                if k >= idx + count:
                    break
                if k >= len(STORIES):
                    break
                headline, summary, outlet = STORIES[k]
                x = MARGIN + 1 + c * (COL_W + COL_GUT)
                draw_story(cv, x, y + r * CELL_H, headline, summary,
                           outlet, accent)
            # (loop continues)
        idx += count
        y += rows * CELL_H + SEC_GAP
    # Footer.
    cv.draw_text_center(W // 2, y + 4,
                        "ALL FORTY STORIES VERIFIED AGAINST REPORTING PUBLISHED ON THURSDAY 19 NOVEMBER 2026.",
                        1, GREY)
    cv.draw_text_center(W // 2, y + 15,
                        "DRAWN BY A DETERMINISTIC PYTHON PROGRAM (STDLIB ONLY). NO PHOTOS, NO EXTERNAL DATA.",
                        1, GREY)
    print("layout height:", y + 26, "of", H)
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
    data = encode_png(draw(Canvas(W, H, PAPER)))
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()
