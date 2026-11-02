# gen-assets.py — regenerates the app icons and the social preview image (og.png)
# Mark: a white 8-bit TV with antennas, a tiny controller (d-pad + two buttons) on its screen. Black background.
# Pure Python, no dependencies (stdlib zlib only). Run: python3 gen-assets.py
import zlib, struct

def canvas(w, h, bg): return bytearray(bg * (w * h))

def setpx(px, w, h, x, y, c):
    if 0 <= x < w and 0 <= y < h:
        i = (y * w + x) * 4; px[i:i + 4] = c

def rect(px, w, h, x, y, rw, rh, c):
    for yy in range(y, y + rh):
        for xx in range(x, x + rw): setpx(px, w, h, xx, yy, c)

def rgba(s, a=255):
    s = s.lstrip('#'); return bytes((int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a))

def write_png(path, px, w, h):
    raw = bytearray()
    for y in range(h):
        raw.append(0); raw += px[y * w * 4:(y + 1) * w * 4]
    comp = zlib.compress(bytes(raw), 9)
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
        + chunk(b'IDAT', comp) + chunk(b'IEND', b''))

# 16x13 TV: antennas, 1px frame, on the screen a d-pad (left) and two buttons (right, diagonal like the app)
TV = ["...W.......W....",
      "....W.....W.....",
      ".....W...W......",
      "WWWWWWWWWWWWWWWW",
      "W..............W",
      "W..............W",
      "W...W.......W..W",
      "W..WWW....W....W",
      "W...W..........W",
      "W..............W",
      "W..............W",
      "WWWWWWWWWWWWWWWW",
      ".WW..........WW.",
      "................"]

def draw(px, w, h, art, ox, oy, s, c):
    for ry, row in enumerate(art):
        for rx, ch in enumerate(row):
            if ch == 'W': rect(px, w, h, ox + rx * s, oy + ry * s, s, s, c)

BG, WHITE, GREY = rgba('#000000'), rgba('#FFFFFF'), rgba('#999999')
TW, TH = len(TV[0]), len(TV) - 1   # last row is spacing

def icon(size, path):
    s = max(1, int(size * 0.74) // TW)
    px = canvas(size, size, BG)
    draw(px, size, size, TV, (size - TW * s) // 2, (size - TH * s) // 2, s, WHITE)
    write_png(path, px, size, size)

# 5x8 lowercase pixel font, just the letters the preview needs
FONT = {
 'e': [".....", ".....", ".WWW.", "W...W", "WWWWW", "W....", ".WWW.", "....."],
 'm': [".....", ".....", "WW.W.", "W.W.W", "W.W.W", "W.W.W", "W.W.W", "....."],
 'u': [".....", ".....", "W...W", "W...W", "W...W", "W..WW", ".WW.W", "....."],
 'n': [".....", ".....", "W.WW.", "WW..W", "W...W", "W...W", "W...W", "....."],
 's': [".....", ".....", ".WWWW", "W....", ".WWW.", "....W", "WWWW.", "....."],
 'g': [".....", ".....", ".WWWW", "W...W", "W...W", ".WWWW", "....W", ".WWW."],
 'b': ["W....", "W....", "WWWW.", "W...W", "W...W", "W...W", "WWWW.", "....."],
 'a': [".....", ".....", ".WWW.", "....W", ".WWWW", "W...W", ".WWWW", "....."],
 '.': [".....", ".....", ".....", ".....", "..W..", ".....", ".....", "....."],
 ' ': [".....", ".....", ".....", ".....", ".....", ".....", ".....", "....."],
}

def text(px, w, h, msg, x, y, s, c):
    for ch in msg:
        draw(px, w, h, FONT[ch], x, y, s, c); x += 6 * s
    return x

def text_w(msg, s): return len(msg) * 6 * s - s

def og(path):
    w, h = 1200, 630
    px = canvas(w, h, BG)
    rect(px, w, h, 40, 40, w - 80, 1, WHITE); rect(px, w, h, 40, h - 41, w - 80, 1, WHITE)
    rect(px, w, h, 40, 40, 1, h - 80, WHITE); rect(px, w, h, w - 41, 40, 1, h - 80, WHITE)
    s = 20; tvw = TW * s
    draw(px, w, h, TV, 110, (h - TH * s) // 2, s, WHITE)
    tx = 110 + tvw + 80
    text(px, w, h, 'emu emu', tx, 230, 13, WHITE)
    text(px, w, h, 'nes . snes . gb . gba . sega', tx, 370, 3, GREY)
    write_png(path, px, w, h)

icon(32, 'favicon.png'); icon(180, 'apple-touch-icon.png')
icon(192, 'icon-192.png'); icon(512, 'icon-512.png')
og('og.png')
