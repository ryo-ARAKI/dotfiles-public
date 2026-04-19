import tempfile
import textwrap
import re
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

    def test_load_manifest_skips_blank_and_comment_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "base.tsv"
            manifest_path.write_text(
                textwrap.dedent(
                    """\
                    # comment

                    home/.bashrc\t~/.bashrc\t0644\talways
                       # indented comment
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

    def test_load_manifest_raises_value_error_for_malformed_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "base.tsv"
            manifest_path.write_text("home/.bashrc\t~/.bashrc\t0644\n", encoding="utf-8")

            with self.assertRaisesRegex(
                ValueError,
                rf"Malformed manifest row in {re.escape(str(manifest_path))} at line 1: expected 4 tab-separated columns, got 3",
            ):
                load_manifest(manifest_path, layer="base")

    def test_load_manifest_accepts_meaningfully_distinct_duplicate_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "base.tsv"
            manifest_path.write_text(
                textwrap.dedent(
                    """\
                    home/.bashrc\t~/.bashrc\t0644\talways
                    home/.bashrc_remote\t~/.bashrc\t0644\tremote
                    """
                ),
                encoding="utf-8",
            )

            entries = load_manifest(manifest_path, layer="base")

        self.assertEqual(
            entries,
            [
                ManifestEntry("base", "home/.bashrc", "~/.bashrc", "0644", "always"),
                ManifestEntry("base", "home/.bashrc_remote", "~/.bashrc", "0644", "remote"),
            ],
        )

    def test_load_manifest_rejects_ambiguous_duplicate_context_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "base.tsv"
            manifest_path.write_text(
                textwrap.dedent(
                    """\
                    home/.bashrc\t~/.bashrc\t0644\tremote
                    home/.bashrc_alt\t~/.bashrc\t0644\tremote
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                rf"ambiguous duplicate target in {re.escape(str(manifest_path))}: ~/.bashrc for when remote",
            ):
                load_manifest(manifest_path, layer="base")
