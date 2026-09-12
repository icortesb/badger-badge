import pixfont
import ui

PORTRAIT = "assets/portrait.jpg"
NAME = "Ivan Cortes"
ROLE = "Full-stack dev"


def render(d, jpeg):
    ui.clear(d)
    ui.tabs(d, "badge")
    ui.window(d, 2, 14, 100, 112, "ivan.jpg")
    ui.image(d, jpeg, PORTRAIT, 4, 25, 96, 100)
    d.set_pen(ui.BLACK)
    d.text(NAME, 112, 28, 184, 2)
    pixfont.text(d, ROLE, 112, 52)
    pixfont.text(d, "dishape.dev", 112, 70)
    d.text("$ _", 112, 104, 184, 2)
    d.update()
