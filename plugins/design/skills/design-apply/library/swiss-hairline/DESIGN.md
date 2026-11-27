---
name: swiss-hairline
mood: Crisp grotesk on white, giant tight headlines, hairline grid, one electric blue.
fits: [landing, product-page, docs, dashboard]
family: quiet-minimal
loud: false
source: https://vercel.com
source_note: Refero Styles DESIGN.md (near-white canvas, 8% hairlines, ink-black action, tight negative tracking), pulled 2026-11-27
---

# swiss-hairline

## Mood
Crisp grotesk on white, giant tight headlines, hairline grid, one electric blue.

## When to use
Landing and product pages, docs, dashboards that should feel precise and unadorned.

## Palette
- `--bg` #ffffff light, #0c0c0c dark: page background
- `--surface` #f6f6f5 light, #141414 dark: raised area
- `--ink` #111111 light, #f2f2f2 dark: main text
- `--muted` #5c5c5c light, #a0a0a0 dark: secondary text
- `--line` #e4e4e4 light, #2a2a2a dark: hairlines
- `--accent` #1a3cff light, #7088ff dark: the one color that means something
- `--accent-ink` #ffffff light, #0c0c0c dark: text on accent
- `--ok` #0f7a43 light, #4cc38a dark: state: good
- `--warn` #8a5200 light, #f2b544 dark: state: caution
- `--bad` #c4261d light, #f26b57 dark: state: error

## Type pairing
Schibsted Grotesk for everything, weight 500 headlines at -.055em tracking, JetBrains Mono for data. Display `"Schibsted Grotesk"`, body `"Schibsted Grotesk"`, mono `"JetBrains Mono"`. Headline `clamp(44px,7vw,104px)`, weight 500, tracking -.055em, line .96. Body 16px at 1.55, measure 58ch. Google Fonts only.

## Spacing
Base 8px on a strict grid. Columns divided by hairlines, 96px between sections.

## Radius
0. Square edges everywhere.

## Borders
1px light-grey hairlines divide columns and rows. No boxes around content. Token: `--border: 1px solid var(--line)`.

## Shadows
None.

## Motion
Fast and dry: 100 to 220ms, no overshoot. Hover underlines slide in. Curve `cubic-bezier(.2,0,0,1)`, 100ms fast, 220ms medium. Reduced motion sets both to 0ms.

## Do
- Set one huge headline and let space do the rest.
- Align everything to the column hairlines.
- Use the blue only on the action.

## Don't
- Do not round corners.
- Do not add shadows or gradients.
- Do not use more than two weights.

## Source
Refero Styles DESIGN.md (near-white canvas, 8% hairlines, ink-black action, tight negative tracking), pulled 2026-11-27.
Inspiration: https://vercel.com, https://wise.com/us/.
Palette notes via Refero Styles (styles.refero.design); values adapted, not copied.
