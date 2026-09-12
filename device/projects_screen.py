import badger2040
import ui

LINE_H = 11


def _draw(d, project, count):
    ui.clear(d)
    ui.tabs(d, "projects")
    d.set_pen(ui.BLACK)
    for i, line in enumerate(project["lines"][:count]):
        d.text(line, 4, 16 + i * LINE_H, 288, 1)


def render(d, project, animate):
    lines = project["lines"]
    if animate:
        d.set_update_speed(badger2040.UPDATE_TURBO)
        for count in range(1, len(lines)):
            _draw(d, project, count)
            d.update()
        d.set_update_speed(badger2040.UPDATE_FAST)
    _draw(d, project, len(lines))
    d.update()
