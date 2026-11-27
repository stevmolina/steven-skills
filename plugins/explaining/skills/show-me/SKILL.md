---
name: show-me
description: Help the user understand the current topic visually with concise diagrams, code-shape sketches, and focused HTML artifacts. Use when the user asks to see how something works, for example "with a picture", "show me", "draw how X works", "diagram this", "visualize", or when an explanation has three or more connected parts.
---

> Local notes: if `~/.agents/skill-notes/show-me.md` exists, read it first. It holds this setup's private facts for this skill (names, brands, paths, house rules) and wins over the generic text here.

Help the user understand the current topic of conversation visually. Skip the preamble and keep prose brief. Pick the smallest view that makes the key point clear.

**A picture means a drawing.** When the user asks for a picture, a diagram, a drawing, or "how X works" visually, draw boxes and arrows: a Mermaid `flowchart` or `sequenceDiagram`, or an HTML/SVG figure. A numbered list of steps, a bullet outline or a file tree is not a picture, even inside a code block. Keep it to 8 boxes or fewer, label every arrow with what moves along it, and add a key for any symbol or color.

- Show logic or an algorithm as pseudocode:

```text
on(save)
  if content is unchanged
    return cached result
  write new content
  return fresh result
```

- Show runtime control flow as a call tree:

```text
submitForm
  createSession
    persistPrompt
    launchAgent
  navigateToSession
```

- Show UI structure as a component tree, including state and module boundaries that matter:

```tsx
<SessionPage> (apps/example/src/routes/session.tsx)
  useSessionEvents()
  <SessionToolbar>
    <RunSkillButton> (packages/ui)
```

- Show file responsibility or a broad refactor as a shallow file tree:

```text
src/
├── commands/       # parses user actions
├── sessions/       # owns session state
└── transport/      # sends API requests
```

- Show component interaction, control flow, or data flow with Mermaid:

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Daemon
    User->>UI: choose command
    UI->>Daemon: send expanded prompt
    Daemon-->>UI: stream result
```

- Use `diff` when the point is what changes and the surrounding shape already exists. Match the diff shape to the topic.

For a component change:

```diff
 <SessionPage>
   useSessionEvents()
   <SessionToolbar>
+    <RunSkillButton />
   <SessionTimeline>
+    <SkillResultCard />
```

For a file-layout change:

```diff
 src/
 ├── commands/
+│   └── show-me.ts       # expands the slash command
 ├── sessions/
-└── transport.ts
+└── transport/
+    ├── client.ts
+    └── stream.ts
```

For a call-tree or call-stack change:

```diff
 submitForm
   createSession
     persistPrompt
+    expandSkillMention
     launchAgent
-  navigateToSession
+  navigateToSession
+    subscribeToEvents
```

For a state or control-flow change:

```diff
 on(save)
-  write content
+  if content is unchanged
+    return cached result
+  write new content
+  invalidate cache
```

- Show the whole block when most of it is new, when omitted context would hide ownership or order, or when the user needs a copyable target shape:

```ts
function expandSkill(command: string): string {
  const skillName = command.slice(1)
  return `use the ${skillName} skill`
}
```

- For a visual UI, layout, state comparison, or concept too dense for Mermaid, write one focused HTML file, a diagram, an infographic, or a short slide deck, whichever fits the point. Match the product's colors, type, spacing, and components; use real labels and data; support desktop and mobile. Then open it for the user:

```
Bash(open path/to/show-me-{description}.html)
```

- Place each visual next to the short text it supports. Keep only the calls, files, props, states, and boundaries needed to answer the user's current question.

You may use one of these, you may use several, it is unlikely you will use all of them. Use your judgement and don't overwhelm the user.

## Business topics

For a client's business (not code), pick the format by the shape of the idea: a rule with
numbers gets a calculator, a job someone does gets a game, how the parts fit gets a 3D
scene, one tricky idea gets an animated explainer (Manim or Remotion), a process gets a
Remotion video, the big picture on the go gets an audio overview. When a topic has three or
more connected parts, build a visual without being asked.

Start from a template in `templates/`. Each is one HTML file, light and dark, no build step.
Edit the data object at the top; use real names and numbers only.

Never ship the plain default look. Follow your design method and dress the page in the
style family that fits what it shows (`styles/README.md`): Control Room for a map or diagram,
Explorable for a calculator, Playground for a game, Editorial for an explainer or story. Copy the
family's tokens into the page, pull one fresh reference, and vary type, accent or layout so no
two pages look cloned. Blend in the client's product brand when the lesson is about their
product. Add motion and interaction by default and redraw the layout for the phone. The bar:
it would look at home next to Brilliant or Linear.

- `game.html`: the learner plays a person in the business. Intro screen, levels, score, a "why"
  card with the real rule after each mistake, and quips for a light tone.
- `calculator.html`: sliders and inputs, a live result, and one sentence that explains the rule
  with the current numbers.
- `scene-3d.html`: Three.js from a CDN. Labelled boxes, edges, and dots flowing along them in
  the direction things move. Drag to orbit; click a name to read what it does.

Save the result where the project keeps its learning material and open it in a browser to check
it renders before showing it.

## Look at it before you report

Every picture gets checked by eye before you say it is done. Never report a diagram you have
not seen rendered.

1. Render it to an image. For an HTML or SVG file, take a screenshot with a browser tool or
   headless Chrome (`chrome --headless --screenshot=out.png --window-size=1280,900 file.html`).
   For Mermaid, render it (`npx -y @mermaid-js/mermaid-cli -i in.mmd -o out.png`) or put it in
   a small HTML page and screenshot that.
2. Open the PNG and look at it. Check: it is boxes and arrows, not a list; every label is
   readable and inside its box; no arrow points at nothing; it fits a phone width; light and
   dark both read when the page has both.
3. Fix what is wrong and look again. Say in your reply that you checked the render, and show
   or link the screenshot.
