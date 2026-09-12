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
    import links
    import links_screen
    import projects
    import projects_screen
    import state

    shot("badge", badge_screen.render)
    contact_defaults = {"first": "", "last": "", "email": "", "phone": ""}
    items = links.items(state.load("assets/contact.json", contact_defaults))
    for i, item in enumerate(items):
        shot("links-{}".format(i), lambda d, j, i=i: links_screen.render(d, items, i))
        module = links_screen.draw_qr(badger2040.Badger2040(), item["payload"], 0, 0, links_screen.QR_BOX)
        print("  {} -> módulo de {} px".format(item["label"], module))
    for p in projects.PROJECTS:
        shot("project-" + p["name"], lambda d, j, p=p: projects_screen.render(d, p, False))


if __name__ == "__main__":
    main()
