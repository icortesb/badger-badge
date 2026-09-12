import combo


def press_all(buttons, progress=0):
    completed = False
    for b in buttons:
        progress, completed = combo.advance(progress, b)
    return progress, completed


def test_full_sequence_completes_and_resets():
    assert press_all(["up", "up", "down", "down", "a", "b"]) == (0, True)


def test_partial_sequence_tracks_progress():
    assert press_all(["up", "up", "down"]) == (3, False)


def test_wrong_button_resets():
    assert press_all(["up", "up", "c"]) == (0, False)


def test_wrong_button_that_starts_sequence_keeps_one():
    assert press_all(["up", "up", "down", "up"]) == (1, False)


def test_extra_up_still_completes():
    assert press_all(["up", "up", "up", "down", "down", "a", "b"]) == (0, True)


def test_corrupt_progress_is_clamped():
    assert combo.advance(99, "c") == (0, False)
    assert combo.advance(-3, "up") == (1, False)
