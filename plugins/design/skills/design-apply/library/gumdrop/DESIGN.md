---
name: gumdrop
mood: Candy-bright and glossy: hot pink on cream, soft gradients, round everything, springy.
fits: [landing, game, product-page, explainer]
family: playful
loud: true
source: https://rainbow.me
source_note: Drawn from the saved playful references (Rainbow, Klarna app page, Brilliant); no single Refero style, palette and rules written for this library
---

# gumdrop

## Mood
Candy-bright and glossy: hot pink on cream, soft gradients, round everything, springy.

## When to use
Consumer landings, games, onboarding, anything meant to feel like a toy.

## Palette
- `--bg` #fff7fb light, #1b0f24 dark: page background
- `--surface` #ffffff light, #28163a dark: raised area
- `--ink` #2a1233 light, #fff2fa dark: main text
- `--muted` #6b5278 light, #cdb4d8 dark: secondary text
- `--line` #f0d9e6 light, #4a2d5e dark: hairlines
- `--accent` #ff6fae light, #ff7eb6 dark: the one color that means something
- `--accent-ink` #2a1233 light, #2a1233 dark: text on accent
- `--ok` #14803a light, #5ee09a dark: state: good
- `--warn` #8a5200 light, #ffd23f dark: state: caution
- `--bad` #c62828 light, #ff8080 dark: state: error

## Type pairing
Fredoka at 700 for rounded headlines, Outfit for reading, Fira Code for scores. Display `"Fredoka"`, body `"Outfit"`, mono `"Fira Code"`. Headline `clamp(44px,8vw,112px)`, weight 700, tracking -.02em, line .98. Body 17px at 1.55, measure 54ch. Google Fonts only.

## Spacing
Base 8px. Fat tap targets, bubbly 32px card padding.

## Radius
28px cards, pill buttons and tags.

## Borders
2px pale-pink outline. Color blobs and gradients do more work than lines. Token: `--border: 2px solid var(--line)`.

## Shadows
Soft pink glow under raised pieces (10px 28px at 28%).

## Motion
Springy: 180 to 380ms with overshoot. Hover wiggles, taps squish, success bursts. Curve `cubic-bezier(.34,1.56,.64,1)`, 180ms fast, 380ms medium. Reduced motion sets both to 0ms.

## Do
- Mix --c-lilac, --c-sun, --c-mint, --c-sky and --c-coral freely.
- Use --grad for one hero shape.
- Keep ink dark on every colored fill.

## Don't
- Do not put white text on pink or yellow.
- Do not use thin type.
- Do not go halfway: if loud, be loud.

## Source
Drawn from the saved playful references (Rainbow, Klarna app page, Brilliant); no single Refero style, palette and rules written for this library.
Inspiration: https://rainbow.me, https://www.klarna.com/us/klarna-app/, https://brilliant.org.
Palette notes via Refero Styles (styles.refero.design); values adapted, not copied.
