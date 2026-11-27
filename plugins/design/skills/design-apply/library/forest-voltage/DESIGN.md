---
name: forest-voltage
mood: Confident fintech: white canvas, fog cards, deep forest ink, one lime that means go.
fits: [landing, product-page, dashboard, video]
family: product-saas
loud: false
source: https://wise.com/us/
source_note: Refero Styles DESIGN.md (white canvas, fog cards, forest ink, lime voltage accent), pulled 2026-11-27
---

# forest-voltage

## Mood
Confident fintech: white canvas, fog cards, deep forest ink, one lime that means go.

## When to use
Money, product and pricing pages where trust and speed matter.

## Palette
- `--bg` #ffffff light, #0e1a08 dark: page background
- `--surface` #e8ebe6 light, #16260f dark: raised area
- `--ink` #0e0f0c light, #f2f6ee dark: main text
- `--muted` #454745 light, #aebba5 dark: secondary text
- `--line` #d3d8cf light, #2a3d20 dark: hairlines
- `--accent` #9fe870 light, #9fe870 dark: the one color that means something
- `--accent-ink` #163300 light, #163300 dark: text on accent
- `--ok` #1f7a3a light, #7ad48a dark: state: good
- `--warn` #8a5200 light, #f2b544 dark: state: caution
- `--bad` #b3261e light, #f26b57 dark: state: error
- Extras: `--fog` #e8ebe6 / #16260f, `--forest` #163300

## Type pairing
Bricolage Grotesque at 800 for tight, heavy headlines. Figtree for reading, Fira Code for amounts. Display `"Bricolage Grotesque"`, body `"Figtree"`, mono `"Fira Code"`. Headline `clamp(44px,8vw,120px)`, weight 800, tracking -.04em, line .94. Body 17px at 1.55, measure 56ch. Google Fonts only.

## Spacing
Base 8px. Big numbers, tight headline, 24 to 32px card padding.

## Radius
20px cards, pill buttons.

## Borders
Almost none. Fog-colored cards on white do the separating; a 1px line only on inputs. Token: `--border: 1px solid var(--line)`.

## Shadows
None. Flat fog cards.

## Motion
Friendly: 140 to 300ms with a small overshoot on buttons and toggles. Numbers count up. Curve `cubic-bezier(.3,1.3,.4,1)`, 140ms fast, 300ms medium. Reduced motion sets both to 0ms.

## Do
- Put a real number in the hero.
- Use lime only for the action and the active state.
- Invert a section to forest ink for contrast.

## Don't
- Do not set lime as text on white.
- Do not add drop shadows.
- Do not use more than one accent.

## Source
Refero Styles DESIGN.md (white canvas, fog cards, forest ink, lime voltage accent), pulled 2026-11-27.
Inspiration: https://wise.com/us/, https://www.revolut.com/.
Palette notes via Refero Styles (styles.refero.design); values adapted, not copied.
