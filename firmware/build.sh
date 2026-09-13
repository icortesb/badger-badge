#!/usr/bin/env bash
# Compila el firmware del badge: Pimoroni badger2040 v0.0.5 + la app congelada.
# Corre dentro del contenedor de firmware/Containerfile con el repo montado en /src.
set -euo pipefail

SRC=/src
WORK="$SRC/firmware/.work"
OUT="$SRC/firmware/out"
BOARD=PIMORONI_BADGER2040

MICROPYTHON_VERSION=v1.23.0
PIMORONI_PICO_VERSION=v1.23.0-1
BADGER_VERSION=v0.0.5
DIR2UF2_VERSION=v0.0.4
PY_DECL_VERSION=v0.0.1

mkdir -p "$WORK" "$OUT"
cd "$WORK"
git config --global --add safe.directory '*'

clone() { # repo tag dir
    [ -d "$3" ] || git clone --depth 1 --branch "$2" "https://github.com/$1.git" "$3"
}

if [ ! -f micropython/.submodules-ok ]; then
    clone micropython/micropython "$MICROPYTHON_VERSION" micropython
    git -C micropython submodule update --init \
        lib/pico-sdk lib/cyw43-driver lib/lwip lib/mbedtls lib/micropython-lib lib/tinyusb lib/btstack
    touch micropython/.submodules-ok
fi
if [ ! -f pimoroni-pico/.submodules-ok ]; then
    clone pimoroni/pimoroni-pico "$PIMORONI_PICO_VERSION" pimoroni-pico
    git -C pimoroni-pico submodule update --init --recursive
    touch pimoroni-pico/.submodules-ok
fi
clone pimoroni/badger2040 "$BADGER_VERSION" badger2040
clone gadgetoid/dir2uf2 "$DIR2UF2_VERSION" dir2uf2
clone gadgetoid/py_decl "$PY_DECL_VERSION" py_decl

if [ ! -f .patched ]; then
    git -C micropython/lib/pico-sdk apply "$WORK/badger2040/firmware/startup_overclock.patch"
    git -C micropython apply "$WORK/badger2040/firmware/932f76c6ba64c5a3e68de3324556d9979f09303b.patch"
    git -C micropython apply "$WORK/badger2040/firmware/micropython_nano_specs.patch"
    touch .patched
fi

[ -x micropython/mpy-cross/build/mpy-cross ] || make -C micropython/mpy-cross

export CCACHE_DIR="$WORK/ccache"
BOARD_DIR="$WORK/badger2040/firmware/$BOARD"
(
    # El build dir tiene que ser ports/rp2/build: micropython.cmake de Pimoroni
    # busca pimoroni-pico con una ruta relativa desde ahí.
    cd micropython/ports/rp2
    cmake -S . -B build \
        -DPICO_BUILD_DOCS=0 \
        -DMICROPY_BOARD="$BOARD" \
        -DMICROPY_BOARD_DIR="$BOARD_DIR" \
        -DUSER_C_MODULES="$BOARD_DIR/micropython.cmake" \
        -DMICROPY_FROZEN_MANIFEST="$SRC/firmware/manifest.py" \
        -DCMAKE_C_COMPILER_LAUNCHER=ccache \
        -DCMAKE_CXX_COMPILER_LAUNCHER=ccache
    cmake --build build -j "$(nproc)"
)
cp micropython/ports/rp2/build/firmware.uf2 "$OUT/badge-firmware.uf2"

# Filesystem del .uf2 completo: main.py + assets (con contact.json, sin el ejemplo).
FS="$WORK/fs"
rm -rf "$FS"
mkdir -p "$FS"
cp "$SRC/device/main.py" "$FS/main.py"
cp -r "$SRC/device/assets" "$FS/assets"
rm -f "$FS/assets/contact.example.json"

# dir2uf2 escribe <stem del uf2 base>-<stem de --filename>.uf2 en el directorio actual.
(
    cd "$OUT"
    PYTHONPATH="$WORK/py_decl" python3 "$WORK/dir2uf2/dir2uf2" \
        --append-to "$OUT/badge-firmware.uf2" \
        --manifest "$SRC/firmware/fs-manifest.txt" \
        --filename full.uf2 \
        "$FS/"
    mv badge-firmware-full.uf2 badge-full.uf2
    rm -f full.bin full.uf2
)

ls -l "$OUT"
