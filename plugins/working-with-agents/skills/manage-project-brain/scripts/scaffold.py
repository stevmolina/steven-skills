#!/usr/bin/env python3
"""Scaffold a manage-project-brain/v1 brain. Dry-run by default; --apply mutates.

Creates missing structure only. It never overwrites or truncates an existing file.
The single exception to "writes new files only" is .gitignore: when one already
exists and does not cover sources/private/, the rule is appended to it, leaving
every existing rule in place. When no .gitignore exists, write sources/private/.
Usage: scaffold.py <brain-dir> [--apply] [--engagement NAME]
"""
import argparse
import fnmatch
import os
import sys

DIRS = ["wiki", "workspace", "sources", "sources/raw", "sources/private"]
FILES = [
    "README.md",
    "AGENTS.md",
    "wiki/index.md",
    "wiki/scope.md",
    "wiki/access.md",
    "wiki/stakeholders.md",
    "wiki/decisions.md",
    "wiki/glossary.md",
    "sources/README.md",
]
IGNORE_RULE = "sources/private/"

# Minimal stubs. The shape and caps live in references/standard.md, not a copied tree.
STUBS = {
    "README.md": """# {{ENGAGEMENT}} knowledge

Private brain for the {{ENGAGEMENT}} engagement. Schema: manage-project-brain/v1.

- `wiki/` is current truth. Start at `wiki/index.md`.
- `workspace/` is active unresolved reasoning. It can be wrong.
- `status/` is optional dated dailies and snapshots, not current truth.
- `sources/` is Markdown-first received evidence, immutable and append-only; original
  non-Markdown material is in `sources/raw/`.
- `sources/private/` is gitignored and never committed.

Maintenance contract: `AGENTS.md`.
""",
    "AGENTS.md": """# {{ENGAGEMENT}} brain, maintenance contract

Schema: manage-project-brain/v1, which `lint.py` enforces.
Only what lint cannot check is written here; the standard covers the rest.
`CLAUDE.md` symlinks to this file.

- Live systems outrank every document here.
- Never print or quote `sources/private/` contents or secrets.
- Product repos own technical truth. Name them by repo, never by path: TODO name them.
  Tasks live on TODO name the board.
- Filenames are lowercase kebab-case, `YYYY-MM-DD-` prefixed when the file is about a moment in time.
- Report "as of" a date. Verify a connector before claiming access.
- Plumbing this brain declares: TODO list it, or delete this line.

Lint before committing: `manage-project-brain/scripts/lint.py .`
""",
    "wiki/index.md": """# {{ENGAGEMENT}}: index

One-paragraph orientation: what the engagement is and where it stands. Keep it short;
detail lives in the five pages below.

- [Scope](scope.md): what we owe and what is out.
- [Access](access.md): accounts, systems, who grants what.
- [Stakeholders](stakeholders.md): people and roles.
- [Decisions](decisions.md): direction changes and corrections.
- [Glossary](glossary.md): engagement terms.

Sources of received evidence: `../sources/README.md`.
""",
    "wiki/scope.md": """# Scope

<!-- What is contracted, what is active, what is parked, what is out.
Every claim cites its source (SOW line, email, decision row). -->
""",
    "wiki/access.md": """# Access

<!-- Accounts, systems, credentials ownership. Every claim is volatile:
date each one (verified YYYY-MM-DD) and name who grants it.
Never store secret values here. -->
""",
    "wiki/stakeholders.md": """# Stakeholders

<!-- People, roles, what each owns or approves, contact identity. Cite sources. -->
""",
    "wiki/decisions.md": """# Decisions

| Date | Status | Decision or correction | Source |
|------|--------|------------------------|--------|
""",
    "wiki/glossary.md": """# Glossary

<!-- Engagement terminology only. Product internals belong in the product repo. -->
""",
    "sources/README.md": """# Sources manifest

Received evidence. Immutable, append-only, dated filenames (YYYY-MM-DD-<what>.<ext>).
This file records provenance only, never interpretation. Every file under `sources/`
(except `private/`) needs one row: filename, received date, origin, and the full
64-character SHA-256. Abbreviated hashes are not acceptable.
Keep original non-Markdown evidence in `raw/`, preserving meaningful subdirectories.

| File | Received | Origin (who/where) | SHA-256 |
|------|----------|--------------------|---------|

<!-- Shape of a row (hash is the full 64 hex characters of `shasum -a 256 <file>`):
| `raw/2026-08-15-sow.pdf` | 2026-08-15 | Email from Jane Doe, client | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
-->

`private/` is gitignored and never committed. Do not list secret values here; hashes
and provenance only. Remove credentials rather than preserving them.
""",
    ".gitignore": IGNORE_RULE + "\n",
}


def parse_gitignore(text):
    pats = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        neg = line.startswith("!")
        if neg:
            line = line[1:].strip()
        line = line.rstrip("/")
        if line:
            pats.append((neg, line))
    return pats


def _pattern_matches(pat, relpath):
    p = pat[1:] if pat.startswith("/") else pat
    segs = relpath.strip("/").split("/")
    if "/" in p:
        return any(fnmatch.fnmatch("/".join(segs[:i]), p)
                   for i in range(1, len(segs) + 1))
    return any(fnmatch.fnmatch(s, p) for s in segs)


def covers_private(text):
    ignored = False
    for neg, pat in parse_gitignore(text):
        if _pattern_matches(pat, "sources/private"):
            ignored = not neg
    return ignored


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("brain")
    ap.add_argument("--apply", action="store_true",
                    help="actually create files (default is dry-run)")
    ap.add_argument("--engagement", default=None,
                    help="engagement name substituted for {{ENGAGEMENT}}")
    args = ap.parse_args()

    brain = os.path.abspath(args.brain)
    name = args.engagement or os.path.basename(os.path.dirname(brain)) or "engagement"
    planned = []

    for d in DIRS:
        path = os.path.join(brain, d)
        if not os.path.isdir(path):
            planned.append(("mkdir", d))

    for f in FILES:
        path = os.path.join(brain, f)
        if not os.path.exists(path):
            planned.append(("write", f))

    claude = os.path.join(brain, "CLAUDE.md")
    if not os.path.lexists(claude):
        planned.append(("symlink", "CLAUDE.md -> AGENTS.md"))

    gitignore = os.path.join(brain, ".gitignore")
    if not os.path.exists(gitignore):
        planned.append(("write", ".gitignore"))
    elif not covers_private(open(gitignore, encoding="utf-8").read()):
        planned.append(("append", f".gitignore += {IGNORE_RULE}"))

    if not planned:
        print("Nothing missing. Brain structure is complete.")
        return 0

    mode = "APPLY" if args.apply else "DRY-RUN (pass --apply to create)"
    print(f"[{mode}] {brain}")
    for action, target in planned:
        print(f"  {action:8} {target}")

    if not args.apply:
        return 0

    for action, target in planned:
        if action == "mkdir":
            os.makedirs(os.path.join(brain, target), exist_ok=True)
        elif action == "write":
            dst = os.path.join(brain, target)
            os.makedirs(os.path.dirname(dst) or brain, exist_ok=True)
            body = STUBS[target].replace("{{ENGAGEMENT}}", name)
            # Refuse to overwrite even in a race.
            with open(dst, "x", encoding="utf-8") as fh:
                fh.write(body)
        elif action == "symlink":
            os.symlink("AGENTS.md", claude)
        elif action == "append":
            # Append-only: every existing ignore rule is preserved.
            with open(gitignore, encoding="utf-8") as fh:
                existing = fh.read()
            with open(gitignore, "a", encoding="utf-8") as fh:
                if existing and not existing.endswith("\n"):
                    fh.write("\n")
                fh.write(IGNORE_RULE + "\n")
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
