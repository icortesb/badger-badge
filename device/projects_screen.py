import ui

LINE_H = 11
QR_REGION = (182, 14, 112, 112)


def line_region(i):
    return (4, 16 + i * LINE_H, 176, LINE_H)


def _is_cursor_line(project, i):
    lines = project["lines"]
    return i == len(lines) - 1 and lines[i].endswith("_")


def draw_line(d, project, i):
    line = project["lines"][i]
    d.set_pen(ui.BLACK)
    if _is_cursor_line(project, i):
        d.text(line[:-1], 4, 16 + i * LINE_H, 288, 1)
        cursor(d, project, True)
    else:
        d.text(line, 4, 16 + i * LINE_H, 288, 1)


def draw_qr(d, project):
    ui.qr(d, project["url"], QR_REGION[0], QR_REGION[1], QR_REGION[2])


def draw(d, project, lines=None, qr=True):
    ui.clear(d)
    ui.tabs(d, "projects")
    count = len(project["lines"]) if lines is None else lines
    for i in range(count):
        draw_line(d, project, i)
    if qr:
        draw_qr(d, project)


def cursor(d, project, visible):
    i = len(project["lines"]) - 1
    prefix = project["lines"][i][:-1]
    x = 4 + d.measure_text(prefix, 1)
    y = 16 + i * LINE_H
    w = d.measure_text("_", 1)
    d.set_pen(ui.WHITE)
    d.rectangle(x, y, w, LINE_H)
    d.set_pen(ui.BLACK)
    if visible:
        d.text("_", x, y, 288, 1)
    return (x, y, w, LINE_H)
