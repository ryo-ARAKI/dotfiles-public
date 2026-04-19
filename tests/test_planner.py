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

    def test_when_filtering_removes_non_matching_entries(self) -> None:
        entries = [
            ManifestEntry("base", "home/.bashrc", "~/.bashrc", "0644", "always"),
            ManifestEntry("base", "home/.bashrc_remote", "~/.bashrc", "0644", "remote"),
        ]

        plan = build_plan(entries, context="local")

        self.assertEqual(plan["~/.bashrc"].source, "home/.bashrc")


if __name__ == "__main__":
    unittest.main()
