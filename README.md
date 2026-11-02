# emu emu

A simple game player for your phone: NES, SNES, Game Boy / Game Boy Color, GBA, and Sega (Genesis, Master System, Game Gear). Portrait layout, touch controls, a game library with a tab per system, save states, and plug-in controller support (8BitDo FlipPad, any MFi / Bluetooth / USB pad).

Live: `https://djessemann.github.io/emu-emu/`

## Use it

- Open the link in Safari, tap Share → Add to Home Screen. It opens full screen and works offline.
- Tap **+** to add games (`.nes`, `.sfc`/`.smc`, `.gb`/`.gbc`, `.gba`, `.md`/`.gen`/`.bin`, `.sms`, `.gg`, or a `.zip` with one of those inside). Each game goes in its system's tab automatically.
- Tap a game to play. **☰** (bottom left) opens the menu: save, load, library, restart, sound.
- Games and saves stay in this browser on this device only.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole app (HTML, CSS, JS inline) |
| `vendor/fceumm/` | NES core, FCEUmm (GPL-2.0) |
| `vendor/snes9x/` | SNES core, Snes9x (non-commercial license) |
| `vendor/gambatte/` | Game Boy / Color core, Gambatte (GPL-2.0) |
| `vendor/mgba/` | GBA core, mGBA (MPL-2.0) |
| `vendor/genesis_plus_gx/` | Sega core, Genesis Plus GX (non-commercial license) |
| `vendor/jszip.min.js` | Reads .zip files, JSZip 3.10.1 (MIT) |
| `manifest.json` | Makes it installable as a home screen app |
| `sw.js` | Service worker, caches the app for offline use |
| `*.png` | Icons and the social preview (`og.png`), made by `gen-assets.py` |
| `CLAUDE.md` | Project notes for Claude Code |

The cores are the web builds EmulatorJS publishes on npm (`@emulatorjs/core-*`, 4.2.3). Each folder has the core's license. emu emu is free and will stay free.
