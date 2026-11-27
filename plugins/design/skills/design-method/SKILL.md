---
name: design-method
description: >-
  The full method for designing a landing, a product page, a site redesign or a product
  video: brief, taste, fresh references, three named directions, tokens per project, a
  full HTML mockup, then the build as a pull request. Use when asked to design, redesign
  or restyle a site or page, give a product a brand, or make a product video look right.
---

# Design method

> Local notes: if `~/.agents/skill-notes/design-method.md` exists, read it first. It holds
> this setup's private facts for this skill (the reference page, the taste and guidelines
> files, each project's brand) and wins over the generic text here.

This file is the process. It holds no styles. Styles come from fresh references, the
library in `../design-apply/library/`, and each project's own brand. Use `design-find`
for the side-by-side gallery and `design-apply` for the automatic check. Use
`frontend-design` for build craft when you have it.

## 1. Brief and design read

Five lines before touching anything: product, audience, the page's one job, what is live
today (URL, meta, analytics), and constraints (stack, deadline, assets). For a redesign,
screenshot the current page first.

## 2. Read the taste and the guidelines

Read the taste file and the guidelines file your local notes name. Without them, read
`../design-apply/guidelines.md`. Treat both as signal, not a template: what keeps getting
picked, what was rejected and why, which way to lean and when to break it.

## 3. Fresh references

- The reference sources in your local notes first.
- Refero Styles (`../design-apply/scripts/refero.mjs list` and `get`), Godly, Awwwards,
  Land-book, the best landing-page roundups.
- At least 3 references from the product's own industry and 1 from outside it. Screenshot
  each and write one line on what to steal.

## 4. Three named directions

Each direction gets a name, a one-line mood ("warm parchment atelier"), type pairing,
palette, layout idea, motion idea and a hero sketch.

- At least one must be new to the person: not in the taste file and not another
  project's brand.
- Do not clone another of their project brands unless they ask.
- Save each direction as a library system (`design-find` step 3) and render the
  gallery, ideally with the real hero copy as the sample. They pick from the gallery.
- Log the pick and the rejections in the taste file.

## 5. Brand tokens per project

In the project's repo, not in the library: `brand.md` (name, mood line, rules, don'ts)
and `tokens.css` using the token names in `../design-apply/library/README.md`, plus
anything the brand needs (more colors, motion durations). Everything downstream reads
these tokens, including videos.

## 6. Full HTML mockup

One static HTML file with every section and real copy. Content in the HTML so a server
or crawler can read it without JavaScript. Run `../design-apply/scripts/check.mjs` on it,
fix, then send desktop and phone screenshots for approval. Do not build until approved.
A loud brand declares itself with `<meta name="design-check" content="loud">`.

## 7. Build as a pull request

Branch and pull request, never the main branch. For a redesign keep URLs, title, meta,
canonical, OG image, structured data and analytics. Screenshots in the pull request.

## 8. Optional product video

Same tokens. 20 to 30 seconds, cuts on the beat, show outcomes not implementation, no
handles or private data on frame. Check frame screenshots before the final render.

## 9. QA

- [ ] `check.mjs` passes (or every override is named and deliberate)
- [ ] Not one of the generic looks in `../design-apply/guidelines.md`
- [ ] Content readable without JavaScript; title, meta, canonical, OG intact
- [ ] Focus states, alt text, keyboard navigation
- [ ] `prefers-reduced-motion` respected
- [ ] No layout shift; hero image sized; fonts preloaded or swapped
- [ ] Phone at 375 px looks designed, not squeezed
- [ ] Copy is short; one idea per section

## 10. Log the call

A dated line in the taste file: what was picked, what was rejected, and why in the
person's words. Commit it.

## Motion rules

- Every animation has a reason: guide the eye, show state, or show the product.
- Animate `transform` and `opacity` only.
- Respect `prefers-reduced-motion`: swap for a fade or nothing.
- Scroll storytelling: pin sparingly, scrub for story, batch for lists, clean up on
  unmount, never hijack native scroll.
- One orchestrated hero entrance beats many scattered micro-animations.

## Sources

- [taste-skill](https://github.com/Leonxlnx/taste-skill)
- [anthropics frontend-design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)
- [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- [gsap-skills](https://github.com/greensock/gsap-skills)
- [Refero Styles](https://styles.refero.design)
