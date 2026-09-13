import pixfont
import ui

PORTRAIT = "assets/portrait.jpg"
NAME = "Ivan Cortes"
ROLE = "Full-stack dev"
PROMPT_X = 112
PROMPT_Y = 104


def draw(d, jpeg):
    ui.clear(d)
    ui.tabs(d, "badge")
    ui.window(d, 2, 14, 100, 112, "ivan.jpg")
    ui.image(d, jpeg, PORTRAIT, 4, 25, 96, 100)
    d.set_pen(ui.BLACK)
    d.text(NAME, 112, 28, 184, 2)
    pixfont.text(d, ROLE, 112, 52)
    pixfont.text(d, "dishape.dev", 112, 70)
    d.text("$", PROMPT_X, PROMPT_Y, 184, 2)
    cursor(d, True)


def cursor(d, visible):
    d.set_font("bitmap8")
    x = PROMPT_X + d.measure_text("$ ", 2)
    w = d.measure_text("_", 2)
    d.set_pen(ui.WHITE)
    d.rectangle(x, PROMPT_Y, w, 16)
    d.set_pen(ui.BLACK)
    if visible:
        d.text("_", x, PROMPT_Y, 184, 2)
    return (x, PROMPT_Y, w, 16)
