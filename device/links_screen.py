import pixfont
import ui

QR_BOX = 112


def draw(d, items, index):
    ui.clear(d)
    ui.tabs(d, "links")
    if not items:
        d.text("Sin links", 8, 30, 280, 2)
        return
    index %= len(items)
    item = items[index]
    ui.qr(d, item["payload"], 2, 14, QR_BOX)
    d.set_pen(ui.BLACK)
    d.text(item["label"], 122, 26, 170, 2)
    pixfont.text(d, item["text"], 122, 50)
    d.text("{}/{}".format(index + 1, len(items)), 122, 112, 170, 1)
