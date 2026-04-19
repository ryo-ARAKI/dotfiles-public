import unittest

from dotfiles_installer.manifest import ManifestEntry
from dotfiles_installer.planner import build_plan


class BuildPlanTests(unittest.TestCase):
    def test_private_overrides_base_for_same_target(self) -> None:
        entries = [
            ManifestEntry("base", "home/.bashrc", "~/.bashrc", "0644", "always"),
            ManifestEntry("private", "home/.bashrc_remote", "~/.bashrc", "0644", "always"),
        ]

        plan = build_plan(entries, context="remote")

        self.assertEqual(plan["~/.bashrc"].source, "home/.bashrc_remote")
        self.assertEqual(plan["~/.bashrc"].layer, "private")

    def test_host_overrides_private_and_base_for_same_target(self) -> None:
        entries = [
            ManifestEntry("base", "home/.bashrc", "~/.bashrc", "0644", "always"),
            ManifestEntry("private", "home/.bashrc_private", "~/.bashrc", "0644", "always"),
            ManifestEntry("host", "home/.bashrc_host", "~/.bashrc", "0644", "always"),
        ]

        plan = build_plan(entries, context="local")

        self.assertEqual(plan["~/.bashrc"].source, "home/.bashrc_host")
        self.assertEqual(plan["~/.bashrc"].layer, "host")

    def test_when_filtering_removes_non_matching_entries(self) -> None:
        entries = [
            ManifestEntry("base", "home/.bashrc", "~/.bashrc", "0644", "always"),
            ManifestEntry("base", "home/.bashrc_remote", "~/.bashrc", "0644", "remote"),
        ]

        plan = build_plan(entries, context="local")

        self.assertEqual(plan["~/.bashrc"].source, "home/.bashrc")

    def test_same_layer_same_target_prefers_specific_when_regardless_of_row_order(self) -> None:
        for context, entries, expected_source in (
            (
                "local",
                [
                    ManifestEntry("base", "home/.bashrc", "~/.bashrc", "0644", "always"),
                    ManifestEntry("base", "home/.bashrc_remote", "~/.bashrc", "0644", "remote"),
                ],
                "home/.bashrc",
            ),
            (
                "local",
                [
                    ManifestEntry("base", "home/.bashrc_remote", "~/.bashrc", "0644", "remote"),
                    ManifestEntry("base", "home/.bashrc", "~/.bashrc", "0644", "always"),
                ],
                "home/.bashrc",
            ),
            (
                "remote",
                [
                    ManifestEntry("base", "home/.bashrc", "~/.bashrc", "0644", "always"),
                    ManifestEntry("base", "home/.bashrc_remote", "~/.bashrc", "0644", "remote"),
                ],
                "home/.bashrc_remote",
            ),
            (
                "remote",
                [
                    ManifestEntry("base", "home/.bashrc_remote", "~/.bashrc", "0644", "remote"),
                    ManifestEntry("base", "home/.bashrc", "~/.bashrc", "0644", "always"),
                ],
                "home/.bashrc_remote",
            ),
        ):
            with self.subTest(context=context, entries=entries):
                plan = build_plan(entries, context=context)
                self.assertEqual(plan["~/.bashrc"].source, expected_source)


if __name__ == "__main__":
    unittest.main()
