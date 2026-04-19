import tempfile
import tomllib
import unittest
from pathlib import Path

from dotfiles_installer.codex_config import apply_codex_config
from dotfiles_installer.codex_config import plan_codex_config


class CodexConfigTests(unittest.TestCase):
    def test_plan_raises_when_public_fragment_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_root = Path(tmp) / "base"
            base_root.mkdir()

            with self.assertRaisesRegex(ValueError, "config.public.toml"):
                plan_codex_config(base_root, None, home_root=base_root)

    def test_plan_raises_when_private_fragment_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base_root = root / "base"
            private_root = root / "private"
            (base_root / "config" / "codex").mkdir(parents=True)
            private_root.mkdir()

            (base_root / "config" / "codex" / "config.public.toml").write_text(
                'model = "gpt-5.4"\n',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "config.private.toml"):
                plan_codex_config(base_root, private_root, home_root=root / "home")

    def test_plan_raises_when_generated_toml_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base_root = root / "base"
            (base_root / "config" / "codex").mkdir(parents=True)
            (base_root / "config" / "codex" / "config.public.toml").write_text(
                'model = "gpt-5.4"\ninvalid = [\n',
                encoding="utf-8",
            )

            with self.assertRaises(tomllib.TOMLDecodeError):
                plan_codex_config(base_root, None, home_root=root / "home")

    def test_apply_returns_nochange_when_generated_config_matches_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base_root = root / "base"
            home_root = root / "home"
            backup_root = root / "backup"
            (base_root / "config" / "codex").mkdir(parents=True)
            home_codex = home_root / ".codex"
            home_codex.mkdir(parents=True)

            public_text = 'model = "gpt-5.4"\n'
            (base_root / "config" / "codex" / "config.public.toml").write_text(public_text, encoding="utf-8")
            (home_codex / "config.toml").write_text(public_text, encoding="utf-8")

            plan = plan_codex_config(base_root, None, home_root=home_root)
            status = apply_codex_config(plan, backup_root=backup_root, dry_run=False)

            self.assertEqual(status, "nochange")
            self.assertFalse(backup_root.exists())

    def test_apply_creates_backup_when_generated_config_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base_root = root / "base"
            home_root = root / "home"
            backup_root = root / "backup"
            (base_root / "config" / "codex").mkdir(parents=True)
            home_codex = home_root / ".codex"
            home_codex.mkdir(parents=True)

            (base_root / "config" / "codex" / "config.public.toml").write_text(
                'model = "gpt-5.4"\n',
                encoding="utf-8",
            )
            (home_codex / "config.toml").write_text('model = "gpt-5.3-codex"\n', encoding="utf-8")

            plan = plan_codex_config(base_root, None, home_root=home_root)
            status = apply_codex_config(plan, backup_root=backup_root, dry_run=False)

            self.assertEqual(status, "applied")
            self.assertEqual((home_codex / "config.toml").read_text(encoding="utf-8"), 'model = "gpt-5.4"\n')
            backup_path = backup_root / (home_codex / "config.toml").relative_to((home_codex / "config.toml").anchor)
            self.assertTrue(backup_path.exists())
            self.assertEqual(backup_path.read_text(encoding="utf-8"), 'model = "gpt-5.3-codex"\n')


if __name__ == "__main__":
    unittest.main()
