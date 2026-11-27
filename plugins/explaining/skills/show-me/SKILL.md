---
name: show-me
description: Help the user understand the current topic visually with concise diagrams, code-shape sketches, and focused HTML artifacts.
---

> Local notes: if `~/.agents/skill-notes/show-me.md` exists, read it first. It holds this setup's private facts for this skill (names, brands, paths, house rules) and wins over the generic text here.

Help the user understand the current topic of conversation visually. Skip the preamble and keep prose brief. Pick the smallest view that makes the key point clear.

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

- For a visual UI, layout, state comparison, or concept too dense for Mermaid, write one focused HTML file, a diagram, an infographic, or a short slide deck, whichever fits the point. Use real labels and data; support desktop and mobile. Then open it for the user:

```
Bash(open path/to/show-me-{description}.html)
```

- **Design before you show.** Any HTML visual goes through the `design-apply` skill (design plugin) first: it picks a design system (the product's brand, else the library match for the page's purpose), you build with its tokens, and its automatic check must pass before the user sees the page. Lean on type, space and one accent; draw the idea, and do not put each step in its own bordered box or a code chip in every line. Without the design plugin, follow the same leanings and match the product's colors, type and spacing.

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

Never ship the plain default look. Dress the page with `design-apply`: for a map or diagram
it usually picks control-room, for a calculator explorable, for a game playground, for a
story editorial (these four used to live in this skill's `styles/` folder and are now
systems in the design library). Pull one fresh reference and vary type, accent or layout so
no two pages look cloned. Blend in the client's product brand when the lesson is about
their product. Add motion and interaction by default and redraw the layout for the phone.
Run the check before showing.

- `game.html`: the learner plays a person in the business. Intro screen, levels, score, a "why"
  card with the real rule after each mistake, and quips for a light tone.
- `calculator.html`: sliders and inputs, a live result, and one sentence that explains the rule
  with the current numbers.
- `scene-3d.html`: Three.js from a CDN. Labelled boxes, edges, and dots flowing along them in
  the direction things move. Drag to orbit; click a name to read what it does.

Save the result where the project keeps its learning material and open it in a browser to check
it renders before showing it.
