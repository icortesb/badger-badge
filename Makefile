PORT ?= /dev/ttyACM0
PHOTO ?= $(HOME)/Downloads/20250429_092914.jpg
MP = mpremote connect $(PORT)

.PHONY: test assets preview deploy

test:
	PYTHONDONTWRITEBYTECODE=1 uv run --with pytest --with pillow pytest -q

assets:
	uv run --with pillow python tools/build_assets.py --photo $(PHOTO)

preview:
	PYTHONDONTWRITEBYTECODE=1 uv run --with pillow --with segno python sim/preview.py
