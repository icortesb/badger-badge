# Botones: cola de eventos capturados por interrupción (no se pierden durante un refresco).
DEBOUNCE_MS = 150
CHORD_MS = 150
IDLE_MS = 120000
PINS = ((12, "a"), (13, "b"), (14, "c"), (15, "up"), (11, "down"))
CHORD = ("up", "down")

# ticks_ms envuelve en 2^30: usar ticks_diff cuando está disponible (MicroPython);
# en CPython (tests) el módulo time no lo tiene, así que restamos directo.
try:
    from time import ticks_diff as _diff
except ImportError:
    def _diff(a, b):
        return a - b


class ButtonQueue:
    def __init__(self, chord=False):
        self._events = []
        self._last = {}
        # El combo ▲+▼ ("exit") sólo tiene sentido dentro del quiz; fuera de él,
        # esperar CHORD_MS a un posible partner sólo agrega latencia a la navegación.
        self.chord = chord

    def push(self, name, now_ms):
        last = self._last.get(name)
        # Registrar siempre, incluso si se descarta por rebote: un tren de rebotes
        # sigue extendiendo la ventana de debounce en vez de reiniciarla desde el primero.
        self._last[name] = now_ms
        if last is not None and _diff(now_ms, last) < DEBOUNCE_MS:
            return
        self._events.append((name, now_ms))

    def pending(self):
        return len(self._events) > 0

    def clear(self):
        self._events = []

    def pop(self, now_ms):
        if not self._events:
            return None
        name, at = self._events[0]
        if self.chord and name in CHORD:
            partner = self._events[1] if len(self._events) > 1 else None
            if partner is not None and partner[0] in CHORD and partner[0] != name and _diff(partner[1], at) < CHORD_MS:
                del self._events[0:2]
                return "exit"
            if partner is None and _diff(now_ms, at) < CHORD_MS:
                return None
        del self._events[0]
        return name


def install():
    import badger2040
    import machine
    import time

    queue = ButtonQueue()
    for pin, name in PINS:
        def handler(_pin, name=name):
            # El flanco de subida puede llegar con la línea ya vuelta a bajar (rebote
            # de contacto muy corto): sólo encolar si sigue en alto.
            if _pin.value() == 1:
                queue.push(name, time.ticks_ms())

        badger2040.BUTTONS[pin].irq(trigger=machine.Pin.IRQ_RISING, handler=handler)
    return queue


def add_wake_buttons(queue):
    import badger2040
    import time

    for pin, name in PINS:
        if badger2040.pressed_to_wake_get_once(pin):
            queue.push(name, time.ticks_ms())


def wait(d, queue, idle_ms=IDLE_MS):
    import time

    start = time.ticks_ms()
    while True:
        d.keepalive()
        now = time.ticks_ms()
        event = queue.pop(now)
        if event is not None:
            return event
        if time.ticks_diff(now, start) > idle_ms:
            return "exit"
        time.sleep_ms(10)
