---
name: explorable
mood: A warm paper desk where the numbers are toys: serif headline, huge rolling figures, color that names a variable.
fits: [calculator, explainer, game, report]
family: quiet-minimal
loud: false
source: https://brilliant.org
source_note: Converted from the show-me Explorable style; references Brilliant, ciechanow.ski, ncase.me, Distill
---

# explorable

## Mood
A warm paper desk where the numbers are toys: serif headline, huge rolling figures, color that names a variable.

## When to use
Calculators, explorables, rule-with-numbers explainers, reports where a reader plays with inputs.

## Palette
- `--bg` #f3f2ef light, #121211 dark: page background
- `--surface` #ffffff light, #1b1b1a dark: raised area
- `--ink` #141413 light, #f2f1ec dark: main text
- `--muted` #66655f light, #a3a19a dark: secondary text
- `--line` #e4e2dc light, #2e2d2a dark: hairlines
- `--accent` #2f5bea light, #7c9bff dark: the one color that means something
- `--accent-ink` #ffffff light, #121211 dark: text on accent
- `--ok` #17784c light, #4cc38a dark: state: good
- `--warn` #8a5200 light, #f2b544 dark: state: caution
- `--bad` #b42318 light, #f26b57 dark: state: error
- Extras: `--press` 0 3px 0 var(--line), `--sheet-2` #faf9f6 / #20201e, `--var-1` #2f5bea / #7c9bff, `--var-1-soft` #e7edfd / #1b2340, `--var-2` #7a4cf0 / #b195ff, `--var-2-soft` #efe9fd / #271e3f, `--var-3` #e0662d / #ff9a66, `--var-3-soft` #fcece3 / #3a2216

## Type pairing
Instrument Serif for headlines (italic for the turn), Instrument Sans for reading, Geist Mono for figures. Display `"Instrument Serif"`, body `"Instrument Sans"`, mono `"Geist Mono"`. Headline `clamp(44px,7vw,96px)`, weight 400, tracking -.02em, line 1. Body 17px at 1.6, measure 62ch. Google Fonts only.

## Spacing
Base 8px. One control per idea, generous gaps between the sentence and its figure.

## Radius
16px for panels, 10px for inputs, pill for chips.

## Borders
1px warm hairline. Chunky controls add a 3px bottom edge instead of a heavier border. Token: `--border: 1px solid var(--line)`.

## Shadows
One soft drop under raised panels (12px blur, 6% ink). Pressable buttons use the bottom edge (--press).

## Motion
Feedback, never decoration: values tween in 350 to 500 ms, markers glide with a soft overshoot (--spring), a crossed threshold pops once. Curve `cubic-bezier(.22,1,.36,1)`, 160ms fast, 450ms medium. Reduced motion sets both to 0ms.

## Do
- Give each variable one color (--var-1..3) and keep it in the word, the slider and the bar.
- Make numbers huge and let them roll.
- Keep 2 to 4 variable colors per page.

## Don't
- Do not use the variable colors as decoration.
- Do not show a result without the input that moved it.
- Do not use more than one serif weight.

## Source
Converted from the show-me Explorable style; references Brilliant, ciechanow.ski, ncase.me, Distill.
Inspiration: https://brilliant.org, https://ciechanow.ski/bicycle/, https://ncase.me/trust/, https://distill.pub/2017/momentum/.
