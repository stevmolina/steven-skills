---
name: playground
mood: Saturday-morning energy: loud saturated colors on white, thick rounded shapes, 3D buttons, bouncy feedback.
fits: [game, explainer, landing]
family: playful
loud: true
source: https://www.duolingo.com
source_note: Converted from the show-me Playground style; references Duolingo, Brilliant, Rainbow, ncase.me
---

# playground

## Mood
Saturday-morning energy: loud saturated colors on white, thick rounded shapes, 3D buttons, bouncy feedback.

## When to use
Games where the learner plays a person in the business, onboarding quizzes, kid-friendly landings.

## Palette
- `--bg` #ffffff light, #131f24 dark: page background
- `--surface` #ffffff light, #1a2a31 dark: raised area
- `--ink` #3c3c3c light, #f1f7fb dark: main text
- `--muted` #6b6b6b light, #9fb1bb dark: secondary text
- `--line` #e5e5e5 light, #37464f dark: hairlines
- `--accent` #58cc02 light, #58cc02 dark: the one color that means something
- `--accent-ink` #0d2600 light, #0d2600 dark: text on accent
- `--ok` #1f7a1f light, #58cc02 dark: state: good
- `--warn` #8a5200 light, #ffc800 dark: state: caution
- `--bad` #d33232 light, #ff6b6b dark: state: error
- Extras: `--sheet-2` #f7f7f7 / #202f36

## Type pairing
Baloo 2 for headlines at weight 800, Nunito for reading, JetBrains Mono for scores. Display `"Baloo 2"`, body `"Nunito"`, mono `"JetBrains Mono"`. Headline `clamp(40px,6.5vw,88px)`, weight 800, tracking -.01em, line 1.05. Body 17px at 1.55, measure 58ch. Google Fonts only.

## Spacing
Base 8px. Big tap targets (48px or more), roomy cards.

## Radius
18px for cards, 12px for small pieces, pill for tags.

## Borders
2px solid light grey outline on every box. Buttons swap the outline for a colored 4px bottom edge. Token: `--border: 2px solid var(--line)`.

## Shadows
No blur. Elevation is a flat 4px bottom edge in a darker shade of the fill (--edge plus a --c-*-edge color).

## Motion
Bouncy: right answers pop with overshoot and confetti, wrong ones shake once (400ms) and explain why. Curve `cubic-bezier(.34,1.56,.64,1)`, 160ms fast, 260ms medium. Reduced motion sets both to 0ms.

## Do
- Use several of --c-green, --c-blue, --c-pink, --c-yellow, --c-purple at once.
- Give every button a bottom edge.
- Explain a wrong answer in one line.

## Don't
- Do not mix flat and 3D buttons on one page.
- Do not put white text on --c-green or --c-yellow.
- Do not use the state colors as decoration.

## Source
Converted from the show-me Playground style; references Duolingo, Brilliant, Rainbow, ncase.me.
Inspiration: https://www.duolingo.com, https://brilliant.org/courses/logic-deduction/, https://rainbow.me, https://ncase.me/trust/.
