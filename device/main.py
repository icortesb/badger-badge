import time

import machine

import badger2040
import jpegdec

import badge_screen
import battery
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
BLINK_MS = 600
BATTERY_AWAKE_MS = 10000
USB_BLINK_MS = 60000

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
policy.partials = app["partials"]
if woken:
    buttons.add_wake_buttons(queue)

vbus_pin = machine.Pin(24, machine.Pin.IN)
# En un wake a batería (reboot) el framebuffer arranca en cero (negro) y sin fuente
# bitmap8 seteada: draw_cursor no puede parpetear sobre eso sin pintar la pestaña primero.
framebuffer_ready = False


def on_usb():
    return vbus_pin.value() == 1


def current_project():
    return projects.PROJECTS[app["project"] % len(projects.PROJECTS)]


def draw_cursor(visible):
    global framebuffer_ready
    if not framebuffer_ready:
        ui.battery_volts = None if on_usb() else battery.read_volts()
        if app["tab"] == "badge":
            badge_screen.draw(d, jpeg)
        elif app["tab"] == "projects":
            projects_screen.draw(d, current_project())
        framebuffer_ready = True
    if app["tab"] == "badge":
        return badge_screen.cursor(d, visible)
    if app["tab"] == "projects":
        return projects_screen.cursor(d, current_project(), visible)
    return None


def type_project(kind):
    project = current_project()
    total = len(project["lines"])
    projects_screen.draw(d, project, lines=1, qr=False)
    screen.show(d, policy, kind, screen.CONTENT)
    for i in range(1, total):
        if queue.pending():
            projects_screen.draw(d, project)
            screen.show(d, policy, "content", screen.CONTENT)
            return
        projects_screen.draw_line(d, project, i)
        screen.show(d, policy, "detail", projects_screen.line_region(i))
    if queue.pending():
        projects_screen.draw(d, project)
        screen.show(d, policy, "content", screen.CONTENT)
        return
    projects_screen.draw_qr(d, project)
    screen.show(d, policy, "detail", projects_screen.QR_REGION)


def render(kind):
    global framebuffer_ready
    ui.battery_volts = None if on_usb() else battery.read_volts()
    if app["tab"] == "projects":
        type_project(kind)
        framebuffer_ready = True
        return
    if app["tab"] == "links":
        links_screen.draw(d, link_items, app["link"])
    else:
        badge_screen.draw(d, jpeg)
    screen.show(d, policy, kind, screen.CONTENT)
    framebuffer_ready = True


def wait_release():
    while d.pressed_any():
        d.keepalive()
        time.sleep_ms(10)


def main(cold):
    global app
    cursor_on = True
    now = time.ticks_ms()
    awake_until = time.ticks_add(now, BATTERY_AWAKE_MS)
    blink_until = time.ticks_add(now, USB_BLINK_MS)
    next_blink = time.ticks_add(now, BLINK_MS)
    if cold:
        app["tab"] = "badge"
        app["combo"] = 0
        state.save(APP_PATH, app)
        render("tab")
    while True:
        d.keepalive()
        now = time.ticks_ms()
        name = queue.pop(now)
        if name is not None and name != "exit":
            before = (app["tab"], app["link"], app["project"])
            before_app = dict(app)
            app, action = nav.handle(app, name, len(link_items), len(projects.PROJECTS))
            if action == "quiz":
                # Import diferido: el quiz no se carga en cada wake a batería.
                import random
                import quiz_screen
                quiz_screen.run(d, jpeg, random, queue)
                app["tab"] = "badge"
                app["partials"] = policy.partials
                state.save(APP_PATH, app)
                render("tab")
            else:
                app["partials"] = policy.partials
                if app != before_app:
                    state.save(APP_PATH, app)
                if app["tab"] != before[0]:
                    render("tab")
                elif (app["link"], app["project"]) != before[1:]:
                    render("content")
            cursor_on = True
            now = time.ticks_ms()
            awake_until = time.ticks_add(now, BATTERY_AWAKE_MS)
            blink_until = time.ticks_add(now, USB_BLINK_MS)
            next_blink = time.ticks_add(now, BLINK_MS)
            continue
        if queue.pending():
            time.sleep_ms(10)
            continue
        usb = on_usb()
        # En USB nunca se apaga: sólo importa si todavía estamos dentro de la
        # ventana de parpadeo (se reinicia con cada evento). En batería, la
        # ventana de "despierto" antes de halt() se mantiene igual que antes.
        if usb:
            blinking = time.ticks_diff(blink_until, now) > 0
        else:
            blinking = time.ticks_diff(awake_until, now) > 0
        if blinking and time.ticks_diff(now, next_blink) >= 0:
            region = draw_cursor(not cursor_on)
            if region is not None:
                cursor_on = not cursor_on
                screen.show(d, policy, "detail", region)
            next_blink = time.ticks_add(time.ticks_ms(), BLINK_MS)
        if not blinking and not cursor_on:
            # Se acabó la ventana de parpadeo (USB) o el rato despierto (batería):
            # dejar el cursor sólido una sola vez y no seguir titilando.
            region = draw_cursor(True)
            if region is not None:
                screen.show(d, policy, "detail", region)
            cursor_on = True
        if not usb and not blinking:
            if queue.pending():
                continue
            d.halt()
            # Si seguimos vivos (botón apretado), seguir atendiendo.
            awake_until = time.ticks_add(time.ticks_ms(), BATTERY_AWAKE_MS)
        time.sleep_ms(10)


def error_screen(exc):
    ui.clear(d)
    d.text("Error", 4, 4, 288, 2)
    d.text(repr(exc), 4, 26, 288, 1)
    d.text("Cualquier botón reinicia", 4, 116, 288, 1)
    d.set_update_speed(badger2040.UPDATE_MEDIUM)
    d.update()


if DEV_MODE:
    ui.clear(d)
    d.text("Modo dev: REPL", 4, 40, 288, 2)
    d.update()
else:
    cold = not woken
    while True:
        try:
            main(cold)
        except Exception as exc:
            error_screen(exc)
            try:
                state.save(APP_PATH, dict(nav.DEFAULTS, tab="badge"))
            except Exception:
                pass
            queue.clear()
            wait_release()
            while not d.pressed_any():
                if on_usb():
                    d.keepalive()
                    time.sleep_ms(50)
                else:
                    d.halt()
            wait_release()
            queue.clear()
            app = state.load(APP_PATH, nav.DEFAULTS)
            policy.partials = app["partials"]
            cold = True
