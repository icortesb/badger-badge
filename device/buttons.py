# Botones: los flancos se capturan en una IRQ dura (hard=True) que sólo toca
# arrays preasignados (nada de listas: una IRQ dura no puede pedir memoria).
# El loop principal drena ese buffer circular hacia la ButtonQueue real.
import array

DEBOUNCE_MS = 60
CHORD_MS = 150
IDLE_MS = 120000
PINS = ((12, "a"), (13, "b"), (14, "c"), (15, "up"), (11, "down"))
NAMES = tuple(name for _, name in PINS)
CHORD = ("up", "down")
RING = 32

# ticks_ms envuelve en 2^30: usar ticks_diff cuando está disponible (MicroPython);
# en CPython (tests) el módulo time no lo tiene, así que restamos directo.
try:
    from time import ticks_diff as _diff
except ImportError:
    def _diff(a, b):
        return a - b

# Buffer circular: la IRQ sólo escribe _pos[0] (head), el loop principal sólo
# escribe _pos[1] (tail) al drenar. Un int de un array es una sola palabra de
# 32 bits: en un solo núcleo (RP2040 corriendo esto en el core 0) no hace
# falta lock para que la IRQ y el loop se pisen. Se sacrifica un slot para
# distinguir "lleno" de "vacío" sin un contador aparte.
_ring_idx = array.array("i", [0] * RING)
_ring_ms = array.array("i", [0] * RING)
_pos = array.array("i", [0, 0])  # [0] = head (IRQ), [1] = tail (drain)
_last_edge = array.array("i", [-100000] * len(PINS))


def accept_edge(last_ms, now_ms, pressed):
    # Función pura con la decisión de debounce de la IRQ, testeable sin
    # hardware: hay que seguir presionado (filtra rebote de liberación) y
    # que haya pasado DEBOUNCE_MS desde el último flanco ACEPTADO (no desde
    # el último rebote, así un tren de rebotes no corre la ventana).
    return bool(pressed) and _diff(now_ms, last_ms) >= DEBOUNCE_MS


def drain(queue):
    # Sólo lo llama el loop principal (nunca la IRQ): puede asignar memoria
    # sin problema. Mueve todo lo que la IRQ juntó en el ring hacia queue.
    head = _pos[0]
    tail = _pos[1]
    while tail != head:
        queue.push_raw(NAMES[_ring_idx[tail]], _ring_ms[tail])
        tail += 1
        if tail == RING:
            tail = 0
    _pos[1] = tail


class ButtonQueue:
    def __init__(self, chord=False, source=None):
        self._events = []
        self._last = {}
        # El combo ▲+▼ ("exit") sólo tiene sentido dentro del quiz; fuera de
        # él, esperar CHORD_MS a un posible partner sólo demoraría ▲/▼.
        self.chord = chord
        # Se llama antes de pending()/pop(): install() lo apunta a drain(self)
        # para no tener que acordarse de drenar en cada lugar que consulta la cola.
        self.source = source

    def _pull(self):
        if self.source is not None:
            self.source()

    def push(self, name, now_ms):
        # Debounce por software para tests/uso directo; en el badge real el
        # debounce ya pasó en la IRQ (accept_edge) antes de llegar acá.
        last = self._last.get(name, -100000)
        if not accept_edge(last, now_ms, True):
            return
        self._last[name] = now_ms
        self._events.append((name, now_ms))

    def push_raw(self, name, now_ms):
        # Ya debounceado (viene del ring o de add_wake_buttons): encolar directo.
        self._events.append((name, now_ms))

    def pending(self):
        self._pull()
        return len(self._events) > 0

    def clear(self):
        self._events = []

    def pop(self, now_ms):
        self._pull()
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
    queue.source = lambda: drain(queue)
    for i, (pin, _name) in enumerate(PINS):
        def handler(_pin, i=i):
            # IRQ dura: nada de asignar memoria acá. El flanco de subida puede
            # llegar con la línea ya vuelta a bajar (rebote de liberación muy
            # corto); accept_edge exige que siga en alto.
            now = time.ticks_ms()
            if accept_edge(_last_edge[i], now, _pin.value() == 1):
                head = _pos[0]
                nxt = head + 1
                if nxt == RING:
                    nxt = 0
                if nxt != _pos[1]:
                    _ring_idx[head] = i
                    _ring_ms[head] = now
                    _pos[0] = nxt
                # Si el ring está lleno el evento se pierde, pero el debounce
                # sigue midiendo desde este flanco igual.
                _last_edge[i] = now

        badger2040.BUTTONS[pin].irq(trigger=machine.Pin.IRQ_RISING, handler=handler, hard=True)
    return queue


def add_wake_buttons(queue):
    import badger2040
    import time

    for pin, name in PINS:
        if badger2040.pressed_to_wake_get_once(pin):
            queue.push_raw(name, time.ticks_ms())


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
