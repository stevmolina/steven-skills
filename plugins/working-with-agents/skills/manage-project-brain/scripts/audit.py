#!/usr/bin/env python3
"""Inventory and classify an existing brain. Always read-only.

Walks the brain, classifies every file against the manage-project-brain/v1 model,
hashes contents (path, sha256, size), inventories file symlinks, directory symlinks
and empty directories, and reports git state when available.
Private/ignored files are counted, hashed, and sized; contents are never printed.

Output separates the informational inventory from compliance failures. In --json
form those are the top-level keys `inventory` and `failures`.
Usage: audit.py <brain-dir> [--json]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

WIKI_PAGES = {"index.md", "scope.md", "access.md", "stakeholders.md",
              "decisions.md", "glossary.md"}
PLUMBING_FILES = {".gitignore", ".gitattributes", ".mcp.json", "bootstrap.sh",
                  "doppler.yaml"}
PLUMBING_DIRS = {"tools"}
VENDORED_AGENT_DIRS = {".claude", ".agents", ".cursor", ".codex", ".github"}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}


def sha256(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 16), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return "unreadable"


def classify(rel, agents_text=""):
    parts = rel.split(os.sep)
    top = parts[0]
    if rel in ("README.md", "AGENTS.md", "CLAUDE.md"):
        return "model:root"
    if top == "wiki":
        if len(parts) == 2 and parts[1] in WIKI_PAGES:
            return "model:wiki"
        return "violation:unexpected-wiki-page"
    if top == "status":
        return "model:status"
    if top == "workspace":
        low = rel.lower()
        if any(seg in ("archive", "archives", "snapshots", "status") for seg in
               (p.lower() for p in parts[1:-1])) or "handoff" in low:
            return "violation:workspace-archive-or-handoff"
        return "model:workspace"
    if top == "sources":
        if len(parts) > 1 and parts[1] == "private":
            return "model:sources-private"
        return "model:sources"
    if top in VENDORED_AGENT_DIRS:
        if top + "/" in agents_text:
            return "plumbing:declared-agent-tree"
        return "violation:vendored-agent-tree"
    if (len(parts) == 1 and top in PLUMBING_FILES) or top in PLUMBING_DIRS:
        return "plumbing"
    if len(parts) == 1:
        return "violation:unclassified-root-file"
    return "violation:extra-knowledge-tree"


def git(brain, *args):
    try:
        out = subprocess.run(["git", "-C", brain, *args], capture_output=True,
                             text=True, timeout=30)
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


def walk(brain):
    files, file_links, dir_links, empty_dirs = [], [], [], []
    try:
        with open(os.path.join(brain, "AGENTS.md"), encoding="utf-8") as fh:
            agents_text = fh.read()
    except OSError:
        agents_text = ""
    for root, dirs, names in os.walk(brain):
        for d in list(dirs):
            full = os.path.join(root, d)
            if os.path.islink(full):
                dir_links.append({"path": os.path.relpath(full, brain),
                                  "target": os.readlink(full)})
                dirs.remove(d)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        if not dirs and not names and os.path.abspath(root) != brain:
            empty_dirs.append(os.path.relpath(root, brain))
        for f in names:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, brain)
            is_link = os.path.islink(full)
            cls = classify(rel, agents_text)
            if is_link:
                file_links.append({"path": rel, "target": os.readlink(full),
                                   "dangling": not os.path.exists(full)})
            files.append({
                "path": rel,
                "class": cls,
                "symlink": os.readlink(full) if is_link else None,
                "size": 0 if is_link else (os.path.getsize(full)
                                           if os.path.exists(full) else 0),
                "sha256": None if is_link else sha256(full),
                "private": cls == "model:sources-private",
            })
    files.sort(key=lambda e: e["path"])
    return files, file_links, dir_links, sorted(empty_dirs)


def compliance_failures(files, file_links, dir_links):
    out = []
    for e in files:
        if e["class"].startswith("violation:"):
            out.append({"category": e["class"].split(":", 1)[1],
                        "path": e["path"],
                        "detail": "outside the manage-project-brain/v1 layout"})
    for link in file_links:
        if link["path"] == "CLAUDE.md" and link["target"] == "AGENTS.md":
            continue
        out.append({"category": "unexpected-symlink", "path": link["path"],
                    "detail": f"file symlink -> {link['target']}"
                              + (" (dangling)" if link["dangling"] else "")})
    for link in dir_links:
        out.append({"category": "unexpected-symlink", "path": link["path"],
                    "detail": f"directory symlink -> {link['target']}"})
    out.sort(key=lambda f: (f["category"], f["path"]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("brain")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    brain = os.path.abspath(args.brain)
    if not os.path.isdir(brain):
        print(f"error: not a directory: {brain}", file=sys.stderr)
        return 2

    entries, file_links, dir_links, empty_dirs = walk(brain)
    gitinfo = {
        "head": git(brain, "rev-parse", "HEAD"),
        "branch": git(brain, "branch", "--show-current"),
        "dirty": git(brain, "status", "--porcelain"),
        "ignored": git(brain, "ls-files", "--others", "--ignored",
                       "--exclude-standard"),
    }
    counts = {}
    for e in entries:
        counts[e["class"]] = counts.get(e["class"], 0) + 1
    inventory = {
        "git": gitinfo,
        "counts": counts,
        "files": entries,
        "file_symlinks": file_links,
        "dir_symlinks": dir_links,
        "empty_dirs": empty_dirs,
    }
    failures = compliance_failures(entries, file_links, dir_links)

    if args.json:
        print(json.dumps({"brain": brain, "inventory": inventory,
                          "failures": failures}, indent=2))
        return 0

    print("== INVENTORY (informational) ==")
    print(f"brain: {brain}")
    print(f"git: branch={gitinfo['branch']} head={gitinfo['head']}")
    if gitinfo["dirty"]:
        print(f"dirty files:\n{gitinfo['dirty']}")
    print("\nclassification counts:")
    for k in sorted(counts):
        print(f"  {counts[k]:4}  {k}")
    print("\nfile symlinks:")
    for link in file_links or []:
        flag = " DANGLING" if link["dangling"] else ""
        print(f"  {link['path']} -> {link['target']}{flag}")
    if not file_links:
        print("  (none)")
    print("\ndirectory symlinks:")
    for link in dir_links:
        print(f"  {link['path']} -> {link['target']}")
    if not dir_links:
        print("  (none)")
    print("\nempty directories:")
    for d in empty_dirs:
        print(f"  {d}")
    if not empty_dirs:
        print("  (none)")
    print("\nmanifest (path  sha256  size):")
    for e in entries:
        if e["symlink"] is not None:
            print(f"  {e['path']}  -> {e['symlink']}")
        else:
            print(f"  {e['path']}  {e['sha256']}  {e['size']}")

    print("\n== COMPLIANCE FAILURES ==")
    for f in failures:
        print(f"  {f['category']}: {f['path']}  ({f['detail']})")
    if not failures:
        print("  (none)")
    print(f"\n{len(failures)} compliance failure(s), {len(entries)} file(s) "
          f"inventoried")
    return 0


if __name__ == "__main__":
    sys.exit(main())
