# Design scripts

Two Node scripts (Node 20 or newer). Both render pages in headless Chromium.

## check.mjs: is this page calm and readable?

    node check.mjs page.html            # or a URL
    node check.mjs page.html --json     # machine output
    node check.mjs page.html --out report.json

It renders the page at desktop (1440x900) and phone (390x844), each in light and dark, and
prints one row per check. Exit code 0 means no fail (warnings are fine), 1 means at least
one fail, 2 means the script could not run.

| Check | What it counts | Pass | Warn | Fail |
|---|---|---|---|---|
| colors | chromatic colors with no meaning, after merging near duplicates | <=1 | 2 | >=3 |
| words | visible words in the first view, desktop | <=90 | <=140 | >140 |
| words | visible words in the first view, phone | <=70 | <=110 | >110 |
| chips | inline code chips (`code`, `kbd`, `samp`, or mono text with a fill or border) on one screen | <=3 | <=6 | >6 |
| contrast | text below WCAG AA (4.5:1, or 3:1 for text 24px+ or 18.66px+ bold) | 0 | | >=1 |
| boxes | bordered, ringed, filled or lifted boxes of 2500px² or more on one screen | <=3 | 4-5 | >=6 |
| diagram boxes | outlined or filled rectangles inside one SVG drawing | <=8 | | >=9 |

What counts as meaning for colors: anything close to the `:root` tokens `--accent`,
`--accent-ink`, `--accent-text`, `--ok`, `--warn`, `--bad`, or any token named `--meaning-*`, `--state-*`,
`--flow-*` or `--mark*` (tints of those count too). The base palette `--bg`, `--surface`,
`--ink`, `--muted` and `--line` never counts, even when tinted. Grey-ish colors (OKLCH
chroma under 0.035), images and gradients are ignored.

Contrast skips text over a background image or gradient and says how many it skipped.
Boxes skip form fields, buttons, images, inline elements and short links. A "screen" is
one viewport height of the full page; the row shows the worst screen.

### Overrides

Put this in the page when the look is deliberate:

    <meta name="design-check" content="loud,cards">

| Value | Effect |
|---|---|
| `loud` | colors pass up to 6, warn up to 8 (a deliberately loud brand) |
| `cards` | boxes pass up to 12, warn up to 15 (cards are the content) |

The report names every check that was relaxed.

## gallery.mjs: compare systems side by side

    node gallery.mjs --systems quiet-ledger,swiss-hairline --out /tmp/gallery
    node gallery.mjs --systems a,b,c --sample my-page.html --title "Pick a look"
    node gallery.mjs --systems a,b --preview

| Option | Meaning |
|---|---|
| `--systems` | comma list; a folder name in the library, or a path to a folder with `DESIGN.md` and `tokens.css` |
| `--library` | library folder (default `../library`) |
| `--sample` | page to dress (default `../sample/sample.html`); keep its `<style id="tokens"></style>` slot |
| `--out` | output folder (default: `design-gallery` in the system temp folder) |
| `--title` | gallery heading |
| `--preview` | also save each desktop light shot as `<system>/preview.png` |

For each system it writes `<out>/<name>.html`, screenshots in `<out>/shots/` (desktop light
and dark, phone light) and runs the check. Then it writes `<out>/gallery.html`, which shows
the candidates side by side with their check numbers, and `<out>/report.json`. A system
with `loud: true` in its front matter gets the `loud` override.

## Playwright

`lib/browser.mjs` finds Playwright in this folder, then in the global npm root, and
otherwise installs `playwright-core` once into `~/.cache/design-check`. It launches
Playwright's Chromium, then installed Google Chrome, and as a last resort downloads
Chromium once. `DESIGN_CHECK_FORCE_INSTALL=1` skips the first two library places, to test
a clean machine.

## Fixtures

`fixtures/good.html` passes every check. `fixtures/boxy.html` fails all five.
`fixtures/systems/` holds three small test systems for the gallery.
