---
name: ship
description: >-
  Build and ship a change: branch, implement, review, push, PR, merge.
  Scales to the work. Simple goes straight through. Complex uses a strong
  parent as orchestrator and cheaper subagents to implement, then local
  auditors plus Greptile or CodeRabbit when those CLIs exist. Use on
  "ship this", "ship it", "/ship", "merge it", "push and merge", "merge and
  deploy", "merge and rebuild", "commit, push", "PR and merge", and
  whenever a code change is approved and needs to reach main. A bare "merge"
  or "push" on finished work means ship, not a raw git command.
---

# Ship

> Local notes: if `~/.agents/skill-notes/ship.md` exists, read it first. It holds this setup's private facts for this skill (names, brands, paths, house rules) and wins over the generic text here.

Runs to the end without check-ins: the go that started the task covers push, PR,
review, merge and deploy. Never commit to the default branch.
Merging does not always deploy. Read the repo's AGENTS.md or CLAUDE.md for
how it deploys; some repos auto-deploy on merge, others need a deploy step.

Risk decides the finish line, judged by real harm rather than topic: most changes are low risk, and the go that started the task covers them end to end.
Sensitive work stops at a PR for a human to approve:
- **Low risk** (UI, copy, docs, styling, small fixes, tests, tooling): merge and
  deploy yourself.
- **Sensitive** (auth, payments, migrations, production data, secrets, infra,
  deletes, hard to undo): stop at step 8 with a PR that carries proof, and hand
  it to the reviewer.

## 0. Preflight and size

Run the `preflight` skill first when the task needs anything outside this repo
(a login, a secret, a deploy host). Ask for every missing login once, now.

Then size the work.

Pick **simple** or **complex** before spawning anyone. Say which, in one line.

**Simple** (default when unsure is still simple): one module, no new interface,
docs, copy, a typo, an obvious bugfix, a config flag. Parent does the work.
No implementation subagents. No local auditor panel. No Greptile loop.

**Complex**: new subsystem, auth, migrations, cross-service contracts, unclear
shape, or a change you would not merge without a second pair of eyes.

User override: `/ship quick` forces simple. `/ship full` forces complex.

## 1. Implement (before git)

### Simple
Edit in this session. Stop when the change works. Go to step 2.

### Complex
Parent is orchestrator and planner. Stay on the strong model in this chat.
Do not implement the bulk yourself.

1. Write a short plan: files, done-when, what not to touch.
2. Spawn implementation subagents on a **medium or small** model (sonnet, grok,
   or the host's mid tier). Pass `model` on every spawn. Mechanical edits,
   search, and fill-in go there. One writer in a shared tree. Worktrees only
   when two agents will write the same repo at the same time (each
   writer in its own worktree).
3. Parent reviews the diff against the plan, then continues.

## 2. Branch
- On `main`/default: `git checkout -b <type>/<short-slug>`
  (type = feat/fix/refactor/chore).
- Else reuse the current feature branch.

## 3. Commit
- Stage the change, review `git diff --staged`.
- Write a conventional-commit message from the change. No co-author trailer.

## 4. Review locally  (simple: skip)

Run what exists. Skip a tool that is not installed. Do not invent a fallback
loop. Verify every finding against the real code. Fix real bugs. Note false
positives. Keep going; findings go in the PR body and the final report.

1. **Local auditor.** Spawn one readonly subagent on a **strong** model,
   different from whoever wrote the code when the host allows it. Brief: the
   diff, the intent, "what would break in production". It does not edit.
2. **Greptile**, if `greptile` is on PATH. Invoke **greploop** (iterate to
   5/5, nothing pushed). If greploop is the wrong shape for this diff, one
   `greptile` review is enough.
3. **CodeRabbit**, if `coderabbit` or `cr` is on PATH. Invoke
   **coderabbit-review**.

Simple mode skips this whole step. `/ship quick` does too.

## 4b. Proof
- Anything with a UI: open it (T3 preview or the `browse` skill), click through
  the change, take screenshots. Record a short video with
  `preview_recording_start` / `_stop` when the change is about a flow.
- Anything else: the test output, or the command and its result.
- Proof goes in the PR body. A sensitive PR without proof is not ready.

## 5. Push
- `git push -u origin <branch>`.

## 6. Open PR
- `gh pr create` with what changed and why. Use the repo template if one
  exists.

## 7. Handle bot reviews  (simple: skip)
- Do not wait for CodeRabbit, Gemini, or Greptile. If their comments are
  already there when you look, verify them, fix the valid ones and reply with a
  one-line resolution. Skip false positives. Comments that come after the merge
  go in a follow-up PR.

## 8. Merge or hand off
- Low risk: turn on auto-merge right after the push,
  `gh pr merge <pr> --auto --squash` (or `--merge` when the repo says so).
  GitHub merges when the required checks pass. When the repo has no required
  checks, the same command merges at once.
- Never wait for CI in a foreground loop (`sleep`, `until`, repeated
  `gh pr checks`). Start ONE background watch and keep working or end the turn:
  `gh pr checks <pr> --watch --fail-fast --interval 30` as a background command,
  or `watch_pull_request` in T3. Its end wakes you.
- A required check fails: read the log (`gh run view <id> --log-failed`), fix,
  push. A flake gets one `gh run rerun <id> --failed`. A failure in files the PR
  does not touch comes from main: fix main in its own PR. Never stop to ask
  "merge anyway?".
- Sensitive: do not merge. Report the PR link, what it changes in plain words,
  the proof, and what the auditors found. The reviewer approves and merges.
- Fix what you can first: a conflict, a red check, a bot finding. Stop only
  when a reviewer requested changes you cannot resolve or a finding needs
  the reviewer's judgment, and say exactly which.

## 9. Deploy
- If the repo says merging does not deploy on its own, run its deploy step
  now, in the same task, without asking again.
- Done means live: confirm the deployed version matches the merge commit and
  say how you checked. A merge alone is not a ship.
- When an automatic job deploys or rebuilds after the merge, start it (or let
  it start), report, and check its status once at the end. Do not hold the turn
  in a status loop.

## 9b. After merge
- Read the `## After merge` section of the repo's AGENTS.md or CLAUDE.md and run
  every step in it: rebuild, reinstall a desktop app, restart a service, open
  the app. No such section: open what changed (preview, the deployed URL, or
  the command) and look at it.
- Attach at least one screenshot of the merged result for any UI change,
  inline in the chat, not as a path. Never a mockup or invented UI.

## 10. Report
End with three short parts, for someone who did not watch the work:
1. **What changed for you**: one or two plain sentences.
2. **How it works**: three steps, big idea first, each new term defined.
3. **What to check**: the link, the screenshot or the video, and how it was
   verified.
Then a proof section: what it does, how it is set up, how it works inside (three to six steps), a super simple diagram, real screenshots and a short screen recording taken from the running change on the branch. If something could not be shown, say which item is missing and why.
