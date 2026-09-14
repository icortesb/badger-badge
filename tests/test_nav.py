import nav


def handle(state, button):
    return nav.handle(state, button, 4, 2)


def test_abc_switch_tabs():
    s = dict(nav.DEFAULTS)
    assert handle(s, "b")[0]["tab"] == "links"
    assert handle(s, "c")[0]["tab"] == "projects"
    assert handle(dict(s, tab="links"), "a")[0]["tab"] == "badge"


def test_up_down_wrap_on_links():
    s = dict(nav.DEFAULTS, tab="links", link=0)
    assert handle(s, "up")[0]["link"] == 3
    assert handle(dict(s, link=3), "down")[0]["link"] == 0


def test_up_down_on_projects():
    s = dict(nav.DEFAULTS, tab="projects", project=0)
    assert handle(s, "down")[0]["project"] == 1
    assert handle(dict(s, project=1), "down")[0]["project"] == 0


def test_up_down_ignored_on_badge():
    s = dict(nav.DEFAULTS)
    new, action = handle(s, "down")
    assert (new["tab"], new["link"], new["project"], action) == ("badge", 0, 0, None)


def test_combo_triggers_quiz_and_resets():
    s = dict(nav.DEFAULTS)
    action = None
    for b in ["up", "up", "down", "down", "a", "b"]:
        s, action = handle(s, b)
    assert action == "quiz"
    assert s["combo"] == 0


def test_combo_progress_is_stored():
    s, _ = handle(dict(nav.DEFAULTS), "up")
    assert s["combo"] == 1


def test_does_not_mutate_input():
    s = dict(nav.DEFAULTS)
    handle(s, "b")
    assert s == nav.DEFAULTS


def test_unknown_tab_and_bad_values_are_repaired():
    new, _ = handle({"tab": "zzz", "link": "x", "combo": None}, "up")
    assert new["tab"] == "badge"
    assert new["link"] == 0
    assert new["combo"] == 1


def test_link_index_normalized_when_count_shrinks():
    new, _ = nav.handle(dict(nav.DEFAULTS, tab="links", link=3), "b", 3, 2)
    assert new["link"] == 0


def test_partials_defaults_to_zero():
    assert nav.DEFAULTS["partials"] == 0


def test_partials_is_preserved_through_handle():
    s = dict(nav.DEFAULTS, partials=5)
    new, _ = handle(s, "b")
    assert new["partials"] == 5


def test_partials_invalid_values_normalize_to_zero():
    new, _ = handle({"partials": "x"}, "up")
    assert new["partials"] == 0
    new, _ = handle({"partials": -3}, "up")
    assert new["partials"] == 0
