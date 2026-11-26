# Style families for learning pages

Learning pages are never the default plain look.
Pick a family by what the page shows, then make it your own.
The method is your own design method; keep a taste file of the calls you make.

| The page shows | Family | Token file | Feels like |
|---|---|---|---|
| a system map or diagram, how the parts fit | Control Room | `control-room.css` | Linear, Raycast, Vercel: near-black, hairlines, flow along the edges |
| a calculator or explorable, a rule with numbers | Explorable | `explorable.css` | Brilliant, Ciechanowski: warm paper, serif headline, huge rolling numbers |
| a game where the learner plays someone | Playground | `playground.css` | Duolingo, Brilliant paths, Rainbow: loud colours, 3D buttons, bounce |
| an explainer or story, start to end | Editorial | `editorial.css` | The Pudding, Stripe Press, Distill: huge soft display, sticky figure, scroll steps |

Each token file opens with its mood and 2 to 4 reference URLs.

## Rules

- **Starting points, not uniforms.** Pull at least one fresh reference each time (Refero Styles, Godly, Awwwards, or a product in the topic's own industry), screenshot it, and change at least one of type, accent or layout so two pages never look cloned.
- **Client pages blend the client's brand** when the lesson is about their product: its figures font, its state colours, its signature line. Keep the family's layout and motion.
- **Alive by default.** Hover and press states, an orchestrated entrance, numbers that tween, flow that moves in the direction things travel. Animate `transform` and `opacity`, and respect `prefers-reduced-motion`.
- **Light and dark, phone and desktop.** Both modes designed, a toggle on the page, and a phone layout that is redrawn, not shrunk.
- **Quality bar.** Would it look at home next to Brilliant or Linear? If it looks like a default dashboard, it is not done.
- **Self-contained.** One HTML file, Google Fonts and CDN libraries allowed, no build step, copy the tokens into the page's `:root` (the lesson site serves single files).
- **Log the call.** When the user picks or rejects a family, add a dated line to the taste file.
