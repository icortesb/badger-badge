PORT ?= /dev/ttyACM0
PHOTO ?= $(HOME)/Downloads/20250429_092914.jpg
MP = mpremote connect $(PORT)
# Misma versión que el firmware del badge (MicroPython 1.21, mpy v6.1).
MPY_CROSS = uv tool run --from mpy-cross==1.21.0 mpy-cross

.PHONY: test assets preview build deploy font

test:
	PYTHONDONTWRITEBYTECODE=1 uv run --with pytest --with pillow --with segno pytest -q

assets:
	uv run --with pillow python tools/build_assets.py --photo $(PHOTO)

preview:
	PYTHONDONTWRITEBYTECODE=1 uv run --with pillow --with segno python sim/preview.py

# Si el badge no responde: mantener A+C y tocar RESET (o reconectar USB) para entrar en modo dev, y correr make deploy.
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
