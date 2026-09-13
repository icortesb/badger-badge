import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sim"))

import badger2040  # noqa: E402
import jpegdec  # noqa: E402
import ui  # noqa: E402

LOGO_PATH = str(Path(__file__).resolve().parents[1] / "device" / "assets" / "logos" / "python.jpg")


def test_image_leaves_pen_black_after_decode():
    d = badger2040.Badger2040()
    jpeg = jpegdec.JPEG(d.display)
    ui.image(d, jpeg, LOGO_PATH, 8, 26, 80, 80)
    assert d.pen == 0


def test_image_leaves_pen_black_when_file_missing():
    d = badger2040.Badger2040()
    jpeg = jpegdec.JPEG(d.display)
    ui.image(d, jpeg, "does/not/exist.jpg", 8, 26, 80, 80)
    assert d.pen == 0
