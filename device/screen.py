# Política de refresco del e-ink: completo al cambiar de pestaña, parcial dentro de ella.
WIDTH = 296
HEIGHT = 128
CONTENT = (0, 12, 296, 116)
CLEANUP_EVERY = 8
FULL = "full"
PARTIAL = "partial"
FAST = "fast"
TURBO = "turbo"
NORMAL = "normal"


def align(x, y, w, h):
    # El UC8151 refresca por bloques de 8 px: expandir la región y recortarla a la pantalla.
    x0 = max(0, (x // 8) * 8)
    y0 = max(0, (y // 8) * 8)
    x1 = min(WIDTH, -(-(x + w) // 8) * 8)
    y1 = min(HEIGHT, -(-(y + h) // 8) * 8)
    return x0, y0, x1 - x0, y1 - y0


class Policy:
    def __init__(self):
        self.partials = 0
        # Refrescos parciales (content o detail) desde el último refresco
        # completo de cualquier tipo: cuenta cuánto fantasma puede haber
        # acumulado la pantalla, para saber si vale la pena una limpieza NORMAL.
        self.dirty = 0

    def plan(self, kind, region=None, speed=None):
        if kind == "tab":
            self.partials = 0
            self.dirty = 0
            return FULL, FAST, None
        if kind == "content":
            self.partials += 1
            if self.partials >= CLEANUP_EVERY:
                self.partials = 0
                self.dirty = 0
                return FULL, FAST, None
            self.dirty += 1
            return PARTIAL, speed or TURBO, align(*region)
        if kind == "detail":
            # Los detalles (cursor, líneas tipeadas, QR) no cuentan para el cleanup
            # periódico: son parches chicos, no el motivo de que el e-ink se ensucie.
            # `speed` deja pisar el TURBO por defecto: un parche denso (el QR)
            # no termina de asentar los píxeles con TURBO y queda gris/lavado.
            # Sí suman a `dirty`: son parciales igual, y también ensucian la
            # pantalla de a poco (el cursor titilando, sobre todo).
            self.dirty += 1
            return PARTIAL, speed or TURBO, align(*region)
        if kind == "clean":
            self.partials = 0
            self.dirty = 0
            return FULL, NORMAL, None
        raise ValueError(kind)


def show(d, policy, kind, region=None, speed=None):
    import badger2040

    mode, chosen_speed, area = policy.plan(kind, region, speed)
    if chosen_speed == FAST:
        update_speed = badger2040.UPDATE_FAST
    elif chosen_speed == NORMAL:
        update_speed = badger2040.UPDATE_NORMAL
    else:
        update_speed = badger2040.UPDATE_TURBO
    d.set_update_speed(update_speed)
    if mode == FULL:
        d.display.update()
    else:
        d.display.partial_update(*area)
