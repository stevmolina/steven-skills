---
name: night-studio
mood: A soft dark studio: graphite surfaces, ivory text, one periwinkle accent, almost no borders.
fits: [dashboard, product-page, report, docs]
family: quiet-minimal
loud: false
scheme: dark
source: https://mercury.com
source_note: Refero Styles DESIGN.md (onyx canvas, graphite cards, ivory text, periwinkle action), pulled 2026-11-27
---

# night-studio

## Mood
A soft dark studio: graphite surfaces, ivory text, one periwinkle accent, almost no borders.

## When to use
Dashboards, finance and product pages, long reading sessions at night.

## Palette
- `--bg` #f4f4f8 light, #171721 dark: page background
- `--surface` #ffffff light, #1e1e2a dark: raised area
- `--ink` #1a1a26 light, #ededf3 dark: main text
- `--muted` #5b5b6d light, #b4b4c0 dark: secondary text
- `--line` rgba(26,26,38,.12) light, rgba(237,237,243,.10) dark: hairlines
- `--accent` #4553d6 light, #8490ff dark: the one color that means something
- `--accent-ink` #ffffff light, #0f0f18 dark: text on accent
- `--ok` #1d7a52 light, #6fd1a0 dark: state: good
- `--warn` #8a5200 light, #e6b866 dark: state: caution
- `--bad` #b3261e light, #f08a8a dark: state: error

## Type pairing
DM Sans for headlines and reading at weight 500, DM Mono for amounts and labels. Display `"DM Sans"`, body `"DM Sans"`, mono `"DM Mono"`. Headline `clamp(40px,5.6vw,80px)`, weight 500, tracking -.035em, line 1.04. Body 16px at 1.6, measure 60ch. Google Fonts only.

## Spacing
Base 8px. Cards pad 32px, sections 96px apart.

## Radius
12px on the few surfaces that exist, pill buttons.

## Borders
1px line at 10% ivory. Separation comes mostly from the step from --bg to --surface. Token: `--border: 1px solid var(--line)`.

## Shadows
One soft drop under floating panels only.

## Motion
Calm: 140 to 300ms ease-out-expo. Surfaces lift 2px on hover. Curve `cubic-bezier(.22,1,.36,1)`, 140ms fast, 300ms medium. Reduced motion sets both to 0ms.

## Do
- Layer --surface on --bg instead of drawing borders.
- Keep text ivory, never pure white.
- Use the periwinkle for the single main action.

## Don't
- Do not use pure black.
- Do not glow or gradient the accent.
- Do not stack three surface levels.

## Source
Refero Styles DESIGN.md (onyx canvas, graphite cards, ivory text, periwinkle action), pulled 2026-11-27.
Inspiration: https://mercury.com, https://superhuman.com.
Palette notes via Refero Styles (styles.refero.design); values adapted, not copied.
