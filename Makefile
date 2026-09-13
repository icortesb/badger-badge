PORT ?= /dev/ttyACM0
PHOTO ?= $(HOME)/Downloads/20250429_092914.jpg
MP = mpremote connect $(PORT)
# Misma versión que el firmware del badge (MicroPython 1.23, mpy v6.3).
MPY_CROSS = uv tool run --from mpy-cross==1.23.0 mpy-cross

.PHONY: test assets preview build deploy font flash firmware

FW ?= full
UF2 ?= firmware/out/badge-$(FW).uf2

test:
	PYTHONDONTWRITEBYTECODE=1 uv run --with pytest --with pillow --with segno pytest -q

assets:
	uv run --with pillow python tools/build_assets.py --photo $(PHOTO)

preview:
	PYTHONDONTWRITEBYTECODE=1 uv run --with pillow --with segno python sim/preview.py

# Si el badge no responde: enchufar el USB manteniendo A+C (modo dev) y correr make deploy.
# Precompila todo menos main.py a .mpy: el badge no compila fuentes en cada wake a batería.
build: test
	test -f device/assets/contact.json
	rm -rf build
	mkdir -p build
	cp -r device/assets build/assets
	rm -f build/assets/contact.example.json
	cp device/main.py build/main.py
	for f in device/*.py; do \
		name=$$(basename $$f .py); \
		[ $$name = main ] || $(MPY_CROSS) -o build/$$name.mpy $$f || exit 1; \
	done

deploy: build
	$(MP) run tools/wipe.py
	cd build && $(MP) fs cp -r . :
	$(MP) fs ls :
	$(MP) reset

font:
	uv run python tools/build_font.py

# Flashea un .uf2 en modo BOOTSEL. make flash (completo) | make flash FW=firmware | make flash UF2=ruta.uf2
flash:
	sh tools/flash.sh $(UF2)

# Firmware propio (Pimoroni badger2040 v0.0.5 + app congelada) en podman.
firmware: test
	test -f device/assets/contact.json
	find device -name __pycache__ -type d -exec rm -rf {} +
	podman build -t badger-badge-fw firmware
	podman run --rm -v "$(CURDIR)":/src:Z badger-badge-fw bash /src/firmware/build.sh
