# gen-assets.py — regenerates favicon/app icons (8-bit d-pad mark)
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

# 7x7 d-pad: white cross with a black center dot
DPAD = ["..WWW..",
        "..WWW..",
        "WWWWWWW",
        "WWW.WWW",
        "WWWWWWW",
        "..WWW..",
        "..WWW.."]

def mark(px, w, h, ox, oy, s):
    for ry, row in enumerate(DPAD):
        for rx, ch in enumerate(row):
            if ch == 'W': rect(px, w, h, ox + rx * s, oy + ry * s, s, s, rgba('#FFFFFF'))

BG = rgba('#000000')

def icon(size, path):
    s = max(1, int(size * 0.62) // 7); cw = 7 * s
    px = canvas(size, size, BG); mark(px, size, size, (size - cw) // 2, (size - cw) // 2, s)
    write_png(path, px, size, size)

icon(32, 'favicon.png'); icon(180, 'apple-touch-icon.png')
icon(192, 'icon-192.png'); icon(512, 'icon-512.png')
