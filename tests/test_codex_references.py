"""Portable Working Agreements links and ordinary reference-file deployment."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from markdown_links import assert_markdown_links


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

    def assert_references(self, home):
        for name in REFERENCE_NAMES:
            target = home / ".codex/references" / name
            self.assertTrue(target.is_file(), f"Reference not deployed: {target}")
            self.assertEqual(target.read_bytes(), (CODEX / "references" / name).read_bytes())
            self.assertEqual(target.stat().st_mode & 0o777, 0o644)

    def test_managed_document_links_and_anchors_resolve(self):
        references = [CODEX / "references" / name for name in REFERENCE_NAMES]
        linked = assert_markdown_links(self, [CODEX / "AGENTS.common.md"], CODEX)
        self.assertTrue(set(references).issubset(linked))
        handoff_links = assert_markdown_links(self, [CODEX / "codex-handoff-prompt.md"], CODEX)
        self.assertIn(CODEX / "references/model-selection.md", handoff_links)
        assert_markdown_links(
            self, [REPO / "README.md", CODEX / "README.md", *references], REPO,
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
                agreements = (deployed / "AGENTS.md").read_text()
                if context == "local":
                    self.assertTrue(agreements.startswith(common))
                    self.assertEqual(agreements[len(common):].strip(), extra.strip())
                else:
                    self.assertEqual(agreements, common)
                documents = [deployed / "AGENTS.md",
                             *(deployed / "references" / name for name in REFERENCE_NAMES)]
                handoff = deployed / "codex-handoff-prompt.md"
                self.assertEqual(handoff.exists(), context == "local")
                if context == "local":
                    self.assertEqual(handoff.read_bytes(), (CODEX / handoff.name).read_bytes())
                    documents.append(handoff)
                assert_markdown_links(self, documents, deployed)

    def test_remote_legacy_private_common_remains_a_complete_override(self):
        private = self.private_fixture()
        legacy = "# Legacy private common\n\nKeep complete override.\n"
        (private / "config/codex/AGENTS.common.md").write_text(legacy, encoding="utf-8")
        home = self.root / "remote"
        self.successful_install(home, "remote", "--yes", "--private", str(private),
                                "--only", "AGENTS.md")
        self.assertEqual((home / ".codex/AGENTS.md").read_text(), legacy)

    def test_precise_reference_selector_installs_only_three_references(self):
        home = self.root / "home"
        self.successful_install(home, "local", "--yes", "--only", REFERENCE_SELECTOR)
        self.assert_references(home)
        self.assertEqual(set(snapshot(home)),
                         {f".codex/references/{name}" for name in REFERENCE_NAMES})

    def test_agents_selector_does_not_automatically_select_references(self):
        home = self.root / "home"
        self.successful_install(home, "local", "--yes", "--only", "AGENTS.md")
        self.assertEqual(set(snapshot(home)), {".codex/AGENTS.md"})
        self.assertEqual((home / ".codex/AGENTS.md").read_bytes(),
                         (CODEX / "AGENTS.common.md").read_bytes())

    def test_two_stage_update_dry_run_and_reapply_preserve_backups(self):
        private = self.private_fixture()
        home = self.root / "home"
        deployed = home / ".codex"
        (deployed / "references").mkdir(parents=True)
        agents = deployed / "AGENTS.md"
        previous = {"AGENTS.md": b"Previous agreements\n"}
        agents.write_bytes(previous["AGENTS.md"])
        for name in REFERENCE_NAMES:
            previous[name] = b"Previous reference\n"
            (deployed / "references" / name).write_bytes(previous[name])
        args = ("--private", str(private))
        for selector, count in ((REFERENCE_SELECTOR, 3), ("AGENTS.md", 1)):
            before = tree_state(home)
            dry = self.successful_install(home, "local", *args, "--dry-run", "--only", selector)
            self.assertEqual(tree_state(home), before)
            self.assertIn("would apply", dry.stdout)
            applied = self.successful_install(home, "local", *args, "--yes", "--only", selector)
            self.assertIn(f"applied={count} skipped=0 nochange=0", applied.stdout)
            self.assert_references(home)
            if selector == REFERENCE_SELECTOR:
                self.assertEqual(agents.read_bytes(), previous["AGENTS.md"])
        self.assertTrue(agents.read_text().startswith((CODEX / "AGENTS.common.md").read_text()))
        assert_markdown_links(
            self, [agents, *(deployed / "references" / name for name in REFERENCE_NAMES)], deployed,
        )
        backup = home / ".dotfiles-backup"
        for name, old_content in previous.items():
            with self.subTest(backup=name):
                matches = [path for path in backup.rglob(name) if path.is_file()]
                self.assertEqual(len(matches), 1, f"Missing or duplicate backup: {name}")
                self.assertEqual(matches[0].read_bytes(), old_content)
        before = tree_state(home)
        for selector, count in ((REFERENCE_SELECTOR, 3), ("AGENTS.md", 1)):
            for flag in ("--dry-run", "--yes"):
                result = self.successful_install(home, "local", *args, flag, "--only", selector)
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
