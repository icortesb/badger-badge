import time

import machine

import badger2040
import jpegdec

import badge_screen
import buttons
import links
import links_screen
import nav
import projects
import projects_screen
import screen
import state
import ui

APP_PATH = "data/app.json"
CONTACT_PATH = "assets/contact.json"

woken = badger2040.woken_by_button()
d = badger2040.Badger2040()
# Sólo entra en modo dev con USB conectado (VBUS_DETECT = GPIO 24 en el Badger 2040):
# así A+C en batería no puede dejar la placa despierta en el REPL.
DEV_MODE = (
    machine.Pin(24, machine.Pin.IN).value() == 1
    and badger2040.pressed_to_wake(badger2040.BUTTON_A)
    and badger2040.pressed_to_wake(badger2040.BUTTON_C)
)
jpeg = jpegdec.JPEG(d.display)
link_items = links.items(state.load(CONTACT_PATH, links.CONTACT_DEFAULTS))
app = state.load(APP_PATH, nav.DEFAULTS)
queue = buttons.install()
policy = screen.Policy()
if woken:
    buttons.add_wake_buttons(queue)


def render(kind):
    if app["tab"] == "links":
        links_screen.draw(d, link_items, app["link"])
    elif app["tab"] == "projects":
        project = projects.PROJECTS[app["project"] % len(projects.PROJECTS)]
        projects_screen.draw(d, project)
    else:
        badge_screen.draw(d, jpeg)
    screen.show(d, policy, kind, screen.CONTENT)


def wait_release():
    while d.pressed_any():
        d.keepalive()
        time.sleep_ms(10)


def main():
    global app
    if not woken:
        app["tab"] = "badge"
        app["combo"] = 0
        state.save(APP_PATH, app)
        render("tab")
    while True:
        d.keepalive()
        name = queue.pop(time.ticks_ms())
        if name is None or name == "exit":
            if not queue.pending():
                d.halt()
            time.sleep_ms(10)
            continue
        before = (app["tab"], app["link"], app["project"])
        before_app = dict(app)
        app, action = nav.handle(app, name, len(link_items), len(projects.PROJECTS))
        if action == "quiz":
            # Import diferido: el quiz no se carga en cada wake a batería.
            import random
            import quiz_screen
            quiz_screen.run(d, jpeg, random, queue)
            app["tab"] = "badge"
            state.save(APP_PATH, app)
            render("tab")
        else:
            if app != before_app:
                state.save(APP_PATH, app)
            if app["tab"] != before[0]:
                render("tab")
            elif (app["link"], app["project"]) != before[1:]:
                render("content")


def error_screen(exc):
    ui.clear(d)
    d.text("Error", 4, 4, 288, 2)
    d.text(repr(exc), 4, 26, 288, 1)
    d.text("Cualquier botón reinicia", 4, 116, 288, 1)
    d.update()


if DEV_MODE:
    ui.clear(d)
    d.text("Modo dev: REPL", 4, 40, 288, 2)
    d.update()
else:
    try:
        main()
    except Exception as exc:
        error_screen(exc)
        try:
            state.save(APP_PATH, dict(nav.DEFAULTS, tab="error"))
        except Exception:
            pass
        wait_release()
        while not d.pressed_any():
            d.halt()
        machine.reset()
