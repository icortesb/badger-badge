import pytest

import battery as bat


def test_level_clamps_below_empty():
    assert bat.level(2.0) == 0


def test_level_at_empty_is_zero():
    assert bat.level(2.3) == 0


def test_level_at_full_is_max():
    assert bat.level(3.0) == 4


def test_level_clamps_above_full():
    assert bat.level(3.4) == 4


def test_level_midpoint():
    expected = int((2.65 - bat.EMPTY_V) / (bat.FULL_V - bat.EMPTY_V) * bat.LEVELS + 0.5)
    assert bat.level(2.65) == expected


def test_label_formats_one_decimal():
    assert bat.label(2.94) == "2.9V"


def test_level_is_monotonic_between_empty_and_full():
    volts = bat.EMPTY_V
    prev = bat.level(volts)
    while volts <= bat.FULL_V + 1e-9:
        cur = bat.level(volts)
        assert cur >= prev
        prev = cur
        volts += 0.05


def test_vdd_from_ref_matches_measured_raw():
    assert bat.vdd_from_ref(25094) == pytest.approx(3.238, abs=0.005)


def test_vdd_from_ref_zero_raw_is_zero():
    assert bat.vdd_from_ref(0) == 0.0


def test_vdd_from_ref_lower_supply_gives_larger_raw_and_smaller_vdd():
    assert 27000 < 30000
    assert bat.vdd_from_ref(27000) > bat.vdd_from_ref(30000)
