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
    import ui

    shot("badge", badge_screen.render)
    items = links.items(state.load("assets/contact.json", links.CONTACT_DEFAULTS))
    for i, item in enumerate(items):
        shot("links-{}".format(i), lambda d, j, i=i: links_screen.render(d, items, i))
        module = ui.qr(badger2040.Badger2040(), item["payload"], 0, 0, links_screen.QR_BOX)
        print("  {} -> módulo de {} px".format(item["label"], module))
    for p in projects.PROJECTS:
        shot("project-" + p["name"], lambda d, j, p=p: projects_screen.render(d, p))

    import random

    import quiz_engine
    import quiz_screen

    round_ = quiz_engine.build_round(state.load("assets/quiz.json", []), random.Random(7))
    logo = next(q for q in round_ if q["type"] == "logo")
    trivia = next(q for q in round_ if q["type"] == "trivia")
    shot("quiz-logo", lambda d, j: quiz_screen.draw_question(d, j, logo, 1, 10, 0))
    shot("quiz-trivia", lambda d, j: quiz_screen.draw_question(d, j, trivia, 2, 10, 1))
    shot("quiz-wrong", lambda d, j: quiz_screen.draw_feedback(d, trivia, (trivia["answer"] + 1) % 3, 2, 10, 1))
    shot("quiz-result", lambda d, j: quiz_screen.draw_result(d, 7, 10))
    shot("quiz-initials", lambda d, j: quiz_screen.draw_initials(d, [8, 21, 0], 1))
    board = [{"i": "IVA", "s": 9}, {"i": "BOB", "s": 7}, {"i": "ANA", "s": 7}, {"i": "ZED", "s": 4}, {"i": "LOL", "s": 1}]
    shot("quiz-board", lambda d, j: quiz_screen.draw_board(d, board, 1))


if __name__ == "__main__":
    main()
