# badger-badge

A terminal-styled conference badge for the [Pimoroni Badger 2040](https://shop.pimoroni.com/products/badger-2040), written in MicroPython. The on-screen text is in Spanish.

- **badge** — dithered stencil portrait framed as a terminal window, name and role.
- **links** — QR codes for GitHub, LinkedIn, a website and a vCard contact.
- **proyectos** — short project blurbs with a QR to each repo.
- **hidden quiz** — press `▲ ▲ ▼ ▼ A B` for 10 questions mixing programming-language logos and dev trivia, with a score title and a top-5 leaderboard with initials.

After each button press the cursor blinks twice and settles solid. Ghosting from partial refreshes is cleared by the full refresh on every tab change and after every 8 content changes (no extra timed clean refresh, to save panel cycles and battery). Runs on battery: once settled, it powers off, keeping the image on the e-ink display, and wakes on any button. On USB it stays powered on.

## Controls

| Button | Action |
|---|---|
| A / B / C | badge / links / projects tab |
| ▲ ▼ | previous / next QR or project |
| ▲ ▲ ▼ ▼ A B | open the quiz |
| A / B / C (quiz) | answer; any button continues |
| ▲ + ▼ together | leave the quiz |

## Hardware and firmware

Badger 2040 (non-W, RP2040, 296×128 1-bit e-ink). The app targets MicroPython 1.23: either Pimoroni's official badger2040 v0.0.5 firmware plus `make deploy`, or the custom firmware below with the app frozen in.

## Setup

Requires [uv](https://docs.astral.sh/uv/), [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html), `rsvg-convert`, `podman` (for `make firmware`) and `udisks2` (for `make flash`).

```sh
cp device/assets/contact.example.json device/assets/contact.json   # your vCard data (git-ignored)
make test       # pytest over the pure logic
make preview    # render every screen to sim/out/*.png with a fake badger2040
make deploy     # WIPES the badge, then installs the app precompiled to .mpy
make push       # like deploy, but keeps /data (quiz leaderboard and game count)
make stats      # prints the leaderboard and game count stored on the badge
make restart    # restarts the app over serial, no reset and no re-plugging
```

### Custom firmware (optional)

```sh
make firmware   # podman: builds Pimoroni badger2040 v0.0.5 with the app frozen in
make flash      # installs firmware/out/badge-full.uf2; enters BOOTSEL on its own if the badge is connected, otherwise hold BOOT/USR while plugging in USB
```

`make deploy` and `make push` restart the app over serial (no hardware reset), so the replug note is mainly about `make flash`: its UF2 install does power-cycle the board, and on USB only, if it doesn't come back, unplug and replug it.

`badge-full.uf2` also contains `main.py` and `assets/` (including your `contact.json`), so keep it local. Flashing it replaces the whole badge filesystem, including the quiz leaderboard. `make flash FW=firmware` installs only the firmware and keeps whatever is already on the badge — but a `main.py` or any `.mpy` left there by `make deploy` or `make push` shadow the frozen modules, so use `make flash` (full, the default) to go back to the frozen build. Files uploaded with `make deploy` or `make push` take priority over the frozen modules, so you can iterate without reflashing. On the author's badge, loading the app's modules on each wake went from 123 ms (.mpy on the filesystem) to 21 ms (frozen).

`make deploy` erases everything on the badge, including the quiz leaderboard. Back up the factory files first if you want them (`mpremote fs cp -r :. backup/`).

If the badge stops answering on USB, plug it in while holding **A + C**: it boots into a dev mode that skips the app and leaves the REPL free, then run `make deploy` again.

To make it yours, edit `device/badge_screen.py` (name and role), `device/links.py`, `device/projects.py` and `device/assets/quiz.json`, and rebuild images with `make assets PHOTO=path/to/photo.jpg`.

## Layout

```
device/   code and assets copied to the badge (main.py, screens, pure logic, assets/)
sim/      fake badger2040 / jpegdec / qrcode modules and the PNG preview script
tools/    asset builders (portrait, logos, pixel font) and the on-device wipe script
tests/    pytest suite
```

## Credits

- Logos from [Simple Icons](https://simpleicons.org) (CC0).
- `device/pixfont.py` is generated from the `bitmap8` font data in [pimoroni-pico](https://github.com/pimoroni/pimoroni-pico) (MIT) to draw it at 1.5×.

## License

[MIT](LICENSE)
