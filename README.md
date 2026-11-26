# steven-skills

Agent skills I use every day, packaged as Claude Code plugins. Each skill is a folder with
a `SKILL.md`, so they also work in any agent that reads skill folders (Codex, Cursor,
Gemini, Grok and others).

## Install in Claude Code

    claude plugin marketplace add stevmolina/steven-skills
    claude plugin install shipping@steven-skills

Plugin skills are namespaced, so `ship` runs as `/shipping:ship`.

| Plugin | Skills |
|---|---|
| `shipping` | `ship` (branch, review, proof, merge), `grill` (stress-test a plan), `coderabbit-review` (run CodeRabbit and triage) |
| `explaining` | `show-me` (visual explainers), `simpler` (plain rewrite), `raw` (bare, copy-ready draft) |
| `working-with-agents` | `handoff` (start a fresh thread with full context), `preflight` (test every login before a task), `capture-skill` (turn a workflow into a skill), `manage-project-brain` (a knowledge repo standard) |
| `video` | `product-demo-video` (Remotion demo and feature films, with a film kit) |

## Use without plugins

Copy or link a skill folder into your agent's skills folder, for example
`~/.claude/skills/<skill>` or `~/.agents/skills/<skill>`.

## Local notes

Some skills start by reading `~/.agents/skill-notes/<skill>.md` when it exists. That file
is yours: put names, brands, paths and house rules there, and keep it out of this repo.

## Credits

`show-me` is based on [humanlayer/skills](https://github.com/humanlayer/skills) (MIT); see
its `NOTICE.md`. Skills I use but did not write are installed from their own repos, not
copied here.

## Privacy check

`scripts/check-private.py` blocks client names, IP addresses, emails, key-shaped strings,
home paths and private references. It runs in CI and in the pre-push hook
(`git config core.hooksPath .githooks`).

MIT license.
