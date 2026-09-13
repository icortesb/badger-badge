import buttons


def drain(q, now):
    out = []
    while True:
        ev = q.pop(now)
        if ev is None:
            return out
        out.append(ev)


def test_events_come_out_in_order():
    q = buttons.ButtonQueue()
    q.push("a", 0)
    q.push("b", 10)
    q.push("c", 20)
    assert drain(q, 1000) == ["a", "b", "c"]


def test_same_button_is_debounced():
    q = buttons.ButtonQueue()
    q.push("a", 0)
    q.push("a", 100)
    q.push("a", 300)
    assert drain(q, 1000) == ["a", "a"]


def test_debounce_is_per_button():
    q = buttons.ButtonQueue()
    q.push("a", 0)
    q.push("b", 5)
    assert drain(q, 1000) == ["a", "b"]


def test_debounce_window_extends_with_each_bounce():
    q = buttons.ButtonQueue()
    q.push("a", 0)
    q.push("a", 100)
    q.push("a", 200)
    q.push("a", 300)
    assert drain(q, 1000) == ["a"]


def test_debounce_window_does_not_extend_past_the_gap():
    q = buttons.ButtonQueue()
    q.push("a", 0)
    q.push("a", 200)
    assert drain(q, 1000) == ["a", "a"]


def test_chord_off_by_default_pops_up_and_down_immediately():
    q = buttons.ButtonQueue()
    assert q.chord is False
    q.push("up", 0)
    q.push("down", 50)
    assert q.pop(50) == "up"
    assert q.pop(50) == "down"


def test_up_down_close_together_is_exit_in_both_orders():
    q = buttons.ButtonQueue(chord=True)
    q.push("up", 0)
    q.push("down", 60)
    assert drain(q, 1000) == ["exit"]
    q = buttons.ButtonQueue(chord=True)
    q.push("down", 0)
    q.push("up", 149)
    assert drain(q, 1000) == ["exit"]


def test_up_down_far_apart_are_separate():
    q = buttons.ButtonQueue(chord=True)
    q.push("up", 0)
    q.push("down", 150)
    assert drain(q, 1000) == ["up", "down"]


def test_lone_up_waits_for_chord_window():
    q = buttons.ButtonQueue(chord=True)
    q.push("up", 1000)
    assert q.pop(1050) is None
    assert q.pending()
    assert q.pop(1150) == "up"
    assert not q.pending()


def test_lone_up_then_late_down_within_window_is_exit():
    q = buttons.ButtonQueue(chord=True)
    q.push("up", 1000)
    assert q.pop(1020) is None
    q.push("down", 1080)
    assert q.pop(1090) == "exit"


def test_up_followed_by_other_button_is_not_held():
    q = buttons.ButtonQueue(chord=True)
    q.push("up", 1000)
    q.push("a", 1010)
    assert q.pop(1020) == "up"
    assert q.pop(1020) == "a"


def test_clear_and_empty_pop():
    q = buttons.ButtonQueue()
    assert q.pop(0) is None
    q.push("a", 0)
    q.clear()
    assert not q.pending()
    assert q.pop(10) is None


def test_diff_falls_back_to_plain_subtraction_on_cpython():
    assert buttons._diff(10, 3) == 7
