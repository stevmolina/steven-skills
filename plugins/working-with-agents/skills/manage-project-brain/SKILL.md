---
name: manage-project-brain
description: Create, audit, lint, and migrate a project knowledge repository ("brain") to the manage-project-brain/v1 standard. Use when the user wants to scaffold a new engagement brain, check an existing knowledge repo against the standard, migrate a knowledge repo to the six-page wiki model, or asks whether a document belongs in the brain or in a product repository.
---

# Manage Project Brain

> Local notes: if `~/.agents/skill-notes/manage-project-brain.md` exists, read it first. It holds this setup's private facts for this skill (names, brands, paths, house rules) and wins over the generic text here.

A brain is a private per-engagement knowledge repository. This skill holds the
manage-project-brain/v1 standard and three scripts to scaffold, audit, and lint a
brain. The full normative spec is `references/standard.md`; read it before migrating
an existing repo. That file is the shape. `scaffold.py` writes empty stubs from it.

## The v1 model, in brief

```
knowledge/
├── README.md            (max 15 lines, human map only)
├── AGENTS.md            (max 50 lines, ~150 words: only what lint.py cannot check)
├── CLAUDE.md -> AGENTS.md
├── wiki/                (exactly six pages, max 300 words each;
│                         decisions.md ledger rows are cap-exempt)
│   ├── index.md  scope.md  access.md  stakeholders.md  decisions.md  glossary.md
├── workspace/           (active unresolved reasoning only)
├── status/              (optional; dated dailies and snapshots)
└── sources/             (immutable received evidence)
    ├── README.md        (provenance manifest: file, date, origin,
    │                     full 64-hex SHA-256, one row per file)
    ├── raw/             (original non-Markdown files: PDFs, exports, assets)
    └── private/         (gitignored, and the rule must actually cover it)
```

Repository plumbing (.gitignore, safe .mcp.json, bootstrap.sh, tools/) may remain when
operationally required; it is not part of the model. Nothing else belongs at the root:
a second knowledge tree (docs/, openspec/), root-level topic files (ACCESS.md, SOW.md,
status files), and vendored .claude/ or .agents/ skill trees are all lint errors.

## Ownership rule

The brain owns scope, stakeholders, access ownership, direction changes, terminology,
client evidence, and active commercial or operational analysis. Product repositories own
how code works, runtime behavior, deployment, schemas and migrations, specs, testing,
and operator guides. Never remove a brain document until its unique current facts have a
verified canonical home. Details and the removal protocol: `references/standard.md`.

## Scripts

All three default to read-only. Only `scaffold.py --apply` mutates. It never overwrites
or truncates an existing file; its one edit to an existing file is appending
`sources/private/` to a .gitignore that does not already cover it. When there is no
.gitignore it writes `sources/private/`.

```
python3 scripts/scaffold.py <brain-dir> [--apply]     # create missing structure
python3 scripts/audit.py <brain-dir> [--json]         # inventory and classify
python3 scripts/lint.py <brain-dir> [--stale-days N]  # validate against v1
python3 run-tests.py                                  # the script test suite
```

`audit.py` separates an informational inventory (files, hashes, file and directory
symlinks, empty directories, git state) from compliance failures; `--json` puts them
under the top-level keys `inventory` and `failures`.

`lint.py` exits nonzero on errors: wrong wiki filenames, caps exceeded, broken links,
an index.md that does not link the other five pages, missing citations or freshness
dates, invalid decision statuses, workspace files without status/updated/owner/exit-condition
metadata or stale beyond the threshold, any archive, status-history, or snapshot folder
or status/snapshot file under workspace, extra knowledge trees and unclassified files
outside the standard layout, unexpected symlinks, a manifest that omits a source file or
records an abbreviated or wrong SHA-256, a `sources/private/` that is not effectively
gitignored, and inline secret literals in .mcp.json.

Tests live in `scripts/tests/` and run with `python3 run-tests.py` or
`python3 -m unittest discover -s scripts/tests`. They are stdlib-only and offline.

## Migrating an existing brain

1. Audit read-only (`audit.py`), classify every file, hash everything.
2. Preserve tracked work with a checkpoint commit, tag, and manifest outside the repo.
   Keep private files outside Git; remove credentials rather than preserving them.
3. Move unique technical facts to the owning product repo and commit there first.
4. Compile the six wiki pages with sources and dates.
5. Remove superseded authored files in a later brain commit; keep received sources.
6. `lint.py` must pass; an independent reviewer compares pre/post manifests.
