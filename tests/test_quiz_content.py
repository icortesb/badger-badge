import json
import re
from collections import Counter
from pathlib import Path

QUIZ = Path(__file__).resolve().parents[1] / "device" / "assets" / "quiz.json"


def load():
    return json.loads(QUIZ.read_text(encoding="utf-8"))


def texts(q):
    yield q["explain"]
    yield from q["options"]
    if "question" in q:
        yield q["question"]


def test_schema_and_limits():
    for q in load():
        assert q["type"] in ("logo", "trivia"), q
        assert q["level"] in (1, 2, 3), q
        assert len(q["options"]) == 3 and len(set(q["options"])) == 3, q
        assert q["answer"] in (0, 1, 2), q
        assert len(q["explain"]) <= 140, q
        for text in texts(q):
            assert "¿" not in text, q
            assert all(ord(c) < 256 for c in text), q
        if q["type"] == "logo":
            assert re.fullmatch(r"logos/[a-z0-9]+\.jpg", q["image"]), q
            assert all(len(o) <= 14 for o in q["options"]), q
        else:
            assert len(q["question"]) <= 110, q
            assert all(len(o) <= 40 for o in q["options"]), q


def test_pool_has_ten_per_type_and_level():
    counts = Counter((q["type"], q["level"]) for q in load())
    for qtype in ("logo", "trivia"):
        for level in (1, 2, 3):
            assert counts[(qtype, level)] == 10, (qtype, level)


def test_no_duplicate_questions():
    keys = [q.get("image") or q["question"] for q in load()]
    assert len(keys) == len(set(keys))
