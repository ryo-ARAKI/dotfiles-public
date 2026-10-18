"""User-visible selection and safe application of generated Codex files."""
import os
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from dotfiles_installer.codex_agents import plan_codex_agents
from dotfiles_installer.codex_runtime import apply_codex_file


REPO = Path(__file__).resolve().parents[1]


def install(home: Path, *args: str, input: str | None = None):
    home.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [str(REPO / "install"), "--context", "local", *args],
        env=dict(os.environ, HOME=str(home)), input=input,
        capture_output=True, text=True, check=False,
    )


class CodexWorkflowTests(unittest.TestCase):
    def test_only_config_toml_selects_base_and_profiles_by_substring(self):
        for selector in ("config.toml", ".toml", "~/.codex/config.toml"):
            with self.subTest(selector=selector), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp) / "home"
                result = install(home, "--yes", "--only", selector)
                self.assertEqual(result.returncode, 0, msg=result.stderr)
                self.assertTrue((home / ".codex/config.toml").is_file())
                self.assertFalse((home / ".codex/AGENTS.md").exists())
                if selector == "config.toml":
                    self.assertEqual(
                        {p.name for p in (home / ".codex").iterdir()},
                        {"config.toml", "quick.config.toml", "deep.config.toml",
                         "subagent.config.toml", "reviewer.config.toml"},
                    )
                if selector == "~/.codex/config.toml":
                    self.assertEqual(len(list((home / ".codex").iterdir())), 1)

    def test_only_local_private_fragment_selects_generated_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            private = root / "private"
            (private / "manifest").mkdir(parents=True)
            (private / "manifest/private.tsv").write_text("", encoding="utf-8")
            fragments = private / "config/codex"
            fragments.mkdir(parents=True)
            (fragments / "config.private.toml").write_text("", encoding="utf-8")
            (fragments / "config.private.local.toml").write_text(
                '[mcp_servers.synthetic]\ncommand = "synthetic-secret"\n', encoding="utf-8",
            )
            home = root / "home"
            result = install(home, "--yes", "--private", str(private),
                             "--only", "config.private.local.toml")
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            target = home / ".codex/config.toml"
            self.assertTrue(target.is_file())
            self.assertEqual(tomllib.loads(target.read_text())["mcp_servers"]["synthetic"]["command"],
                             "synthetic-secret")
            self.assertEqual(len(list(target.parent.iterdir())), 1)
            self.assertNotIn("synthetic-secret", result.stdout + result.stderr)

    def test_agents_confirmation_preserves_target_on_skip_or_quit(self):
        for answer, expected_code in (("n\n", 0), ("q\n", 1), ("invalid\nn\n", 0)):
            with self.subTest(answer=answer), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp) / "home"
                target = home / ".codex/AGENTS.md"
                target.parent.mkdir(parents=True)
                before = "Keep synthetic-private-rules\n"
                target.write_text(before, encoding="utf-8")
                result = install(home, "--only", "AGENTS.md", input=answer)
                self.assertEqual(result.returncode, expected_code, msg=result.stderr)
                self.assertEqual(target.read_text(), before)
                self.assertFalse((home / ".dotfiles-backup").exists())
                self.assertNotIn("synthetic-private-rules", result.stdout + result.stderr)
                self.assertLess(result.stdout.index("~/.codex/AGENTS.md"),
                                result.stdout.index("Apply"))

    def test_all_confirmation_covers_remaining_generated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            result = install(home, "--only", ".config.toml", input="a\n")
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(
                {p.name for p in (home / ".codex").iterdir()},
                {"quick.config.toml", "deep.config.toml", "subagent.config.toml", "reviewer.config.toml"},
            )
            self.assertIn("Summary: applied=4 skipped=0 nochange=0", result.stdout)


class CodexAgentsSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / "base"
        source = self.base / "config/codex/AGENTS.common.md"
        source.parent.mkdir(parents=True)
        source.write_text("Managed rules\n", encoding="utf-8")
        self.home = self.root / "home"
        self.target = self.home / ".codex/AGENTS.md"
        self.target.parent.mkdir(parents=True)
        self.target.write_text("Previous rules\n", encoding="utf-8")
        self.target.chmod(0o600)
        self.backup = self.root / "backup"

    def plan(self):
        return plan_codex_agents(None, base_root=self.base, home_root=self.home)

    def test_agents_reject_a_stale_plan_without_creating_backup(self):
        plan = self.plan()
        self.target.write_text("Changed during confirmation\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed after planning"):
            apply_codex_file(plan, backup_root=self.backup, dry_run=False)
        self.assertEqual(self.target.read_text(), "Changed during confirmation\n")
        self.assertFalse(self.backup.exists())

    def test_agents_preserve_restrictive_mode_and_reapply_without_backup(self):
        apply_codex_file(self.plan(), backup_root=self.backup, dry_run=False)
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o600)
        backups = [p for p in self.backup.rglob("*") if p.is_file()]
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "Previous rules\n")
        self.assertEqual(apply_codex_file(self.plan(), backup_root=self.backup, dry_run=False),
                         "nochange")
        self.assertEqual([p for p in self.backup.rglob("*") if p.is_file()], backups)

    def test_agents_atomic_replace_failure_keeps_previous_target(self):
        with patch("dotfiles_installer.codex_runtime.os.replace", side_effect=OSError("fixture")):
            with self.assertRaises(OSError):
                apply_codex_file(self.plan(), backup_root=self.backup, dry_run=False)
        self.assertEqual(self.target.read_text(), "Previous rules\n")
        self.assertEqual(list(self.target.parent.iterdir()), [self.target])
