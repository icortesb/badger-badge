import gc
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
BLINK_MS = 1200
BLINKS = 2
IDLE_CLEAN_MS = 3000

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
policy.partials = nav._int(app["partials"])
if woken:
    buttons.add_wake_buttons(queue)

vbus_pin = machine.Pin(24, machine.Pin.IN)
# Ver ensure_framebuffer(): en un wake a batería (reboot) arranca en False.
framebuffer_ready = False


def on_usb():
    return vbus_pin.value() == 1


def current_project():
    return projects.PROJECTS[app["project"] % len(projects.PROJECTS)]


def ensure_framebuffer():
    # En un wake a batería (reboot) el framebuffer arranca en cero (negro) y sin
    # fuente bitmap8 seteada: draw_cursor y la limpieza no pueden operar sobre
    # eso sin pintar la pestaña primero. Sólo dibuja una vez por wake.
    global framebuffer_ready
    if framebuffer_ready:
        return
    ui.battery_volts = None if on_usb() else battery.read_volts()
    if app["tab"] == "badge":
        badge_screen.draw(d, jpeg)
    elif app["tab"] == "projects":
        projects_screen.draw(d, current_project())
    framebuffer_ready = True


def draw_cursor(visible):
    ensure_framebuffer()
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
    if cold:
        app["tab"] = "badge"
        app["combo"] = 0
        render("tab")
        app["partials"] = policy.partials
        state.save(APP_PATH, app)
    now = time.ticks_ms()
    cursor_on = True
    toggles_left = BLINKS * 2
    next_blink = time.ticks_add(now, BLINK_MS)
    last_event_ms = now
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
                render("tab")
                app["partials"] = policy.partials
                state.save(APP_PATH, app)
            else:
                if app["tab"] != before[0]:
                    render("tab")
                elif (app["link"], app["project"]) != before[1:]:
                    render("content")
                app["partials"] = policy.partials
                if app != before_app:
                    state.save(APP_PATH, app)
            now = time.ticks_ms()
            cursor_on = True
            toggles_left = BLINKS * 2
            next_blink = time.ticks_add(now, BLINK_MS)
            last_event_ms = now
            continue
        if queue.pending():
            time.sleep_ms(10)
            continue
        # Cursor: titila BLINKS veces (cada titileo son 2 cambios de estado)
        # y queda fijo visible. Después de un rato quieto, si hubo refrescos
        # parciales, una limpieza NORMAL completa saca el fantasma acumulado.
        if toggles_left > 0 and time.ticks_diff(now, next_blink) >= 0:
            region = draw_cursor(not cursor_on)
            if region is not None:
                cursor_on = not cursor_on
                screen.show(d, policy, "detail", region)
                toggles_left -= 1
            else:
                # Pestaña sin cursor (links): nada que titilar.
                toggles_left = 0
            next_blink = time.ticks_add(time.ticks_ms(), BLINK_MS)
        if toggles_left == 0 and not cursor_on:
            # No debería pasar (el titileo siempre termina visible), pero por
            # las dudas: dejar el cursor sólido en vez de apagado.
            region = draw_cursor(True)
            if region is not None:
                screen.show(d, policy, "detail", region)
            cursor_on = True
        if (
            toggles_left == 0
            and time.ticks_diff(now, last_event_ms) >= IDLE_CLEAN_MS
            and policy.dirty > 0
        ):
            ensure_framebuffer()
            screen.show(d, policy, "clean")
            if app["partials"] != policy.partials:
                app["partials"] = policy.partials
                state.save(APP_PATH, app)
        if not on_usb() and toggles_left == 0 and policy.dirty == 0:
            if queue.pending():
                continue
            d.halt()
            # Si seguimos vivos (botón apretado), el próximo pop() de la cola
            # entra por la rama de arriba y reinicia el titileo; si no, la
            # cola sigue vacía y este bloque vuelve a llamar a halt().
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
            try:
                gc.collect()
                error_screen(exc)
            except Exception:
                pass
            try:
                state.save(APP_PATH, dict(nav.DEFAULTS, tab="error"))
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
            policy.partials = nav._int(app["partials"])
            cold = True
