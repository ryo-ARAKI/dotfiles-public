import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from dotfiles_installer.apply import apply_entry
from dotfiles_installer.manifest import load_manifest
from markdown_links import assert_markdown_links


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SOURCE = Path("config/codex/plugins/ryo-workflows")
PLUGIN_TARGET = "~/plugins/ryo-workflows/"


def plugin_entries():
    return [
        entry
        for entry in load_manifest(ROOT / "manifest/base.tsv", layer="base")
        if Path(entry.source).is_relative_to(PLUGIN_SOURCE)
        or entry.target.startswith(PLUGIN_TARGET)
    ]


class PluginDistributionTests(unittest.TestCase):
    def test_plugin_metadata_exposes_arxiv_discovery_terms(self):
        metadata = json.loads((ROOT / PLUGIN_SOURCE / ".codex-plugin/plugin.json").read_text())
        keywords = {keyword.lower() for keyword in metadata["keywords"]}
        self.assertTrue({"arxiv", "latex", "pdf"} <= keywords)
        self.assertIn("arXiv", metadata["interface"]["longDescription"])
        self.assertIn("Create an arXiv version diff PDF", metadata["interface"]["defaultPrompt"])

    def test_manifest_deploys_all_plugin_resources_in_local_context(self):
        expected = {
            (
                str(path.relative_to(ROOT)),
                PLUGIN_TARGET + str(path.relative_to(ROOT / PLUGIN_SOURCE)),
                "0644",
                "local",
            )
            for path in (ROOT / PLUGIN_SOURCE).rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        actual = {
            (entry.source, entry.target, entry.mode, entry.when)
            for entry in plugin_entries()
        }
        self.assertEqual(actual, expected)

    def test_deployed_plugin_discovers_every_skill_and_resolves_references(self):
        with tempfile.TemporaryDirectory(prefix="workflow-distribution-", dir="/tmp") as directory:
            root = Path(directory)
            deployed = root / "plugin"
            for entry in plugin_entries():
                if entry.when not in {"local", "always"}:
                    continue
                target = deployed / entry.target.removeprefix(PLUGIN_TARGET)
                apply_entry(
                    replace(entry, target=str(target)),
                    repo_root=ROOT,
                    backup_root=root / "backups",
                )
                self.assertEqual(target.read_bytes(), (ROOT / entry.source).read_bytes())
                self.assertEqual(target.stat().st_mode & 0o777, 0o644)

            metadata = json.loads((deployed / ".codex-plugin/plugin.json").read_text())
            self.assertEqual(metadata["name"], "ryo-workflows")
            skills = (deployed / metadata["skills"]).resolve()
            self.assertTrue(skills.is_relative_to(deployed))
            discovered = {path.parent.name for path in skills.glob("*/SKILL.md")}
            expected = {
                path.parent.name
                for path in (ROOT / PLUGIN_SOURCE / "skills").glob("*/SKILL.md")
            }
            self.assertTrue(expected)
            self.assertEqual(discovered, expected)

            assert_markdown_links(self, deployed.rglob("*.md"), deployed)


if __name__ == "__main__":
    unittest.main()
