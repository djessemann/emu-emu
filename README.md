# Pocket 6502

A simple NES player for your phone. Portrait layout, touch controls, a game library, save states, and plug-in controller support (8BitDo FlipPad, any MFi / Bluetooth / USB pad).

Live: `https://djessemann.github.io/6502-emu/`

## Use it

- Open the link in Safari, tap Share → Add to Home Screen. It opens full screen and works offline.
- Tap **+** to add `.nes` files, or `.zip` files with a `.nes` inside.
- Tap a game to play. **☰** (bottom left) opens the menu: save, load, library, restart, sound.
- Games and saves stay in this browser on this device only.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole app (HTML, CSS, JS inline) |
| `vendor/fceumm/` | NES emulator core, FCEUmm (GPL-2.0), web build from EmulatorJS |
| `vendor/jszip.min.js` | Reads .zip files, JSZip 3.10.1 (MIT) |
| `manifest.json` | Makes it installable as a home screen app |
| `sw.js` | Service worker, caches the app for offline use |
| `*.png` | Icons, made by `gen-assets.py` |
| `CLAUDE.md` | Project notes for Claude Code |
