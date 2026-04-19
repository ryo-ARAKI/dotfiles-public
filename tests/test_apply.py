import tempfile
import unittest
from pathlib import Path

from dotfiles_installer.apply import apply_entry
from dotfiles_installer.manifest import ManifestEntry


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
            self.assertEqual(target.read_text(encoding="utf-8"), "new\n")


if __name__ == "__main__":
    unittest.main()
