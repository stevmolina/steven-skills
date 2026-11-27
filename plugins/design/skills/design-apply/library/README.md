# Design system library

One folder per design system. Each system is named by its mood, not by the site that
inspired it, and cites that site as its source. Systems are starting points: borrow the
tokens, then vary type, accent or layout so two pages never look cloned.

Client and company brands never go here. A project's own brand lives in that project's
repo (`brand.md` and `tokens.css`) and always wins over this library.

## A system folder

```
library/<system>/
  DESIGN.md     mood line, when to use, palette, type, spacing, radius, borders,
                shadows, motion, do and don't, source
  tokens.css    the token contract below, light and dark
  preview.png   the shared sample page rendered in this system (made by the gallery script)
```

`DESIGN.md` starts with a front matter block the scripts and skills read:

```yaml
---
name: quiet-ledger            # folder name, kebab-case, a mood
mood: Warm paper, one ink accent, numbers set like a ledger.
fits: [explainer, report, calculator]     # page purposes, see below
family: quiet-minimal          # quiet-minimal | product-saas | playful | editorial-luxury | agency-motion | notebook
loud: false                    # true when many colors are the point (the check then allows them)
source: https://example.com    # the site or Refero style it was drawn from
source_note: Refero Styles DESIGN.md, pulled 2026-11-27
---
```

Page purposes used in `fits`: `explainer`, `diagram`, `calculator`, `game`, `report`,
`landing`, `product-page`, `dashboard`, `docs`, `video`.

## The token contract

Every `tokens.css` defines these on `:root`. The sample page, the gallery and
`design-apply` only use these names, so any system can dress any page. Extra tokens are
fine; missing ones are not.

| Token | What it is |
|---|---|
| `--bg` | page background |
| `--surface` | a raised area (panel, card) when one is needed |
| `--ink` | main text |
| `--muted` | secondary text, still AA on `--bg` |
| `--line` | hairline color for rules and dividers |
| `--accent` | the one color that means something (the action, the highlight) |
| `--accent-ink` | text drawn on top of `--accent` |
| `--ok` `--warn` `--bad` | state colors; they mean a state and nothing else |
| `--font-display` | headline family |
| `--font-body` | reading family |
| `--font-mono` | code and figures |
| `--h1` | headline size, usually a `clamp()` |
| `--h1-weight` `--h1-track` `--h1-lead` | headline weight, letter spacing, line height |
| `--body` `--lead` | body size and line height |
| `--measure` | reading width, like `62ch` |
| `--space` | the base spacing unit; layouts use multiples of it |
| `--radius` | corner radius for the few boxes that exist |
| `--border` | the full border shorthand a box uses, like `1px solid var(--line)` |
| `--shadow` | elevation, or `none` |
| `--ease` `--t-fast` `--t-med` | motion curve and two durations |

Rules for the file:

- Load fonts with one `@import` from Google Fonts at the top. No other network calls.
- Dark mode in `@media (prefers-color-scheme: dark)` under
  `:root:not([data-theme="light"])`, and again under `:root[data-theme="dark"]`.
  A system that is dark by nature does the reverse for light.
- `prefers-reduced-motion: reduce` sets both durations to `0ms`.
- `--ink` and `--muted` on `--bg`, and `--accent-ink` on `--accent`, pass WCAG AA (4.5:1).

## Using a system

`design-apply` picks one, copies `tokens.css` into the page's `<style>`, and builds the
page with these names. To see systems side by side, `design-find` renders the sample page
in each one:

    node ../scripts/gallery.mjs --systems quiet-ledger,ink-and-hairline --out /tmp/gallery
