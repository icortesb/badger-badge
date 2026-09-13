import random
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
import quiz_screen
import state
import ui

APP_PATH = "state/app.json"
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
jpeg = jpegdec.JPEG(d.display)
link_items = links.items(state.load(CONTACT_PATH, links.CONTACT_DEFAULTS))
app = state.load(APP_PATH, nav.DEFAULTS)


def render(animate):
    d.set_update_speed(badger2040.UPDATE_MEDIUM)
    if app["tab"] == "links":
        links_screen.render(d, link_items, app["link"])
    elif app["tab"] == "projects":
        project = projects.PROJECTS[app["project"] % len(projects.PROJECTS)]
        projects_screen.render(d, project, animate)
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
        render(False)
    while True:
        d.keepalive()
        for pin, name in BUTTONS:
            if d.pressed(pin):
                before = (app["tab"], app["link"], app["project"])
                app, action = nav.handle(app, name, len(link_items), len(projects.PROJECTS))
                if action == "quiz":
                    wait_release()
                    quiz_screen.run(d, jpeg, random)
                    app["tab"] = "badge"
                    state.save(APP_PATH, app)
                    render(False)
                else:
                    state.save(APP_PATH, app)
                    after = (app["tab"], app["link"], app["project"])
                    if after != before:
                        render(True)
                wait_release()
                break
        d.halt()


def error_screen(exc):
    ui.clear(d)
    d.text("Error", 4, 4, 288, 2)
    d.text(repr(exc), 4, 26, 288, 1)
    d.text("Cualquier botón reinicia", 4, 116, 288, 1)
    d.update()


try:
    main()
except Exception as exc:
    error_screen(exc)
    try:
        state.save(APP_PATH, nav.DEFAULTS)
    except Exception:
        pass
    wait_release()
    while not d.pressed_any():
        d.halt()
    machine.reset()
