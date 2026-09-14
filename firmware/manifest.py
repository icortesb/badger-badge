# Manifest congelado: el de la placa de Pimoroni (badger2040.py, badger_os.py) + la app.
include("$(BOARD_DIR)/manifest.py")

freeze(
    "/src/device",
    (
        "badge_screen.py",
        "battery.py",
        "buttons.py",
        "combo.py",
        "links.py",
        "links_screen.py",
        "nav.py",
        "pixfont.py",
        "projects.py",
        "projects_screen.py",
        "quiz_engine.py",
        "quiz_screen.py",
        "screen.py",
        "state.py",
        "ui.py",
    ),
)
