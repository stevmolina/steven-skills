---
name: grill
description: Stress-test a plan before any code is written, a few questions per round with a recommended answer each, then emit a paste-ready implement prompt. Use whenever the user wants a plan, design or decision challenged before building, in plain words or as a command, for example "grill this plan", "grill me", "stress-test this", "poke holes in this", "what am I missing", "challenge this before we build", /grill or /grill-me.
argument-hint: "[quick] what to grill"
---

> Local notes: if `~/.agents/skill-notes/grill.md` exists, read it first. It holds this setup's private facts for this skill (names, brands, paths, house rules) and wins over the generic text here.

This chat does not write product code. Look facts up, then decide with the user. When the tree is empty, follow the `handoff` skill: it writes the implement brief and starts the new thread.

## Lookup

Read the ticket, repo, and existing code first. If a ticket URL is in the prompt, fetch that ticket. Do not ask the user anything you can open. One short line of what you opened, then the first round.

## Rounds

Map a design tree. Ask only the frontier (questions whose prerequisites are already settled). Cap a round at **3** questions. `/grill quick` means **3 questions in the whole session**.

Header each round with how many are left, for example `2 of ~5 left`.

Each question, in plain words:

```
**Q1. <one-line question>**
A) ...
B) ...
C) ...
Recommend: B. <one why>
```

Separate questions with a horizontal rule.

They answer `1a 2b 3a`, or `yes` to take every recommendation. Do not ask a question the ticket already settled, or one whose answer is implicit in current code.

If a question would need `/simpler`, rewrite it before sending. No jargon they did not use. No LOCKED labels. A recap is `DECISIONS:` plus dated bullets.

Do not write files unless the user asks to save a design decision.

## Done

When the user says proceed, prompt, enough, or the frontier is empty and they confirm: read `handoff` and follow it: it writes the implement brief and starts the new thread. Tell the next agent not to continue this grilling chat.

If the user wants to continue grilling in a new session, hand off that instead: the brief is for another `/grill`, not for implementation.
