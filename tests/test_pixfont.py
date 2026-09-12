import pixfont


class Canvas:
    def __init__(self):
        self.on = set()

    def rectangle(self, x, y, w, h):
        for px in range(x, x + w):
            for py in range(y, y + h):
                self.on.add((px, py))


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
