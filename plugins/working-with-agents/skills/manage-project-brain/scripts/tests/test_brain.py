#!/usr/bin/env python3
"""Focused tests for the manage-project-brain scripts.

Every test builds a minimal brain in a tempdir. The conforming fixture must lint
clean; each violating fixture reproduces a false negative found in an
earlier audit and asserts the linter (or auditor) now reports it.

Run: python3 run-tests.py           (from the skill root)
  or python3 -m unittest discover -s scripts/tests -t scripts
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
LINT = os.path.join(SCRIPTS, "lint.py")
AUDIT = os.path.join(SCRIPTS, "audit.py")
SCAFFOLD = os.path.join(SCRIPTS, "scaffold.py")

TODAY = __import__("datetime").date.today().isoformat()
SOURCE_BODY = "Statement of work body, received verbatim.\n"
SOURCE_HASH = hashlib.sha256(SOURCE_BODY.encode()).hexdigest()

PAGES = {
    "index.md": """# Acme: index

One paragraph of orientation about the Acme engagement.

- [Scope](scope.md): what we owe and what is out.
- [Access](access.md): who grants what.
- [Stakeholders](stakeholders.md): people and roles.
- [Decisions](decisions.md): direction changes.
- [Glossary](glossary.md): engagement terms.
""",
    "scope.md": """# Scope

Phase one is the widget rebuild. Source: 2026-08-01-sow.md, verified 2026-08-01.
""",
    "access.md": """# Access

As of 2026-08-01, Alice Doe grants the CRM account; verified in the admin console.
""",
    "stakeholders.md": """# Stakeholders

Alice Doe, sponsor, approves scope. Source: kickoff call 2026-08-01.
""",
    "decisions.md": """# Decisions

| Date | Status | Decision or correction | Source |
|------|--------|------------------------|--------|
| 2026-08-01 | Active | Widget rebuild before reporting | kickoff call |
""",
    "glossary.md": """# Glossary

Widget: the client-facing unit we rebuild. Source: 2026-08-01-sow.md.
""",
}

README = """# Acme knowledge

Private brain for the Acme engagement. Schema: manage-project-brain/v1.

- `wiki/` is current truth. Start at `wiki/index.md`.
- `sources/` is received evidence.
- `sources/private/` is gitignored and never committed.
"""

AGENTS = """# Acme brain, maintenance contract

Schema: manage-project-brain/v1.

Six wiki pages, sourced and dated. Workspace files carry Status, Updated, Owner, Exit.
"""

WORKSPACE_FILE = f"""Status: open question on pricing plans
Updated: {TODAY}
Owner: Bob
Exit: removed once the plan list is agreed in writing.

Working notes.
"""

MANIFEST = f"""# Sources manifest

Provenance only, never interpretation.

| File | Received | Origin (who/where) | SHA-256 |
|------|----------|--------------------|---------|
| `2026-08-01-sow.md` | 2026-08-01 | Email from Alice Doe | {SOURCE_HASH} |

`private/` is gitignored and never committed.
"""


def write_bytes(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def make_brain(root):
    """A brain that satisfies manage-project-brain/v1 in full."""
    write(os.path.join(root, "README.md"), README)
    write(os.path.join(root, "AGENTS.md"), AGENTS)
    os.symlink("AGENTS.md", os.path.join(root, "CLAUDE.md"))
    write(os.path.join(root, ".gitignore"), "sources/private/\n")
    for name, body in PAGES.items():
        write(os.path.join(root, "wiki", name), body)
    write(os.path.join(root, "workspace", "pricing-question.md"), WORKSPACE_FILE)
    write(os.path.join(root, "sources", "README.md"), MANIFEST)
    write(os.path.join(root, "sources", "2026-08-01-sow.md"), SOURCE_BODY)
    os.makedirs(os.path.join(root, "sources", "private"), exist_ok=True)
    return root


def run(script, *args):
    proc = subprocess.run([sys.executable, script, *args], capture_output=True,
                          text=True)
    return proc.returncode, proc.stdout + proc.stderr


class BrainCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="brain-test-")
        self.brain = make_brain(os.path.join(self.dir, "knowledge"))

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def lint(self, *extra):
        return run(LINT, self.brain, *extra)

    def audit_json(self):
        code, out = run(AUDIT, self.brain, "--json")
        self.assertEqual(code, 0, out)
        return json.loads(out)

    def assertLintError(self, needle, *extra):
        code, out = self.lint(*extra)
        self.assertEqual(code, 1, f"expected a lint error; got:\n{out}")
        self.assertIn(needle, out)
        return out

    def assertLintClean(self, *extra):
        code, out = self.lint(*extra)
        self.assertEqual(code, 0, f"expected a clean lint; got:\n{out}")
        return out


class TestConforming(BrainCase):
    def test_conforming_brain_passes(self):
        out = self.assertLintClean()
        self.assertNotIn("ERROR", out)

    def test_claude_symlink_is_not_an_error(self):
        out = self.assertLintClean()
        self.assertNotIn("CLAUDE.md", out)

    def test_six_pages_enforced(self):
        os.remove(os.path.join(self.brain, "wiki", "glossary.md"))
        self.assertLintError("wiki/glossary.md: missing")

    def test_extra_wiki_page_rejected(self):
        write(os.path.join(self.brain, "wiki", "timeline.md"), "# Timeline\n")
        self.assertLintError("unexpected wiki page")

    def test_client_registers_allowed(self):
        write(os.path.join(self.brain, "wiki", "asks.md"),
              "# Asks\n\n| ID | Ask | Asked (date, channel, who) | Status | Proof "
              "| Waiting work | Last checked |\n|---|---|---|---|---|---|---|\n"
              "| A-001 | Product list | 2026-10-01, email, Carol | partial | tracker "
              "only | pricing | 2026-11-25 |\n")
        write(os.path.join(self.brain, "wiki", "known-facts.md"),
              "# Known facts\n\n- Supplier is Acme. "
              "<!-- source: call | verified_at: 2026-11-25 -->\n")
        out = self.assertLintClean()
        self.assertNotIn("unexpected wiki page", out)

    def test_decision_module_page_allowed(self):
        write(os.path.join(self.brain, "wiki", "decisions-rules.md"),
              "# Decisions: rules\n\n| Date | Status | Decision | Source |\n"
              "|---|---|---|---|\n| 2026-11-01 | Active | Flat rate. | call |\n")
        out = self.assertLintClean()
        self.assertNotIn("unexpected wiki page", out)

    def test_decision_module_bad_status_rejected(self):
        write(os.path.join(self.brain, "wiki", "decisions-rules.md"),
              "# Decisions: rules\n\n| Date | Status | Decision | Source |\n"
              "|---|---|---|---|\n| 2026-11-01 | Maybe | Flat rate. | call |\n")
        self.assertLintError("wiki/decisions-rules.md:5: invalid status")

    def test_asks_bad_status_rejected(self):
        write(os.path.join(self.brain, "wiki", "asks.md"),
              "# Asks\n\n| ID | Ask | Asked (date, channel, who) | Status | Proof "
              "| Waiting work | Last checked |\n|---|---|---|---|---|---|---|\n"
              "| A-001 | x | 2026-10-01 | maybe | - | - | 2026-11-25 |\n")
        self.assertLintError("status must be open, partial or done")

    def test_readme_line_cap(self):
        write(os.path.join(self.brain, "README.md"), README + "\nx" * 20)
        self.assertLintError("exceeds the 15-line cap")

    def test_wiki_word_cap(self):
        write(os.path.join(self.brain, "wiki", "glossary.md"),
              "# Glossary\n\nSource: sow.\n" + "word " * 400)
        self.assertLintError("exceeds the 300-word cap")

    def test_decision_status_must_be_valid(self):
        page = PAGES["decisions.md"] + "| 2026-08-02 | Done | Ship it | call |\n"
        write(os.path.join(self.brain, "wiki", "decisions.md"), page)
        self.assertLintError("invalid status 'Done'")

    def test_workspace_metadata_required(self):
        write(os.path.join(self.brain, "workspace", "loose.md"), "Some notes.\n")
        self.assertLintError("missing metadata")

    def test_decisions_ledger_rows_stay_cap_exempt(self):
        rows = "".join(f"| 2026-08-{d:02d} | Active | Decision number {d} "
                       f"with a long explanatory sentence | kickoff call |\n"
                       for d in range(1, 29))
        write(os.path.join(self.brain, "wiki", "decisions.md"),
              PAGES["decisions.md"] + rows)
        self.assertLintClean()


class TestLayout(BrainCase):
    """Gap 1: extra knowledge trees and unclassified technical files."""

    def test_openspec_tree_flagged(self):
        write(os.path.join(self.brain, "openspec", "project.md"), "# spec\n")
        out = self.assertLintError("layout: openspec/")
        self.assertIn("extra knowledge tree", out)

    def test_docs_tree_flagged(self):
        write(os.path.join(self.brain, "docs", "architecture.md"), "# arch\n")
        self.assertLintError("layout: docs/")

    def test_root_access_sow_and_status_files_flagged(self):
        for name in ("ACCESS.md", "SOW.md", "status-2026-08-01.md"):
            write(os.path.join(self.brain, name), "# x\n")
        out = self.assertLintError("layout: ACCESS.md")
        self.assertIn("layout: SOW.md", out)
        self.assertIn("layout: status-2026-08-01.md", out)

    def test_vendored_skill_trees_flagged(self):
        write(os.path.join(self.brain, ".claude", "skills", "x", "SKILL.md"), "x\n")
        write(os.path.join(self.brain, ".agents", "rules", "x.md"), "x\n")
        out = self.assertLintError("layout: .claude/")
        self.assertIn("layout: .agents/", out)
        self.assertIn("vendored agent/skill tree", out)

    def test_skills_lock_flagged(self):
        write(os.path.join(self.brain, "skills-lock.json"), "{}\n")
        self.assertLintError("layout: skills-lock.json")

    def test_vendored_tree_declared_in_agents_md_is_a_warning_only(self):
        write(os.path.join(self.brain, ".claude", "skills", "x", "SKILL.md"), "x\n")
        agents = os.path.join(self.brain, "AGENTS.md")
        with open(agents, encoding="utf-8") as f:
            body = f.read()
        write(agents, body + "\nOperational plumbing: .claude/skills/x writes demo prompts.\n")
        out = self.assertLintClean()
        self.assertIn("allowed because AGENTS.md declares it", out)

    def test_permitted_plumbing_not_flagged(self):
        write(os.path.join(self.brain, "bootstrap.sh"), "#!/bin/sh\n")
        write(os.path.join(self.brain, "tools", "sync.py"), "print(1)\n")
        write(os.path.join(self.brain, ".mcp.json"),
              json.dumps({"mcpServers": {"tracker": {"command": "npx",
                                                     "env": {"EXAMPLE_API_TOKEN":
                                                             "${EXAMPLE_API_TOKEN}"}}}}))
        self.assertLintClean()


class TestSymlinks(BrainCase):
    """Gap 2: symlink and empty-directory inventory."""

    def test_unexpected_dir_symlink_is_a_lint_error(self):
        os.symlink(os.path.join(self.brain, "wiki"),
                   os.path.join(self.brain, "sources", "wiki-link"))
        self.assertLintError("unexpected directory symlink")

    def test_unexpected_file_symlink_is_a_lint_error(self):
        os.symlink("../README.md", os.path.join(self.brain, "sources", "copy.md"))
        self.assertLintError("unexpected file symlink")

    def test_audit_inventories_symlinks_and_empty_dirs(self):
        os.symlink(os.path.join(self.brain, "wiki"),
                   os.path.join(self.brain, "sources", "wiki-link"))
        os.makedirs(os.path.join(self.brain, "workspace", "empty"))
        data = self.audit_json()
        inv = data["inventory"]
        self.assertIn({"path": "CLAUDE.md", "target": "AGENTS.md",
                       "dangling": False}, inv["file_symlinks"])
        self.assertEqual([l["path"] for l in inv["dir_symlinks"]],
                         [os.path.join("sources", "wiki-link")])
        self.assertIn(os.path.join("workspace", "empty"), inv["empty_dirs"])
        cats = {(f["category"], f["path"]) for f in data["failures"]}
        self.assertIn(("unexpected-symlink", os.path.join("sources", "wiki-link")),
                      cats)
        self.assertNotIn(("unexpected-symlink", "CLAUDE.md"), cats)

    def test_audit_text_separates_inventory_from_failures(self):
        write(os.path.join(self.brain, "openspec", "project.md"), "# spec\n")
        code, out = run(AUDIT, self.brain)
        self.assertEqual(code, 0, out)
        self.assertIn("== INVENTORY (informational) ==", out)
        self.assertIn("== COMPLIANCE FAILURES ==", out)
        self.assertLess(out.index("== INVENTORY"), out.index("== COMPLIANCE"))
        self.assertIn("extra-knowledge-tree", out.split("== COMPLIANCE")[1])

    def test_audit_flags_vendored_and_unclassified(self):
        write(os.path.join(self.brain, ".claude", "skills", "x", "SKILL.md"), "x\n")
        write(os.path.join(self.brain, "skills-lock.json"), "{}\n")
        cats = {f["category"] for f in self.audit_json()["failures"]}
        self.assertIn("vendored-agent-tree", cats)
        self.assertIn("unclassified-root-file", cats)


class TestPrivateIgnore(BrainCase):
    """Gap 3: effective sources/private/ ignore behavior."""

    def test_missing_gitignore_is_an_error(self):
        os.remove(os.path.join(self.brain, ".gitignore"))
        self.assertLintError("sources/private/ is not effectively ignored")

    def test_gitignore_that_misses_private_is_an_error(self):
        write(os.path.join(self.brain, ".gitignore"), "*.log\n.DS_Store\n")
        self.assertLintError("sources/private/ is not effectively ignored")

    def test_bare_private_pattern_counts(self):
        write(os.path.join(self.brain, ".gitignore"), "private/\n")
        self.assertLintClean()

    def test_negation_defeats_the_rule(self):
        write(os.path.join(self.brain, ".gitignore"),
              "sources/private/\n!sources/private\n")
        self.assertLintError("sources/private/ is not effectively ignored")

    def test_claim_without_directory_still_requires_the_rule(self):
        shutil.rmtree(os.path.join(self.brain, "sources", "private"))
        write(os.path.join(self.brain, ".gitignore"), "*.log\n")
        out = self.assertLintError("sources/private/ is not effectively ignored")
        self.assertIn("claims private storage", out)

    def test_git_check_ignore_is_authoritative(self):
        if shutil.which("git") is None:
            self.skipTest("git not available")
        subprocess.run(["git", "-C", self.brain, "init", "-q"], check=True,
                       capture_output=True)
        write(os.path.join(self.brain, ".gitignore"), "sources/private/\n")
        self.assertLintClean()
        write(os.path.join(self.brain, ".gitignore"), "*.log\n")
        self.assertLintError("git check-ignore")


class TestSourcesManifest(BrainCase):
    """Gap 4: manifest shape, full hashes, coverage, and hash correctness."""

    def test_abbreviated_hash_is_an_error(self):
        write(os.path.join(self.brain, "sources", "README.md"),
              MANIFEST.replace(SOURCE_HASH, SOURCE_HASH[:12] + "…"))
        self.assertLintError("abbreviated SHA-256")

    def test_twelve_char_prefix_is_an_error(self):
        write(os.path.join(self.brain, "sources", "README.md"),
              MANIFEST.replace(SOURCE_HASH, SOURCE_HASH[:12]))
        self.assertLintError("abbreviated SHA-256")

    def test_file_missing_from_manifest_is_an_error(self):
        write(os.path.join(self.brain, "sources", "2026-08-02-call.md"), "notes\n")
        self.assertLintError("has no manifest entry")

    def test_hash_mismatch_is_an_error(self):
        write(os.path.join(self.brain, "sources", "2026-08-01-sow.md"),
              "tampered body\n")
        self.assertLintError("does not match file content")

    def test_missing_date_is_an_error(self):
        write(os.path.join(self.brain, "sources", "README.md"),
              MANIFEST.replace("| 2026-08-01 | Email", "|  | Email"))
        self.assertLintError("no received date")

    def test_missing_origin_is_an_error(self):
        write(os.path.join(self.brain, "sources", "README.md"),
              MANIFEST.replace("| Email from Alice Doe |", "|  |"))
        self.assertLintError("no origin")

    def test_missing_hash_is_an_error(self):
        write(os.path.join(self.brain, "sources", "README.md"),
              MANIFEST.replace(SOURCE_HASH, ""))
        self.assertLintError("no full 64-hex SHA-256")

    def test_private_files_are_not_manifest_required(self):
        write(os.path.join(self.brain, "sources", "private", "secret.env"), "K=1\n")
        self.assertLintClean()

    def test_non_markdown_source_must_live_under_raw(self):
        payload = b"%PDF-1.4\n"
        write_bytes(os.path.join(self.brain, "sources", "brief.pdf"), payload)
        digest = hashlib.sha256(payload).hexdigest()
        readme = os.path.join(self.brain, "sources", "README.md")
        with open(readme, encoding="utf-8") as f:
            body = f.read()
        write(readme, body +
              f"| `brief.pdf` | 2026-08-02 | Client email | `{digest}` |\n")
        self.assertLintError("non-Markdown received evidence belongs in sources/raw/")

    def test_non_markdown_raw_source_is_valid(self):
        payload = b"%PDF-1.4\n"
        write_bytes(os.path.join(self.brain, "sources", "raw", "brief.pdf"), payload)
        digest = hashlib.sha256(payload).hexdigest()
        readme = os.path.join(self.brain, "sources", "README.md")
        with open(readme, encoding="utf-8") as f:
            body = f.read()
        write(readme, body +
              f"| `raw/brief.pdf` | 2026-08-02 | Client email | `{digest}` |\n")
        self.assertLintClean()



class TestManifestOriginWithDate(BrainCase):
    """An origin cell that mentions a date is still an origin."""

    def test_origin_cell_containing_a_date_is_not_blanked(self):
        payload = b"received bytes"
        write_bytes(os.path.join(self.brain, "sources", "asset.md"), payload)
        digest = hashlib.sha256(payload).hexdigest()
        readme = os.path.join(self.brain, "sources", "README.md")
        with open(readme, encoding="utf-8") as f:
            body = f.read()
        write(readme, body +
              f"| `asset.md` | 2026-07-21 | Bob, revised 2026-06-22 | `{digest}` |\n")
        self.assertLintClean()

    def test_bare_date_origin_cell_is_still_missing_origin(self):
        payload = b"received bytes"
        write_bytes(os.path.join(self.brain, "sources", "asset.md"), payload)
        digest = hashlib.sha256(payload).hexdigest()
        readme = os.path.join(self.brain, "sources", "README.md")
        with open(readme, encoding="utf-8") as f:
            body = f.read()
        write(readme, body +
              f"| `asset.md` | 2026-07-21 | 2026-06-22 | `{digest}` |\n")
        self.assertLintError("no origin")


class TestWorkspaceStatus(BrainCase):
    """Gap 5: status and snapshot reporting under workspace/."""

    def test_status_file_flagged(self):
        write(os.path.join(self.brain, "workspace", "status-2026-08-01.md"),
              WORKSPACE_FILE)
        self.assertLintError("status-report: workspace/status-2026-08-01.md")

    def test_snapshot_file_flagged(self):
        write(os.path.join(self.brain, "workspace", "snapshot-pricing.md"),
              WORKSPACE_FILE)
        self.assertLintError("status-report: workspace/snapshot-pricing.md")

    def test_dated_status_suffix_flagged_in_subdir(self):
        write(os.path.join(self.brain, "workspace", "notes",
                           "acme-status-2026-08-01.md"), WORKSPACE_FILE)
        self.assertLintError("acme-status-2026-08-01.md")

    def test_ordinary_workspace_file_not_flagged(self):
        write(os.path.join(self.brain, "workspace", "pricing-plans.md"),
              WORKSPACE_FILE)
        out = self.assertLintClean()
        self.assertNotIn("status-report", out)


class TestStatusDir(BrainCase):
    """Dated status lives at brain root status/, not under workspace/."""

    def test_root_status_dir_is_allowed(self):
        write(os.path.join(self.brain, "status", "2026-08-19.md"),
              "*Daily Status - 2026-08-19*\n")
        write(os.path.join(self.brain, "status", "2026-08-19-status.md"),
              "# snapshot\n")
        out = self.assertLintClean()
        self.assertNotIn("extra knowledge tree", out)
        self.assertNotIn("status-report", out)


class TestIndexLinks(BrainCase):
    """Gap 6: index.md must link the other five pages."""

    def test_bare_filename_mentions_are_not_links(self):
        write(os.path.join(self.brain, "wiki", "index.md"),
              "# Acme: index\n\nSee scope.md, access.md, stakeholders.md, "
              "decisions.md and glossary.md.\n")
        out = self.assertLintError("no relative Markdown link to scope.md")
        for page in ("access.md", "stakeholders.md", "decisions.md", "glossary.md"):
            self.assertIn(f"no relative Markdown link to {page}", out)

    def test_partial_link_set_flagged(self):
        write(os.path.join(self.brain, "wiki", "index.md"),
              "# Acme: index\n\n- [Scope](scope.md)\n- [Access](access.md)\n"
              "- [Stakeholders](stakeholders.md)\n- [Decisions](decisions.md)\n")
        out = self.assertLintError("no relative Markdown link to glossary.md")
        self.assertNotIn("link to scope.md", out)

    def test_empty_index_is_a_warning_not_an_error(self):
        write(os.path.join(self.brain, "wiki", "index.md"), "# Acme: index\n")
        out = self.assertLintClean()
        self.assertIn("WARN", out)
        self.assertIn("no relative Markdown link to scope.md", out)


class TestFreshness(BrainCase):
    """Gap 7: per-claim freshness on volatile pages."""

    def test_undated_volatile_page_is_an_error(self):
        write(os.path.join(self.brain, "wiki", "access.md"),
              "# Access\n\nAlice granted the CRM account; verified by her.\n")
        self.assertLintError("carry no")

    def test_undated_volatile_line_on_a_dated_page_is_a_warning(self):
        write(os.path.join(self.brain, "wiki", "access.md"),
              "# Access\n\nAs of 2026-08-01, verified in the admin console.\n\n"
              "- The staging site is deployed on Vercel under the client account.\n")
        out = self.assertLintClean()
        self.assertIn("volatile claim carries no date", out)

    def test_index_page_is_exempt_from_volatile_freshness(self):
        write(os.path.join(self.brain, "wiki", "index.md"),
              "# Index\n\n- [scope.md](scope.md)\n- [access.md](access.md): accounts and "
              "connector state\n- [stakeholders.md](stakeholders.md)\n"
              "- [decisions.md](decisions.md)\n- [glossary.md](glossary.md)\n")
        self.assertLintClean()

    def test_volatile_deployment_claim_on_scope_page(self):
        write(os.path.join(self.brain, "wiki", "scope.md"),
              "# Scope\n\nSource: SOW. The app is deployed to production and the "
              "client account is provisioned.\n")
        self.assertLintError("volatile claims")


class TestMcpSecrets(BrainCase):
    """Gap 8: inline secrets in .mcp.json."""

    def _mcp(self, env):
        write(os.path.join(self.brain, ".mcp.json"),
              json.dumps({"mcpServers": {"x": {"command": "npx", "env": env}}},
                         indent=2))

    def test_env_placeholders_are_fine(self):
        self._mcp({"API_KEY": "${ACME_API_KEY}", "BASE_URL": "https://acme.test",
                   "USER": "<your-username>"})
        self.assertLintClean()

    def test_openai_style_key_flagged(self):
        self._mcp({"OPENAI_API_KEY": "sk-" + "x" * 40})
        self.assertLintError("inline secret literal")

    def test_github_token_flagged(self):
        self._mcp({"GH": "gh" + "p_" + "A" * 36})
        self.assertLintError("github token")

    def test_slack_token_flagged(self):
        self._mcp({"SLACK": "xo" + "xb-" + "0" * 10 + "-" + "a" * 16})
        self.assertLintError("slack token")

    def test_jwt_flagged(self):
        self._mcp({"SUPABASE": ".".join(["ey" + "J" + "a" * 10, "b" * 10, "c" * 10])})
        self.assertLintError("jwt")

    def test_sensitive_key_with_literal_value_flagged(self):
        EXAMPLE_LIVE = "example-live-" + "0" * 12
        self._mcp({"EXAMPLE_API_TOKEN": EXAMPLE_LIVE})
        out = self.assertLintError("inline secret literal")
        self.assertIn("EXAMPLE_API_TOKEN", out)
        self.assertNotIn(EXAMPLE_LIVE, out)

    def test_invalid_json_flagged(self):
        write(os.path.join(self.brain, ".mcp.json"), "{not json")
        self.assertLintError("not valid JSON")


class TestScaffold(unittest.TestCase):
    """Gap 10: scaffold .gitignore behavior matches the documented contract."""

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="brain-scaffold-")
        self.brain = os.path.join(self.dir, "knowledge")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_dry_run_writes_nothing(self):
        code, out = run(SCAFFOLD, self.brain)
        self.assertEqual(code, 0, out)
        self.assertFalse(os.path.exists(self.brain))

    def test_apply_creates_gitignore_covering_private(self):
        code, out = run(SCAFFOLD, self.brain, "--apply", "--engagement", "acme")
        self.assertEqual(code, 0, out)
        with open(os.path.join(self.brain, ".gitignore"), encoding="utf-8") as fh:
            self.assertIn("sources/private/", fh.read())

    def test_scaffolded_brain_lints_clean(self):
        run(SCAFFOLD, self.brain, "--apply", "--engagement", "acme")
        code, out = run(LINT, self.brain)
        self.assertEqual(code, 0, out)

    def test_existing_gitignore_is_appended_never_overwritten(self):
        os.makedirs(self.brain)
        write(os.path.join(self.brain, ".gitignore"), "*.log\n")
        run(SCAFFOLD, self.brain, "--apply", "--engagement", "acme")
        with open(os.path.join(self.brain, ".gitignore"), encoding="utf-8") as fh:
            body = fh.read()
        self.assertIn("*.log", body)
        self.assertIn("sources/private/", body)

    def test_existing_coverage_is_left_alone(self):
        os.makedirs(self.brain)
        write(os.path.join(self.brain, ".gitignore"), "private/\n")
        run(SCAFFOLD, self.brain, "--apply", "--engagement", "acme")
        with open(os.path.join(self.brain, ".gitignore"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "private/\n")

    def test_existing_files_are_never_overwritten(self):
        os.makedirs(os.path.join(self.brain, "wiki"))
        write(os.path.join(self.brain, "wiki", "scope.md"), "# mine\n")
        run(SCAFFOLD, self.brain, "--apply", "--engagement", "acme")
        with open(os.path.join(self.brain, "wiki", "scope.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "# mine\n")


if __name__ == "__main__":
    unittest.main()
