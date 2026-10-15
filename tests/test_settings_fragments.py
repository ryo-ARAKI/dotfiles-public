import json
import os
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SettingsFragmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / "base"
        self.private = self.root / "private"
        self.home = self.root / "home"
        for directory in (self.base, self.private, self.home):
            directory.mkdir()
        shutil.copy2(ROOT / "install", self.base / "install")
        shutil.copytree(ROOT / "dotfiles_installer", self.base / "dotfiles_installer")
        self.write(self.private / "manifest/private.tsv", "")
        self.write(self.base / "config/codex/config.public.toml", 'model = "fixture"\n')
        self.write(self.private / "config/codex/config.private.toml", "")
        self.rows = []

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def add(self, source, target, text):
        self.write(self.base / source, text)
        self.rows.append(f"{source}\t{target}\t0644\tlocal\n")

    def run_install(self, *arguments):
        self.write(self.base / "manifest/base.tsv", "".join(self.rows))
        return subprocess.run(
            [str(self.base / "install"), "--yes", "--context", "local",
             "--private", str(self.private), *arguments],
            env={**os.environ, "HOME": str(self.home)},
            capture_output=True, text=True,
        )

    def test_jsonc_common_settings_and_private_values_are_composed_without_disclosure(self):
        self.add("config/Code/User/settings.json", "~/.config/Code/User/settings.json", '''{
          // URL and comment-like text must survive parsing.
          "example.url": "https://example.test/a,//b",
          "editor.fontSize": 16,
          "nested": {"common": true, "override": "base",},
        }''')
        self.write(self.private / "config/Code/User/settings.private.json", json.dumps({
            "nested": {"override": "private-value", "extra": [1, 2]},
        }))
        result = self.run_install("--only", "settings.private.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.home / ".config/Code/User/settings.json"
        self.assertTrue(target.is_file(), "Selecting a private fragment must select its composed target")
        self.assertEqual(json.loads(target.read_text()), {
            "example.url": "https://example.test/a,//b", "editor.fontSize": 16,
            "nested": {"common": True, "override": "private-value", "extra": [1, 2]},
        })
        self.assertNotIn("private-value", result.stdout + result.stderr)
        second = self.run_install("--only", "settings.json")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("nochange:", second.stdout)
        self.assertEqual(list(self.home.glob(".dotfiles-backup/**/*settings.json")), [])

    def test_toml_tables_arrays_and_private_substitutions_survive_composition(self):
        self.add("config/starship.toml", "~/.config/starship.toml", '''format = "$directory\\n$character"
[directory.substitutions]
Documents = "doc"
[[battery.display]]
threshold = 30
style = "bold red"
''')
        self.write(self.private / "config/starship.private.toml", '''[directory.substitutions]
"personal-work" = "work"
''')
        target = self.home / ".config/starship.toml"
        self.write(target, "# Previous config\n")
        result = self.run_install("--only", "starship")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(tomllib.loads(target.read_text()), {
            "format": "$directory\n$character",
            "directory": {"substitutions": {"Documents": "doc", "personal-work": "work"}},
            "battery": {"display": [{"threshold": 30, "style": "bold red"}]},
        })
        backups = list(self.home.glob(".dotfiles-backup/**/*starship.toml"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "# Previous config\n")
        self.assertEqual(target.stat().st_mode & 0o777, 0o644)

    def test_invalid_private_fragment_stops_before_any_manifest_write(self):
        self.add("home/marker", "~/marker", "must not be installed")
        self.add("config/Code/User/settings.json", "~/.config/Code/User/settings.json", "{}")
        self.write(self.private / "config/Code/User/settings.private.json", '{"private-value":')
        result = self.run_install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("settings.private.json", result.stderr)
        self.assertFalse((self.home / "marker").exists())
        self.assertNotIn("private-value", result.stdout + result.stderr)

    def test_ambiguous_or_non_json_values_stop_before_any_manifest_write(self):
        self.add("home/marker", "~/marker", "must not be installed")
        self.add("config/Code/User/settings.json", "~/.config/Code/User/settings.json", "{}")
        for private in (
            '{"private-value": 1, "private-value": 2}',
            '{"private-value": NaN}',
            '{"private-value": Infinity}',
        ):
            with self.subTest(private=private):
                self.write(self.private / "config/Code/User/settings.private.json", private)
                result = self.run_install()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.home / "marker").exists())
                self.assertNotIn("private-value", result.stdout + result.stderr)

    def test_host_file_still_overrides_public_and_private_fragments(self):
        self.add("config/starship.toml", "~/.config/starship.toml", 'palette = "public"\n')
        self.write(self.private / "config/starship.private.toml", 'palette = "private"\n')
        hosts = self.root / "hosts"
        self.write(hosts / "manifest/example.tsv", "starship.toml\t~/.config/starship.toml\t0644\tlocal\n")
        self.write(hosts / "starship.toml", 'palette = "host"\n')
        result = self.run_install("--hosts", str(hosts), "--host-name", "example", "--only", "starship")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.home / ".config/starship.toml").read_text(), 'palette = "host"\n')

    def test_dry_run_composes_without_writes_or_private_values_in_output(self):
        self.add("config/starship.toml", "~/.config/starship.toml", 'palette = "public"\n')
        self.write(self.private / "config/starship.private.toml", 'palette = "private-value"\n')
        result = self.run_install("--dry-run", "--only", "starship")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("would apply:", result.stdout)
        self.assertNotIn("private-value", result.stdout + result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_public_common_agents_are_available_without_private_repository(self):
        self.write(self.base / "config/codex/AGENTS.common.md", "# Shared rules\n")
        self.write(self.base / "manifest/base.tsv", "")
        result = subprocess.run(
            [str(self.base / "install"), "--yes", "--only", "AGENTS.md"],
            env={**os.environ, "HOME": str(self.home)}, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.home / ".codex/AGENTS.md"
        self.assertTrue(target.exists(), "Public-only installs must include the common working agreements")
        self.assertEqual(target.read_text(), "# Shared rules\n")
