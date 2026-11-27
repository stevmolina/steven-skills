---
name: kinetic-poster
mood: Poster-scale type on near-black, cream text, acid green, discipline tags in color, motion everywhere.
fits: [landing, video, product-page]
family: agency-motion
loud: false
source: https://gsap.com
source_note: Refero Styles DESIGN.md (near-black canvas, cream text, green brand accent, colored discipline labels), pulled 2026-11-27; agency feel also from the saved agency references
---

# kinetic-poster

## Mood
Poster-scale type on near-black, cream text, acid green, discipline tags in color, motion everywhere.

## When to use
Agency sites, launch pages, motion films, anything where the type and the movement are the brand.

## Palette
- `--bg` #fffce1 light, #0e100f dark: page background
- `--surface` #fff7c2 light, #171a18 dark: raised area
- `--ink` #0e100f light, #fffce1 dark: main text
- `--muted` #55564a light, #a8a893 dark: secondary text
- `--line` #cfcaa0 light, #42433d dark: hairlines
- `--accent` #0ae448 light, #0ae448 dark: the one color that means something
- `--accent-ink` #0e100f light, #0e100f dark: text on accent
- `--ok` #0f7a3a light, #3ddc84 dark: state: good
- `--warn` #8a5200 light, #ffb02e dark: state: caution
- `--bad` #b3261e light, #ff5d5d dark: state: error

## Type pairing
Syne at 800, set at poster size with -.05em tracking. Hanken Grotesk for reading, Spline Sans Mono for labels. Display `"Syne"`, body `"Hanken Grotesk"`, mono `"Spline Sans Mono"`. Headline `clamp(56px,14vw,220px)`, weight 800, tracking -.05em, line .88. Body 17px at 1.55, measure 54ch. Google Fonts only.

## Spacing
Base 8px. Tight leading (.88) on giant type, 120px between sections.

## Radius
Pill for buttons and tags, 0 for media.

## Borders
1px dark hairlines; outlined pill buttons in cream. Token: `--border: 1px solid var(--line)`.

## Shadows
None. Glow and gradient come from the media, not the UI.

## Motion
Bold: 600ms ease-in-out-quart reveals, scroll-scrubbed headlines, marquees, hover that swaps words. Respect reduced motion. Curve `cubic-bezier(.76,0,.24,1)`, 200ms fast, 600ms medium. Reduced motion sets both to 0ms.

## Do
- Set the headline as big as the viewport allows.
- Color-code categories with the --tag-* colors.
- Scrub motion to scroll, never hijack it.

## Don't
- Do not use the tag colors as the accent.
- Do not animate body text.
- Do not use rounded boxes for content.

## Source
Refero Styles DESIGN.md (near-black canvas, cream text, green brand accent, colored discipline labels), pulled 2026-11-27; agency feel also from the saved agency references.
Inspiration: https://gsap.com, https://www.basicagency.com/, https://www.instrument.com/.
Palette notes via Refero Styles (styles.refero.design); values adapted, not copied.
