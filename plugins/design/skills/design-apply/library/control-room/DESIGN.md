---
name: control-room
mood: Near-black control room: hairlines made of light, one glowing accent, flow shown by motion.
fits: [diagram, dashboard, docs, product-page]
family: product-saas
loud: false
source: https://linear.app
source_note: Converted from the show-me Control Room style; references Linear, Raycast, Vercel, Stripe
---

# control-room

## Mood
Near-black control room: hairlines made of light, one glowing accent, flow shown by motion.

## When to use
System maps, diagrams, dashboards, docs for developer products: anything about how parts connect.

## Palette
- `--bg` #fafafa light, #08090a dark: page background
- `--surface` #ffffff light, #0f1012 dark: raised area
- `--ink` #0b0b0c light, #f7f8f8 dark: main text
- `--muted` #62666d light, #8a8f98 dark: secondary text
- `--line` rgba(0,0,0,.08) light, rgba(255,255,255,.08) dark: hairlines
- `--accent` #4353ff light, #8b9cff dark: the one color that means something
- `--accent-ink` #ffffff light, #08090a dark: text on accent
- `--ok` #17784c light, #4cc38a dark: state: good
- `--warn` #8a5200 light, #f2b544 dark: state: caution
- `--bad` #b42318 light, #f26b57 dark: state: error
- Extras: `--accent-soft` rgba(67,83,255,.08) / rgba(139,156,255,.12), `--faint` #9a9ea6 / #5c6068, `--flow-a` #4353ff / #8b9cff, `--flow-b` #17784c / #4cc38a, `--flow-c` #8a8f98 / #a1a1a8, `--flow-d` #7c4dff / #c39bff, `--line-strong` rgba(0,0,0,.16) / rgba(255,255,255,.16), `--sheet-2` #f4f4f5 / #16171a

## Type pairing
Geist for display and body, Geist Mono for figures. Headlines weight 600, tracking -.045em. Display `"Geist"`, body `"Geist"`, mono `"Geist Mono"`. Headline `clamp(40px,6vw,84px)`, weight 600, tracking -.045em, line 1.02. Body 16px at 1.55, measure 64ch. Google Fonts only.

## Spacing
Base 8px. Sections breathe at 80px or more; panels use 16 to 24px padding.

## Radius
12px for panels, 8px for chips, 18px for hero containers.

## Borders
Hairlines made of white at 8% opacity (black at 8% in light). Stronger line at 16% for the selected node. Token: `--border: 1px solid var(--line)`.

## Shadows
A 1px ring plus one soft drop. On focus, a faint accent glow (0 0 40px at 18%).

## Motion
Quick and exact, ease-out-expo, no bounce. Dots travel along edges (--flow-speed). Selecting a node lights its links and dims the rest. Curve `cubic-bezier(.16,1,.3,1)`, 140ms fast, 320ms medium. Reduced motion sets both to 0ms.

## Do
- Let depth come from white opacity, not new colors.
- Use mono for every number and label.
- Animate only to show direction of flow.

## Don't
- Do not add a second glow color.
- Do not use bounce or spring easing.
- Do not fill panels with solid bright colors.

## Source
Converted from the show-me Control Room style; references Linear, Raycast, Vercel, Stripe.
Inspiration: https://linear.app, https://www.raycast.com, https://vercel.com, https://stripe.com.
