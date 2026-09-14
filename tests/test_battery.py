import battery as bat


def test_level_clamps_below_empty():
    assert bat.level(2.0) == 0


def test_level_at_empty_is_zero():
    assert bat.level(2.2) == 0


def test_level_at_full_is_max():
    assert bat.level(3.0) == 4


def test_level_clamps_above_full():
    assert bat.level(3.4) == 4


def test_level_midpoints():
    assert bat.level(2.6) == 2
    assert bat.level(2.8) == 3


def test_label_formats_one_decimal():
    assert bat.label(2.94) == "2.9V"


def test_level_is_monotonic_between_empty_and_full():
    volts = 2.2
    prev = bat.level(volts)
    while volts <= 3.0 + 1e-9:
        cur = bat.level(volts)
        assert cur >= prev
        prev = cur
        volts += 0.05
