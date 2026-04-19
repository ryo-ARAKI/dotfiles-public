import tempfile
import textwrap
import unittest
from pathlib import Path

from dotfiles_installer.manifest import ManifestEntry, load_manifest


class LoadManifestTests(unittest.TestCase):
    def test_load_manifest_parses_tsv_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "base.tsv"
            manifest_path.write_text(
                textwrap.dedent(
                    """\
                    home/.bashrc\t~/.bashrc\t0644\talways
                    config/fish/config.fish\t~/.config/fish/config.fish\t0644\talways
                    """
                ),
                encoding="utf-8",
            )

            entries = load_manifest(manifest_path, layer="base")

        self.assertEqual(
            entries,
            [
                ManifestEntry("base", "home/.bashrc", "~/.bashrc", "0644", "always"),
                ManifestEntry(
                    "base",
                    "config/fish/config.fish",
                    "~/.config/fish/config.fish",
                    "0644",
                    "always",
                ),
            ],
        )


if __name__ == "__main__":
    unittest.main()
