"""Fake mínimo de badger2040 para renderizar pantallas a PNG. Las fuentes son aproximadas."""
from PIL import Image, ImageDraw, ImageFont

WIDTH = 296
HEIGHT = 128
BUTTON_DOWN, BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_UP = 11, 12, 13, 14, 15
UPDATE_NORMAL, UPDATE_MEDIUM, UPDATE_FAST, UPDATE_TURBO = 0, 1, 2, 3
CHAR_W = {"bitmap6": 5, "bitmap8": 6, "bitmap14_outline": 10}
CHAR_H = {"bitmap6": 6, "bitmap8": 8, "bitmap14_outline": 14}


def woken_by_button():
    return False


def pressed_to_wake(button):
    return False


def _wrap(text, max_chars):
    lines = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split(" "):
            candidate = word if not line else line + " " + word
            if len(candidate) > max_chars and line:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return lines


class Badger2040:
    def __init__(self):
        self.image = Image.new("1", (WIDTH, HEIGHT), 1)
        self.draw = ImageDraw.Draw(self.image)
        self.display = self
        self.pen = 0
        self.font = "bitmap8"
        self.updates = 0

    def set_pen(self, pen):
        self.pen = 0 if pen < 8 else 1

    def set_font(self, font):
        self.font = font

    def set_update_speed(self, speed):
        pass

    def led(self, value):
        pass

    def keepalive(self):
        pass

    def halt(self):
        pass

    def pressed(self, button):
        return False

    def pressed_any(self):
        return False

    def clear(self):
        self.draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), fill=self.pen)

    def rectangle(self, x, y, w, h):
        if w > 0 and h > 0:
            self.draw.rectangle((x, y, x + w - 1, y + h - 1), fill=self.pen)

    def line(self, x1, y1, x2, y2):
        self.draw.line((x1, y1, x2, y2), fill=self.pen)

    def pixel(self, x, y):
        self.draw.point((x, y), fill=self.pen)

    def measure_text(self, text, scale=1):
        return int(len(text) * CHAR_W[self.font] * scale)

    def text(self, text, x, y, wordwrap=WIDTH, scale=1):
        char_w = max(1, int(CHAR_W[self.font] * scale))
        line_h = int((CHAR_H[self.font] + 2) * scale)
        font = ImageFont.load_default(size=max(6, int(CHAR_H[self.font] * scale * 1.25)))
        for i, line in enumerate(_wrap(text, max(1, wordwrap // char_w))):
            self.draw.text((x, y + i * line_h), line, font=font, fill=self.pen)

    def update(self):
        self.updates += 1
