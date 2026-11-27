---
name: atelier-noir
mood: Huge thin type on black, porcelain text, a trace of champagne, almost nothing else.
fits: [landing, product-page, video, report]
family: editorial-luxury
loud: false
scheme: dark
source: https://www.apple.com/mac-pro/
source_note: Refero Styles DESIGN.md (obsidian stage, porcelain text, hairline steel borders, one concentrated accent), pulled 2026-11-27; luxury mood also from the fashion references
---

# atelier-noir

## Mood
Huge thin type on black, porcelain text, a trace of champagne, almost nothing else.

## When to use
Premium product reveals, fashion and luxury pages, brand films, keynote-style launches.

## Palette
- `--bg` #f5f5f7 light, #000000 dark: page background
- `--surface` #ffffff light, #0e0e0e dark: raised area
- `--ink` #0c0c0d light, #f5f5f7 dark: main text
- `--muted` #5c5c61 light, #a1a1a6 dark: secondary text
- `--line` #d2d2d7 light, #2b2b2e dark: hairlines
- `--accent` #8a6a2c light, #c8a977 dark: the one color that means something
- `--accent-ink` #ffffff light, #0b0907 dark: text on accent
- `--ok` #1f6b3a light, #8fcf9f dark: state: good
- `--warn` #7a5200 light, #d9b36a dark: state: caution
- `--bad` #a3261c light, #e58a80 dark: state: error

## Type pairing
Bodoni Moda at 400 set enormous for headlines, Jost light for reading, mono only for specs. Display `"Bodoni Moda"`, body `"Jost"`, mono `"IBM Plex Mono"`. Headline `clamp(56px,11vw,176px)`, weight 400, tracking -.03em, line .9. Body 16px at 1.65, measure 52ch. Google Fonts only.

## Spacing
Base 8px. Vast space: 160px or more between sections, short copy.

## Radius
0. Edges are straight; images are full-bleed.

## Borders
1px steel hairline, used rarely, for a spec table or a divider. Token: `--border: 1px solid var(--line)`.

## Shadows
None. Depth is the stage: black behind, product lit.

## Motion
Slow and smooth: 700ms ease-out on reveals, parallax on the hero, nothing bounces. Curve `cubic-bezier(.16,1,.3,1)`, 200ms fast, 700ms medium. Reduced motion sets both to 0ms.

## Do
- Let one headline fill the screen.
- Use the champagne for a rule, a link or a price, no more.
- Use full-bleed imagery with little text.

## Don't
- Do not add color beyond the champagne.
- Do not use bold weights.
- Do not box content in cards.

## Source
Refero Styles DESIGN.md (obsidian stage, porcelain text, hairline steel borders, one concentrated accent), pulled 2026-11-27; luxury mood also from the fashion references.
Inspiration: https://www.apple.com/mac-pro/, https://www.gucci.com/us/en/, https://www.chanel.com/us/.
Palette notes via Refero Styles (styles.refero.design); values adapted, not copied.
