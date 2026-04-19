import io
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


def write_codex_fragments(base_repo: Path, private_repo: Path | None = None) -> None:
    (base_repo / "config" / "codex").mkdir(parents=True, exist_ok=True)
    (base_repo / "config" / "codex" / "config.public.toml").write_text(
        'model = "gpt-5.4"\n',
        encoding="utf-8",
    )
    if private_repo is not None:
        (private_repo / "config" / "codex").mkdir(parents=True, exist_ok=True)
        (private_repo / "config" / "codex" / "config.private.toml").write_text(
            '\n[projects."/tmp/private-project"]\ntrust_level = "trusted"\n',
            encoding="utf-8",
        )


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

    def test_install_reprompts_until_valid_response(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base_repo = root / "base"
            home = root / "home"
            target = home / ".bashrc"

            (base_repo / "manifest").mkdir(parents=True)
            (base_repo / "home").mkdir(parents=True)
            home.mkdir()

            (base_repo / "manifest" / "base.tsv").write_text(
                "home/.bashrc\t~/.bashrc\t0644\talways\n",
                encoding="utf-8",
            )
            (base_repo / "home" / ".bashrc").write_text("new\n", encoding="utf-8")
            write_codex_fragments(base_repo)
            target.write_text("old\n", encoding="utf-8")

            install_module = load_install_module()

            with (
                patch.object(install_module, "ROOT", base_repo),
                patch.object(install_module.Path, "home", return_value=home),
                patch.dict("os.environ", {"HOME": str(home)}, clear=False),
                patch("sys.argv", ["install"]),
                patch("builtins.input", side_effect=["maybe", "", "y"]) as prompt,
            ):
                self.assertEqual(install_module.main(), 0)

            self.assertEqual(prompt.call_count, 3)
            self.assertEqual(target.read_text(encoding="utf-8"), "new\n")

    def test_install_shows_new_file_diff_before_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base_repo = root / "base"
            home = root / "home"
            target = home / ".bashrc"

            (base_repo / "manifest").mkdir(parents=True)
            (base_repo / "home").mkdir(parents=True)
            home.mkdir()

            (base_repo / "manifest" / "base.tsv").write_text(
                "home/.bashrc\t~/.bashrc\t0644\talways\n",
                encoding="utf-8",
            )
            (base_repo / "home" / ".bashrc").write_text("new\nline\n", encoding="utf-8")
            write_codex_fragments(base_repo)

            install_module = load_install_module()
            stdout = io.StringIO()

            with (
                patch.object(install_module, "ROOT", base_repo),
                patch.object(install_module.Path, "home", return_value=home),
                patch.dict("os.environ", {"HOME": str(home)}, clear=False),
                patch("sys.argv", ["install"]),
                patch("builtins.input", side_effect=["y"]) as prompt,
                patch("sys.stdout", stdout),
            ):
                self.assertEqual(install_module.main(), 0)

            output = stdout.getvalue()
            self.assertIn("New file: ~/.bashrc", output)
            self.assertIn("--- /dev/null", output)
            self.assertIn("+++ home/.bashrc", output)
            self.assertIn("applied: codex: config/codex/config.public.toml -> ~/.codex/config.toml", output)
            self.assertIn("Summary: applied=2 skipped=0 nochange=0 overridden=0", output)
            self.assertEqual(prompt.call_count, 1)
            self.assertEqual(target.read_text(encoding="utf-8"), "new\nline\n")

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
            write_codex_fragments(base_repo, private_repo)

            base_target.write_text("old base\n", encoding="utf-8")
            private_target.write_text("old private\n", encoding="utf-8")

            install_module = load_install_module()

            with (
                patch.object(install_module, "ROOT", base_repo),
                patch.object(install_module.Path, "home", return_value=home),
                patch.dict("os.environ", {"HOME": str(home)}, clear=False),
                patch("sys.argv", ["install", "--yes", "--private", str(private_repo)]),
            ):
                self.assertEqual(install_module.main(), 0)

            self.assertEqual(base_target.read_text(encoding="utf-8"), "base\n")
            self.assertEqual(private_target.read_text(encoding="utf-8"), "private\n")

    def test_install_uses_host_repo_root_for_host_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base_repo = root / "base"
            hosts_repo = root / "hosts"
            home = root / "home"
            target = home / ".vimrc"

            (base_repo / "manifest").mkdir(parents=True)
            (base_repo / "home").mkdir(parents=True)
            (hosts_repo / "manifest").mkdir(parents=True)
            (hosts_repo / "home").mkdir(parents=True)
            home.mkdir()

            (base_repo / "manifest" / "base.tsv").write_text(
                "home/.vimrc\t~/.vimrc\t0644\talways\n",
                encoding="utf-8",
            )
            (hosts_repo / "manifest" / "h200.tsv").write_text(
                "home/.vimrc\t~/.vimrc\t0644\talways\n",
                encoding="utf-8",
            )
            (base_repo / "home" / ".vimrc").write_text("base\n", encoding="utf-8")
            (hosts_repo / "home" / ".vimrc").write_text("host\n", encoding="utf-8")
            write_codex_fragments(base_repo)
            target.write_text("old\n", encoding="utf-8")

            install_module = load_install_module()

            with (
                patch.object(install_module, "ROOT", base_repo),
                patch.object(install_module.Path, "home", return_value=home),
                patch.dict("os.environ", {"HOME": str(home)}, clear=False),
                patch("sys.argv", ["install", "--yes", "--hosts", str(hosts_repo), "--host-name", "h200"]),
            ):
                self.assertEqual(install_module.main(), 0)

            self.assertEqual(target.read_text(encoding="utf-8"), "host\n")


if __name__ == "__main__":
    unittest.main()
