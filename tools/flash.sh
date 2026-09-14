#!/bin/sh
# Copia un .uf2 al badge en modo BOOTSEL. Si el badge está conectado y
# corriendo, el target `flash` del Makefile ya lo mandó solo a BOOTSEL antes
# de llamar a este script (machine.bootloader() por serial, avisado acá con
# AUTO_BOOTSEL=1); si no, hay que mantener BOOT/USR al enchufar el USB.
set -eu

uf2="$1"
[ -f "$uf2" ] || { echo "No existe $uf2" >&2; exit 1; }

dev=/dev/disk/by-label/RPI-RP2
if [ "${AUTO_BOOTSEL:-0}" = "1" ]; then
    echo "Esperando la unidad RPI-RP2..."
else
    echo "Mantené BOOT/USR en el badge y enchufá el USB (espero 60 s)..."
fi
i=0
while [ ! -e "$dev" ]; do
    i=$((i + 1))
    [ "$i" -le 60 ] || { echo "No apareció la unidad RPI-RP2" >&2; exit 1; }
    sleep 1
done

# Esperar un toque: el automounter del escritorio puede ganarle la carrera a este script.
sleep 2

mnt=$(findmnt -n -o TARGET "$dev" || true)
if [ -z "$mnt" ]; then
    if ! udisksctl mount -b "$dev" >/dev/null 2>&1; then
        # Puede haber fallado porque el automounter ya lo montó justo ahora; reconsultar
        # antes de rendirse.
        mnt=$(findmnt -n -o TARGET "$dev" || true)
        [ -n "$mnt" ] || { echo "No se pudo montar $dev" >&2; exit 1; }
    else
        mnt=$(findmnt -n -o TARGET "$dev")
    fi
fi

cp "$uf2" "$mnt/"
sync
echo "Flasheado $uf2; el badge se reinicia solo."
