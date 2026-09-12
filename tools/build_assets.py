"""Genera device/assets/portrait.jpg y device/assets/logos/*.jpg."""
import argparse
import json
import subprocess
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "device" / "assets"
CACHE = ROOT / "tools" / ".cache"
SIMPLE_ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@16.30.0/icons/{}.svg"
PORTRAIT_SIZE = (96, 100)
LOGO_BOX = 80
LOGO_INNER = 68


def save_1bit_jpeg(img, path, dither):
    mode = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
    mono = img.convert("L").convert("1", dither=mode)
    path.parent.mkdir(parents=True, exist_ok=True)
    mono.convert("L").save(path, "JPEG", quality=100)


def build_portrait(photo, crop, dither):
    img = ImageOps.exif_transpose(Image.open(photo)).crop(crop)
    img = ImageOps.fit(img, PORTRAIT_SIZE, Image.Resampling.LANCZOS)
    img = ImageOps.autocontrast(img.convert("L"), cutoff=2)
    save_1bit_jpeg(img, ASSETS / "portrait.jpg", dither)
    print("wrote portrait.jpg")


def logo_slugs():
    quiz = json.loads((ASSETS / "quiz.json").read_text(encoding="utf-8"))
    return sorted({Path(q["image"]).stem for q in quiz if q["type"] == "logo"})


def fetch_svg(slug):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "{}.svg".format(slug)
    if not path.exists():
        with urllib.request.urlopen(SIMPLE_ICONS.format(slug)) as response:
            path.write_bytes(response.read())
    return path


def build_logo(slug):
    png = CACHE / "{}.png".format(slug)
    subprocess.run(
        ["rsvg-convert", "-w", str(LOGO_INNER), "-h", str(LOGO_INNER), "-o", str(png), str(fetch_svg(slug))],
        check=True,
    )
    icon = Image.open(png).convert("RGBA")
    canvas = Image.new("RGBA", (LOGO_BOX, LOGO_BOX), "white")
    canvas.alpha_composite(icon, ((LOGO_BOX - icon.width) // 2, (LOGO_BOX - icon.height) // 2))
    save_1bit_jpeg(canvas, ASSETS / "logos" / "{}.jpg".format(slug), dither=False)
    print("wrote logos/{}.jpg".format(slug))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--photo", type=Path)
    parser.add_argument("--crop", default="235,195,475,445", help="left,top,right,bottom en la foto original")
    parser.add_argument("--dither", action="store_true", help="puntos en vez de stencil")
    args = parser.parse_args()
    if args.photo:
        build_portrait(args.photo, tuple(int(v) for v in args.crop.split(",")), args.dither)
    for slug in logo_slugs():
        build_logo(slug)


if __name__ == "__main__":
    main()
