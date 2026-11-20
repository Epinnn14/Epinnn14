"""Hang Spider-Man from the GitHub stats card.

Wraps profile/stats.svg (and the light version) in a bordered box and hangs
profile/spiderman.webp from its bottom edge, writing profile/about.svg and
profile/about-light.svg. Run by the README workflow after the stats cards.
"""
import base64
import pathlib
import re
import struct

ROOT = pathlib.Path(__file__).resolve().parents[2]
SPIDER = ROOT / "profile" / "spiderman.webp"

SPIDER_H = 150          # rendered height of the figure, web included
WEB_X = 0.566           # where the web starts, as a fraction of the figure width
ANCHOR = 0.69           # where it hangs from, as a fraction of the card width

THEMES = {
    "about.svg": ("stats.svg", "#161B22", "#30363D"),
    "about-light.svg": ("stats-light.svg", "#F6F8FA", "#D0D7DE"),
}


def image_size(data):
    """Width and height of a PNG or WebP (VP8X/VP8L/VP8) file."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    chunk = data[12:16]
    if chunk == b"VP8X":
        return 1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little")
    if chunk == b"VP8L":
        b = int.from_bytes(data[21:25], "little")
        return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    if chunk == b"VP8 ":
        return struct.unpack("<H", data[26:28])[0] & 0x3FFF, struct.unpack("<H", data[28:30])[0] & 0x3FFF
    raise ValueError("unsupported image format")


def build(stats_name, fill, stroke, spider_png):
    svg = (ROOT / "profile" / stats_name).read_text(encoding="utf-8")
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg).strip()
    m = re.search(r'<svg\b[^>]*?\swidth="([\d.]+)"[^>]*?\sheight="([\d.]+)"', svg, re.S)
    w, h = float(m.group(1)), float(m.group(2))

    pw, ph = image_size(spider_png)
    mime = "image/png" if spider_png[:4] == b"\x89PNG" else "image/webp"
    sh = SPIDER_H
    sw = pw * sh / ph
    sx = w * ANCHOR - sw * WEB_X
    sy = h - 3                      # web tucks under the box edge
    total_h = sy + sh
    b64 = base64.b64encode(spider_png).decode()

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w:g}" height="{total_h:g}" viewBox="0 0 {w:g} {total_h:g}" role="img" aria-label="GitHub stats card with Spider-Man hanging from it">
  <image x="{sx:.1f}" y="{sy:g}" width="{sw:.1f}" height="{sh:g}" href="data:{mime};base64,{b64}" xlink:href="data:{mime};base64,{b64}"/>
  <rect x="0.5" y="0.5" width="{w - 1:g}" height="{h - 1:g}" rx="6" fill="{fill}" stroke="{stroke}"/>
  {svg}
</svg>
'''


def main():
    spider_png = SPIDER.read_bytes()
    for out, (stats_name, fill, stroke) in THEMES.items():
        (ROOT / "profile" / out).write_text(build(stats_name, fill, stroke, spider_png), encoding="utf-8")
        print("wrote", out)


if __name__ == "__main__":
    main()
