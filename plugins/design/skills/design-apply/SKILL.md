---
name: design-apply
description: >-
  Dress any page, explainer, diagram, report or video in a real design system before it is
  shown, then run an automatic check (colors, words, contrast, boxes) and fix what fails.
  Use before producing anything visual: an HTML page, an explainer "with a picture", a
  diagram, a dashboard, a landing, a Remotion video. Fast path for quick explainers.
---

# Design apply

> Local notes: if `~/.agents/skill-notes/design-apply.md` exists, read it first. It holds
> this setup's private facts for this skill (guidelines and taste files, project brands,
> house rules) and wins over the generic text here.

Goal: nothing visual leaves this agent in the default look. Every page gets a named system,
follows the guidelines, and passes the check before anyone sees it.

Paths below are relative to this skill's folder. Scripts need Node 20+; they install a
headless browser on first use.

## 1. Pick a system (seconds)

Take the first that applies:

1. **The project has a brand.** The repo has `brand.md`, `tokens.css`, a theme file or a
   live site. Use its colors, fonts and radius. Map them onto the token names in
   `library/README.md` so the rest of this skill works. The brand always wins.
2. **The library fits.** Match the page's purpose to `fits:` in each
   `library/*/DESIGN.md` front matter. Defaults when nothing else steers you:

   | Page | First choice | Also good |
   |---|---|---|
   | explainer "with a picture" | quiet-ledger | editorial, explorable |
   | system map, diagram | control-room | swiss-hairline |
   | calculator, rule with numbers | explorable | quiet-ledger |
   | game, playful lesson | playground | gumdrop, dotted-notebook |
   | report, status, docs | quiet-ledger | night-studio, swiss-hairline |
   | dashboard | night-studio | control-room, forest-voltage |
   | landing, product page | ask design-find | swiss-hairline, forest-voltage, kinetic-poster |
   | video | the product's brand | atelier-noir, kinetic-poster |

   Do not reuse the system the previous page in this project used unless it is the brand.
3. **Nothing fits, or it is a landing or product page.** Run `design-find` and let the
   person pick.

Read the chosen `DESIGN.md` in full: its Do and Don't lists are part of the system.

## 2. Build with the tokens

- Copy the system's `tokens.css` into the page as its own first `<style id="tokens">`
  block in the head (the id lets the gallery swap systems) (its font `@import` only works at the top of a stylesheet), or link it in a project
  that has a build.
- Use only the contract names (`--bg`, `--ink`, `--accent`, `--font-display`, `--space`...)
  in the page's own CSS. No new hex values except inside the token block.
- Follow `guidelines.md` (or the personal guidelines file your local notes name). The
  short version: one idea per screen, hierarchy from type not boxes, one accent that
  means something, plain words, calm motion, light and dark, a real phone layout.
- For a diagram, draw the real mechanism with real names, in SVG, using the tokens.
  Prefer lines and type to a box per step.
- For a Remotion video, turn the tokens into the video's `theme.ts`.
- Vary at least one of type, accent or layout from the system's sample so pages do not
  look cloned.

## 3. Check, fix, then show

    node scripts/check.mjs path/to/page.html

It renders the page at desktop and phone, light and dark, and reports:

- colors with no meaning (pass 1 or fewer)
- words in the first view (pass 90 desktop, 70 phone)
- code chips per screen (pass 3 or fewer)
- text below WCAG AA contrast (pass 0)
- bordered or filled boxes per screen (pass 3 or fewer)

Fix every fail and rerun until it exits 0. Warnings are allowed when you can say why.
When a fail is the point (a loud brand, a card gallery), add
`<meta name="design-check" content="loud">` or `content="cards"` and name the reason in
your reply. Thresholds and details: `scripts/README.md`.

Then look at it yourself: screenshot desktop and phone and read the images. The check
cannot tell if one clear thing stands out; you can. Only then open it for the person.

## 4. Report

Say which system you used and why in one line, and that the check passed (or which
override you used). If the person reacts to the look, hand that to `design-find`'s
taste log.

## Fast path (quick explainer)

Steps 1 to 3 with no research: purpose table, copy tokens, write the page, run the check
once, fix, show. Budget: under a minute of overhead on top of writing the content.
