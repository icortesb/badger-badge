import state


DEFAULTS = {"tab": "badge", "combo": 0}


def test_missing_file_returns_copy_of_defaults(tmp_path):
    data = state.load(str(tmp_path / "nope.json"), DEFAULTS)
    assert data == DEFAULTS
    assert data is not DEFAULTS


def test_corrupt_file_returns_defaults(tmp_path):
    path = tmp_path / "app.json"
    path.write_text("{not json")
    assert state.load(str(path), DEFAULTS) == DEFAULTS


def test_roundtrip_creates_parent_dir(tmp_path):
    path = str(tmp_path / "state" / "app.json")
    state.save(path, {"tab": "links", "combo": 2})
    assert state.load(path, DEFAULTS) == {"tab": "links", "combo": 2}


def test_missing_keys_are_filled_and_unknown_keys_dropped(tmp_path):
    path = str(tmp_path / "app.json")
    state.save(path, {"tab": "projects", "old": 1})
    assert state.load(path, DEFAULTS) == {"tab": "projects", "combo": 0}


def test_wrong_top_level_type_returns_defaults(tmp_path):
    path = str(tmp_path / "app.json")
    state.save(path, [1, 2])
    assert state.load(path, DEFAULTS) == DEFAULTS


def test_list_defaults_return_stored_list(tmp_path):
    path = str(tmp_path / "board.json")
    state.save(path, [{"i": "ABC", "s": 3}])
    assert state.load(path, []) == [{"i": "ABC", "s": 3}]


def test_save_overwrites_existing(tmp_path):
    path = str(tmp_path / "app.json")
    state.save(path, {"tab": "links", "combo": 0})
    state.save(path, {"tab": "badge", "combo": 1})
    assert state.load(path, DEFAULTS) == {"tab": "badge", "combo": 1}
