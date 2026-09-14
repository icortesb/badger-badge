import sys
from pathlib import Path

import segno

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sim"))

import badger2040  # noqa: E402

import qrcache  # noqa: E402
import ui  # noqa: E402

PAYLOAD = "https://github.com/icortesb"
BOX = 112


def _black_pixels(d):
    on = set()
    for x in range(BOX):
        for y in range(BOX):
            if d.image.getpixel((x, y)) == 0:
                on.add((x, y))
    return on


def test_qr_from_cache_matches_live_drawing_for_same_payload(tmp_path, monkeypatch):
    matrix = segno.make(PAYLOAD, error="m", micro=False).matrix
    matrix = [[bool(v) for v in row] for row in matrix]
    cache_file = tmp_path / "qr.bin"
    cache_file.write_bytes(qrcache.encode(matrix))
    monkeypatch.setattr(qrcache, "path", lambda payload: str(cache_file))

    d_cache = badger2040.Badger2040()
    module_cache = ui.qr(d_cache, PAYLOAD, 0, 0, BOX)

    d_live = badger2040.Badger2040()
    module_live = ui._qr_live(d_live, PAYLOAD, 0, 0, BOX)

    assert module_cache == module_live
    assert _black_pixels(d_cache) == _black_pixels(d_live)
    assert _black_pixels(d_cache)  # sanity: the QR actually drew something


def test_qr_falls_back_to_live_drawing_when_cache_file_missing(tmp_path, monkeypatch):
    missing = tmp_path / "does-not-exist.bin"
    monkeypatch.setattr(qrcache, "path", lambda payload: str(missing))

    d_cache = badger2040.Badger2040()
    module_cache = ui.qr(d_cache, PAYLOAD, 0, 0, BOX)

    d_live = badger2040.Badger2040()
    module_live = ui._qr_live(d_live, PAYLOAD, 0, 0, BOX)

    assert module_cache == module_live
    assert _black_pixels(d_cache) == _black_pixels(d_live)
