"""Portable Working Agreements links and ordinary reference-file deployment."""

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from dotfiles_installer.manifest import load_manifest


REPO = Path(__file__).resolve().parents[1]
CODEX = REPO / "config/codex"
REFERENCE_NAMES = (
    "model-selection.md", "worktree-and-git.md", "execution-diagnostics.md",
)
REFERENCE_SELECTOR = "config/codex/references/"


def snapshot(root: Path):
    return {
        str(path.relative_to(root)): (path.read_bytes(), path.stat().st_mode & 0o777)
        for path in root.rglob("*") if path.is_file()
    }


def tree_state(root: Path):
    return snapshot(root), {str(path.relative_to(root)) for path in root.rglob("*") if path.is_dir()}


class CodexReferencesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def install(self, home, context, *args, input=None):
        home.mkdir(parents=True, exist_ok=True)
        return subprocess.run(
            [str(REPO / "install"), "--context", context, *args],
            env=dict(os.environ, HOME=str(home)), input=input,
            capture_output=True, text=True, check=False,
        )

    def successful_install(self, home, context, *args):
        result = self.install(home, context, *args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def private_fixture(self):
        private = self.root / "private"
        (private / "manifest").mkdir(parents=True, exist_ok=True)
        (private / "manifest/private.tsv").write_text("", encoding="utf-8")
        codex = private / "config/codex"
        codex.mkdir(parents=True, exist_ok=True)
        (codex / "config.private.toml").write_text("", encoding="utf-8")
        (codex / "AGENTS.local.extra.md").write_text(
            "## Synthetic local guidance\n\nLocal fixture only.\n", encoding="utf-8",
        )
        return private

    def assert_links_resolve(self, documents, boundary):
        linked = set()
        for document in documents:
            self.assertTrue(document.is_file(), f"Missing document: {document}")
            links = re.findall(r"\[[^\]]+\]\(([^\s)]+)\)", document.read_text())
            for link in links:
                parsed = urlsplit(link)
                if parsed.scheme or parsed.netloc:
                    continue
                with self.subTest(document=str(document), link=link):
                    path = unquote(parsed.path)
                    target = (document.parent / path).resolve() if path else document
                    self.assertTrue(target.is_relative_to(boundary))
                    self.assertTrue(target.is_file(), f"Missing resource: {link}")
                    linked.add(target)
                    if parsed.fragment:
                        headings = re.findall(r"^#{1,6} (.+)$", target.read_text(), re.MULTILINE)
                        anchors = {
                            re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
                            for heading in headings
                        }
                        self.assertIn(unquote(parsed.fragment), anchors, f"Missing heading: {link}")
        return linked

    def assert_references(self, home):
        for name in REFERENCE_NAMES:
            target = home / ".codex/references" / name
            self.assertTrue(target.is_file(), f"Reference not deployed: {target}")
            self.assertEqual(target.read_bytes(), (CODEX / "references" / name).read_bytes())
            self.assertEqual(target.stat().st_mode & 0o777, 0o644)

    def test_manifest_registers_portable_references_for_both_contexts(self):
        entries = load_manifest(REPO / "manifest/base.tsv", "base")
        references = [entry for entry in entries if entry.source.startswith(REFERENCE_SELECTOR)]
        self.assertEqual(
            {(entry.source, entry.target, entry.mode, entry.when) for entry in references},
            {(f"{REFERENCE_SELECTOR}{name}", f"~/.codex/references/{name}", "0644", "always")
             for name in REFERENCE_NAMES},
        )

    def test_managed_document_links_and_anchors_resolve(self):
        references = [CODEX / "references" / name for name in REFERENCE_NAMES]
        linked = self.assert_links_resolve([CODEX / "AGENTS.common.md"], CODEX)
        self.assertTrue(set(references).issubset(linked))
        handoff_links = self.assert_links_resolve([CODEX / "codex-handoff-prompt.md"], CODEX)
        self.assertIn(CODEX / "references/model-selection.md", handoff_links)
        self.assert_links_resolve(
            [REPO / "README.md", CODEX / "README.md", *references], REPO,
        )

    def test_codex_payloads_deploy_with_context_specific_local_guidance(self):
        private = self.private_fixture()
        common = (CODEX / "AGENTS.common.md").read_text()
        extra = (private / "config/codex/AGENTS.local.extra.md").read_text()
        for context in ("local", "remote"):
            with self.subTest(context=context):
                home = self.root / context
                self.successful_install(home, context, "--yes", "--private", str(private),
                                        "--only", "~/.codex/")
                self.assert_references(home)
                deployed = home / ".codex"
                self.assertEqual((deployed / "AGENTS.md").read_text(),
                                 common + ("\n\n" + extra if context == "local" else ""))
                documents = [deployed / "AGENTS.md",
                             *(deployed / "references" / name for name in REFERENCE_NAMES)]
                handoff = deployed / "codex-handoff-prompt.md"
                self.assertEqual(handoff.exists(), context == "local")
                if context == "local":
                    self.assertEqual(handoff.read_bytes(), (CODEX / handoff.name).read_bytes())
                    documents.append(handoff)
                self.assert_links_resolve(documents, deployed)

    def test_legacy_private_common_remains_a_complete_override(self):
        private = self.private_fixture()
        legacy = "# Legacy private common\n\nKeep complete override.\n"
        (private / "config/codex/AGENTS.common.md").write_text(legacy, encoding="utf-8")
        extra = (private / "config/codex/AGENTS.local.extra.md").read_text()
        for context in ("local", "remote"):
            with self.subTest(context=context):
                home = self.root / context
                self.successful_install(home, context, "--yes", "--private", str(private),
                                        "--only", "~/.codex/")
                self.assertEqual((home / ".codex/AGENTS.md").read_text(),
                                 legacy + ("\n\n" + extra if context == "local" else ""))
                self.assert_references(home)

    def test_precise_reference_selector_installs_only_three_references(self):
        for context in ("local", "remote"):
            with self.subTest(context=context):
                home = self.root / context
                self.successful_install(home, context, "--yes", "--only", REFERENCE_SELECTOR)
                self.assert_references(home)
                self.assertEqual(set(snapshot(home)),
                                 {f".codex/references/{name}" for name in REFERENCE_NAMES})

    def test_agents_selector_does_not_automatically_select_references(self):
        for context in ("local", "remote"):
            with self.subTest(context=context):
                home = self.root / context
                self.successful_install(home, context, "--yes", "--only", "AGENTS.md")
                self.assertEqual(set(snapshot(home)), {".codex/AGENTS.md"})
                self.assertEqual((home / ".codex/AGENTS.md").read_bytes(),
                                 (CODEX / "AGENTS.common.md").read_bytes())

    def test_two_stage_update_dry_run_and_reapply_preserve_backups(self):
        private = self.private_fixture()
        for context in ("local", "remote"):
            with self.subTest(context=context):
                home = self.root / context
                deployed = home / ".codex"
                (deployed / "references").mkdir(parents=True)
                agents = deployed / "AGENTS.md"
                agents.write_text("Previous agreements\n", encoding="utf-8")
                for name in REFERENCE_NAMES:
                    (deployed / "references" / name).write_text("Previous reference\n", encoding="utf-8")
                args = ("--private", str(private))
                for selector, count in ((REFERENCE_SELECTOR, 3), ("AGENTS.md", 1)):
                    before = tree_state(home)
                    dry = self.successful_install(home, context, *args, "--dry-run", "--only", selector)
                    self.assertEqual(tree_state(home), before)
                    self.assertIn("would apply", dry.stdout)
                    applied = self.successful_install(home, context, *args, "--yes", "--only", selector)
                    self.assertIn(f"Summary: applied={count} skipped=0 nochange=0", applied.stdout)
                    self.assert_references(home)
                    if selector == REFERENCE_SELECTOR:
                        self.assertEqual(agents.read_text(), "Previous agreements\n")
                self.assert_links_resolve(
                    [agents, *(deployed / "references" / name for name in REFERENCE_NAMES)], deployed,
                )
                backup = home / ".dotfiles-backup"
                self.assertEqual(len(snapshot(backup)), 4)
                before = tree_state(home)
                for selector, count in ((REFERENCE_SELECTOR, 3), ("AGENTS.md", 1)):
                    for flag in ("--dry-run", "--yes"):
                        result = self.successful_install(home, context, *args, flag, "--only", selector)
                        self.assertIn(f"applied=0 skipped=0 nochange={count}", result.stdout)
                        self.assertEqual(tree_state(home), before)

    def test_reference_skip_and_partial_quit_are_not_complete_application(self):
        for answers, code, applied, skipped in (("n\nn\nn\n", 0, 0, 3), ("y\nq\n", 1, 1, 0)):
            with self.subTest(answers=answers):
                home = self.root / f"home-{applied}"
                result = self.install(home, "local", "--only", REFERENCE_SELECTOR, input=answers)
                self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                self.assertIn(f"Summary: applied={applied} skipped={skipped} nochange=0", result.stdout)
                self.assertEqual(len(snapshot(home)), applied)
                self.assertFalse((home / ".codex/AGENTS.md").exists())
                for path in (home / ".codex/references").glob("*.md"):
                    self.assertEqual(path.read_bytes(), (CODEX / "references" / path.name).read_bytes())

    def test_reference_payloads_keep_base_private_host_precedence(self):
        private = self.private_fixture()
        hosts = self.root / "hosts"
        (hosts / "manifest").mkdir(parents=True)
        name = "worktree-and-git.md"
        for layer, manifest, content in (
            (private, "private.tsv", "# Private reference\n"),
            (hosts, "fixture.tsv", "# Host reference\n"),
        ):
            source = layer / REFERENCE_SELECTOR / name
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(content, encoding="utf-8")
            (layer / "manifest" / manifest).write_text(
                f"{REFERENCE_SELECTOR}{name}\t~/.codex/references/{name}\t0644\talways\n",
                encoding="utf-8",
            )
        for context in ("local", "remote"):
            with self.subTest(context=context):
                home = self.root / context
                args = ("--yes", "--only", REFERENCE_SELECTOR, "--private", str(private))
                self.successful_install(home, context, *args)
                self.assertEqual((home / ".codex/references" / name).read_text(), "# Private reference\n")
                self.successful_install(home, context, *args, "--hosts", str(hosts), "--host-name", "fixture")
                self.assertEqual((home / ".codex/references" / name).read_text(), "# Host reference\n")
                for public in ("model-selection.md", "execution-diagnostics.md"):
                    self.assertEqual((home / ".codex/references" / public).read_bytes(),
                                     (CODEX / "references" / public).read_bytes())
