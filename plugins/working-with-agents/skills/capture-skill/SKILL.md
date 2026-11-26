---
name: capture-skill
description: Capture a reusable workflow as a skills.sh skill under ~/.agents/skills/ (symlinked into ~/.claude/skills/). Defaults to the current conversation's workflow; captures a different subject if named. Use when the user says "capture this", "capture-skill", "turn this into a skill", or "make a skill from what we did".
argument-hint: "optional: skill name and/or a different subject to capture"
---

# Capture Skill

> Local notes: if `~/.agents/skill-notes/capture-skill.md` exists, read it first. It holds this setup's private facts for this skill (names, brands, paths, house rules) and wins over the generic text here.

Turn a proven workflow into a reusable skill following the skills.sh standard
(vercel-labs/skills): a `SKILL.md` in `~/.agents/skills/<name>/`, exposed to
Claude Code via a symlink in `~/.claude/skills/`.

## What to capture

- **Default (blank argument):** distill the workflow from the *current
  conversation*, the generalizable procedure we just ran, not its one-off details.
- **Override:** if the argument names a skill name, a different subject, or a
  narrower scope, capture that instead.

If the conversation holds no reusable, repeatable procedure, say so and stop , 
don't manufacture a skill from a one-off.

## Steps

1. **Identify the procedure.** State in 1–2 sentences the repeatable workflow
   you're capturing and where it came from. Replace conversation-specific
   details (repo names, paths, branches, IDs) with placeholders unless the
   skill is meant to be project-specific.
2. **Confirm before writing:** proposed `name` (kebab-case), the trigger
   phrases, and anything to generalize or drop. Skip only if the user already
   gave an explicit name and scope.
3. **Write `~/.agents/skills/<name>/SKILL.md`** in the format below. Add
   supporting files (`examples/`, helper scripts, `reference.md`) only when
   detail would bloat SKILL.md, keep SKILL.md scannable.
4. **Symlink into Claude Code** (relative, matching existing skills):
   `ln -s ../../.agents/skills/<name> ~/.claude/skills/<name>`
5. **Do not touch the skill lock file** (if your setup has one): it tracks skills installed from a
   source repo, not authored ones.
6. **Report and offer to commit:** confirm files + symlink, note the skill
   activates on the next session start, and offer
   `git -C ~/.agents add skills/<name> && git -C ~/.agents commit`.

## SKILL.md format (skills.sh standard)

```markdown
---
name: <kebab-case, matches the folder name>
description: <what it does + WHEN to use it, with concrete trigger phrases the
  user would say. This is the only text preloaded, make it earn activation.>
argument-hint: "<optional, only if the skill takes arguments>"
---

# <Title>
<One-line overview.>

## When to use
<Triggers / situations. Omit if the description already covers it.>

## Steps
<Numbered procedure. Match specificity to fragility: prose for judgment calls,
exact commands for fragile operations.>

## Example
<Short concrete run-through.>

## Gotchas
<Non-obvious failure modes, if any.>
```

Quality bar: concise (only what Claude doesn't already know), trigger-rich
description, kebab-case `name` matching the folder, a generalized procedure
rather than a transcript.

## Verify (optional)
Offer to dispatch a subagent with a realistic trigger phrase to confirm the new
skill activates and its steps are followable; tighten wording if it misfires.
