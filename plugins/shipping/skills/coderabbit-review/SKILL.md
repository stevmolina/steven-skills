---
name: coderabbit-review
description: "Run the CodeRabbit CLI on a diff and triage findings. Use when the user says coderabbit or coderabbit review."
argument-hint: "optional: scope, e.g. 'uncommitted', 'my commits', or a base branch"
---

# CodeRabbit Review

> Local notes: if `~/.agents/skill-notes/coderabbit-review.md` exists, read it first. It holds this setup's private facts for this skill (names, brands, paths, house rules) and wins over the generic text here.

Run the CodeRabbit CLI over a set of changes, then triage its findings -
CodeRabbit reasons from general principles and often flags false positives, so
every finding is verified against the actual code before any fix.

## Steps

1. **Check the CLI is available:** `coderabbit --version` (also aliased `cr`).
   If missing, stop and tell the user.

2. **Pick the review scope** from what the user asked for, then run
   `coderabbit review --plain [flags]`:
   - **Uncommitted / unstaged changes** → `--type uncommitted`
   - **Committed work (e.g. unpushed commits)** → `--type committed`
   - **All local changes** (committed + uncommitted, the default) → no `--type`
   - **A branch vs a base** → `--base <base>` (e.g. `--base main`); check out the
     branch first if it isn't the current one
   - **Against a specific commit on this branch** → `--base-commit <sha>`
   - **Limit to a subdirectory** → `--dir <path>`

   `--agent` emits structured findings if you need machine-readable output.
   A review can take several minutes.

3. **Triage every finding, don't trust it blindly.** For each, open the cited
   code and verify the claim against the real implementation, library/runtime
   behavior, and invariants. Classify as **real bug**, **false positive**, or
   **style/observability nit**, each with a one-line reason.

4. **Fix only the real ones,** minimal changes, then typecheck/lint.

5. **Re-run the same invocation** to confirm `No findings`.

6. **Commit/push only if asked** (branch first if on the default branch).

## Example
> "use coderabbit to check my unpushed commits"

Run `coderabbit review --plain --type committed` → 4 findings. Verify each: 1
real bug (stale UI state), 1 observability nit, 2 false positives (premise wrong
once checked against the library's singleton behavior). Fix the real one, re-run
→ `No findings`.

## Gotchas
- CodeRabbit's reasoning is often plausible but wrong for the specific code -
  the verification pass is the point, not a formality.
- `--type` defaults to `all` (committed + uncommitted); set it explicitly when
  you only want one slice.
- A clean re-run confirms the flagged items are resolved, not that the code is
  bug-free.
