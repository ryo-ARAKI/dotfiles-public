import tempfile
import unittest
from importlib import machinery
from importlib import util
from pathlib import Path
from unittest.mock import patch

from dotfiles_installer.apply import apply_entry
from dotfiles_installer.manifest import ManifestEntry


def load_install_module() -> object:
    loader = machinery.SourceFileLoader("install_module", str(Path(__file__).resolve().parents[1] / "install"))
    spec = util.spec_from_loader(loader.name, loader)
    assert spec is not None and spec.loader is not None
    module = util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class ApplyEntryTests(unittest.TestCase):
    def test_apply_entry_creates_backup_and_writes_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "repo" / "home" / ".bashrc"
            target = root / "target" / ".bashrc"
            backup_root = root / "backup"
            source.parent.mkdir(parents=True)
            target.parent.mkdir(parents=True)
            source.write_text("new\n", encoding="utf-8")
            target.write_text("old\n", encoding="utf-8")

            entry = ManifestEntry("base", "home/.bashrc", str(target), "0644", "always")
            backup_path = apply_entry(entry, repo_root=source.parents[1], backup_root=backup_root)

            self.assertTrue(backup_path.exists())
            self.assertEqual(backup_path.read_text(encoding="utf-8"), "old\n")
            self.assertEqual(target.read_text(encoding="utf-8"), "new\n")
            self.assertEqual(target.stat().st_mode & 0o777, 0o644)

    def test_install_uses_private_repo_root_for_private_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base_repo = root / "base"
            private_repo = root / "private"
            home = root / "home"
            base_target = home / ".bashrc"
            private_target = home / ".vimrc"

            (base_repo / "manifest").mkdir(parents=True)
            (base_repo / "home").mkdir(parents=True)
            (private_repo / "manifest").mkdir(parents=True)
            (private_repo / "home").mkdir(parents=True)
            home.mkdir()

            (base_repo / "manifest" / "base.tsv").write_text(
                "home/.bashrc\t~/.bashrc\t0644\talways\n",
                encoding="utf-8",
            )
            (private_repo / "manifest" / "private.tsv").write_text(
                "home/.vimrc\t~/.vimrc\t0644\talways\n",
                encoding="utf-8",
            )
            (base_repo / "home" / ".bashrc").write_text("base\n", encoding="utf-8")
            (base_repo / "home" / ".vimrc").write_text("wrong\n", encoding="utf-8")
            (private_repo / "home" / ".vimrc").write_text("private\n", encoding="utf-8")

            base_target.write_text("old base\n", encoding="utf-8")
            private_target.write_text("old private\n", encoding="utf-8")

            install_module = load_install_module()

            with (
                patch.object(install_module, "ROOT", base_repo),
                patch.object(install_module.Path, "home", return_value=home),
                patch.dict("os.environ", {"HOME": str(home)}, clear=False),
                patch("sys.argv", ["install", "--private", str(private_repo)]),
            ):
                self.assertEqual(install_module.main(), 0)

            self.assertEqual(base_target.read_text(encoding="utf-8"), "base\n")
            self.assertEqual(private_target.read_text(encoding="utf-8"), "private\n")


if __name__ == "__main__":
    unittest.main()
