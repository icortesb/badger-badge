"""Guard against MicroPython shadowing a device/*.py module with a same-named
data directory created at runtime (e.g. state.save("state/app.json", ...)
creates a "state" directory next to state.py, and MicroPython then imports
that directory as a namespace package instead of state.py on the next boot).
"""
import re
from pathlib import Path

DEVICE = Path(__file__).resolve().parents[1] / "device"

# Matches a quoted string literal that looks like "<dir>/<rest>" — the
# directory-name part excludes "." so domains/URLs (e.g. "github.com/x")
# don't false-positive.
PATH_LITERAL = re.compile(r'"([A-Za-z_][A-Za-z0-9_]*)/[A-Za-z0-9_./-]*"')


def _offenders():
    offenders = []
    for path in sorted(DEVICE.glob("*.py")):
        text = path.read_text()
        for match in PATH_LITERAL.finditer(text):
            dirname = match.group(1)
            module = DEVICE / (dirname + ".py")
            if module.exists():
                offenders.append((path.name, match.group(0), module.name))
    return offenders


def test_data_path_dirs_do_not_shadow_device_modules():
    assert _offenders() == []
