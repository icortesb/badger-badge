# Nivel de batería del Badger 2040 (2 pilas AAA). El pin 29 lee VSYS / 3.
FULL_V = 3.0
EMPTY_V = 2.2
LEVELS = 4


def level(volts):
    if volts <= EMPTY_V:
        return 0
    if volts >= FULL_V:
        return LEVELS
    return int((volts - EMPTY_V) / (FULL_V - EMPTY_V) * LEVELS + 0.5)


def label(volts):
    return "{:.1f}V".format(volts)


def read_volts():
    import machine

    return machine.ADC(29).read_u16() * 3 * 3.3 / 65535
