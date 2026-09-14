# Nivel de batería del Badger 2040 (2 pilas AAA). El GPIO29 no está cableado
# en esta revisión de placa: en vez de medir VSYS directamente, se mide la
# propia alimentación (VDD) contra la referencia de 1.24V en GPIO28. Con
# batería el regulador entra en dropout (VDD < 3.3V), así que VDD sigue de
# cerca la tensión de las pilas; con USB no se muestra (VDD ronda 3.24-3.3V,
# el riel de 3.3V, y no refleja batería alguna).
FULL_V = 3.0
EMPTY_V = 2.3
LEVELS = 4


def level(volts):
    if volts <= EMPTY_V:
        return 0
    if volts >= FULL_V:
        return LEVELS
    return int((volts - EMPTY_V) / (FULL_V - EMPTY_V) * LEVELS + 0.5)


def label(volts):
    return "{:.1f}V".format(volts)


def vdd_from_ref(vref_raw):
    if vref_raw <= 0:
        return 0.0
    return 1.24 * 65535 / vref_raw


def read_volts():
    import machine
    import time

    en = machine.Pin(27, machine.Pin.OUT)
    en.value(1)
    time.sleep_ms(10)
    total = 0
    for _ in range(4):
        total += machine.ADC(28).read_u16()
    en.value(0)
    return vdd_from_ref(total / 4)
