# Política de refresco del e-ink: completo al cambiar de pestaña, parcial dentro de ella.
WIDTH = 296
HEIGHT = 128
CONTENT = (0, 12, 296, 116)
CLEANUP_EVERY = 8
FULL = "full"
PARTIAL = "partial"
FAST = "fast"
TURBO = "turbo"


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

    def plan(self, kind, region=None):
        if kind == "tab":
            self.partials = 0
            return FULL, FAST, None
        if kind == "content":
            self.partials += 1
            if self.partials >= CLEANUP_EVERY:
                self.partials = 0
                return FULL, FAST, None
            return PARTIAL, TURBO, align(*region)
        if kind == "detail":
            self.partials += 1
            return PARTIAL, TURBO, align(*region)
        raise ValueError(kind)


def show(d, policy, kind, region=None):
    import badger2040

    mode, speed, area = policy.plan(kind, region)
    d.set_update_speed(badger2040.UPDATE_FAST if speed == FAST else badger2040.UPDATE_TURBO)
    if mode == FULL:
        d.display.update()
    else:
        d.display.partial_update(*area)
