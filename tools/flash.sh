#!/bin/sh
# Copia un .uf2 al badge en modo BOOTSEL (mantener BOOT/USR al enchufar el USB).
set -eu

uf2="$1"
[ -f "$uf2" ] || { echo "No existe $uf2" >&2; exit 1; }

dev=/dev/disk/by-label/RPI-RP2
echo "Mantené BOOT/USR en el badge y enchufá el USB (espero 60 s)..."
i=0
while [ ! -e "$dev" ]; do
    i=$((i + 1))
    [ "$i" -le 60 ] || { echo "No apareció la unidad RPI-RP2" >&2; exit 1; }
    sleep 1
done

mnt=$(findmnt -n -o TARGET "$dev" || true)
if [ -z "$mnt" ]; then
    udisksctl mount -b "$dev" >/dev/null
    mnt=$(findmnt -n -o TARGET "$dev")
fi

cp "$uf2" "$mnt/"
sync
echo "Flasheado $uf2; el badge se reinicia solo."
