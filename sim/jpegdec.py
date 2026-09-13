from PIL import Image

JPEG_SCALE_FULL = 0


class JPEG:
    def __init__(self, display):
        self.display = display
        self.path = None

    def open_file(self, path):
        open(path, "rb").close()
        self.path = path

    def decode(self, x=0, y=0, scale=JPEG_SCALE_FULL, dither=True):
        mode = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
        img = Image.open(self.path).convert("L").convert("1", dither=mode)
        self.display.image.paste(img, (x, y))
        self.display.set_pen(15)
