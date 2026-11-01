# Pocket 6502 — project notes for Claude Code

**Pocket 6502** is a dead-simple NES emulator for phones: portrait first, touch controls, a ROM library, one save state per game, and plug-in controller support. It started as a Claude artifact and is moving here to be hosted on GitHub Pages.

- Repo: `djessemann/6502-emu` (default branch `main`)
- Live: `https://djessemann.github.io/6502-emu/`
- Owner is non-technical: do the git, build and deploy work yourself rather than handing over instructions. Explain results in plain, short English.

## First-time setup (do this first)

1. Push every file in this folder to `main` of `djessemann/6502-emu`, at the repo root. (Done.)
2. Make sure `.nojekyll` is at the root (it is in this folder).
3. Turn on **GitHub Pages → Deploy from a branch → `main` → `/ (root)`**. If you can't change Pages settings from the session, say so plainly and tell the owner exactly where to click: repo **Settings → Pages → Source: Deploy from a branch → Branch: main / (root) → Save**.
4. Wait for the Pages build, then confirm `https://djessemann.github.io/6502-emu/` loads (index.html, not the README).
5. Tell the owner: open the link in Safari on the iPhone → Share → **Add to Home Screen**. Games added in the old Claude artifact don't carry over (browser storage is per site), so ROMs need to be added again.

## Repo layout (keep it minimal)

```
index.html          # the whole app: HTML + CSS + JS inline
vendor/fceumm/      # emulator core: FCEUmm (GPL-2.0) as EmulatorJS builds it (RetroArch + core in WebAssembly),
                    # fceumm_libretro.js/.wasm unpacked from npm @emulatorjs/core-fceumm 4.2.3 (fceumm-wasm.data, a 7z)
vendor/jszip.min.js # zip reader, JSZip 3.10.1 (MIT), local copy for offline use
manifest.json       # PWA manifest (installable, standalone)
sw.js               # service worker, precaches the app shell for offline
favicon.png, apple-touch-icon.png, icon-192.png, icon-512.png
gen-assets.py       # regenerates the icons (pure Python, stdlib only)
.nojekyll
README.md
CLAUDE.md
```

- No build step, no framework, no npm at runtime. Same spirit as the owner's `nesprite` and `nes-tracker` repos.
- **`index.html` must stay at the repo root** or Pages renders the README instead.
- **Bump `CACHE` in `sw.js`** (`pocket6502-v6` → `v7` …) whenever any cached file changes, or installed users keep the stale version. If you add a new file the app needs, add it to `ASSETS` too.
- Keep everything self-contained: no external fonts, scripts or fetches, or offline breaks.

## How the app works

### Screens
- **Library:** header with the name, `+` (add games) and `···` (opens "remove games" and "help"). Rows show the game name only, sorted A–Z. "remove games" puts an `×` on each row until "done". Empty state is one dashed "add a game" box.
- **Player:** game screen on top (kept below the iPhone status bar: status bar style is `black-translucent` so the safe-area inset is reported, and in the home screen app when upright the top padding is inset + 40px, floor 90px, because iOS draws a fade that reaches below the status bar and can't be turned off), d-pad bottom left, B/A bottom right (diagonal, NES-style), and a bottom row with `☰` (menu, far left), `select`, `start`.
- **Menu (☰):** pauses the game. Game name + `×` (resume). `save` / `load` (one slot; load is disabled until a save exists), then three icon buttons: library, restart, sound. Saving or loading closes the menu and shows a one-word flash ("saved", "loaded").
- **Landscape:** d-pad left, screen center, buttons right.

### Input
- **Touch:** one pointer handler on `#player` hit-tests zones by rectangle (`measure()` caches rects). D-pad is 8-way by angle from center with a small dead zone, and a thumb that starts on it stays locked to it while sliding. Pressing between A and B hits both. Light haptic tick where supported.
- **Keyboard:** arrows, Z = B, X = A, Enter = Start, Shift = Select, Esc = menu.
- **Controllers (gameplay only, by owner's choice — no menu/library navigation):** standard Gamepad API, polled every frame while the player is open. Any connected pad flips the player into `pad-mode`: on-screen d-pad/A/B/select/start hide, the screen gets bigger, ☰ stays. A/B: buttons 0/2 = A, 1/3 = B. This was swapped once; the owner confirmed on the FlipPad that the old by-position mapping put A and B backwards. D-pad 12–15 plus left stick, select 8, start 9. Built for the **8BitDo FlipPad** (USB-C, Apple-supported). Browsers only report a pad after its first button press.

### Saving (all in IndexedDB `pocket6502`, version 2)
| Store | Key | Holds |
|---|---|---|
| `meta` | `id` (keyPath) | `{id, name, file, size, mapper, added, played}` |
| `data` | game id | ROM bytes (`Uint8Array`) |
| `states` | game id | auto "resume" snapshot (FCEUmm state bytes, `Uint8Array`), written on leave, app switch, and every 30s |
| `slots` | game id | the one manual save state `{at, s}`, `s` = FCEUmm state bytes |
| `sram` | game id | in-game battery save: the core's `.srm` file (8 KB `$6000–$7FFF` for normal carts, same bytes the old jsnes build stored), copied every 2s when it changed |

- Game id = FNV-1a hash of the ROM bytes (dedupes re-adds).
- `states`/`slots` written by the old jsnes engine are plain objects, not `Uint8Array`: they're ignored (and old resume snapshots deleted).
- Restart clears `states` only. In-game saves and the save state survive.
- Removing a game deletes it from all five stores.
- If IndexedDB is blocked, everything falls back to memory and a note says games won't be kept.

### Emulator
- **FCEUmm** via EmulatorJS's prebuilt web core (`EJS_Runtime` factory in `fceumm_libretro.js`). We don't use EmulatorJS's UI, only the core, driven through its exported functions with `cwrap`: `simulate_input` (libretro ids: B 0, select 2, start 3, up 4, down 5, left 6, right 7, A 8), `save_state_info` + `HEAPU8` (get state), `load_state` (from a file in the core's FS), `toggleMainLoop` (pause), `system_restart`, `cmd_savefiles` + `save_file_path` (the `.srm`), `get_current_frame_count`.
- The core's own keyboard input is off (its `parent` is a detached div, so its key listeners never fire) and its joypad driver is `null`; our touch/keyboard/gamepad code feeds every button.
- Config: `RA_CFG` is written to `/home/web_user/.config/retroarch/retroarch.cfg`; core options (`CORE_OPTS`: square pixels `fceumm_aspect = "PP"`, no vertical overscan crop, so 256×240 like before) are written through the `callbacks.setupCoreSettingFile` hook.
- The wasm is fetched and compiled in the background when the app opens and handed to the core with `instantiateWasm`, so tapping a game is quick.
- **One game per page load.** Leaving a game saves and then reloads the page: each core instance holds a 128 MB heap and the old one isn't fully freed, so reloading is how memory stays flat on iPhone.
- Audio: the core creates its own AudioContext after the tap, which iOS would keep muted. `window.AudioContext` is wrapped so the core gets a context made (and resumed) inside the tap. Pause and the sound toggle suspend/resume that context.
- Draws with WebGL on a fresh clone of `#screen` per game (a canvas can't switch from 2D to WebGL).
- FCEUmm runs nearly every mapper, including expansion audio (VRC6, VRC7, Namco 163, Sunsoft 5B, MMC5). `.fds` (Famicom Disk System) would also need the `disksys.rom` BIOS, so imports stay `.nes` only for now.
- **License:** FCEUmm is GPL-2.0 (`vendor/fceumm/LICENSE.txt`). Shipping it means the app as a whole is GPL. Owner is fine with that. The app will stay free (no paid version planned); a free App Store release is possible later (small theoretical risk: Apple's terms vs GPL).

## UI style (match `nesprite` and `nes-tracker`)

- Black `#000` background, white text and **1px white borders**, muted `#999`, monospace (`ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace`).
- **No rounded corners anywhere**, except the round A/B buttons (owner asked for circles). No shadows, gradients, or animation.
- **Active / held = inverted:** white fill, black text.
- Dialogs are in-app overlays (black box, white border), never `alert/confirm/prompt`. Confirm pattern: `cancel` outlined + primary inverted.
- Copy is lowercase, short, and plain. Owner did a UX pass to strip it down: prefer icons where the meaning is obvious (`+`, `···`, `☰`, `×`, library grid, restart arrow, speaker), and keep words only where an icon would be a guess (`select`, `start`, `a`, `b`, `save`, `load`, `done`). No timestamps, file sizes, or "may not run" labels — those were removed on purpose.
- Icons are inline SVG, 20px, `stroke: currentColor`, square line caps. App icon is a white 8-bit d-pad on black (`gen-assets.py`).

## Git

- Work directly on `main` and push there unless the owner says otherwise.
- Commit when a change is complete, with a clear message. Bump the `sw.js` cache name in the same commit as any app change.

## Roadmap the owner has discussed

0. **More systems (later, not started):** same approach as NES, one EmulatorJS prebuilt core per system from npm (`@emulatorjs/core-<name>`, unpack the `<name>-wasm.data` 7z), same UI, a per-system button set. Picks:
   - **SNES:** `snes9x`. Good accuracy and fast enough on phones. (bsnes is more exact but too slow for phones in WebAssembly, and has no prebuilt.) Non-commercial license; fine, the app will stay free.
   - **Sega Master System / Genesis (also Game Gear, Sega CD):** `genesis_plus_gx`. The most accurate Sega 8/16-bit core, one core for all of them. Non-commercial license, same as above. (`picodrive` adds 32X if ever wanted.)
   - **Game Boy / Game Boy Color:** `gambatte` (GPL-2.0), the most accurate GB/GBC core. Or use `mgba` for these too, to have one core for all three Nintendo handhelds.
   - **Game Boy Advance:** `mgba` (MPL-2.0, a permissive license). Best GBA core by a distance.
   - Each core is about 4–5 MB. Load a system's core only when a game for it is opened, and keep "one game per page load".
   - SNES, GBA and Genesis need more buttons (X/Y, L/R, C), so the on-screen pad needs a layout per system.

1. **TV mode (web):** a ☰ menu option that hides everything but the game, for Apple TV screen mirroring. Limit: mirroring copies the phone's orientation, so with the phone upright (FlipPad) the game is small on the TV; it only fills the TV with the phone sideways.
2. **Native iPhone app via TestFlight (the real fix for the TV):** wrap this web app in a native shell and use iOS's external-display support to send a full-size game picture to the TV while the phone stays upright in the FlipPad. Needs Xcode on the owner's MacBook Pro M4 and the $99/yr Apple Developer account. TestFlight builds last 90 days; internal testing needs no review.
