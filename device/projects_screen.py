import ui

LINE_H = 11


def render(d, project):
    ui.clear(d)
    ui.tabs(d, "projects")
    d.set_pen(ui.BLACK)
    for i, line in enumerate(project["lines"]):
        d.text(line, 4, 16 + i * LINE_H, 288, 1)
    ui.qr(d, project["url"], 182, 14, 112)
    d.update()
