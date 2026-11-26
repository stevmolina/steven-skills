---
name: handoff
description: Hand the current work to a fresh thread with its full context, and start that thread. Use when the user says handoff, /handoff, seed, "do this in another session", "in a new thread", "give me a prompt for another session", "send an agent to do this", or after a grill or plan is settled and building should start elsewhere.
argument-hint: "What the new thread is for"
---

# Handoff

> Local notes: if `~/.agents/skill-notes/handoff.md` exists, read it first. It holds this setup's private facts for this skill (names, brands, paths, house rules) and wins over the generic text here.

The user should never have to copy and paste a prompt between chats. Write the brief, then start the
thread yourself.

## 1. Write the brief

The brief is the new thread's first message. It must let a fresh agent finish the work
without this chat.

- The goal, and what the new thread is for (the argument, when given).
- What is decided, and what was ruled out, with the one reason each.
- Where things are: repo and branch, files, PRs, tickets, brain pages. Point to them by
  path or URL; do not copy their content.
- The finish line: merged by itself for low-risk work, or a PR with proof for review when a mistake would be hard to undo or hurt someone else.
- A Suggested skills line naming the skills the next agent should run (`ship`,
  `preflight`...).
- Redact secrets, keys, passwords and personal data.
- Ignore chat length budgets here: a complete brief beats a short one.

## 2. Start the thread

- **In T3:** load `t3_thread_launch` with ToolSearch and launch the thread with the brief
  as its prompt. Code work gets a worktree strategy on the repo; research or talk stays in
  the project root. Reply with the thread's `link`, one line on what it will do, nothing
  else.
- **Elsewhere, or when the user asks for the text:** the entire reply is the brief. No
  greeting, no wrapper fence, no "paste this", no closing line.

## 3. After a grill

When the decision tree is settled, the brief is the implement prompt, and the new thread
must not continue the grilling. If the user wants to keep grilling in a new session, the
brief is for another `/grill`.
