# badger-badge

A terminal-styled conference badge for the [Pimoroni Badger 2040](https://shop.pimoroni.com/products/badger-2040), written in MicroPython. The on-screen text is in Spanish.

- **badge** — dithered stencil portrait framed as a terminal window, name and role.
- **links** — QR codes for GitHub, LinkedIn, a website and a vCard contact.
- **proyectos** — short project blurbs with a QR to each repo.
- **hidden quiz** — press `▲ ▲ ▼ ▼ A B` for 10 questions mixing programming-language logos and dev trivia, with a score title and a top-5 leaderboard with initials.

Runs on battery: the badge powers off after each screen change and wakes on any button, keeping the image on the e-ink display.

## Controls

| Button | Action |
|---|---|
| A / B / C | badge / links / projects tab |
| ▲ ▼ | previous / next QR or project |
| ▲ ▲ ▼ ▼ A B | open the quiz |
| A / B / C (quiz) | answer; any button continues |
| ▲ + ▼ together | leave the quiz |

## Hardware and firmware

Badger 2040 (non-W, RP2040, 296×128 1-bit e-ink) with Pimoroni's MicroPython v1.21.0 badger firmware.

## Setup

Requires [uv](https://docs.astral.sh/uv/), [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) and `rsvg-convert`.

```sh
cp device/assets/contact.example.json device/assets/contact.json   # your vCard data (git-ignored)
make test       # pytest over the pure logic
make preview    # render every screen to sim/out/*.png with a fake badger2040
make deploy     # WIPES the badge, then installs the app precompiled to .mpy
```

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
