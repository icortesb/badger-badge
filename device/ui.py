import jpegdec

WIDTH = 296
HEIGHT = 128
TAB_H = 12
BLACK = 0
WHITE = 15
TAB_LABELS = (("badge", "badge"), ("links", "links"), ("projects", "proyectos"))


def clear(d):
    d.set_pen(WHITE)
    d.clear()
    d.set_pen(BLACK)
    d.set_font("bitmap8")


def tabs(d, active):
    d.set_pen(BLACK)
    d.rectangle(0, 0, WIDTH, TAB_H)
    d.set_pen(WHITE)
    d.set_font("bitmap8")
    d.text("ivan@dishape", 3, 2, WIDTH, 1)
    x = WIDTH - 3
    for key, label in reversed(TAB_LABELS):
        shown = "[" + label + "]" if key == active else label
        x -= d.measure_text(shown, 1)
        d.text(shown, x, 2, WIDTH, 1)
        x -= 6
    d.set_pen(BLACK)


def window(d, x, y, w, h, title):
    d.set_pen(BLACK)
    d.rectangle(x, y, w, h)
    d.set_pen(WHITE)
    d.rectangle(x + 1, y + 10, w - 2, h - 11)
    d.set_font("bitmap6")
    d.text("[" + title + "]", x + 3, y + 2, w, 1)
    d.set_pen(BLACK)
    d.set_font("bitmap8")


def image(d, jpeg, path, x, y, w, h):
    try:
        jpeg.open_file(path)
        jpeg.decode(x, y, jpegdec.JPEG_SCALE_FULL, dither=False)
    except OSError:
        d.set_pen(BLACK)
        d.rectangle(x, y, w, h)
        d.set_pen(WHITE)
        d.rectangle(x + 1, y + 1, w - 2, h - 2)
        d.set_pen(BLACK)
        d.set_font("bitmap6")
        d.text(path, x + 3, y + 3, w - 6, 1)
        d.set_font("bitmap8")
