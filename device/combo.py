SEQUENCE = ("up", "up", "down", "down", "a", "b")


def advance(progress, button, sequence=SEQUENCE):
    progress = max(0, min(progress, len(sequence) - 1))
    pressed = list(sequence[:progress]) + [button]
    for start in range(len(pressed)):
        tail = tuple(pressed[start:])
        if tail == tuple(sequence[:len(tail)]):
            if len(tail) == len(sequence):
                return 0, True
            return len(tail), False
    return 0, False
