# Film kit

A copy of the motion system behind a set of product films. Copy it into a Remotion project, then add one folder per product.

## What is here

| Path | What it does |
|---|---|
| `src/kit/film/timeline.ts` | Plain data and timing: scene types, beat fitting (18 frames = one beat at 100 BPM), caption ducking windows, sound cues on recorded clicks, the music plan. No React, so Node can read it. |
| `src/kit/film/Film.tsx` | Renders a `FilmCut` (scene list) in `wide` (16:9) or `tall` (9:16): title, footage scenes, drawn panels, end card, music and sounds. |
| `src/kit/film/AppWindow.tsx` | Real footage in a framed window that tilts in; `Spotlight` and `NumberCallout` (number or quote) pinned to capture marks. |
| `src/kit/film/pieces.tsx`, `Cards.tsx` | Stage, wordmark, ring, kinetic words, caption card, chapter tag, speed and note tags, title and end cards. |
| `src/kit/film/theme.ts` | `FilmTheme`: one per product, from the app's own tokens. `dark: true` for dark apps. |
| `src/kit/film/Sound.tsx` | Music bed with ducking plus UI sounds. |
| `src/kit/Shot.tsx`, `shot-meta.ts`, `registry.ts` | Footage camera (zoom keys in footage px, source frames), cursor overlay, composition registry type. |
| `scripts/make_audio.py` | Original music beds and UI sounds, synthesized (no samples). `bed --seconds --drop --outro --key`, `sfx --dir`. |
| `scripts/film-plan.mjs` | Prints each cut's frames, music drop and outro from the scene data; `--beds` prints the `make_audio.py` commands. Edit its product list. |
| `scripts/studio-sheet.mjs` | Contact sheet from a running Studio (seek, screenshot, tile). `SHEET_WAIT=3000` for multi-clip scenes. |
| `scripts/render-films.sh` | Render, master to -16 LUFS with a -2 dBFS limiter, decode check, loudness and ducking report, contact sheet. Edit the FOLDER and PREFIX maps. |
| `scripts/duck-check.py` | Measures how far the music sits under captions in the final file (design 5.7 dB). |
| `example/` | A fictional Northwind Tasks film (board, task detail, weekly summary): `theme.ts` (colors and fonts), `filmCuts.ts` (scenes, camera keys, captions, callouts), `Film.tsx` (theme and compositions). |
| `reference/` | Not included. Local notes may provide contact sheets of the approved look (16:9 main, 9:16 social). |

## Setup notes

- Packages: `remotion`, `@remotion/media`, `@remotion/transitions`, `@remotion/google-fonts` (same version), React 19.
- Footage: 1600x900 CSS px captures (any pixel density), each with a JSON meta: `width`, `height`, `fps`,
  `frames`, `cursor` (moves and clicks by source frame) and `marks` (named boxes in footage px). Clicks
  become sound cues; marks place spotlights and callouts.
- Audio files are generated, not committed: `uv run --with numpy --with scipy python scripts/make_audio.py sfx --dir public/audio/sfx`,
  then the bed commands from `node scripts/film-plan.mjs --beds`.
- `film-plan.mjs` bundles the `filmCuts.ts` files with the project's own esbuild; keep `filmCuts.ts`
  free of React and font imports.
