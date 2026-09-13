PORT ?= /dev/ttyACM0
PHOTO ?= $(HOME)/Downloads/20250429_092914.jpg
MP = mpremote connect $(PORT)

.PHONY: test assets preview deploy font

test:
	PYTHONDONTWRITEBYTECODE=1 uv run --with pytest --with pillow --with segno pytest -q

assets:
	uv run --with pillow python tools/build_assets.py --photo $(PHOTO)

preview:
	PYTHONDONTWRITEBYTECODE=1 uv run --with pillow --with segno python sim/preview.py

deploy: test
	test -f device/assets/contact.json
	find device -name __pycache__ -type d -exec rm -rf {} +
	$(MP) run tools/wipe.py
	cd device && $(MP) fs cp -r . :
	$(MP) fs ls :
	$(MP) reset

font:
	uv run python tools/build_font.py
