---
name: editorial
mood: A visual essay: huge soft display type, calm serif reading text, side notes, one highlighter that marks the live word.
fits: [explainer, report, landing, video]
family: editorial-luxury
loud: false
source: https://pudding.cool
source_note: Converted from the show-me Editorial style; references The Pudding, Stripe Press, Distill
---

# editorial

## Mood
A visual essay: huge soft display type, calm serif reading text, side notes, one highlighter that marks the live word.

## When to use
Stories told start to end, long explainers, annual reports, launch essays.

## Palette
- `--bg` #fbf8f3 light, #201819 dark: page background
- `--surface` #ffffff light, #2a2122 dark: raised area
- `--ink` #1d1a16 light, #f3ece4 dark: main text
- `--muted` #6a6256 light, #b5a99c dark: secondary text
- `--line` #e7e0d4 light, #3d3233 dark: hairlines
- `--accent` #c2371b light, #ff7a5c dark: the one color that means something
- `--accent-ink` #ffffff light, #201819 dark: text on accent
- `--ok` #17784c light, #4cc38a dark: state: good
- `--warn` #8a5200 light, #f2b544 dark: state: caution
- `--bad` #b42318 light, #f26b57 dark: state: error
- Extras: `--mark` #ffd84d / #c9a227

## Type pairing
Fraunces at weight 850 with SOFT 100 for display, Newsreader for reading, JetBrains Mono for kickers. Display `"Fraunces"`, body `"Newsreader"`, mono `"JetBrains Mono"`. Headline `clamp(48px,9vw,128px)`, weight 850, tracking -.035em, line .98. Body 19px at 1.6, measure 62ch. Google Fonts only.

## Spacing
Base 8px. Generous margins, a 62ch column, side notes in the gutter.

## Radius
4px, almost square. Full-bleed color blocks carry the shape.

## Borders
1px warm hairlines between steps. Full-bleed blocks (--block-1..3) instead of boxes. Token: `--border: 1px solid var(--line)`.

## Shadows
None. Depth comes from a sticky figure and from color blocks.

## Motion
Scroll-driven: a sticky figure changes as steps scroll past (600ms eased). Never hijack native scroll. Curve `cubic-bezier(.25,1,.5,1)`, 180ms fast, 600ms medium. Reduced motion sets both to 0ms.

## Do
- Mark the live word with --mark.
- Open each section with a mono kicker.
- Let the figure lead the paragraph.

## Don't
- Do not use --block colors as text color.
- Do not add cards around paragraphs.
- Do not animate more than one thing per step.

## Source
Converted from the show-me Editorial style; references The Pudding, Stripe Press, Distill.
Inspiration: https://pudding.cool, https://pudding.cool/2024/10/crokinole/, https://press.stripe.com, https://distill.pub/2017/momentum/.
