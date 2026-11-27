---
name: quiet-ledger
mood: Warm paper, serif headlines, one ink-blue accent, figures set like a ledger.
fits: [explainer, report, calculator, docs]
family: quiet-minimal
loud: false
source: https://www.notion.com
source_note: Refero Styles DESIGN.md (warm canvas, alpha-built hierarchy, 8% hairlines), pulled 2026-11-27; paper tone also from a second Refero style on the same warm canvas
---

# quiet-ledger

## Mood
Warm paper, serif headlines, one ink-blue accent, figures set like a ledger.

## When to use
Reports, memos, explainers and calculators for readers who want to think, not be sold to.

## Palette
- `--bg` #f6f3ec light, #1b1914 dark: page background
- `--surface` #fbf9f4 light, #23201a dark: raised area
- `--ink` #211e19 light, #efe9dc dark: main text
- `--muted` #675f53 light, #b0a794 dark: secondary text
- `--line` #ddd6c8 light, #373228 dark: hairlines
- `--accent` #1f4b99 light, #8fb2f0 dark: the one color that means something
- `--accent-ink` #ffffff light, #14161c dark: text on accent
- `--ok` #2f6b3a light, #7fc08a dark: state: good
- `--warn` #855500 light, #e0b04a dark: state: caution
- `--bad` #a12a1f light, #ee8c7d dark: state: error

## Type pairing
Literata for headlines at weight 500, Public Sans for reading, IBM Plex Mono for figures that line up in columns. Display `"Literata"`, body `"Public Sans"`, mono `"IBM Plex Mono"`. Headline `clamp(40px,5.6vw,76px)`, weight 500, tracking -.02em, line 1.06. Body 17px at 1.65, measure 60ch. Google Fonts only.

## Spacing
Base 8px. Long lines of 60ch, rows 16px apart, sections 80px apart.

## Radius
2px. Almost nothing is boxed.

## Borders
1px warm rule between rows. Tables and lists use rules, never cards. Token: `--border: 1px solid var(--line)`.

## Shadows
None.

## Motion
Almost still. Links and rows ease color over 120ms. Numbers may fade in once. Curve `cubic-bezier(.2,.7,.2,1)`, 120ms fast, 260ms medium. Reduced motion sets both to 0ms.

## Do
- Build hierarchy from size and weight.
- Set numbers in mono, right aligned.
- Use the accent for the one action or link that matters.

## Don't
- Do not wrap content in cards.
- Do not add a second accent.
- Do not use pure white or pure black.

## Source
Refero Styles DESIGN.md (warm canvas, alpha-built hierarchy, 8% hairlines), pulled 2026-11-27; paper tone also from a second Refero style on the same warm canvas.
Inspiration: https://www.notion.com, https://superhuman.com.
Palette notes via Refero Styles (styles.refero.design); values adapted, not copied.
