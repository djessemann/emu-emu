# emu — project notes for Claude Code

**emu** (formerly emu emu, Pocket 6502; the repo and URL stay `emu-emu`) is a dead-simple multi-system emulator for phones: NES, SNES, Game Boy / Color, GBA and Sega (Genesis, Master System, Game Gear). Portrait first, touch controls, a game library with one tab per system, one save state per game, and plug-in controller support. Hosted on GitHub Pages. It stays free (no paid version planned).

- Repo: `djessemann/emu-emu` (default branch `main`; earlier names `snappy-emu`, `6502-emu`)
- Live: `https://djessemann.github.io/emu-emu/`
- Owner is non-technical: do the git, build and deploy work yourself rather than handing over instructions. Explain results in plain, short English.

## Hosting

- GitHub Pages deploys `main` from the repo root (`.nojekyll` at the root). If Pages ever needs turning on: repo **Settings → Pages → Source: Deploy from a branch → Branch: main / (root) → Save**.
- Renaming the repo moves the Pages URL and breaks home-screen icons (each home-screen web app also has its own storage, so games must be re-added). Avoid renames.
- Social preview: `og.png` (1200×630) via `og:`/`twitter:` meta tags in `index.html`, absolute URLs on the live domain; update them if the URL changes. GitHub's own repo preview image can only be set by the owner in Settings → General → Social preview.

## Repo layout (keep it minimal)

```
index.html          # the whole app: HTML + CSS + JS inline
vendor/<core>/      # one emulator core per system, as EmulatorJS builds them (RetroArch + core in WebAssembly):
                    #   fceumm (NES), snes9x (SNES), gambatte (GB/GBC), mgba (GBA), genesis_plus_gx (Sega)
                    # <core>_libretro.js/.wasm unpacked from npm @emulatorjs/core-<core> 4.2.3 (<core>-wasm.data, a 7z;
                    # not the -thread / -legacy variants), plus the core's LICENSE.txt, core.json, build.json
vendor/jszip.min.js # zip reader, JSZip 3.10.1 (MIT), local copy for offline use
manifest.json       # PWA manifest (installable, standalone)
sw.js               # service worker, precaches the app shell for offline
favicon.png, apple-touch-icon.png, icon-192.png, icon-512.png, og.png
gen-assets.py       # regenerates the icons and og.png (pure Python, stdlib only)
.nojekyll
README.md
CLAUDE.md
```

- No build step, no framework, no npm at runtime. Same spirit as the owner's `nesprite` and `nes-tracker` repos.
- **`index.html` must stay at the repo root** or Pages renders the README instead.
- **Bump `CACHE` in `sw.js`** (`emuemu-v9` → `v10` …) whenever any file changes, or installed users keep the stale version. `ASSETS` (stored on install) is the app shell plus the NES core; everything else the app fetches, including the other cores, is stored the first time it loads (runtime caching in the fetch handler).
- Keep everything self-contained: no external fonts, scripts or fetches, or offline breaks.

## How the app works

### Screens
- **Library:** header with the name, `+` (add games) and `···` (opens "remove games" and "help"). Under it, a row of system tabs: `nes · snes · gb · gba · sega` (active = inverted); the last tab used is remembered (`prefs` key `tab`). Rows show the game name only, sorted A–Z, for the current tab. Adding games sorts each into its system by file type and switches to the tab of the last one added ("added 2 snes games, 1 gba game."). "remove games" puts an `×` on each row until "done". Empty tab: one dashed "add a {system} game" box with that system's file types.
- **Player:** game screen on top, shaped per system (`--ar`), taking the space left above the controls (kept below the iPhone status bar: status bar style is `black-translucent` so the safe-area inset is reported, and in the home screen app when upright the top padding is inset + 40px, floor 90px, because iOS draws a fade that reaches below the status bar and can't be turned off). Controls in one fixed block at the bottom (below). Bottom row: `☰` (menu, far left), `select`, `start` centered (Sega has `start` only).
- **Menu (☰):** pauses the game. Game name + `×` (resume). `save` / `load` (one slot; load is disabled until a save exists), then three icon buttons: library, restart, sound. Saving or loading closes the menu and shows a one-word flash ("saved", "loaded").
- **Landscape:** d-pad left, screen center, buttons right, `l`/`r` above them, menu row under the screen.

### Controls per system (sizes in points on a 390-pt phone; `--u` scales them)
Taken from Delta's official iPhone portrait layouts (rileytestut/NESDeltaCore, SNESDeltaCore, GBADeltaCore `Controller Skin/info.json`) and GBA4iOS: d-pad ≈ 39% of the width, face buttons 16–18%, d-pad center level with the button-cluster center, small select/start between the thumbs. Control block is 310u tall; inside it (x from the content edge):
- D-pad 153u square at x 4, y 74. Touch area +18 px.
- `two` (NES, GB/GBC, GBA, and Master System / Game Gear labeled `1` `2`): 68u circles, B low-left, A high-right, 16u apart, box 152×102 4u from the right. Touch +20 px, so pressing between them hits both.
- `snes`: 60u circles in a diamond (x top, y left, a right, b bottom), 108u center to center, box 168×168. Touch +8 px.
- `genesis`: a b c, 58u circles in a rising row, box 190×98. Touch +8 px.
- Face cluster centered at y 150. `l`/`r` (SNES, GBA): 120×36u in the top corners. Meta row at y 262, 32u tall.
- Layouts live in `FACES` and `SYSTEMS` in `index.html`; `buildPad()` draws the face buttons per game.

### Input
- **Touch:** one pointer handler on `#player` hit-tests zones by rectangle (`measure()` caches rects). D-pad is 8-way by angle from center with a small dead zone, and a thumb that starts on it stays locked to it while sliding. Pressing between A and B hits both. Light haptic tick where supported.
- **No selectable text:** every element in `#app` has `user-select: none` and `-webkit-touch-callout: none`, control labels are CSS `::before{content:attr(data-label)}` (no text node), and `touchstart` on the player is cancelled except on real `<button>`s. Together these stop iOS's press-and-hold magnifier (the Liquid Glass loupe) and copy menu on the controls.
- **Touch hit-testing** works on whatever `[data-b]` elements are visible: d-pad rect, face circles, `l`/`r` and select/start rects.
- **Keyboard:** arrows, Z = B, X = A, A = Y, S = X, Q = L, W = R, Enter = Start, Shift = Select, Esc = menu. Genesis: Z X C = A B C.
- **Controllers (gameplay only, by owner's choice — no menu/library navigation):** standard Gamepad API, polled every frame while the player is open. Any connected pad flips the player into `pad-mode`: on-screen d-pad/A/B/select/start hide, the screen gets bigger, ☰ stays. The FlipPad reports buttons by label (0 = A on the right, 1 = B bottom, 2 = X top, 3 = Y left); the owner confirmed for NES that 0/2 = A, 1/3 = B (the old by-position mapping was backwards). SNES: a 0, b 1, x 2, y 3. Genesis: A 3, B 1, C 0/2 (the left-to-right row). L 4/6, R 5/7. D-pad 12–15 plus left stick, select 8, start 9. Built for the **8BitDo FlipPad** (USB-C, Apple-supported). Browsers only report a pad after its first button press.

### Saving (all in IndexedDB `pocket6502`, version 2)
| Store | Key | Holds |
|---|---|---|
| `meta` | `id` (keyPath) | `{id, name, file, size, sys, ext, mapper (NES only), added, played}`; `sys` is `nes`/`snes`/`gb`/`gba`/`sega` (missing = `nes`, from before multi-system), `ext` is the file type written into the core (`game.<ext>`) |
| `data` | game id | ROM bytes (`Uint8Array`) |
| `states` | game id | auto "resume" snapshot (core state bytes, `Uint8Array`), written on leave, app switch, and every 30s |
| `slots` | game id | the one manual save state `{at, s}`, `s` = core state bytes |
| `sram` | game id | in-game battery save: the core's `.srm` file, copied every 2s when it changed (NES: 8 KB `$6000–$7FFF`, same bytes the old jsnes build stored) |

- Game id = FNV-1a hash of the ROM bytes (dedupes re-adds).
- IndexedDB name `pocket6502` and `localStorage` prefix `p6502.` are kept from the old name on purpose: renaming them would lose everyone's games.
- `states`/`slots` written by the old jsnes engine are plain objects, not `Uint8Array`: they're ignored (and old resume snapshots deleted).
- Restart clears `states` only. In-game saves and the save state survive.
- Removing a game deletes it from all five stores.
- If IndexedDB is blocked, everything falls back to memory and a note says games won't be kept.

### Emulator
- **Cores** (all EmulatorJS web builds, `EJS_Runtime` factory in `<core>_libretro.js`), per `SYSTEMS` in `index.html`:
  - NES: `fceumm`. Options: `fceumm_aspect = "PP"` (square pixels), no vertical overscan crop → 256×240.
  - SNES: `snes9x`, `snes9x_aspect = "uncorrected"` → 256×224 (8:7).
  - Game Boy / Color: `gambatte` (default greyscale for original GB games).
  - GBA: `mgba` (no BIOS file; it uses its built-in one).
  - Sega: `genesis_plus_gx`. Genesis `genesis_plus_gx_aspect_ratio = "4:3"`, box 4:3 (fills for both 256- and 320-wide modes). Master System 4:3, Game Gear `"Uncorrected"` 160×144. The system is picked by the file type written into the core (`game.md` / `.sms` / `.gg`), so `ext` matters. `.bin` is accepted only with `SEGA` at 0x100.
- We don't use EmulatorJS's UI, only the cores, driven through exported functions with `cwrap`: `simulate_input` (libretro ids: B 0, Y 1, select 2, start 3, up 4, down 5, left 6, right 7, A 8, X 9, L 10, R 11; genesis_plus_gx maps Genesis A/B/C to Y/B/A and Master System 1/2 to B/A, checked with hand-made test ROMs), `save_state_info` + `HEAPU8` (get state), `load_state` (from a file in the core's FS), `toggleMainLoop` (pause), `system_restart`, `cmd_savefiles` + `save_file_path` (the `.srm`), `get_current_frame_count`.
- The core's own keyboard input is off (its `parent` is a detached div, so its key listeners never fire) and its joypad driver is `null`; our touch/keyboard/gamepad code feeds every button.
- Config: `RA_CFG` is written to `/home/web_user/.config/retroarch/retroarch.cfg`; core options are written through the `callbacks.setupCoreSettingFile` hook.
- A core's script is loaded only when a game for it starts (`loadCoreScript`), because each defines the same global `EJS_Runtime`. Its wasm is fetched and compiled ahead of time for the tab you're on (`compileCore`, one kept at a time) and handed over with `instantiateWasm`.
- `prepareCores` fetches the cores of every system you have games for, once, so the service worker stores them for offline play.
- **One game per page load.** Leaving a game saves and then reloads the page: each core instance holds a large heap and the old one isn't fully freed, so reloading is how memory stays flat on iPhone.
- Audio: the core creates its own AudioContext after the tap, which iOS would keep muted. `window.AudioContext` is wrapped so the core gets a context made (and resumed) inside the tap. Pause and the sound toggle suspend/resume that context.
- Draws with WebGL on a fresh clone of `#screen` per game (a canvas can't switch from 2D to WebGL).
- Testing: there are no real games in the repo. Hand-assembled test ROMs per system (red screen, a different color while a button is held) are a quick way to check boot, input mapping and save states in Playwright.
- **Licenses:** FCEUmm and Gambatte GPL-2.0, mGBA MPL-2.0, Snes9x and Genesis Plus GX non-commercial (fine: the app stays free). Each `vendor/<core>/LICENSE.txt`. A free App Store release is possible later (small theoretical risk: Apple's terms vs GPL).

## UI style (match `nesprite` and `nes-tracker`)

- Black `#000` background, white text and **1px white borders**, muted `#999`, monospace (`ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace`).
- **No rounded corners anywhere**, except the round face buttons (owner asked for circles). No shadows, gradients, or animation.
- **Active / held = inverted:** white fill, black text.
- Dialogs are in-app overlays (black box, white border), never `alert/confirm/prompt`. Confirm pattern: `cancel` outlined + primary inverted.
- Copy is lowercase, short, and plain. Owner did a UX pass to strip it down: prefer icons where the meaning is obvious (`+`, `···`, `☰`, `×`, library grid, restart arrow, speaker), and keep words only where an icon would be a guess (`select`, `start`, `a`, `b`, `save`, `load`, `done`). No timestamps, file sizes, or "may not run" labels — those were removed on purpose.
- Icons are inline SVG, 20px, `stroke: currentColor`, square line caps. App icon: a white 8-bit ring (16×16 grid, 2 pixels thick) on black (`gen-assets.py`, which also makes `og.png`).

## Git

- Work directly on `main` and push there unless the owner says otherwise.
- Commit when a change is complete, with a clear message. Bump the `sw.js` cache name in the same commit as any app change.

## Roadmap the owner has discussed

1. **TV mode (web):** a ☰ menu option that hides everything but the game, for Apple TV screen mirroring. Limit: mirroring copies the phone's orientation, so with the phone upright (FlipPad) the game is small on the TV; it only fills the TV with the phone sideways.
2. **Native iPhone app via TestFlight (the real fix for the TV):** wrap this web app in a native shell and use iOS's external-display support to send a full-size game picture to the TV while the phone stays upright in the FlipPad. Needs Xcode on the owner's MacBook Pro M4 and the $99/yr Apple Developer account. TestFlight builds last 90 days; internal testing needs no review.
