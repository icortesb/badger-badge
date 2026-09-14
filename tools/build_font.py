"""Genera device/pixfont.py a partir de font8_data.hpp (pimoroni-pico v1.21.0).

Descarga el header via la API de GitHub (raw.githubusercontent.com no es
alcanzable desde esta máquina), parsea `.max_width`, `.widths = {...}` y
`.data = {...}` con regexes, se queda con los primeros 95 anchos y los
primeros 95 * max_width bytes de datos (ASCII 32..126) y escribe
device/pixfont.py.
"""
import base64
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "device" / "pixfont.py"
API_URL = (
    "https://api.github.com/repos/pimoroni/pimoroni-pico/contents/"
    "libraries/bitmap_fonts/font8_data.hpp?ref=v1.21.0"
)
ASCII_COUNT = 95

HEADER = (
    "# Generado por tools/build_font.py desde pimoroni-pico v1.21.0 "
    "font8_data.hpp. No editar a mano.\n"
)

FUNCTIONS_SRC = '''

def _span(i, num, den):
    return i * num // den, (i + 1) * num // den


def measure(text, num=3, den=2):
    width = 0
    for ch in text:
        code = ord(ch)
        if 32 <= code <= 126:
            width += WIDTHS[code - 32] + 1
    return width * num // den


def text(d, text, x, y, num=3, den=2):
    cx = 0
    for ch in text:
        code = ord(ch)
        if not 32 <= code <= 126:
            continue
        index = code - 32
        base = index * MAX_WIDTH
        for col in range(WIDTHS[index]):
            x0, x1 = _span(cx + col, num, den)
            bits = DATA[base + col]
            row = 0
            while row < 8:
                if bits & (1 << row):
                    r0 = row
                    while row < 8 and bits & (1 << row):
                        row += 1
                    y0 = _span(r0, num, den)[0]
                    y1 = _span(row - 1, num, den)[1]
                    d.rectangle(x + x0, y + y0, x1 - x0, y1 - y0)
                else:
                    row += 1
        cx += WIDTHS[index] + 1
'''


def fetch_header():
    req = urllib.request.Request(
        API_URL,
        headers={"User-Agent": "badge-build-font", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.load(resp)
    return base64.b64decode(payload["content"]).decode("utf-8")


def _numbers(block):
    without_comments = re.sub(r"//.*", "", block)
    return [int(tok, 0) for tok in re.findall(r"0[xX][0-9a-fA-F]+|\d+", without_comments)]


def parse(header_text):
    max_width = int(re.search(r"\.max_width\s*=\s*(\d+)", header_text).group(1))

    widths_block = re.search(r"\.widths\s*=\s*\{(.*?)\}", header_text, re.DOTALL).group(1)
    widths = _numbers(widths_block)[:ASCII_COUNT]

    data_block = re.search(r"\.data\s*=\s*\{(.*)\}\s*\}\s*;", header_text, re.DOTALL).group(1)
    data = _numbers(data_block)[: ASCII_COUNT * max_width]

    if len(widths) != ASCII_COUNT:
        raise ValueError("expected {} widths, got {}".format(ASCII_COUNT, len(widths)))
    if len(data) != ASCII_COUNT * max_width:
        raise ValueError(
            "expected {} data bytes, got {}".format(ASCII_COUNT * max_width, len(data))
        )
    return max_width, bytes(widths), bytes(data)


def render(max_width, widths, data):
    out = HEADER
    out += "MAX_WIDTH = {}\n".format(max_width)
    out += "WIDTHS = {!r}   # {} bytes\n".format(widths, len(widths))
    out += "DATA = {!r}     # {} bytes\n".format(data, len(data))
    out += FUNCTIONS_SRC
    return out


def main():
    header_text = fetch_header()
    max_width, widths, data = parse(header_text)
    OUT.write_text(render(max_width, widths, data))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
