import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sim"))

import badger2040  # noqa: E402
import jpegdec  # noqa: E402
import projects  # noqa: E402
import projects_screen  # noqa: E402
import screen  # noqa: E402


def test_align_expands_to_multiples_of_8():
    assert screen.align(112, 104, 12, 16) == (112, 104, 16, 16)
    assert screen.align(3, 13, 10, 3) == (0, 8, 16, 8)


def test_align_clamps_to_screen():
    assert screen.align(290, 120, 20, 20) == (288, 120, 8, 8)
    assert screen.align(-4, -4, 10, 10) == (0, 0, 8, 8)
    for value in screen.align(*screen.CONTENT):
        assert value % 8 == 0


def test_tab_is_full_and_resets():
    p = screen.Policy()
    p.plan("content", screen.CONTENT)
    assert p.plan("tab") == (screen.FULL, screen.FAST, None)
    assert p.partials == 0


def test_content_is_partial_until_cleanup():
    p = screen.Policy()
    region = screen.align(*screen.CONTENT)
    for _ in range(screen.CLEANUP_EVERY - 1):
        assert p.plan("content", screen.CONTENT) == (screen.PARTIAL, screen.TURBO, region)
    assert p.plan("content", screen.CONTENT) == (screen.FULL, screen.FAST, None)
    assert p.partials == 0


def test_detail_never_escalates_and_does_not_count():
    p = screen.Policy()
    for _ in range(screen.CLEANUP_EVERY * 2):
        mode, speed, _region = p.plan("detail", (112, 104, 12, 16))
        assert (mode, speed) == (screen.PARTIAL, screen.TURBO)
    assert p.partials == 0
    assert p.plan("content", screen.CONTENT)[0] == screen.PARTIAL


def test_detail_speed_override_and_still_does_not_count():
    p = screen.Policy()
    aligned = screen.align(112, 104, 12, 16)
    assert p.plan("detail", (112, 104, 12, 16), speed=screen.FAST) == (screen.PARTIAL, screen.FAST, aligned)
    assert p.partials == 0


def test_unknown_kind_raises():
    p = screen.Policy()
    try:
        p.plan("nope")
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_project_regions_fit_left_of_qr_and_on_screen():
    # Las regiones de partial_update se expanden a bloques de 8px (screen.align):
    # una línea y el QR no deben terminar compartiendo el mismo bloque alineado,
    # o un refresco parcial de una pisaría al otro.
    qr_x0, _qr_y0, _qr_w, _qr_h = screen.align(*projects_screen.QR_REGION)
    for project in projects.PROJECTS:
        for i in range(len(project["lines"])):
            x, y, w, h = screen.align(*projects_screen.line_region(i))
            assert x + w <= qr_x0
            assert y + h <= screen.HEIGHT
    x, y, w, h = projects_screen.QR_REGION
    assert x + w <= screen.WIDTH and y + h <= screen.HEIGHT
