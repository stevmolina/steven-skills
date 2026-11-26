---
name: product-demo-video
description: >-
  Use when making a promo or demo video (Remotion motion design) for one of
  the user's own products, a client feature demo, or a motion film for a
  PR's proof section; or when handing a video to a social team.
---

# Product demo video

> Local notes: if `~/.agents/skill-notes/product-demo-video.md` exists, read it first. It holds this setup's private facts for this skill (names, brands, paths, house rules) and wins over the generic text here.

Goal: a short, beautiful, on-brand motion video that shows what people can DO with the product.

Two kinds, one craft:
- **Promo** for the user's own products: about 20 s, outcome-led, sections 1-2 and 4.
- **Feature film** for client work and big features: real footage of the running app in the
  approved film look (section 3). Main about 45-50 s, social about 20 s, both 16:9 and 9:16.

## 1. Brand first (most important)
- Every product has its own visual identity. The video must look like it came from the product's own site: same colors, fonts, borders, textures, layout feel. Never a generic template.
- Before designing, open the product's live site and its styles (CSS/theme tokens in its repo) and pull the exact palette, fonts and signature elements.
- Feature films use the shared film look below, colored and typed from each app (example in `film-kit/example/`;
  local notes may provide reference contact sheets of the approved look).
  A new product without a brand: propose a distinct style with a link to a reference example, and get approval first.
- If it doesn't feel like that brand, it's wrong, even if it looks nice.

## 2. Story and taste
- Few words on screen, big type. Show outcomes (agent clicks a site, buys something, ships a feature), not implementation or tech terms.
- Dynamic but tasteful: spring/ease motion, staggered reveals, 3D UI cards, cursor-led action, cuts on the music beat. No cheap effects, no clutter.
- Promos end on the product name plus its live link.
- Never invent numbers, quotes or results.

## 3. Feature film

The kit is in `film-kit/` (read its README). Copy `src/kit/` and `scripts/` into the repo's Remotion
project; each product gets `theme.ts` (app tokens), `filmCuts.ts` (scene data) and `Film.tsx`.

**The look**
- Title: wordmark, kinetic headline (one word in the flag color), ring in the product's colors, "Synthetic demo data" chip.
- Chapters: the app floats in a framed window on the product's stage color, tilts in, drifts slightly.
  Chapter tag top left; honesty tags and the chip top right; one caption card under the window, never over the UI.
- The real result gets a spotlight (everything else dims) and a callout card that lifts the exact on-screen
  value: a number (`$1,280`, `42`) or a quote (an email subject, an assistant's answer).
- End card: ring, wordmark, product name and a small "Not real data" line. No big disclaimer lines.
- Structure: title, 3-6 chapters, end card. Every scene is a whole number of beats (18 frames at 30 fps).
- Dark apps keep their dark stage (`dark: true`); drawn panels (run logs, before/after rows) only for data that is not on screen, built from the real files.

**Honesty (non-negotiable)**
- Real footage of the running app only. Every number, name, draft or transcript on screen is the captured output, exactly as shown.
- Any footage faster than real time gets a speed tag; condensed waits and held screenshots get a note tag.
- Demo adapters and fixtures are named on screen (window bar or tag). Fictional names only, no client names, no savings claims.
- No commercial music. Feature films have no voiceover. Teaching films for a client (walkthroughs, explainers, training) do: a calm local voice from start to end.

**Sound**
- One original bed per cut from `make_audio.py`, sized by `film-plan.mjs` (drop on the first chapter, outro on the end card). Vary the key per product.
- Music ducks under every caption and callout (about 5.7 dB); UI ticks on the recorded clicks, a hit and chime on each callout, a whoosh between chapters.
- Master to -16 LUFS integrated with a fixed gain and a -2 dBFS limiter (`render-films.sh`). Fixed gain keeps the ducking.

## 4. Build, check, render
- Start Studio (`pnpm exec remotion studio --port <port> --no-open`) and open it in T3 preview or `browse`. Design there.
- Before rendering, check every cut with `studio-sheet.mjs` contact sheets (main and both socials).
  Blank frames in a sheet usually mean the video had not decoded yet: retry with `SHEET_WAIT=3000`.
- Render with `render-films.sh`: it masters, decode-checks, writes `<name>-loudness.txt` (with the ducking depth) and a contact sheet.
- On a small server, never run Studio and a render at the same time, and prefer one render with moderate
  concurrency (run it under `nice -n 10`) over parallel renders.
- Fonts come from Google Fonts at render time (needs network).

## 5. Hand-off
- Show the user the video plus a contact sheet. Iterate on their feedback.
- Feature films: attach to the PR's proof section, and keep the MP4 standalone so it can
  go to the client without the PR once the user says so.
- Promos: once approved, hand it to whoever posts with suggested social copy. Nothing gets published, scheduled
  or sent to a client without the user's explicit OK.
