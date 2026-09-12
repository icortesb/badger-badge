import segno


class QRCode:
    def __init__(self):
        self.matrix = [[False]]

    def set_text(self, text):
        qr = segno.make(text, error="m", micro=False)
        self.matrix = [[bool(v) for v in row] for row in qr.matrix]

    def get_size(self):
        return len(self.matrix), len(self.matrix)

    def get_module(self, x, y):
        return self.matrix[y][x]
