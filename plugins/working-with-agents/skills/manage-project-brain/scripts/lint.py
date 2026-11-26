#!/usr/bin/env python3
"""Validate a brain against manage-project-brain/v1. Always read-only.

Exit 0 when clean, 1 on any error. Warnings do not affect the exit code.
Deterministic and offline: the only subprocess is a local `git check-ignore`.
Usage: lint.py <brain-dir> [--stale-days N]
"""
import argparse
import datetime
import fnmatch
import hashlib
import json
import math
import os
import re
import subprocess
import sys

WIKI_PAGES = ["index.md", "scope.md", "access.md", "stakeholders.md",
              "decisions.md", "glossary.md"]
# v1.0.2: optional client registers (a bot may read these pages). Their rows are
# cap-exempt like the decisions ledger; only prose counts.
OPTIONAL_PAGES = ["known-facts.md", "asks.md", "asks-done.md"]
# A ledger past 40 Active rows may split by topic into decisions-<topic>.md pages;
# decisions.md then lists the modules. Each module is a ledger like decisions.md.
DECISION_MODULE_RE = re.compile(r"decisions-[a-z0-9-]+\.md")
ASKS_HEADER = ["ID", "Ask", "Asked (date, channel, who)", "Status", "Proof",
               "Waiting work", "Last checked"]
ASK_STATUSES = {"open", "partial", "done"}
VALID_STATUSES = {"Active", "Superseded", "Corrected"}
DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#]+)(?:#[^)]*)?\)")
META_KEYS = ("status", "updated", "owner", "exit")
FORBIDDEN_DIRS = {"archive", "archives", "snapshot", "snapshots", "status",
                  "status-history", "handoffs"}

# The standard layout plus the operational plumbing the standard tolerates.
ALLOWED_ROOT_DIRS = {"wiki", "workspace", "sources", "status", "tools", ".git"}
ALLOWED_ROOT_FILES = {"README.md", "AGENTS.md", "CLAUDE.md", ".gitignore",
                      ".gitattributes", ".mcp.json", "bootstrap.sh",
                      "doppler.yaml", ".DS_Store"}

# Status/snapshot reporting is forbidden under workspace/.
STATUS_STEM_RE = re.compile(r"(^|[-_.])(status|snapshot|standup|digest)([-_.]|$)")

VOLATILE_WORDS = ("access", "deployed", "deployment", "credential", "credentials",
                  "account", "login", "granted", "provisioned", "revoked",
                  "invited", "api key", "seat", "admin rights")

HEX64_RE = re.compile(r"\b[0-9a-fA-F]{64}\b")
HEXISH_RE = re.compile(r"\b[0-9a-fA-F]{6,}\b")
ELLIPSIS_RE = re.compile(r"(…|\.\.\.)")

SECRET_SHAPES = [
    ("openai/anthropic-style key", re.compile(r"sk-[A-Za-z0-9_\-]{16,}")),
    ("github token", re.compile(r"gh[pousr]_[A-Za-z0-9]{16,}")),
    ("slack token", re.compile(r"xox[abposr]-[A-Za-z0-9-]{10,}")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}")),
    ("aws access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("doppler token", re.compile(r"dp\.[a-z]{2}\.[A-Za-z0-9]{20,}|dop_v1_[A-Za-z0-9]{20,}")),
]
SECRET_KEY_RE = re.compile(
    r"(?i)(^|[_\-.])(key|token|secret|password|passwd|pat|credential|credentials|"
    r"apikey|api_key|access_key|private_key)s?$")
PLACEHOLDER_RE = re.compile(r"^\s*(\$\{[^}]+\}|\$[A-Za-z_][A-Za-z0-9_]*|<[^>]+>|"
                            r"\{\{[^}]+\}\}|)\s*$")

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError as e:
        err(f"{path}: unreadable ({e})")
        return ""


def word_count(text):
    return len(text.split())


def strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def body_is_empty(text):
    """A page holding only a heading, an empty table header, or comments counts as empty."""
    stripped = strip_comments(text)
    lines = [l for l in stripped.splitlines() if l.strip()]
    content = [l for l in lines
               if not l.lstrip().startswith("#")
               and not re.fullmatch(r"\|[\s|:-]*\|?", l.strip())
               and not (l.strip().startswith("|") and
                        set(re.sub(r"[^A-Za-z]", "", l)) and
                        re.fullmatch(r"\|(?:[^|]*\|)+", l.strip()) and
                        all(c.strip() and not any(ch.isdigit() for ch in c)
                            for c in l.strip().strip("|").split("|"))
                        and "Date" in l)]
    return not content


def sha256_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 16), b""):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


# ---------------------------------------------------------------- gitignore

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
        if not line:
            continue
        pats.append((neg, line))
    return pats


def _pattern_matches(pat, relpath):
    p = pat[1:] if pat.startswith("/") else pat
    anchored = "/" in p
    segs = relpath.strip("/").split("/")
    if anchored:
        for i in range(1, len(segs) + 1):
            if fnmatch.fnmatch("/".join(segs[:i]), p):
                return True
        return False
    return any(fnmatch.fnmatch(s, p) for s in segs)


def textual_ignored(patterns, relpath):
    ignored = False
    for neg, pat in patterns:
        if _pattern_matches(pat, relpath):
            ignored = not neg
    return ignored


def git_check_ignore(brain, relpath):
    """True/False from git, or None when git cannot answer authoritatively."""
    if not os.path.isdir(os.path.join(brain, ".git")):
        return None
    try:
        r = subprocess.run(["git", "-C", brain, "check-ignore", "-q", relpath],
                           capture_output=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode in (0, 1):
        return r.returncode == 0
    return None


def private_is_ignored(brain):
    """(ignored, how) for sources/private/."""
    via_git = git_check_ignore(brain, "sources/private/")
    if via_git is not None:
        return via_git, "git check-ignore"
    gi = os.path.join(brain, ".gitignore")
    if not os.path.exists(gi):
        return False, "no .gitignore"
    return textual_ignored(parse_gitignore(read(gi)), "sources/private"), ".gitignore"


def claims_private_storage(brain):
    claim = re.compile(r"(?i)(private.{0,80}(gitignor|never committed|not committed|"
                       r"kept out of git|ignored)|(gitignor\w*|ignored).{0,80}private)")
    for rel in ("README.md", "AGENTS.md", os.path.join("sources", "README.md")):
        path = os.path.join(brain, rel)
        if os.path.exists(path) and claim.search(read(path)):
            return rel
    return None


# ---------------------------------------------------------------- layout

def check_layout(brain):
    """Extra knowledge trees and unclassified technical files at the brain root."""
    try:
        entries = sorted(os.listdir(brain))
    except OSError as e:
        err(f"layout: cannot list {brain} ({e})")
        return
    # Plumbing declared by name in AGENTS.md (the maintenance contract) is
    # allowed to exist; undeclared vendored trees are errors.
    try:
        agents_text = open(os.path.join(brain, "AGENTS.md"), encoding="utf-8").read()
    except OSError:
        agents_text = ""
    for name in entries:
        full = os.path.join(brain, name)
        if os.path.isdir(full) and not os.path.islink(full):
            if name in ALLOWED_ROOT_DIRS:
                continue
            if name in (".claude", ".agents", ".cursor", ".codex", ".github"):
                if name + "/" in agents_text or name + "\\" in agents_text:
                    warn(f"layout: {name}/: vendored agent/skill tree present; "
                         f"allowed because AGENTS.md declares it as plumbing")
                else:
                    err(f"layout: {name}/: vendored agent/skill tree is not part of "
                        f"manage-project-brain/v1 and AGENTS.md does not declare it "
                        f"as plumbing (review the path and remove or relocate it)")
            else:
                err(f"layout: {name}/: extra knowledge tree outside the standard "
                    f"layout (wiki/, workspace/, sources/, status/ only); move its "
                    f"content to a wiki page, status/, or the owning product repo")
        else:
            if name in ALLOWED_ROOT_FILES:
                continue
            err(f"layout: {name}: unclassified file at the brain root (allowed: "
                f"README.md, AGENTS.md, CLAUDE.md, plus plumbing .gitignore, "
                f".mcp.json, bootstrap.sh, tools/); move it into wiki/, sources/, "
                f"workspace/, status/, or the owning product repo")


def check_symlinks(brain):
    """CLAUDE.md -> AGENTS.md is expected; every other symlink is flagged."""
    for root, dirs, files in os.walk(brain):
        if ".git" in dirs:
            dirs.remove(".git")
        rel_root = os.path.relpath(root, brain)
        for name in list(dirs) + files:
            full = os.path.join(root, name)
            if not os.path.islink(full):
                continue
            rel = os.path.normpath(os.path.join(rel_root, name))
            if rel == "CLAUDE.md" and os.readlink(full) == "AGENTS.md":
                continue
            kind = "directory" if os.path.isdir(full) else "file"
            err(f"symlink: {rel} -> {os.readlink(full)}: unexpected {kind} symlink "
                f"(only CLAUDE.md -> AGENTS.md is part of the model)")
        dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]


# ---------------------------------------------------------------- wiki

def check_links(brain, rel, text):
    base = os.path.dirname(os.path.join(brain, rel))
    for m in LINK_RE.finditer(text):
        target = m.group(1).strip()
        if re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
            continue
        if not target or target.startswith("<"):
            continue
        candidate = os.path.normpath(os.path.join(base, target))
        if not os.path.exists(candidate):
            err(f"{rel}: broken link -> {target}")


def check_index_links(brain, text):
    linked = set()
    for m in LINK_RE.finditer(text):
        target = m.group(1).strip()
        if re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
            continue
        linked.add(os.path.basename(os.path.normpath(target)))
    empty = body_is_empty(text)
    for page in WIKI_PAGES:
        if page == "index.md" or page in linked:
            continue
        msg = (f"wiki/index.md: no relative Markdown link to {page} "
               f"(a bare filename mention is not a link)")
        warn(msg) if empty else err(msg)


def volatile_lines(text):
    """Yield (lineno, line) for prose lines that assert volatile state."""
    body = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"),
                  text, flags=re.S)
    in_fence = False
    for i, line in enumerate(body.splitlines(), 1):
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not s or s.startswith("#"):
            continue
        # Navigation lines (a link to another wiki page) assert nothing.
        if any(os.path.basename(m.group(1).strip()) in WIKI_PAGES
               for m in LINK_RE.finditer(s)):
            continue
        low = s.lower()
        if any(w in low for w in VOLATILE_WORDS):
            yield i, s


def check_freshness(rel, text):
    page_dated = bool(DATE_RE.search(strip_comments(text)))
    vlines = list(volatile_lines(text))
    if rel.endswith("index.md"):
        # index.md is a map of the other pages, not a claims page; naming
        # access.md or the account pages there is not a volatile claim.
        return
    if vlines and not page_dated:
        err(f"{rel}: volatile claims (access/deployment/account state) carry no "
            f"YYYY-MM-DD verification date anywhere on the page")
        return
    for lineno, line in vlines:
        if not DATE_RE.search(line):
            warn(f"{rel}:{lineno}: volatile claim carries no date "
                 f"(a page-level 'as of' date satisfies this): {line[:70]}")


def check_wiki(brain):
    wiki = os.path.join(brain, "wiki")
    if not os.path.isdir(wiki):
        err("wiki/ missing")
        return
    found = sorted(f for f in os.listdir(wiki) if not f.startswith("."))
    for extra in found:
        full = os.path.join(wiki, extra)
        if os.path.isdir(full):
            err(f"wiki/{extra}: directories are not allowed in wiki/")
        elif DECISION_MODULE_RE.fullmatch(extra):
            check_decision_module(os.path.join(wiki, extra), extra)
        elif extra not in WIKI_PAGES and extra not in OPTIONAL_PAGES:
            err(f"wiki/{extra}: unexpected wiki page (fixed six, plus "
                f"known-facts.md, asks.md, asks-done.md, decisions-<topic>.md)")
    for page in OPTIONAL_PAGES:
        path = os.path.join(wiki, page)
        if os.path.exists(path):
            check_register(page, read(path))
    for page in WIKI_PAGES:
        path = os.path.join(wiki, page)
        if not os.path.exists(path):
            err(f"wiki/{page}: missing (empty pages are fine, absent ones are not)")
            continue
        text = read(path)
        if page == "decisions.md":
            # Ledger rows are cap-exempt (v1.0.1); only prose counts.
            prose = "\n".join(l for l in text.splitlines()
                              if not l.strip().startswith("|"))
            wc = word_count(prose)
            rows = sum(1 for l in text.splitlines()
                       if l.strip().startswith("|")
                       and not set(l.strip()) <= set("|-: ")
                       and not l.strip().lower().startswith("| date"))
            if rows > 40:
                warn(f"wiki/{page}: {rows} rows; roll off oldest "
                     f"Superseded/Corrected rows (Active rows stay)")
        else:
            wc = word_count(text)
        if wc > 300:
            err(f"wiki/{page}: {wc} words exceeds the 300-word cap")
        check_links(brain, f"wiki/{page}", text)
        if page == "index.md":
            check_index_links(brain, text)
        empty = body_is_empty(text)
        if not empty:
            low = text.lower()
            has_citation = ("source" in low or "sow" in low or "per " in low
                            or "verified" in low or "checked" in low)
            if page != "index.md" and not has_citation:
                err(f"wiki/{page}: no citation or verification basis found")
            if page in ("access.md",) and not DATE_RE.search(text):
                err(f"wiki/{page}: volatile access claims carry no "
                    f"YYYY-MM-DD verification date")
            elif page in ("scope.md", "stakeholders.md") and not DATE_RE.search(text):
                warn(f"wiki/{page}: no date found; volatile claims need one")
            check_freshness(f"wiki/{page}", text)
    dec = os.path.join(wiki, "decisions.md")
    if os.path.exists(dec):
        check_decisions(dec)


def check_register(page, text):
    """known-facts.md: one dated, sourced bullet per fact. asks.md: one table."""
    lines = text.splitlines()
    if page in ("asks.md", "asks-done.md"):
        prose = [l for l in lines if not l.strip().startswith("|")]
        tables = [l for l in lines if l.strip().startswith("|")]
        if not tables:
            err(f"wiki/{page}: no asks table")
        for i, l in enumerate(lines, 1):
            if not l.strip().startswith("|") or set(l.strip()) <= set("|-: "):
                continue
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            if cells[0] == "ID":
                if cells != ASKS_HEADER:
                    err(f"wiki/asks.md:{i}: header must be "
                        f"{' | '.join(ASKS_HEADER)}")
                continue
            if not re.fullmatch(r"A-\d{3,}", cells[0]):
                err(f"wiki/asks.md:{i}: first cell must be an id like A-001")
            elif len(cells) != len(ASKS_HEADER):
                err(f"wiki/asks.md:{i}: row needs {len(ASKS_HEADER)} cells")
            elif cells[3].split()[0].lower() not in ASK_STATUSES:
                err(f"wiki/asks.md:{i}: status must be open, partial or done")
    else:
        prose = [l for l in lines if not l.strip().startswith(("- ", "* "))]
        for i, l in enumerate(lines, 1):
            if l.strip().startswith(("- ", "* ")):
                if "source:" not in l or not DATE_RE.search(l):
                    warn(f"wiki/known-facts.md:{i}: fact needs a source and a "
                         f"YYYY-MM-DD date: {l.strip()[:60]}")
    wc = word_count("\n".join(prose))
    if wc > 300:
        err(f"wiki/{page}: {wc} words of prose exceeds the 300-word cap")


def check_decision_module(path, name):
    text = read(path)
    prose = "\n".join(l for l in text.splitlines() if not l.strip().startswith("|"))
    wc = word_count(prose)
    if wc > 300:
        err(f"wiki/{name}: {wc} words of prose exceeds the 300-word cap")
    check_decisions(path, name)


def check_decisions(path, name="decisions.md"):
    for i, line in enumerate(read(path).splitlines(), 1):
        s = line.strip()
        if not s.startswith("|") or set(s) <= set("|-: "):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if cells and cells[0].lower() in ("date",):
            continue
        if len(cells) < 4:
            err(f"wiki/{name}:{i}: row needs Date | Status | "
                f"Decision | Source")
            continue
        if not DATE_RE.match(cells[0]):
            err(f"wiki/{name}:{i}: first cell must be YYYY-MM-DD")
        if cells[1] not in VALID_STATUSES:
            err(f"wiki/{name}:{i}: invalid status {cells[1]!r} "
                f"(Active, Superseded, Corrected)")
        if not cells[3]:
            err(f"wiki/{name}:{i}: empty Source cell")


def check_root(brain):
    readme = os.path.join(brain, "README.md")
    if os.path.exists(readme):
        n = len(read(readme).splitlines())
        if n > 15:
            err(f"README.md: {n} lines exceeds the 15-line cap")
    else:
        err("README.md: missing")
    agents = os.path.join(brain, "AGENTS.md")
    if os.path.exists(agents):
        text = read(agents)
        n = len(text.splitlines())
        if n > 50:
            err(f"AGENTS.md: {n} lines exceeds the 50-line cap")
        wc = word_count(text)
        if wc > 150:
            warn(f"AGENTS.md: {wc} words; state only what this script cannot "
                 f"check, and drop anything the standard already says")
        if "manage-project-brain/v1" not in text:
            err("AGENTS.md: does not identify schema manage-project-brain/v1")
    else:
        err("AGENTS.md: missing")
    claude = os.path.join(brain, "CLAUDE.md")
    if not os.path.lexists(claude):
        err("CLAUDE.md: missing (expected symlink to AGENTS.md)")
    elif not os.path.islink(claude) or os.readlink(claude) != "AGENTS.md":
        err("CLAUDE.md: must be a symlink to AGENTS.md")


# ---------------------------------------------------------------- workspace

def is_status_report(filename):
    stem = os.path.splitext(filename)[0].lower()
    if STATUS_STEM_RE.search(stem):
        return True
    return ("status" in stem or "snapshot" in stem) and bool(DATE_RE.search(stem))


def check_workspace(brain, stale_days):
    ws = os.path.join(brain, "workspace")
    if not os.path.isdir(ws):
        warn("workspace/ missing")
        return
    today = datetime.date.today()
    for root, dirs, files in os.walk(ws):
        for d in list(dirs):
            if d.lower() in FORBIDDEN_DIRS:
                err(f"workspace/{os.path.relpath(os.path.join(root, d), ws)}: "
                    f"forbidden folder (no archives, status history, snapshots)")
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, brain)
            if "handoff" in f.lower():
                err(f"{rel}: completed handoffs do not belong in workspace")
            if is_status_report(f):
                err(f"status-report: {rel}: status and snapshot reporting is "
                    f"forbidden in workspace/ (git history is the archive)")
            if not f.endswith((".md", ".txt")):
                continue
            wc = word_count(read(full))
            if wc > 400:
                warn(f"{rel}: {wc} words; a workspace file past ~400 words has "
                     f"usually become an archive, cut it to what is still open")
            head = read(full)[:2000].lower()
            missing = [k for k in META_KEYS if f"{k}:" not in head]
            if missing:
                err(f"{rel}: missing metadata {', '.join(missing)} "
                    f"(needs status, updated, owner, exit condition)")
            m = DATE_RE.search(read(full)[:2000])
            if m:
                try:
                    d = datetime.date.fromisoformat(m.group(0))
                    if (today - d).days > stale_days:
                        err(f"{rel}: stale (updated {d}, older than "
                            f"{stale_days} days)")
                except ValueError:
                    pass


# ---------------------------------------------------------------- sources

def _manifest_name(cell):
    c = cell.strip()
    m = re.search(r"\[[^\]]*\]\(([^)]+)\)", c)
    if m:
        c = m.group(1)
    c = c.strip().strip("`").strip()
    return c.lstrip("./")


def parse_manifest(text):
    """Return [(lineno, cells)] for real manifest rows."""
    rows = []
    body = strip_comments(text)
    for i, line in enumerate(body.splitlines(), 1):
        s = line.strip()
        if not s.startswith("|") or set(s) <= set("|-: "):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if cells and cells[0].strip("` ").lower() in (
                "file", "filename", "source", "name", "path"):
            continue
        rows.append((i, cells))
    return rows


def sources_files(src):
    out = []
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs
                   if d != "private" or os.path.relpath(root, src) != "."]
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.startswith("."):
                continue
            rel = os.path.relpath(os.path.join(root, f), src)
            if rel == "README.md":
                continue
            out.append(rel)
    return sorted(out)


def check_manifest(brain, src):
    manifest = os.path.join(src, "README.md")
    text = read(manifest)
    rows = parse_manifest(text)
    listed = {}
    for lineno, cells in rows:
        rel = "sources/README.md"
        name = _manifest_name(cells[0]) if cells else ""
        if not name:
            err(f"{rel}:{lineno}: manifest row has no filename")
            continue
        if len(cells) < 4:
            err(f"{rel}:{lineno}: {name}: row needs File | Received date | "
                f"Origin | SHA-256")
        rest = cells[1:]
        date_cells = [c for c in rest if DATE_RE.search(c)]
        if not date_cells:
            err(f"{rel}:{lineno}: {name}: no received date (YYYY-MM-DD)")
        hash_idx, digest, abbreviated = None, None, False
        for j, c in enumerate(rest):
            token = c.strip().strip("`").strip()
            if HEX64_RE.fullmatch(token):
                hash_idx, digest = j, token.lower()
                break
            m = HEXISH_RE.search(token)
            if m and (ELLIPSIS_RE.search(token) or len(m.group(0)) < 64):
                if len(m.group(0)) >= 6 and not DATE_RE.search(c):
                    hash_idx, abbreviated = j, True
                    break
        if digest is None and not abbreviated:
            err(f"{rel}:{lineno}: {name}: no full 64-hex SHA-256 "
                f"(abbreviated or missing hashes are not acceptable)")
        elif abbreviated:
            err(f"{rel}:{lineno}: {name}: abbreviated SHA-256 "
                f"{rest[hash_idx].strip()!r}; record the full 64 hex characters")
        def _has_origin_text(c):
            # a cell carries origin information if anything remains after
            # removing dates and punctuation; "revised 2026-06-22" counts,
            # a bare "2026-06-22" does not
            leftover = DATE_RE.sub("", c)
            return any(ch.isalpha() for ch in leftover)
        origin = [c for j, c in enumerate(rest)
                  if j != hash_idx and c.strip() and _has_origin_text(c)]
        if not origin:
            err(f"{rel}:{lineno}: {name}: no origin (who/where it came from)")
        listed[name] = (lineno, digest)

    actual = sources_files(src)
    for rel_file in actual:
        base = os.path.basename(rel_file)
        entry = listed.get(rel_file) or listed.get(base)
        if entry is None:
            err(f"sources/README.md: {rel_file} exists under sources/ but has no "
                f"manifest entry (file, date, origin, full SHA-256)")
            continue
        lineno, digest = entry
        if digest:
            actual_hash = sha256_file(os.path.join(src, rel_file))
            if actual_hash and actual_hash != digest:
                err(f"sources/README.md:{lineno}: {rel_file}: manifest SHA-256 "
                    f"does not match file content (actual {actual_hash})")
    names = {os.path.basename(a) for a in actual} | set(actual)
    for name, (lineno, _d) in sorted(listed.items()):
        if name not in names:
            warn(f"sources/README.md:{lineno}: {name} is listed but no such file "
                 f"exists under sources/")


def check_sources(brain):
    src = os.path.join(brain, "sources")
    if not os.path.isdir(src):
        warn("sources/ missing")
        return
    if not os.path.exists(os.path.join(src, "README.md")):
        err("sources/README.md: provenance manifest missing")
    else:
        check_manifest(brain, src)
    for root, dirs, files in os.walk(src):
        rel_root = os.path.relpath(root, src)
        dirs[:] = [d for d in dirs
                   if d not in {"private", "raw"} and not d.startswith(".")]
        for filename in files:
            if filename.startswith("."):
                continue
            rel_file = os.path.normpath(os.path.join(rel_root, filename))
            if rel_file == "README.md" or filename.lower().endswith(".md"):
                continue
            err(f"sources/{rel_file}: non-Markdown received evidence belongs in sources/raw/")
    private = os.path.join(src, "private")
    claim = claims_private_storage(brain)
    if os.path.isdir(private) or claim:
        ignored, how = private_is_ignored(brain)
        if not ignored:
            why = ("sources/private/ exists" if os.path.isdir(private)
                   else f"{claim} claims private storage is gitignored")
            err(f".gitignore: {why} but sources/private/ is not effectively "
                f"ignored (checked via {how})")


# ---------------------------------------------------------------- .mcp.json

def shannon(s):
    if not s:
        return 0.0
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    n = float(len(s))
    return -sum((c / n) * math.log(c / n, 2) for c in counts.values())


def is_placeholder(value):
    v = value.strip()
    if not v:
        return True
    if PLACEHOLDER_RE.fullmatch(v):
        return True
    return "${" in v and "}" in v


def looks_secret(key, value):
    if not isinstance(value, str) or is_placeholder(value):
        return None
    for label, rx in SECRET_SHAPES:
        if rx.search(value):
            return label
    if key and SECRET_KEY_RE.search(key) and len(value.strip()) >= 8:
        return "sensitive key name with a literal value"
    v = value.strip()
    if (len(v) >= 28 and re.fullmatch(r"[A-Za-z0-9_\-+=]+", v)
            and any(c.isdigit() for c in v) and any(c.isalpha() for c in v)
            and shannon(v) >= 3.6):
        return "long high-entropy literal"
    return None


def redact(value):
    v = value.strip()
    return f"{v[:4]}...({len(v)} chars)"


def walk_json(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk_json(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_json(v, f"{path}[{i}]")
    else:
        yield path, node


def check_mcp(brain):
    path = os.path.join(brain, ".mcp.json")
    if not os.path.exists(path):
        return
    raw = read(path)
    try:
        data = json.loads(raw)
    except ValueError as e:
        err(f".mcp.json: not valid JSON ({e})")
        return
    for keypath, value in walk_json(data):
        if not isinstance(value, str):
            continue
        key = keypath.split(".")[-1].split("[")[0]
        label = looks_secret(key, value)
        if label:
            err(f"secret: .mcp.json: inline secret literal at {keypath} "
                f"({label}, value {redact(value)}); use ${{ENV_VAR}} or a "
                f"<placeholder> instead")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("brain")
    ap.add_argument("--stale-days", type=int, default=30)
    args = ap.parse_args()
    brain = os.path.abspath(args.brain)
    if not os.path.isdir(brain):
        print(f"error: not a directory: {brain}", file=sys.stderr)
        return 2
    check_root(brain)
    check_layout(brain)
    check_symlinks(brain)
    check_wiki(brain)
    check_workspace(brain, args.stale_days)
    check_sources(brain)
    check_mcp(brain)
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
