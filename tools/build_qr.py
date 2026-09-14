"""Genera device/assets/qr/<key>.bin: QR precalculados por tramos."""
import sys
from pathlib import Path

import segno

ROOT = Path(__file__).resolve().parents[1]
DEVICE = ROOT / "device"
QR_DIR = DEVICE / "assets" / "qr"
sys.path.insert(0, str(DEVICE))

import links  # noqa: E402
import projects  # noqa: E402
import qrcache  # noqa: E402
import state  # noqa: E402


def payloads():
    items = links.items(state.load(str(DEVICE / "assets" / "contact.json"), links.CONTACT_DEFAULTS))
    seen = set()
    result = []
    for item in items:
        if item["payload"] not in seen:
            seen.add(item["payload"])
            result.append(item["payload"])
    for project in projects.PROJECTS:
        if project["url"] not in seen:
            seen.add(project["url"])
            result.append(project["url"])
    return result


def main():
    QR_DIR.mkdir(parents=True, exist_ok=True)
    for old in QR_DIR.glob("*.bin"):
        old.unlink()
    for payload in payloads():
        matrix = segno.make(payload, error="m", micro=False).matrix
        matrix = [[bool(v) for v in row] for row in matrix]
        data = qrcache.encode(matrix)
        out = DEVICE / qrcache.path(payload)
        out.write_bytes(data)
        print("{!r} -> {} ({} bytes)".format(payload[:30], len(matrix), len(data)))


if __name__ == "__main__":
    main()
