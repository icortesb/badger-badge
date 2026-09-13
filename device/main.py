import time

import machine

import badger2040
import jpegdec

import badge_screen
import links
import links_screen
import nav
import projects
import projects_screen
import state
import ui

APP_PATH = "data/app.json"
CONTACT_PATH = "assets/contact.json"
BUTTONS = (
    (badger2040.BUTTON_A, "a"),
    (badger2040.BUTTON_B, "b"),
    (badger2040.BUTTON_C, "c"),
    (badger2040.BUTTON_UP, "up"),
    (badger2040.BUTTON_DOWN, "down"),
)

woken = badger2040.woken_by_button()
d = badger2040.Badger2040()
DEV_MODE = badger2040.pressed_to_wake(badger2040.BUTTON_A) and badger2040.pressed_to_wake(badger2040.BUTTON_C)
jpeg = jpegdec.JPEG(d.display)
link_items = links.items(state.load(CONTACT_PATH, links.CONTACT_DEFAULTS))
app = state.load(APP_PATH, nav.DEFAULTS)


def render():
    d.set_update_speed(badger2040.UPDATE_MEDIUM)
    if app["tab"] == "links":
        links_screen.render(d, link_items, app["link"])
    elif app["tab"] == "projects":
        project = projects.PROJECTS[app["project"] % len(projects.PROJECTS)]
        projects_screen.render(d, project)
    else:
        badge_screen.render(d, jpeg)


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
        render()
    while True:
        d.keepalive()
        for pin, name in BUTTONS:
            if d.pressed(pin):
                before = (app["tab"], app["link"], app["project"])
                before_app = dict(app)
                app, action = nav.handle(app, name, len(link_items), len(projects.PROJECTS))
                if action == "quiz":
                    wait_release()
                    # Import diferido: el quiz no se carga en cada wake a batería.
                    import random
                    import quiz_screen
                    quiz_screen.run(d, jpeg, random)
                    app["tab"] = "badge"
                    state.save(APP_PATH, app)
                    render()
                else:
                    if app != before_app:
                        state.save(APP_PATH, app)
                    after = (app["tab"], app["link"], app["project"])
                    if after != before:
                        render()
                wait_release()
                break
        d.halt()


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
