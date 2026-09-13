import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "firmware" / "manifest.py"
DEVICE = REPO / "device"


def _frozen_module_names():
    tree = ast.parse(MANIFEST.read_text(encoding="utf-8"), filename=str(MANIFEST))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "freeze":
            files_arg = node.args[1]
            return {
                elt.value
                for elt in files_arg.elts
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
            }
    raise AssertionError("no se encontró una llamada a freeze() en firmware/manifest.py")


def test_frozen_modules_match_device_modules():
    frozen = _frozen_module_names()
    on_disk = {p.name for p in DEVICE.glob("*.py")} - {"main.py"}
    assert frozen == on_disk
