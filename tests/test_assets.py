import json
from pathlib import Path

from PIL import Image

ASSETS = Path(__file__).resolve().parents[1] / "device" / "assets"


def test_portrait_size():
    with Image.open(ASSETS / "portrait.jpg") as img:
        assert img.size == (96, 100)


def test_every_logo_question_has_an_image():
    quiz = json.loads((ASSETS / "quiz.json").read_text(encoding="utf-8"))
    for q in quiz:
        if q["type"] == "logo":
            with Image.open(ASSETS / q["image"]) as img:
                assert img.size == (80, 80), q["image"]
