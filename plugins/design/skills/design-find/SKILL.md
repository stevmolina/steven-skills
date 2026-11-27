---
name: design-find
description: >-
  Find new design systems to borrow from: search reference sources, save 3 to 5 candidates
  into the design library, render the same sample content in each, run the automatic check,
  and show a side-by-side gallery so the person picks. Logs the pick and the rejections in
  a taste file. Use when asked to find a style, explore looks, "show me options", restyle a
  page, start a new brand, or when design-apply finds nothing that fits.
---

# Design find

> Local notes: if `~/.agents/skill-notes/design-find.md` exists, read it first. It holds
> this setup's private facts for this skill (reference lists, taste file, project brands)
> and wins over the generic text here.

Goal: the person sees real options side by side, with the same content, and picks with
their eyes. No mood boards of other people's screenshots, no single take.

The library, scripts and token contract live in the sibling skill:
`../design-apply/library/README.md` (read it first), `../design-apply/scripts/`.

## 1. Brief (five lines)

What the page or product is, who reads it, the page's one job, what exists today (a
screenshot if it is a redesign), and constraints (brand, stack, deadline). Read the taste
file your local notes name: what was picked before, what was rejected and why.

## 2. Search the sources

- **Refero Styles**, real sites with their measured styles:

      node ../design-apply/scripts/refero.mjs list
      node ../design-apply/scripts/refero.mjs get <link>

  `get` prints colors by use, type scale, radius, spacing and the page's layout notes.
- The reference lists in your local notes, when they exist.
- Godly, Awwwards, Land-book, and sites from the product's own industry.

Pick 3 to 5 candidates. At least one from outside the industry, at least one quiet
minimal option, and at least one that is new (not in the taste file, not another
project's brand). Do not offer three versions of the same idea: vary family, type and
color temperature.

## 3. Save each candidate as a system

For each one, add `library/<mood-name>/` with `DESIGN.md` and `tokens.css` exactly as
`../design-apply/library/README.md` says. Name it by mood (`salt-and-ink`, not the brand).
Cite the source site; never paste a link that holds an account or a long ID. Take the
measured values from the source, then make them yours: real hex, a Google Fonts pairing
close to the original, light and dark.

Where to save: into the library when it is a git clone you can commit to (open a pull
request with the new systems). Otherwise into the project, at `design/library/<name>/`;
the gallery script takes folder paths too. A client's own brand never goes in a shared
library.

## 4. Render the gallery

    node ../design-apply/scripts/gallery.mjs \
      --systems <name-or-path>,<name-or-path>,<name-or-path> \
      --out <folder> --title "<what we are choosing>"

Pass `--sample <page.html>` to render the person's own content instead of the shared
sample (the page needs `<style id="tokens">` in its head, or the tokens go in first).
The script screenshots each candidate at desktop and phone, light and dark, runs the
check on each, and writes `gallery.html` with everything side by side.

A candidate that fails the check gets fixed (usually contrast or one stray color) and
rendered again before anyone sees it. Then look at the gallery yourself, and open it for
the person. Say in one line what makes each candidate different.

## 5. Log the call

When the person picks, add one dated line to the taste file: what they picked, what they
passed on, and why in their words. Example:

    - 2026-11-27: Landing for X. Picked salt-and-ink ("calm, feels expensive").
      Passed on gumdrop (too loud) and swiss-hairline ("seen it everywhere").

Then hand the pick to `design-apply`, or to `design-method` for a full landing or product.

## Without a taste file

Create one in the project at `design/taste.md` and log there. The point is that the next
agent does not show the same rejected look again.
