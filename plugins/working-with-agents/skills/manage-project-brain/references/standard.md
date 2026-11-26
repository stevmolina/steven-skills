# manage-project-brain/v1, the normative standard

This file is the contract a brain must satisfy. `lint.py` enforces the mechanical parts.
Judgment calls (what counts as a decision, where a technical doc belongs) follow the
rules here.

## Layout

```
knowledge/
├── README.md
├── AGENTS.md
├── CLAUDE.md -> AGENTS.md      (relative symlink)
├── wiki/
│   ├── index.md
│   ├── scope.md
│   ├── access.md
│   ├── stakeholders.md
│   ├── decisions.md
│   └── glossary.md
├── workspace/
├── status/                     (optional; dated dailies and snapshots)
└── sources/
    ├── README.md
    ├── raw/                    (original non-Markdown received evidence)
    └── private/                (gitignored)
```

Operational plumbing (.gitignore, a safe .mcp.json with no inline secrets, bootstrap.sh,
tools/) may remain when required. It is not part of the knowledge model. The linter does
not read it as knowledge, but it does check it: .mcp.json must carry env placeholders
(`${VAR}` or `<placeholder>`) rather than inline secret literals, and .gitignore must
effectively ignore `sources/private/`.

Nothing else lives at the brain root. No second knowledge tree (`docs/`, `openspec/`,
`notes/`), no root-level topic files (ACCESS.md, SOW.md, a loose status file), no vendored
agent or skill trees (`.claude/`, `.agents/`, `skills-lock.json`). Each of those is a
linter error: the content belongs on a wiki page, in `status/`, in `sources/`, or in the
owning product repo. The only symlink in the model is `CLAUDE.md -> AGENTS.md`; any other
symlink is flagged.

## README.md

Maximum 15 lines. A human map: what this brain is, what lives where, where to start.
No project history, no current-status narrative.

## AGENTS.md

Maximum 50 lines, and 150 words is the working target. It must identify the schema as
`manage-project-brain/v1`. CLAUDE.md is a symlink to it.

Write only what `lint.py` cannot check. The six fixed pages, the 300-word cap, the
ledger statuses, the workspace metadata keys, the forbidden folders, and the manifest
shape are all enforced by the script, so restating them in prose adds length and a
second place to drift. What belongs here instead: the product repo and board names,
which files are quoted by line number rather than edited, house writing rules, the
plumbing this brain declares, and any local cap the script does not know. It must not
duplicate project facts that belong in wiki pages.

## wiki/

- Exactly the six fixed filenames. No additional pages, ever. Empty pages are fine.
- Maximum 300 words per page.
- `index.md` is the only normal entry point and carries a relative Markdown link to
  each of the other five pages, `[Scope](scope.md)` style. A bare filename mention is
  not a link.
- Every current claim needs a source or a stated verification basis.
- Volatile claims (access, account states, deployment facts) need a verification date
  in YYYY-MM-DD form. State claims "as of" that date. A page-level "as of" date covers
  the page; a page carrying volatile claims and no date at all is an error.

### wiki/decisions.md

A concise ledger, one row per decision:

```
| Date | Status | Decision or correction | Source |
```

Allowed statuses: `Active`, `Superseded`, `Corrected`. Preserve meaningful direction
changes (a superseded row stays, marked Superseded). Exclude daily events,
implementation trivia, and completed tasks.

Ledger rows are exempt from the 300-word page cap; only prose outside the table counts.
An append-only ledger cannot live under a fixed word budget (v1.0.1 correction, exposed
in early use). Bound the table by rows instead: past 40 rows,
the oldest Superseded and Corrected rows may roll off in a normal commit; git history
keeps them. Active rows never roll off.

## Client registers (v1.0.2, optional)

A client brain may add two more wiki pages, which a bot may read:

- `wiki/known-facts.md`: what the client already told us, one bullet per fact with
  `<!-- source: <where> | verified_at: YYYY-MM-DD -->`, so nobody asks again.
- `wiki/asks.md`: one table with the header
  `ID | Ask | Asked (date, channel, who) | Status | Proof | Waiting work | Last checked`.
  IDs (A-001...) never change. Status is open, partial or done.

Fact bullets and table rows are cap-exempt, like the decisions ledger; only prose counts.
Answered asks may move to `wiki/asks-done.md`, same header, same IDs.

## Decision modules (v1.0.2, optional)

When `decisions.md` passes 40 Active rows, it may split by topic into
`wiki/decisions-<topic>.md` ledgers (same columns, same statuses, rows kept word for
word). `decisions.md` then lists the modules, one line each.

## workspace/

Never created unprompted.
A workspace file exists because the user asked for one.
An audit, a review, or a finding goes in the reply, not into a new file.

Active unresolved reasoning only. Every file carries, near the top:

```
Status: <open question or state>
Updated: YYYY-MM-DD
Owner: <person>
Exit: <condition under which this file is removed>
```

Forbidden: archive folders, status-history folders, snapshot folders, completed
handoffs, and status or snapshot files anywhere under workspace (`status-*.md`,
`snapshot-*.md`, `<topic>-status-YYYY-MM-DD.md` and the like). Dated status
belongs in the optional root folder `status/`, not here. Remove a workspace file
once its durable conclusion reaches wiki, its technical detail reaches a product
repository, or it has no continuing value. Git history is the archive.

## status/

Optional. Dated Slack dailies and agent snapshots, append-only, one pair per day.
Not current truth: live systems, git, and wiki/ beat every file here. Omit the
folder on brains that do not keep a daily. Never put these under `workspace/`.

## sources/

Received evidence and faithful captures: contracts, emails, call notes, PDFs, exports,
client assets. Rules:

- Immutable. Preserve original bytes. Never edit a received file's body.
- Keep `sources/` Markdown-first. Original non-Markdown evidence, including PDFs,
  spreadsheets, email exports, captures, images, and client assets, belongs under
  `sources/raw/`, preserving any meaningful subdirectory. Markdown evidence and its
  authored folder README files may live outside `raw/`.
- Preserve source dates, provenance, and hashes.
- A newer source does not erase an older received source; use dated filenames
  (`YYYY-MM-DD-<what>.<ext>`), never an authored archive folder.
- `sources/README.md` is a short provenance manifest, not an interpretation document.
  One row per file: filename, received date (YYYY-MM-DD), origin, and the full
  64-character SHA-256. Abbreviated or elided hashes (`abc123…`, a 12-char prefix) do
  not verify anything and are errors. Every file under `sources/` except `private/`
  and the manifest itself needs a row, and the recorded hash must match the bytes.
- `sources/private/` is gitignored, and the ignore rule must actually cover it
  (`git check-ignore sources/private/` succeeds). Never print private contents or secrets into logs,
  wiki pages, or commits. Credentials are not evidence: remove them rather than
  preserving them. Retrieve reproducible evidence from its authoritative source when
  it is needed again.

## Technical-document ownership

The brain owns: scope, stakeholders, access ownership, business and architectural
direction changes, engagement terminology, client evidence, active commercial or
operational analysis.

Product repositories own: how code works, runtime behavior, deployment, database
schemas and migrations, product specifications, testing and evaluation, operator and
maintainer guides.

Removal protocol for a technical document found in a brain:

1. Identify the product repository that owns the behavior.
2. Inspect that repo's existing documentation and implementation.
3. Compare the brain copy with both.
4. Extract only unique, current, maintainable information.
5. Prefer updating an existing canonical document over creating a new one.
6. Validate technical claims against code, configuration, schema, or authorized live
   systems before writing them anywhere.
7. Commit and verify the product-repository update first.
8. Remove the brain copy only in a later knowledge-repository commit.
9. The brain may then point to the product repo by identity (repo name), never by a
   machine-specific filesystem path.

The same rule runs in reverse: when a product repo absorbs material that originated in
a brain, its provenance note cites the brain by repo name plus the preservation tag
(for example "from the acme knowledge repo, tag pre-knowledge-migration-2026-08-15"),
never a cross-repo relative path. Cross-repo relative paths die as soon as either repo
restructures.

Do not create a one-for-one replacement document for every removed brain file.

## Preservation before any migration

- Classify every dirty file (in-scope, unrelated, sensitive, unknown) before touching
  the repo. Never commit credentials, PII, or ignored private exports. No catch-all
  commits containing unrelated user work.
- Checkpoint commit of non-sensitive in-scope material, then a dated
  `pre-knowledge-migration-<date>` tag, verified restorable.
- A before-migration path+hash manifest stored outside the brain.
- Keep ignored private material outside Git. Remove credentials rather than preserving
  them, and retrieve reproducible evidence from its authoritative source when needed.
- Permanently delete nothing during initial migration except verified reproducible
  artifacts with explicit justification.
