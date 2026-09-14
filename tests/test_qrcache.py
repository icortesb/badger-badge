import segno

import qrcache


def test_key_is_stable_and_12_hex_chars():
    k1 = qrcache.key("hello")
    k2 = qrcache.key("hello")
    assert k1 == k2
    assert len(k1) == 12
    assert all(c in "0123456789abcdef" for c in k1)


def test_key_differs_for_different_payloads():
    assert qrcache.key("a") != qrcache.key("b")


def test_path_starts_with_assets_qr_and_uses_key():
    p = qrcache.path("hello")
    assert p.startswith("assets/qr/")
    assert p.endswith(".bin")
    assert qrcache.key("hello") in p


def _black_cells(matrix):
    return {(x, y) for y, row in enumerate(matrix) for x, v in enumerate(row) if v}


def _decoded_black_cells(rows):
    got = set()
    for r, runs in enumerate(rows):
        for start, length in runs:
            for x in range(start, start + length):
                got.add((x, r))
    return got


def test_roundtrip_known_5x5_matrix():
    matrix = [
        [1, 0, 0, 0, 1],
        [0, 1, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [1, 0, 0, 0, 1],
    ]
    size, rows = qrcache.decode(qrcache.encode(matrix))
    assert size == 5
    assert _decoded_black_cells(rows) == _black_cells(matrix)


def test_roundtrip_empty_and_full_rows():
    matrix = [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [1, 1, 1, 1],
    ]
    size, rows = qrcache.decode(qrcache.encode(matrix))
    assert size == 4
    assert rows[0] == []
    assert rows[1] == [(0, 4)]
    assert rows[2] == []
    assert rows[3] == [(0, 4)]


def test_roundtrip_real_segno_matrix():
    qr = segno.make("https://github.com/icortesb", error="m", micro=False)
    matrix = [[bool(v) for v in row] for row in qr.matrix]
    size, rows = qrcache.decode(qrcache.encode(matrix))
    assert size == len(matrix)
    assert _decoded_black_cells(rows) == _black_cells(matrix)
