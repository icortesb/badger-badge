import qrcode
import ui

QR_BOX = 112


def draw_qr(d, payload, x, y, box):
    code = qrcode.QRCode()
    code.set_text(payload)
    w, h = code.get_size()
    module = max(1, box // w)
    ox = x + (box - module * w) // 2
    oy = y + (box - module * h) // 2
    d.set_pen(ui.WHITE)
    d.rectangle(x, y, box, box)
    d.set_pen(ui.BLACK)
    for my in range(h):
        for mx in range(w):
            if code.get_module(mx, my):
                d.rectangle(ox + mx * module, oy + my * module, module, module)
    return module


def render(d, items, index):
    ui.clear(d)
    ui.tabs(d, "links")
    if not items:
        d.text("Sin links", 8, 30, 280, 2)
        d.update()
        return
    index %= len(items)
    item = items[index]
    draw_qr(d, item["payload"], 2, 14, QR_BOX)
    d.set_pen(ui.BLACK)
    d.text(item["label"], 122, 26, 170, 2)
    d.text(item["text"], 122, 50, 170, 1)
    d.text("{}/{}".format(index + 1, len(items)), 122, 112, 170, 1)
    d.update()
