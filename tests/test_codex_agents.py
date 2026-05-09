import tempfile
import unittest
from pathlib import Path

from dotfiles_installer.codex_agents import apply_codex_agents
from dotfiles_installer.codex_agents import plan_codex_agents


class CodexAgentsTests(unittest.TestCase):
    def test_plan_includes_private_local_extra_only_for_local_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            private_root = root / "private"
            (private_root / "config" / "codex").mkdir(parents=True)

            common_text = "# Common\n\nShared rules.\n"
            local_text = "## Local\n\nLocal-only rules.\n"
            (private_root / "config" / "codex" / "AGENTS.common.md").write_text(common_text, encoding="utf-8")
            (private_root / "config" / "codex" / "AGENTS.local.extra.md").write_text(
                local_text,
                encoding="utf-8",
            )

            local_plan = plan_codex_agents(private_root, home_root=root / "home", context="local")
            remote_plan = plan_codex_agents(private_root, home_root=root / "home", context="remote")

            self.assertEqual(local_plan.content, f"{common_text}\n\n{local_text}")
            self.assertEqual(remote_plan.content, common_text)
            self.assertIn("AGENTS.local.extra.md", local_plan.source_label)
            self.assertNotIn("AGENTS.local.extra.md", remote_plan.source_label)

    def test_plan_raises_when_private_root_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "dotfiles-private"):
                plan_codex_agents(None, home_root=Path(tmp) / "home")

    def test_plan_raises_when_common_fragment_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            private_root = Path(tmp) / "private"
            private_root.mkdir()

            with self.assertRaisesRegex(ValueError, "AGENTS.common.md"):
                plan_codex_agents(private_root, home_root=Path(tmp) / "home")

    def test_apply_creates_backup_when_generated_agents_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            private_root = root / "private"
            home_root = root / "home"
            backup_root = root / "backup"
            (private_root / "config" / "codex").mkdir(parents=True)
            home_codex = home_root / ".codex"
            home_codex.mkdir(parents=True)

            (private_root / "config" / "codex" / "AGENTS.common.md").write_text("# New\n", encoding="utf-8")
            (home_codex / "AGENTS.md").write_text("# Old\n", encoding="utf-8")

            plan = plan_codex_agents(private_root, home_root=home_root)
            status = apply_codex_agents(plan, backup_root=backup_root, dry_run=False)

            self.assertEqual(status, "applied")
            self.assertEqual((home_codex / "AGENTS.md").read_text(encoding="utf-8"), "# New\n")
            backup_path = backup_root / (home_codex / "AGENTS.md").relative_to((home_codex / "AGENTS.md").anchor)
            self.assertTrue(backup_path.exists())
            self.assertEqual(backup_path.read_text(encoding="utf-8"), "# Old\n")


if __name__ == "__main__":
    unittest.main()
