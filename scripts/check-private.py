#!/usr/bin/env python3
"""Block private facts from this public repo. Runs in the pre-push hook and in CI.

Fails on any tracked text file (or, with paths, those files) that holds:
  - a blocked word: client, product, private skill, host or domain (hashed, see below)
  - an IPv4 address (loopback, 0.0.0.0 and documentation ranges are allowed)
  - an email address (example.com/org/net and noreply addresses are allowed)
  - a key-shaped string: GitHub, Slack, OpenAI/Anthropic, AWS, Google, Doppler tokens,
    private key blocks, and long high-entropy hex
  - a personal home path (/Users/<name>, /home/<name>)
  - a UUID (account and profile ids look like this)
  - a pointer to the owner's private rules or memory folders

A false positive goes in .privacy-allow: one regular expression per line, matched
against "path:line: text". Keep that file short and explain each line with a comment.

Usage: python3 scripts/check-private.py [paths...]
       python3 scripts/check-private.py --hash < plain-list.txt > scripts/blocklist.sha256
"""
import hashlib
import hmac
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Blocked words (client and product names, private skills, hosts, domains) are kept as
# keyed hashes (HMAC-SHA256) in scripts/blocklist.sha256, so this public repo neither
# publishes the list it protects nor lets anyone confirm a guessed name. The key is the
# PRIVACY_KEY secret (a CI secret here; the owner keeps a copy). Without the key, the
# hashed list is skipped. A plain list in ~/.agents/privacy-blocklist.txt (or
# $PRIVACY_BLOCKLIST), when present, is always used, so the owner's own pushes need no key.
# Words are matched whole, one or two at a time, lowercased; "name-dev" or "a.b.com" is
# also checked by its parts.
HASH_FILE = ROOT / "scripts" / "blocklist.sha256"
WORD = re.compile(r"[a-z0-9][a-z0-9._-]*[a-z0-9]|[a-z0-9]")


def keyed(text, key):
    return hmac.new(key, text.encode(), hashlib.sha256).hexdigest()


def blocked_matchers():
    """Functions that say whether a candidate word is blocked."""
    matchers = []
    key = os.environ.get("PRIVACY_KEY", "").encode()
    if key and HASH_FILE.is_file():
        hashes = {l.strip() for l in HASH_FILE.read_text().splitlines() if l.strip() and not l.startswith("#")}
        matchers.append(lambda c: keyed(c, key) in hashes)
    plain = Path(os.environ.get("PRIVACY_BLOCKLIST") or Path.home() / ".agents" / "privacy-blocklist.txt")
    if plain.is_file():
        words = {l.strip().lower() for l in plain.read_text().splitlines() if l.strip() and not l.startswith("#")}
        matchers.append(lambda c: c in words)
    return matchers


def candidates(line):
    """Every word, its parts, and every pair of neighbouring words (with and without a space)."""
    words = WORD.findall(line.lower())
    out = set()
    simple = []
    for w in words:
        out.add(w)
        parts = [x for x in re.split(r"[._-]+", w) if x]
        out.update(parts)
        simple.extend(parts)
    for a, b in zip(simple, simple[1:]):
        out.add(f"{a} {b}")
        out.add(a + b)
    return out


RULES = [
    ("private reference", re.compile(r"~/\.agents/(rules|memory)\b")),
    ("IPv4 address", re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("GitHub token", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("Slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")),
    ("API key", re.compile(r"\bsk-(ant-)?[A-Za-z0-9_-]{20,}")),
    ("AWS key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Doppler token", re.compile(r"\bdp\.(st|pt|sa|ct|scim|audit)\.[A-Za-z0-9_-]{20,}")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("long hex secret", re.compile(r"(?i)(secret|token|key|password)[\"'\s:=]+[0-9a-f]{32,}")),
    ("home path", re.compile(r"/(Users|home)/(?!user\b|you\b|me\b|runner\b|<)[a-z][\w.-]+")),
    ("UUID", re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)),
]
OK_IP = re.compile(r"^(127\.|0\.0\.0\.0$|192\.0\.2\.|198\.51\.100\.|203\.0\.113\.|255\.255\.)")
OK_EMAIL = re.compile(r"(?i)(@example\.(com|org|net)$|^noreply@|^no-reply@|@users\.noreply\.github\.com$)")
TEXT_EXT = None  # every file git calls text


def tracked_files():
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, text=True)
    files = [ROOT / f for f in out.stdout.split("\0") if f]
    # Files staged but not yet committed count too (pre-commit use).
    return files


def allow_rules():
    f = ROOT / ".privacy-allow"
    if not f.is_file():
        return []
    rules = []
    for line in f.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            rules.append(re.compile(line))
    return rules


def is_binary(data):
    return b"\0" in data[:8000]


def scan(paths):
    allow = allow_rules()
    blocked = blocked_matchers()
    if not blocked:
        print("check-private: no PRIVACY_KEY and no plain blocklist, blocked words not checked")
    hits = []
    for path in paths:
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in {"scripts/check-private.py", "scripts/blocklist.sha256", ".privacy-allow"}:
            continue
        data = path.read_bytes()
        if is_binary(data):
            continue
        for n, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
            if blocked and any(m(c) for c in candidates(line) for m in blocked):
                where = f"{rel}:{n}: {line.strip()[:160]}"
                if not any(a.search(where) for a in allow):
                    hits.append(("blocked word", where))
            for kind, rx in RULES:
                for m in rx.finditer(line):
                    text = m.group(0)
                    if kind == "IPv4 address" and (OK_IP.match(text) or any(int(p) > 255 for p in text.split("."))):
                        continue
                    if kind == "email" and OK_EMAIL.search(text):
                        continue
                    where = f"{rel}:{n}: {line.strip()[:160]}"
                    if any(a.search(where) for a in allow):
                        continue
                    hits.append((kind, where))
    return hits


def main(argv):
    if argv[:1] == ["--hash"]:
        # Turn a plain list on stdin into the hash file's lines (needs PRIVACY_KEY).
        key = os.environ.get("PRIVACY_KEY", "").encode()
        if not key:
            print("set PRIVACY_KEY", file=sys.stderr)
            return 2
        for h in sorted({keyed(l.strip().lower(), key) for l in sys.stdin if l.strip() and not l.startswith("#")}):
            print(h)
        return 0
    paths = [Path(p).resolve() for p in argv] if argv else tracked_files()
    hits = scan(paths)
    for kind, where in hits:
        print(f"BLOCKED {kind}: {where}")
    if hits:
        print(f"\ncheck-private: {len(hits)} hit(s). Remove them, or add a reviewed line to .privacy-allow.")
        return 1
    print(f"check-private: {len(paths)} files clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
