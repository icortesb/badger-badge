import time

import badger2040

NAMES = (
    (badger2040.BUTTON_A, "a"),
    (badger2040.BUTTON_B, "b"),
    (badger2040.BUTTON_C, "c"),
    (badger2040.BUTTON_UP, "up"),
    (badger2040.BUTTON_DOWN, "down"),
)
IDLE_MS = 120000


def read(d):
    return {name for pin, name in NAMES if d.pressed(pin)}


def wait(d, idle_ms=IDLE_MS):
    start = time.ticks_ms()
    while True:
        d.keepalive()
        pressed = read(d)
        if pressed:
            time.sleep_ms(60)
            pressed |= read(d)
            while d.pressed_any():
                d.keepalive()
                pressed |= read(d)
                time.sleep_ms(10)
            if "up" in pressed and "down" in pressed:
                return "exit"
            for _, name in NAMES:
                if name in pressed:
                    return name
        if time.ticks_diff(time.ticks_ms(), start) > idle_ms:
            return "exit"
        time.sleep_ms(10)
