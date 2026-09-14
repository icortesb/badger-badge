# Reinicia la app del badge sin reset de hardware ni re-enchufar: por serial,
# interrumpir (Ctrl-C x2), entrar al REPL normal (Ctrl-B) y forzar un soft
# reboot (Ctrl-D), que sí corre main.py (a diferencia de machine.soft_reset()
# desde el raw REPL, o de `mpremote reset`, que en placas con solo USB puede
# dejarlas sin energía).
import sys
import time

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
TIMEOUT_S = 2.0


def main():
    s = serial.Serial(PORT, 115200, timeout=0.2)
    buf = b""
    found = False
    try:
        s.write(b"\r\x03\x03")
        time.sleep(0.3)
        s.write(b"\x02")
        time.sleep(0.3)
        s.reset_input_buffer()
        s.write(b"\x04")
        deadline = time.time() + TIMEOUT_S
        while time.time() < deadline:
            chunk = s.read(400)
            if chunk:
                buf += chunk
                if b"soft reboot" in buf:
                    found = True
                    break
    finally:
        s.close()
    text = buf.decode(errors="replace").strip()
    lines = text.splitlines()
    print(lines[-1] if lines else "")
    if not found:
        sys.exit(1)


if __name__ == "__main__":
    main()
