---
name: dotted-notebook
mood: Dotted paper, handwritten labels on highlighter tags, thick outlines, sticky-note cards.
fits: [explainer, landing, game, diagram]
family: notebook
loud: true
source: https://styles.refero.design
source_note: Original synthesis of the notebook-style portfolio look (dotted grid, highlighter tags, sticky notes); no single source site
---

# dotted-notebook

## Mood
Dotted paper, handwritten labels on highlighter tags, thick outlines, sticky-note cards.

## When to use
Explainers and landings that should feel human, sketched and friendly; process diagrams with sticky notes.

## Palette
- `--bg` #fbf6e9 light, #1d1b16 dark: page background
- `--surface` #fffdf6 light, #26231c dark: raised area
- `--ink` #1b1b1b light, #f4efe0 dark: main text
- `--muted` #5a5648 light, #b9b29c dark: secondary text
- `--line` #d8cfb2 light, #3a362b dark: hairlines
- `--accent` #ff8fb1 light, #ff9dbb dark: the one color that means something
- `--accent-ink` #1b1b1b light, #1d1b16 dark: text on accent
- `--ok` #1f7a3a light, #7fc08a dark: state: good
- `--warn` #855500 light, #e0b04a dark: state: caution
- `--bad` #b3261e light, #ee8c7d dark: state: error
- Extras: `--hl-blue` #a9d8ff / #4a7ca6, `--hl-pink` #ffb3cf / #b4527a, `--hl-yellow` #ffe566 / #b89b1c

## Type pairing
Caveat Brush for headlines and labels, Mulish for reading, Courier Prime for numbers and notes. Display `"Caveat Brush"`, body `"Mulish"`, mono `"Courier Prime"`. Headline `clamp(52px,8.5vw,120px)`, weight 400, tracking 0em, line .98. Body 17px at 1.6, measure 56ch. Google Fonts only.

## Spacing
Base 8px. Cards sit slightly tilted (rotate -1 to 1.5 degrees) with 24px padding.

## Radius
14px, with the thick outline making it feel hand drawn.

## Borders
2px solid ink on every card and tag. Pill tags carry a highlighter fill. Token: `--border: 2px solid var(--ink)`.

## Shadows
A small flat offset (2px 3px) in ink at 18%, like paper on paper.

## Motion
Playful but short: 140 to 320ms springy. Cards straighten on hover, arrows draw themselves. Curve `cubic-bezier(.3,1.4,.5,1)`, 140ms fast, 320ms medium. Reduced motion sets both to 0ms.

## Do
- Use --dots on the page background.
- Label things with highlighter pills (--hl-*).
- Draw arrows between ideas by hand-looking SVG paths.

## Don't
- Do not set body text in the handwritten face.
- Do not tilt more than 1.5 degrees.
- Do not drop the outline, it is the look.

## Source
Original synthesis of the notebook-style portfolio look (dotted grid, highlighter tags, sticky notes); no single source site.
Inspiration: https://styles.refero.design.
