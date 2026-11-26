---
name: preflight
description: Before a task starts, list every login, key, tool and access it needs, test each one, ask the user for all the missing logins at once, then run to the end without stopping. Use at the start of any task that touches outside accounts (GitHub, Google, Slack, a ticket board, a secrets vault, a VPS, a client app, a browser login), when the user says preflight, "do you have everything you need", "can you do it yourself", or before handing work to a worker or a new thread.
---

# Preflight

> Local notes: if `~/.agents/skill-notes/preflight.md` exists, read it first. It holds this setup's private facts for this skill (names, brands, paths, house rules) and wins over the generic text here.

A packing checklist before the trip. The goal: the user is asked once, at the start, and
never again halfway through.

## 1. List what the task needs

Read the task and write a short checklist, one row per need:

| Need | Why | How to test |
|---|---|---|
| GitHub push to `org/repo` | open the PR | `gh auth status`, `git ls-remote` |
| Secret `X` | call the API | `<vault CLI> get X >/dev/null` (never print it) |
| Ticket board | move the ticket | one list call |
| Browser login to app Y | click through the flow | open it with `browse` or T3 preview |
| SSH to a VPS | deploy | `ssh -o BatchMode=yes host true` |

Include the tools too: CLIs on PATH, MCP servers loaded (ToolSearch), disk space for a
build, the dev server port free.

## 2. Test every row yourself

- Run each test. Do not ask the user whether something works: check it.
- Look before saying "no access": the secrets vault, the repo's env, the project's notes, a tool
  gateway, a logged-in browser for pages behind the user's login, a
  full-machine tool. Most "missing" access is already there.
- Install a missing CLI yourself.

## 3. Ask once, for everything missing

One message, a numbered list. For each item: what it is for, and the single link or
command they run. Use a secure secret-request tool where one exists; never ask them to paste a key in
chat. Then keep doing every part of the task that does not need it.

## 4. Re-test and run to the end

When they say done, re-test only the failed rows, then finish the whole task without
check-ins. A login that expires mid-run is the one acceptable second ask.

## Report

At the end, one line: `Preflight: N checks, M asked` so the next run knows what to
expect.
