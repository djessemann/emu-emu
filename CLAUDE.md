# Pocket 6502 — project notes for Claude Code

**Pocket 6502** is a dead-simple NES emulator for phones: portrait first, touch controls, a ROM library, one save state per game, and plug-in controller support. It started as a Claude artifact and is moving here to be hosted on GitHub Pages.

- Repo: `djessemann/snappy-emu` (default branch `main`)
- Live: `https://djessemann.github.io/snappy-emu/`
- Owner is non-technical: do the git, build and deploy work yourself rather than handing over instructions. Explain results in plain, short English.

## First-time setup (do this first)

1. Push every file in this folder to `main` of `djessemann/snappy-emu`, at the repo root. (Done.)
2. Make sure `.nojekyll` is at the root (it is in this folder).
3. Turn on **GitHub Pages → Deploy from a branch → `main` → `/ (root)`**. If you can't change Pages settings from the session, say so plainly and tell the owner exactly where to click: repo **Settings → Pages → Source: Deploy from a branch → Branch: main / (root) → Save**.
4. Wait for the Pages build, then confirm `https://djessemann.github.io/snappy-emu/` loads (index.html, not the README).
5. Tell the owner: open the link in Safari on the iPhone → Share → **Add to Home Screen**. Games added in the old Claude artifact don't carry over (browser storage is per site), so ROMs need to be added again.

## Repo layout (keep it minimal)

```
index.html          # the whole app: HTML + CSS + JS inline
vendor/jsnes.min.js # emulator core, jsnes 1.2.1 (Apache-2.0), local copy for offline use
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
- **Bump `CACHE` in `sw.js`** (`pocket6502-v1` → `v2` …) whenever any cached file changes, or installed users keep the stale version. If you add a new file the app needs, add it to `ASSETS` too.
- Keep everything self-contained: no external fonts, scripts or fetches, or offline breaks.

## How the app works

### Screens
- **Library:** header with the name, `+` (add games) and `···` (opens "remove games" and "help"). Rows show the game name only, sorted by last played. "remove games" puts an `×` on each row until "done". Empty state is one dashed "add a game" box.
- **Player:** game screen on top, d-pad bottom left, B/A bottom right (diagonal, NES-style), and a bottom row with `☰` (menu, far left), `select`, `start`.
- **Menu (☰):** pauses the game. Game name + `×` (resume). `save` / `load` (one slot; load is disabled until a save exists), then three icon buttons: library, restart, sound. Saving or loading closes the menu and shows a one-word flash ("saved", "loaded").
- **Landscape:** d-pad left, screen center, buttons right.

### Input
- **Touch:** one pointer handler on `#player` hit-tests zones by rectangle (`measure()` caches rects). D-pad is 8-way by angle from center with a small dead zone, and a thumb that starts on it stays locked to it while sliding. Pressing between A and B hits both. Light haptic tick where supported.
- **Keyboard:** arrows, Z = B, X = A, Enter = Start, Shift = Select, Esc = menu.
- **Controllers (gameplay only, by owner's choice — no menu/library navigation):** standard Gamepad API, polled every frame while the player is open. Any connected pad flips the player into `pad-mode`: on-screen d-pad/A/B/select/start hide, the screen gets bigger, ☰ stays. A/B map **by position** like an NES pad: right (or top) = A, bottom (or left) = B. D-pad 12–15 plus left stick, select 8, start 9. Built for the **8BitDo FlipPad** (USB-C, Apple-supported). Browsers only report a pad after its first button press.

### Saving (all in IndexedDB `pocket6502`, version 2)
| Store | Key | Holds |
|---|---|---|
| `meta` | `id` (keyPath) | `{id, name, file, size, mapper, added, played}` |
| `data` | game id | ROM bytes (`Uint8Array`) |
| `states` | game id | auto "resume" snapshot (jsnes `toJSON()` minus `romData`), written on leave, app switch, and every 30s |
| `slots` | game id | the one manual save state `{at, s}` |
| `sram` | game id | in-game battery save, `$6000–$7FFF` (8 KB), flushed every 2s when the game wrote to it, only for ROMs with the battery flag |

- Game id = FNV-1a hash of the ROM bytes (dedupes re-adds).
- Restart clears `states` only. In-game saves and the save state survive.
- Removing a game deletes it from all five stores.
- If IndexedDB is blocked, everything falls back to memory and a note says games won't be kept.

### Emulator
- jsnes 1.2.1. Supported mappers: 0, 1, 2, 3, 4, 5, 7, 11, 34, 38, 66, 94, 140, 180. Unsupported ones show an error when opened.
- Runs at 60.0988 fps off `requestAnimationFrame` with an accumulator (fine on 120 Hz screens). Audio: ring buffer into a ScriptProcessor, started inside the first tap (iOS needs a user gesture). Screen wake lock while playing.

## UI style (match `nesprite` and `nes-tracker`)

- Black `#000` background, white text and **1px white borders**, muted `#999`, monospace (`ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace`).
- **No rounded corners anywhere.** No shadows, gradients, or animation.
- **Active / held = inverted:** white fill, black text.
- Dialogs are in-app overlays (black box, white border), never `alert/confirm/prompt`. Confirm pattern: `cancel` outlined + primary inverted.
- Copy is lowercase, short, and plain. Owner did a UX pass to strip it down: prefer icons where the meaning is obvious (`+`, `···`, `☰`, `×`, library grid, restart arrow, speaker), and keep words only where an icon would be a guess (`select`, `start`, `a`, `b`, `save`, `load`, `done`). No timestamps, file sizes, or "may not run" labels — those were removed on purpose.
- Icons are inline SVG, 20px, `stroke: currentColor`, square line caps. App icon is a white 8-bit d-pad on black (`gen-assets.py`).

## Git

- Work directly on `main` and push there unless the owner says otherwise.
- Commit when a change is complete, with a clear message. Bump the `sw.js` cache name in the same commit as any app change.

## Roadmap the owner has discussed

1. **TV mode (web):** a ☰ menu option that hides everything but the game, for Apple TV screen mirroring. Limit: mirroring copies the phone's orientation, so with the phone upright (FlipPad) the game is small on the TV; it only fills the TV with the phone sideways.
2. **Native iPhone app via TestFlight (the real fix for the TV):** wrap this web app in a native shell and use iOS's external-display support to send a full-size game picture to the TV while the phone stays upright in the FlipPad. Needs Xcode on the owner's MacBook Pro M4 and the $99/yr Apple Developer account. TestFlight builds last 90 days; internal testing needs no review.
