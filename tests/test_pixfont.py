import pixfont


class Canvas:
    def __init__(self):
        self.on = set()
        self.calls = 0

    def rectangle(self, x, y, w, h):
        self.calls += 1
        for px in range(x, x + w):
            for py in range(y, y + h):
                self.on.add((px, py))


def _old_text(d, text, x, y, num=3, den=2):
    """Algoritmo anterior (un rectángulo por bit encendido), usado como
    referencia para verificar que el nuevo dibuja los mismos píxeles."""
    cx = 0
    for ch in text:
        code = ord(ch)
        if not 32 <= code <= 126:
            continue
        index = code - 32
        base = index * pixfont.MAX_WIDTH
        for col in range(pixfont.WIDTHS[index]):
            x0, x1 = pixfont._span(cx + col, num, den)
            bits = pixfont.DATA[base + col]
            for row in range(8):
                if bits & (1 << row):
                    y0, y1 = pixfont._span(row, num, den)
                    d.rectangle(x + x0, y + y0, x1 - x0, y1 - y0)
        cx += pixfont.WIDTHS[index] + 1


def test_widths_and_data_sizes():
    assert len(pixfont.WIDTHS) == 95
    assert len(pixfont.DATA) == 95 * pixfont.MAX_WIDTH
    assert pixfont.MAX_WIDTH == 5


def test_space_draws_nothing():
    c = Canvas()
    pixfont.text(c, " ", 0, 0)
    assert c.on == set()
    assert pixfont.measure(" ", 1, 1) == pixfont.WIDTHS[0] + 1


def test_scale_1_1_matches_data_bits():
    c = Canvas()
    pixfont.text(c, "A", 0, 0, 1, 1)
    index = ord("A") - 32
    base = index * pixfont.MAX_WIDTH
    expected = set()
    for col in range(pixfont.WIDTHS[index]):
        bits = pixfont.DATA[base + col]
        for row in range(8):
            if bits & (1 << row):
                expected.add((col, row))
    assert c.on == expected


def test_scale_3_2_pipe_height():
    c = Canvas()
    pixfont.text(c, "|", 0, 0, 3, 2)
    index = ord("|") - 32
    base = index * pixfont.MAX_WIDTH
    bits = pixfont.DATA[base]
    rows = [row for row in range(8) if bits & (1 << row)]
    top_row_first = rows[0]
    top_row_last = rows[-1]
    ys = [y for (x, y) in c.on]
    expected_height = ((top_row_last + 1) * 3 // 2) - (top_row_first * 3 // 2)
    assert max(ys) - min(ys) + 1 == expected_height


def test_measure_full_stack_dev():
    text = "Full-stack dev"
    expected = sum(pixfont.WIDTHS[ord(ch) - 32] + 1 for ch in text) * 3 // 2
    assert pixfont.measure(text) == expected
    assert expected <= 184


def test_non_ascii_skipped():
    assert pixfont.measure("á", 3, 2) == 0


def test_full_stack_dev_pixels_match_old_algorithm():
    text = "Full-stack dev"
    new = Canvas()
    pixfont.text(new, text, 0, 0)
    old = Canvas()
    _old_text(old, text, 0, 0)
    assert new.on == old.on


def test_all_printable_chars_pixels_match_old_algorithm():
    for code in range(32, 127):
        ch = chr(code)
        new = Canvas()
        pixfont.text(new, ch, 0, 0, 3, 2)
        old = Canvas()
        _old_text(old, ch, 0, 0, 3, 2)
        assert new.on == old.on, ch


def test_full_stack_dev_uses_fewer_rectangle_calls_than_old_algorithm():
    text = "Full-stack dev"
    new = Canvas()
    pixfont.text(new, text, 0, 0)
    old = Canvas()
    _old_text(old, text, 0, 0)
    assert new.calls < old.calls


def test_all_chars_draw_nonzero_rectangles_at_3_2():
    for code in range(32, 127):
        c = Canvas()
        ch = chr(code)
        pixfont.text(c, ch, 0, 0, 3, 2)
        index = code - 32
        base = index * pixfont.MAX_WIDTH
        for col in range(pixfont.WIDTHS[index]):
            bits = pixfont.DATA[base + col]
            for row in range(8):
                if bits & (1 << row):
                    x0 = (col) * 3 // 2
                    x1 = (col + 1) * 3 // 2
                    y0 = row * 3 // 2
                    y1 = (row + 1) * 3 // 2
                    assert x1 - x0 >= 1
                    assert y1 - y0 >= 1
