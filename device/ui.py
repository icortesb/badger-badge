import jpegdec
import qrcode

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


def qr(d, payload, x, y, box):
    code = qrcode.QRCode()
    code.set_text(payload)
    w, h = code.get_size()
    module = max(1, box // w)
    ox = x + (box - module * w) // 2
    oy = y + (box - module * h) // 2
    d.set_pen(WHITE)
    d.rectangle(x, y, box, box)
    d.set_pen(BLACK)
    for my in range(h):
        for mx in range(w):
            if code.get_module(mx, my):
                d.rectangle(ox + mx * module, oy + my * module, module, module)
    return module


def image(d, jpeg, path, x, y, w, h):
    try:
        jpeg.open_file(path)
        jpeg.decode(x, y, jpegdec.JPEG_SCALE_FULL, dither=False)
        d.set_pen(BLACK)
    except OSError:
        d.set_pen(BLACK)
        d.rectangle(x, y, w, h)
        d.set_pen(WHITE)
        d.rectangle(x + 1, y + 1, w - 2, h - 2)
        d.set_pen(BLACK)
        d.set_font("bitmap6")
        d.text(path, x + 3, y + 3, w - 6, 1)
        d.set_font("bitmap8")
