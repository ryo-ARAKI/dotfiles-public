import json
import re
import shutil
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from urllib.parse import unquote
from unittest.mock import patch

from dotfiles_installer.apply import apply_entry
from dotfiles_installer.manifest import load_manifest


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

    def test_distribution_boundary_rejects_audit_files_and_missing_resources(self):
        with tempfile.TemporaryDirectory(prefix="distribution-negative-", dir="/tmp") as folder:
            root = Path(folder)
            shutil.copytree(ROOT / PLUGIN_SOURCE, root / PLUGIN_SOURCE)
            (root / "manifest").mkdir()
            shutil.copyfile(ROOT / "manifest/base.tsv", root / "manifest/base.tsv")
            extra = root / PLUGIN_SOURCE / "skills/stage1/unexpected-audit.md"
            extra.parent.mkdir()
            extra.write_text("audit documents must stay outside runtime")
            strict = self.test_manifest_deploys_all_plugin_resources_in_local_context
            with patch(__name__ + ".ROOT", root), self.assertRaises(AssertionError):
                strict()
            extra.unlink()
            (root / PLUGIN_SOURCE / "skills/extrip-to-ics/SKILL.md").unlink()
            with patch(__name__ + ".ROOT", root), self.assertRaises(AssertionError):
                strict()

    def test_public_architecture_has_exactly_the_original_six_skills(self):
        names = {path.parent.name for path in (ROOT / PLUGIN_SOURCE / "skills").glob("*/SKILL.md")}
        self.assertEqual(names, {"dotfiles-deploy", "creating-arxiv-diff-pdfs",
                               "creating-and-editing-typst-figures", "export-editable-typst-figures",
                               "writing-typst-research-reports", "extrip-to-ics"})

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

            for document in deployed.rglob("*.md"):
                links = re.findall(r"\[[^\]]+\]\(([^\s)]+)\)", document.read_text())
                for link in links:
                    if link.startswith(("https:", "http:")):
                        continue
                    with self.subTest(document=str(document.relative_to(deployed)), link=link):
                        path, _, fragment = unquote(link).partition("#")
                        reference = (document.parent / path).resolve() if path else document
                        self.assertTrue(reference.is_relative_to(deployed))
                        self.assertTrue(reference.is_file(), f"Missing resource: {link}")
                        if fragment:
                            headings = re.findall(r"^#{1,6} (.+)$", reference.read_text(), re.MULTILINE)
                            anchors = {
                                re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
                                for heading in headings
                            }
                            self.assertIn(fragment, anchors, f"Missing heading: {link}")


if __name__ == "__main__":
    unittest.main()
