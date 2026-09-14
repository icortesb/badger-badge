# QR precalculados: la matriz se guarda como tramos negros por fila.
import binascii
import hashlib


def key(payload):
    return binascii.hexlify(hashlib.sha256(payload.encode()).digest()[:6]).decode()


def path(payload):
    return "assets/qr/" + key(payload) + ".bin"


def encode(matrix):
    size = len(matrix)
    out = bytearray([size])
    for row in matrix:
        runs = []
        x = 0
        while x < size:
            if row[x]:
                start = x
                while x < size and row[x]:
                    x += 1
                runs.append((start, x - start))
            else:
                x += 1
        out.append(len(runs))
        for start, length in runs:
            out.append(start)
            out.append(length)
    return bytes(out)


def decode(data):
    size = data[0]
    rows = []
    i = 1
    for _ in range(size):
        count = data[i]
        i += 1
        runs = []
        for _ in range(count):
            runs.append((data[i], data[i + 1]))
            i += 2
        rows.append(runs)
    return size, rows
