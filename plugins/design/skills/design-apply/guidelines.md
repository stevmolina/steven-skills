# Design guidelines (generic)

Leanings, not rules. Each one says which way to lean, why, and when to break it. A
project's own brand, and what the person asks for on a given page, win over this file.
If a personal guidelines file is named in your local notes, read that instead: it wins.

## 1. Less on screen
Lean toward one idea per screen, few elements and generous space. Cut before adding.
Why: crowded pages are the most common complaint about generated UI.
Break it when a dense tool earns it, such as a table someone scans every day.

## 2. Fewer clicks, clear flow
Lean toward an obvious main action, close at hand. Organize by what the person does next.
Why: people judge an app by its flow before its colors.
Break it when a rare or risky action deserves a deliberate extra step.

## 3. Hierarchy from type, not boxes
Lean toward a big headline, short lines, and size and weight doing the structure. Few
borders, cards, badges and code chips.
Why: when every step sits in its own bordered box with code in every line, nothing stands
out. That is the single most recognisable generic look.
Break it when cards are the content: a gallery, a bento of features.

## 4. Quiet base, one accent
Lean toward a neutral base and one accent color that means something (the action, a state).
Break it when the brand is loud on purpose. Then go fully loud, not halfway, and say so with
`<meta name="design-check" content="loud">`.

## 5. Show the real thing
Lean toward the product working, a real number, a real screen. Not paths or labels about it.
Break it for an explainer of an internal idea: draw the idea, still with real names.

## 6. Plain words in the UI
Lean toward short labels a person would say out loud. No file paths, IDs or jargon.
Break it when the reader is a developer and the command is the thing they copy. Even then,
one command block beats a code chip in every line.

## 7. Calm motion
Lean toward motion that explains or responds: hover, press, a number that rolls. Quick,
eased, `transform` and `opacity` only, and nothing under `prefers-reduced-motion`.
Break it on a landing page or a video, where bold scroll motion is the brand.

## 8. Elegant means finished
Lean toward aligned edges, spacing on a scale, one type pairing, light and dark both
checked, and a phone layout redrawn for the phone. The bar: it sits next to the best
product sites of its kind and does not look generic.

## Avoid the generic look
- Overused fonts as the display face (Inter, Roboto, Arial, system UI everywhere).
- Purple-to-blue gradients on white.
- Centered hero, three feature cards, logo row, pricing, in that order, by default.
- Timid palettes spread evenly with no dominant color.
- Emoji as icons, stock 3D blobs, glassmorphism by default.

## Quick check before showing a page
- Could a third of the elements go without losing anything?
- Is there one clear first thing to look at?
- Does every color mean something?
- Is there a path, ID or word a user would not say?

`scripts/check.mjs` measures the last three for you (colors, words, contrast, boxes, code
chips). The first one is your judgement.
