"""THE DAY IN NUMBERS - Sunday 22 November 2026.

Draws a data-led news poster: six huge numerals, each standing for one
verified story of Sunday 22 November 2026, in a 2 x 3 grid under a
masthead. Pure Python 3.13 standard library; no network at runtime.
Writes entry.png (1024 x 1024) to MAKEFUN_OUTPUT_DIR (default out/).
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# 5x7 pixel font, one glyph per character. '#' is ink, '.' is blank.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ":": ("00000", "00100", "00000", "00000", "00100", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}

BLANK = ("00000",) * 7


def text_width(text, scale):
    """Pixel width of text at the given scale (6 px per char cell)."""
    return len(text) * 6 * scale - scale


def draw_text(px, x, y, text, scale, color):
    """Draw upper-case text left-aligned at (x, y); returns width used."""
    for ch in text:
        glyph = FONT.get(ch, BLANK)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    fill_rect(px, x + col * scale, y + row * scale,
                              scale, scale, color)
        x += 6 * scale
    return len(text) * 6 * scale - scale


def draw_text_centred(px, cx, y, text, scale, color):
    draw_text(px, cx - text_width(text, scale) // 2, y, text, scale, color)


# ---------------------------------------------------------------- canvas
def new_canvas(w, h, color):
    px = bytearray(w * h * 3)
    px[0::3] = bytes([color[0]]) * (w * h)
    px[1::3] = bytes([color[1]]) * (w * h)
    px[2::3] = bytes([color[2]]) * (w * h)
    return px


def set_px(px, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def fill_rect(px, x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    r, g, b = color
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        n = x1 - x0
        px[base:base + n * 3:3] = bytes([r]) * n
        px[base + 1:base + n * 3 + 1:3] = bytes([g]) * n
        px[base + 2:base + n * 3 + 2:3] = bytes([b]) * n


def fill_circle(px, cx, cy, rad, color):
    for yy in range(cy - rad, cy + rad + 1):
        dy = yy - cy
        dx = int((rad * rad - dy * dy) ** 0.5)
        fill_rect(px, cx - dx, yy, 2 * dx + 1, 1, color)


def draw_line(px, x0, y0, x1, y1, color, thick=1):
    """Simple Bresenham line with square thickness."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        fill_rect(px, x0 - thick // 2, y0 - thick // 2, thick, thick, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def ring(px, cx, cy, rad, color, thick=3):
    for t in range(thick):
        r = rad - t
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5)
            set_px(px, cx - dx, yy, color)
            set_px(px, cx + dx, yy, color)


# ---------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, px, w, h):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += px[y * w * 3:(y + 1) * w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)

# ---------------------------------------------------------------- design
PAPER = (247, 243, 234)   # warm off-white
INK = (26, 26, 26)
NAVY = (20, 33, 61)       # masthead band
GOLD = (252, 191, 73)     # masthead accent
RED = (192, 57, 43)
BLUE = (41, 98, 168)
GREEN = (39, 120, 83)
TEAL = (15, 118, 110)
PURPLE = (109, 72, 160)
ORANGE = (214, 106, 24)
GREY = (110, 110, 100)
LINE = (200, 192, 175)

# Six verified stories of Sunday 22 November 2026.
#   numeral, accent colour, pictogram key, caption lines (<= 26 chars each)
TILES = [
    ("128", RED, "bat",
     ["PANT'S RUNS FOR INDIA", "IN WELLINGTON, 1ST TEST"]),
    ("83", GREEN, "cedar",
     ["YEARS OF LEBANON'S", "INDEPENDENCE, 1943-2026"]),
    ("723", BLUE, "ballot",
     ["SEATS, HONG KONG VOTE", "856 CANDIDATES, 31 AREAS"]),
    ("06:00", TEAL, "globe",
     ["GMT: COP31 APPROVAL", "SESSION OPENS, ANTALYA"]),
    ("16:30", PURPLE, "ball",
     ["KICKOFF, LIVERPOOL V", "MAN UTD, ANFIELD"]),
    ("4TH", ORANGE, "horn",
     ["WEEKEND OF COST-OF-", "LIVING PROTESTS, FRANCE"]),
]


def draw_pictogram(px, kind, cx, cy, color):
    """Small line pictogram centred near (cx, cy), ~64 px across."""
    if kind == "bat":  # cricket ball with a seam
        fill_circle(px, cx, cy, 20, color)
        draw_line(px, cx - 16, cy - 8, cx + 16, cy + 8, PAPER, 4)
        draw_line(px, cx - 14, cy + 12, cx + 14, cy - 4, PAPER, 3)
    elif kind == "cedar":  # cedar tree
        fill_rect(px, cx - 3, cy + 8, 6, 22, color)
        for i, half in enumerate((26, 21, 15)):
            y = cy - 26 + i * 13
            draw_line(px, cx, y, cx - half, y + 14, color, 4)
            draw_line(px, cx, y, cx + half, y + 14, color, 4)
            fill_rect(px, cx - half, y + 12, 2 * half, 3, color)
    elif kind == "ballot":  # ballot box with a tick
        fill_rect(px, cx - 26, cy - 6, 52, 36, color)
        fill_rect(px, cx - 26, cy - 14, 52, 8, PAPER)
        draw_line(px, cx - 18, cy + 12, cx - 6, cy + 24, INK, 5)
        draw_line(px, cx - 6, cy + 24, cx + 24, cy - 16, INK, 5)
    elif kind == "globe":  # globe with meridians
        ring(px, cx, cy, 26, color, 5)
        draw_line(px, cx - 26, cy, cx + 26, cy, color, 3)
        draw_line(px, cx, cy - 26, cx, cy + 26, color, 3)
        fill_circle(px, cx - 12, cy - 12, 5, color)
        fill_circle(px, cx + 13, cy + 11, 5, color)
    elif kind == "ball":  # football
        ring(px, cx, cy, 26, color, 5)
        fill_circle(px, cx, cy, 7, color)
        for dx, dy in ((-18, -12), (18, -12), (-18, 14), (18, 14), (0, -22)):
            fill_circle(px, cx + dx, cy + dy, 4, color)
    elif kind == "horn":  # megaphone
        draw_line(px, cx - 24, cy - 4, cx + 8, cy - 22, color, 4)
        draw_line(px, cx - 24, cy - 4, cx + 8, cy + 14, color, 4)
        draw_line(px, cx + 8, cy - 22, cx + 8, cy + 14, color, 4)
        draw_line(px, cx + 14, cy - 18, cx + 14, cy + 10, color, 6)
        draw_line(px, cx - 24, cy - 4, cx - 30, cy + 14, color, 5)


def draw_tile(px, x, y, w, h, numeral, accent, pic, lines):
    fill_rect(px, x, y, w, h, PAPER)
    fill_rect(px, x, y, w, 10, accent)          # coloured top bar
    fill_rect(px, x, y + h - 2, w, 2, LINE)     # hairline under tile
    # pictogram, top right corner
    draw_pictogram(px, pic, x + w - 52, y + 52, accent)
    # huge numeral, centred on the tile's left two thirds
    scale = 15 if len(numeral) <= 3 else 12
    nw = text_width(numeral, scale)
    nx = x + (w - 110 - nw) // 2 + 8
    draw_text(px, nx, y + 52, numeral, scale, accent)
    # caption, two short lines
    draw_text_centred(px, x + w // 2, y + h - 78, lines[0], 3, INK)
    draw_text_centred(px, x + w // 2, y + h - 48, lines[1], 3, INK)


def draw_masthead(px):
    fill_rect(px, 0, 0, W, 176, NAVY)
    fill_rect(px, 0, 176, W, 6, GOLD)
    draw_text_centred(px, W // 2, 22, "SUNDAY 22 NOVEMBER 2026", 4, GOLD)
    draw_text_centred(px, W // 2, 62, "THE DAY IN NUMBERS", 9, (255, 255, 255))
    draw_text_centred(px, W // 2, 140,
                      "SIX NUMBERS THAT TELL THE DAY", 3, (200, 210, 225))


def draw_footer(px):
    draw_text_centred(px, W // 2, H - 34,
                      "CLIMATE - POLITICS - SPORT - ANNIVERSARY - PROTEST",
                      3, GREY)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    px = new_canvas(W, H, PAPER)
    draw_masthead(px)
    grid_x, grid_y = 16, 198
    cell_w, cell_h = 488, 252
    gap = 12
    for i, (num, accent, pic, lines) in enumerate(TILES):
        col, row = i % 2, i // 2
        draw_tile(px, grid_x + col * (cell_w + gap),
                  grid_y + row * (cell_h + gap),
                  cell_w, cell_h, num, accent, pic, lines)
    draw_footer(px)
    write_png(os.path.join(outdir, "entry.png"), px, W, H)


if __name__ == "__main__":
    main()
