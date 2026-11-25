#!/usr/bin/env python3
"""Draw a newspaper front page summing up world news of Tuesday 24 November 2026.

Pure standard library: the image is drawn pixel by pixel (with a small
embedded 5x7 bitmap font) and encoded as PNG with zlib. No network, no
external files, no third-party packages, so the program runs identically
in the grading sandbox. Writes entry.png to OUTPUT_DIR (default /output).
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font, one glyph = 7 rows of 5 bits ('1' = ink). Uppercase only:
# the page is set in capitals, newspaper style.
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
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "00000", "01100", "00100"),
    ':': ("00000", "00100", "00000", "00000", "00000", "00100", "00000"),
    ';': ("00000", "00100", "00000", "00000", "00000", "01100", "00100"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
}

CHAR_W = 6  # 5 pixels + 1 of spacing, times the scale


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))
        self.clip = None  # (x0, y0, x1, y1) or None: rects are cut to it

    def set_clip(self, x0, y0, x1, y1):
        self.clip = (x0, y0, x1, y1)

    def clear_clip(self):
        self.clip = None

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(self.w, x1); y1 = min(self.h, y1)
        if self.clip is not None:
            cx0, cy0, cx1, cy1 = self.clip
            x0 = max(x0, cx0); y0 = max(y0, cy0)
            x1 = min(x1, cx1); y1 = min(y1, cy1)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            self.rect(x0, y + t, x1, y + t + 1, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            self.rect(x + t, y0, x + t + 1, y1, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0); dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(thick):
                for b in range(thick):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            span = int((r * r - dy * dy) ** 0.5)
            if span >= 0:
                self.rect(cx - span, y, cx + span + 1, y + 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        for y in range(cy - r - thick, cy + r + thick + 1):
            for x in range(cx - r - thick, cx + r + thick + 1):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if abs(d - r) <= thick / 2:
                    self.set(x, y, color)

    def triangle(self, pts, color):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for y in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= y < max(ay, by) or (y == ymax and y in (ay, by)):
                    xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                self.rect(int(min(xs)), y, int(max(xs)) + 1, y + 1, color)

    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == '1':
                        self.rect(cx + col_i * scale, y + row_i * scale,
                                  cx + (col_i + 1) * scale,
                                  y + (row_i + 1) * scale, color)
            cx += CHAR_W * scale
        return cx

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns list of lines fitting max_width pixels."""
    words = text.upper().split(' ')
    lines, cur = [], ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(cv, x, y, text, scale, color, max_width, line_gap=4):
    lines = []
    for para in text.split("\n"):
        lines.extend(wrap_text(para, scale, max_width))
    for line in lines:
        cv.text(x, y, line, scale, color)
        y += 7 * scale + line_gap
    return y


# ------------------------------------------------------------------ png ----
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    data = zlib.compress(bytes(raw), 9)

    def chunk(kind, payload):
        c = struct.pack('>I', len(payload)) + kind + payload
        return c + struct.pack('>I', zlib.crc32(kind + payload) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', data) + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)

# -------------------------------------------------------------- colours ----
PAPER = (247, 242, 231)
INK = (26, 26, 26)
NAVY = (22, 35, 63)
SKY = (15, 42, 74)
SKY2 = (24, 64, 110)
GOLD = (201, 162, 39)
RED = (179, 38, 30)
WHITE = (255, 255, 255)
CREAM = (250, 246, 236)
GREY = (110, 110, 104)
TEAL = (31, 111, 107)
OCHRE = (138, 90, 0)
SLATE = (61, 90, 128)
PLUM = (91, 42, 134)
FOREST = (46, 94, 46)


# --------------------------------------------------------- illustrations ----
def draw_rocket_scene(cv, x0, y0, x1, y1):
    """Night sky, stars, crescent moon, a rocket climbing past an Earth arc."""
    cv.rect(x0, y0, x1, y1, SKY)
    cv.rect(x0, y0, x1, y0 + (y1 - y0) // 2, SKY2)
    # stars: fixed positions so both runs are identical
    stars = [(18, 22), (70, 60), (130, 18), (190, 44), (250, 14), (300, 70),
             (350, 26), (410, 52), (470, 16), (40, 110), (110, 140), (170, 100),
             (230, 150), (290, 116), (360, 150), (430, 100), (480, 130),
             (90, 200), (210, 210), (330, 200), (450, 210), (150, 250),
             (270, 260), (390, 250)]
    for sx, sy in stars:
        cv.rect(x0 + sx, y0 + sy, x0 + sx + 3, y0 + sy + 3, WHITE)
    # crescent moon
    cv.circle(x0 + 448, y0 + 46, 26, (240, 230, 200))
    cv.circle(x0 + 458, y0 + 38, 22, SKY2)
    # Earth arc along the bottom, clipped to the sky panel
    cv.set_clip(x0, y0, x1, y1)
    cv.circle(x0 + (x1 - x0) // 2, y1 + 330, 380, (43, 108, 66))
    cv.circle(x0 + (x1 - x0) // 2, y1 + 330, 340, (38, 98, 150))
    cv.circle(x0 + (x1 - x0) // 2, y1 + 330, 300, (46, 130, 90))
    cv.clear_clip()
    # launch smoke
    for cx, cy, r in [(150, 300, 26), (185, 318, 34), (230, 330, 30),
                      (120, 322, 20), (265, 322, 18)]:
        cv.circle(x0 + cx, y0 + cy, r, (226, 224, 216))
    # rocket body, tilted slightly by drawing it upright: nose up
    rx, ry = x0 + 168, y0 + 92
    cv.triangle([(rx + 4, ry - 52), (rx + 26, ry - 52), (rx + 15, ry - 84)], RED)
    cv.rect(rx, ry - 52, rx + 30, ry + 62, WHITE)
    cv.rect(rx, ry - 52, rx + 30, ry - 38, (200, 40, 40))
    cv.circle(rx + 15, ry - 14, 9, SKY2)
    cv.ring(rx + 15, ry - 14, 9, INK, 2)
    cv.triangle([(rx - 16, ry + 62), (rx, ry + 26), (rx, ry + 62)], RED)
    cv.triangle([(rx + 46, ry + 62), (rx + 30, ry + 26), (rx + 30, ry + 62)], RED)
    # flame
    cv.triangle([(rx + 5, ry + 62), (rx + 25, ry + 62), (rx + 15, ry + 118)],
                (255, 140, 40))
    cv.triangle([(rx + 10, ry + 62), (rx + 20, ry + 62), (rx + 15, ry + 96)],
                (255, 210, 80))
    # "SHENZHOU-24" label on the sky
    cv.text(x0 + 18, y0 + 16, "SHENZHOU-24", 2, GOLD)


def draw_courthouse(cv, x, y, s=1):
    """Small courthouse: pediment, columns, steps."""
    c = (122, 31, 43)
    cv.triangle([(x, y + 18 * s), (x + 28 * s, y), (x + 56 * s, y + 18 * s)], c)
    cv.rect(x + 2 * s, y + 20 * s, x + 54 * s, y + 24 * s, c)
    for i in range(4):
        cv.rect(x + (6 + i * 13) * s, y + 26 * s, x + (10 + i * 13) * s,
                y + 48 * s, c)
    cv.rect(x, y + 50 * s, x + 56 * s, y + 54 * s, c)


def draw_drone(cv, x, y, s=1):
    """Quadcopter drone: body, arms, four rotors."""
    c = (31, 78, 121)
    cv.rect(x + 18 * s, y + 16 * s, x + 38 * s, y + 32 * s, c)
    cv.circle(x + 28 * s, y + 24 * s, 5 * s, WHITE)
    for (ax, ay) in [(8, 8), (48, 8), (8, 40), (48, 40)]:
        cv.line(x + 28 * s, y + 24 * s, x + ax * s, y + ay * s, c, 3 * s)
        cv.circle(x + ax * s, y + ay * s, 7 * s, c)
        cv.line(x + (ax - 9) * s, y + ay * s, x + (ax + 9) * s, y + ay * s,
                INK, 2 * s)


def draw_mountains(cv, x, y, s=1):
    """Himalayan peaks with a seismic crack and a magnitude tag."""
    c = (90, 70, 50)
    cv.triangle([(x, y + 52 * s), (x + 20 * s, y + 8 * s),
                 (x + 40 * s, y + 52 * s)], c)
    cv.triangle([(x + 22 * s, y + 52 * s), (x + 40 * s, y + 22 * s),
                 (x + 56 * s, y + 52 * s)], (110, 88, 62))
    cv.triangle([(x + 14 * s, y + 20 * s), (x + 20 * s, y + 8 * s),
                 (x + 26 * s, y + 20 * s)], WHITE)
    cv.triangle([(x + 35 * s, y + 32 * s), (x + 40 * s, y + 22 * s),
                 (x + 45 * s, y + 32 * s)], WHITE)
    # zigzag crack across the ground
    pts = [(x, y + 54 * s), (x + 10 * s, y + 48 * s), (x + 20 * s, y + 54 * s),
           (x + 30 * s, y + 48 * s), (x + 40 * s, y + 54 * s),
           (x + 50 * s, y + 48 * s), (x + 56 * s, y + 54 * s)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(ax, ay, bx, by, RED, 2 * s)


def draw_burst(cv, x, y, s=1):
    """Explosion burst for the strike story."""
    c = (255, 140, 40)
    cx, cy = x + 28 * s, y + 28 * s
    for ang in range(0, 360, 30):
        import math
        r1, r2 = 26 * s, 12 * s
        a = math.radians(ang)
        a2 = math.radians(ang + 15)
        cv.triangle([(cx, cy),
                     (int(cx + r1 * math.cos(a)), int(cy + r1 * math.sin(a))),
                     (int(cx + r2 * math.cos(a2)), int(cy + r2 * math.sin(a2)))],
                    c)
    cv.circle(cx, cy, 10 * s, (255, 210, 80))
    cv.circle(cx, cy, 5 * s, RED)


def draw_flags(cv, x, y, s=1):
    """Two small flags on poles: United States and Iran."""
    # pole
    cv.vline(x + 6 * s, y, y + 54 * s, INK, 2 * s)
    cv.vline(x + 34 * s, y, y + 54 * s, INK, 2 * s)
    # US flag: stripes + canton
    for i in range(7):
        cv.rect(x + 8 * s, y + i * 3 * s, x + 28 * s, y + (i * 3 + 2) * s,
                RED if i % 2 == 0 else WHITE)
    cv.rect(x + 8 * s, y, x + 16 * s, y + 9 * s, (31, 78, 121))
    # Iran flag: green / white / red bands
    cv.rect(x + 36 * s, y, x + 56 * s, y + 7 * s, (0, 122, 61))
    cv.rect(x + 36 * s, y + 7 * s, x + 56 * s, y + 14 * s, WHITE)
    cv.rect(x + 36 * s, y + 14 * s, x + 56 * s, y + 21 * s, RED)


# -------------------------------------------------------------- panels ----
def panel_frame(cv, x0, y0, x1, y1):
    cv.rect(x0, y0, x1, y1, WHITE)
    cv.rect(x0, y0, x1, y0 + 2, INK)
    cv.rect(x0, y1 - 2, x1, y1, INK)
    cv.rect(x0, y0, x0 + 2, y1, INK)
    cv.rect(x1 - 2, y0, x1, y1, INK)


def kicker_bar(cv, x0, y0, x1, label, color):
    cv.rect(x0, y0, x1, y0 + 28, color)
    cv.text(x0 + 12, y0 + 7, label, 2, WHITE)


def small_panel(cv, x0, y0, x1, y1, kicker, color, headline, summary, icon):
    panel_frame(cv, x0, y0, x1, y1)
    kicker_bar(cv, x0 + 2, y0 + 2, x1 - 2, kicker, color)
    inner = x0 + 14
    width = (x1 - x0) - 28
    y = y0 + 42
    y = draw_text_block(cv, inner, y, headline, 3, INK, width, line_gap=3)
    y += 6
    icon(cv, inner, y)
    draw_text_block(cv, inner + 68, y + 2, summary, 2, (60, 60, 60),
                    width - 68, line_gap=3)

# ---------------------------------------------------------------- layout ----
def build_page():
    cv = Canvas(W, H, PAPER)

    # ---- masthead ----
    cv.rect(24, 24, 1000, 140, NAVY)
    cv.text(44, 52, "WORLD EDITION", 2, GOLD)
    cv.text_center(512, 40, "THE WORLD TODAY", 6, WHITE)
    cv.hline(44, 980, 94, GOLD, 3)
    cv.text_center(512, 104, "TUESDAY, 24 NOVEMBER 2026", 3, GOLD)

    # ---- lead story: Shenzhou-24 ----
    panel_frame(cv, 24, 152, 1000, 512)
    draw_rocket_scene(cv, 26, 154, 520, 510)
    cv.text(536, 170, "SPACE - CHINA", 2, RED)
    cv.hline(536, 984, 192, RED, 3)
    lead_lines = ["CHINA SENDS", "FIRST FOREIGN", "ASTRONAUT TO",
                  "ITS SPACE", "STATION"]
    y = 208
    for line in lead_lines:
        cv.text(536, y, line, 5, INK)
        y += 40
    draw_text_block(cv, 536, 424,
                    "SHENZHOU-24 LIFTS OFF WITH TWO CHINESE CREW AND "
                    "PAKISTAN'S FIRST ASTRONAUT FOR TIANGONG.",
                    2, (60, 60, 60), 448, line_gap=4)

    # ---- row 1: three stories ----
    small_panel(cv, 24, 524, 338, 720, "COURTS - NEW YORK", (122, 31, 43),
                "HUAWEI FOUND GUILTY IN U.S.",
                "A NEW YORK JURY CONVICTS HUAWEI IN A U.S. CRIMINAL "
                "CASE OVER ITS IRAN BUSINESS.",
                draw_courthouse)
    small_panel(cv, 354, 524, 668, 720, "UNITED NATIONS", (31, 78, 121),
                "KILLER ROBOTS MUST HAVE NO PLACE",
                "GUTERRES WARNS THE SECURITY COUNCIL: AI AND DRONES "
                "ARE RESHAPING WAR.",
                draw_drone)
    small_panel(cv, 684, 524, 1000, 720, "DISASTER - NEPAL", OCHRE,
                "QUAKE SHAKES EASTERN NEPAL",
                "MAGNITUDE 5.6 NEAR THE TIBET BORDER. TREMORS FELT IN "
                "INDIA. NO CASUALTIES REPORTED.",
                draw_mountains)

    # ---- row 2: two stories + also-in-the-news ----
    small_panel(cv, 24, 736, 338, 932, "WAR IN UKRAINE", FOREST,
                "RUSSIAN STRIKE KILLS TWO, WOUNDS 48",
                "KYIV SAYS ITS ATTACK ON RUSSIAN SHIPS IN LIBYA WAS "
                "SELF-DEFENCE.",
                draw_burst)
    small_panel(cv, 354, 736, 668, 932, "WASHINGTON", PLUM,
                "TRUMP: TOPPLING IRAN 'PROBABLY DOABLE'",
                "THE PRESIDENT SAYS ISRAEL'S GOAL COULD BE DONE BY FORCE.",
                draw_flags)
    panel_frame(cv, 684, 736, 1000, 932)
    kicker_bar(cv, 686, 738, 998, "ALSO ON 24 NOVEMBER", SLATE)
    draw_text_block(cv, 698, 782,
                    "- MARKETS RALLY: SEOUL +6%, TOKYO +3.9%.\n"
                    "- SOLOMON ISLANDS NAMES AUSTRALIA ITS TOP "
                    "SECURITY PARTNER.\n"
                    "- SENEGAL REINSTATED AS AFCON CHAMPIONS AFTER APPEAL.",
                    2, (60, 60, 60), 288, line_gap=4)

    # ---- footer ----
    cv.text_center(512, 952,
                   "EVERY STORY ABOVE HAPPENED OR WAS FIRST REPORTED ON "
                   "TUESDAY, 24 NOVEMBER 2026.",
                   2, (80, 80, 76))
    return cv


def main():
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build_page()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(cv, path)
    print("wrote %s (%d bytes, %dx%d)" % (path, size, W, H))


if __name__ == "__main__":
    main()
