import random

import quiz_engine as qe


def make_pool(per_bucket=10):
    pool = []
    for level in (1, 2, 3):
        for n in range(per_bucket):
            pool.append({"type": "logo", "level": level, "image": "logos/l{}_{}.jpg".format(level, n),
                         "options": ["ok", "x", "y"], "answer": 0, "explain": ""})
            pool.append({"type": "trivia", "level": level, "question": "t{}_{}".format(level, n),
                         "options": ["x", "ok", "y"], "answer": 1, "explain": ""})
    return pool


def key(q):
    return q.get("image") or q["question"]


def test_round_has_ten_questions_with_level_ramp():
    rnd = qe.build_round(make_pool(), random.Random(1))
    assert [q["level"] for q in rnd] == list(qe.ROUND_LEVELS)


def test_round_alternates_logo_and_trivia():
    rnd = qe.build_round(make_pool(), random.Random(2))
    assert [q["type"] for q in rnd] == ["logo", "trivia"] * 5


def test_round_has_no_repeats():
    for seed in range(20):
        rnd = qe.build_round(make_pool(per_bucket=3), random.Random(seed))
        assert len({key(q) for q in rnd}) == len(rnd) == 10


def test_answer_still_points_to_correct_option():
    for seed in range(20):
        for q in qe.build_round(make_pool(), random.Random(seed)):
            assert q["options"][q["answer"]] == "ok"
            assert sorted(q["options"]) == ["ok", "x", "y"]


def test_does_not_mutate_pool():
    pool = make_pool()
    qe.build_round(pool, random.Random(3))
    assert pool == make_pool()


def test_missing_images_are_skipped():
    rnd = qe.build_round(make_pool(), random.Random(4), exists=lambda path: False)
    assert rnd and all(q["type"] == "trivia" for q in rnd)


def test_small_pool_gives_short_round():
    pool = make_pool()[:4]
    rnd = qe.build_round(pool, random.Random(5))
    assert len(rnd) == 4


def test_titles():
    assert qe.title(0) == qe.title(3) == "Junior de Stack Overflow"
    assert qe.title(4) == qe.title(6) == "En mi máquina anda"
    assert qe.title(7) == qe.title(9) == "Senior que deploya los viernes"
    assert qe.title(10) == "10x dev (o googleaste)"


def board(*scores):
    return [{"i": "AA" + str(n), "s": s} for n, s in enumerate(scores)]


def test_qualifies():
    assert qe.qualifies([], 0)
    assert qe.qualifies(board(9, 8), 1)
    assert not qe.qualifies(board(9, 8, 7, 6, 5), 5)
    assert qe.qualifies(board(9, 8, 7, 6, 5), 6)


def test_insert_keeps_older_above_on_tie():
    new, pos = qe.insert_score(board(9, 7, 7), "NEW", 7)
    assert pos == 3
    assert [r["s"] for r in new] == [9, 7, 7, 7]


def test_insert_at_top_and_truncate():
    new, pos = qe.insert_score(board(9, 8, 7, 6, 5), "NEW", 10)
    assert pos == 0
    assert [r["i"] for r in new][0] == "NEW"
    assert len(new) == 5 and new[-1]["s"] == 6


def test_insert_that_does_not_fit():
    old = board(9, 8, 7, 6, 5)
    new, pos = qe.insert_score(old, "NEW", 5)
    assert pos is None
    assert new == old


def test_step_initials():
    letters, pos = qe.step_initials([0, 0, 0], 0, "down")
    assert (letters, pos) == ([25, 0, 0], 0)
    letters, pos = qe.step_initials(letters, pos, "up")
    assert (letters, pos) == ([0, 0, 0], 0)
    letters, pos = qe.step_initials([0, 0, 0], 0, "up")
    letters, pos = qe.step_initials(letters, pos, "b")
    assert (letters, pos) == ([1, 0, 0], 1)
    assert qe.step_initials(letters, 3, "up") == (letters, 3)
    assert qe.step_initials([2, 3, 4], 1, "a") == ([2, 3, 4], 1)


def test_initials_text():
    assert qe.initials_text([8, 21, 0]) == "IVA"
