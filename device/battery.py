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


def volts_from_adc(battery_raw, vref_raw):
    if vref_raw <= 0:
        return 0.0
    vdd = 1.24 * (65535 / vref_raw)
    return (battery_raw / 65535) * 3 * vdd


def read_volts():
    import machine
    import time

    en = machine.Pin(27, machine.Pin.OUT)
    en.value(1)
    time.sleep_ms(10)
    vref_raw = machine.ADC(28).read_u16()
    battery_raw = machine.ADC(29).read_u16()
    en.value(0)
    return volts_from_adc(battery_raw, vref_raw)
