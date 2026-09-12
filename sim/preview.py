"""Renderiza pantallas a sim/out/*.png usando el fake de badger2040."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sim" / "out"
sys.path[:0] = [str(ROOT / "sim"), str(ROOT / "device")]
os.chdir(ROOT / "device")

import badger2040  # noqa: E402
import jpegdec  # noqa: E402


def shot(name, draw):
    d = badger2040.Badger2040()
    draw(d, jpegdec.JPEG(d.display))
    OUT.mkdir(exist_ok=True)
    path = OUT / "{}.png".format(name)
    d.image.resize((badger2040.WIDTH * 3, badger2040.HEIGHT * 3), 0).save(path)
    print("wrote", path)


def main():
    import badge_screen

    shot("badge", badge_screen.render)


if __name__ == "__main__":
    main()
