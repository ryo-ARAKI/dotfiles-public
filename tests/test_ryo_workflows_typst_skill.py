import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SOURCE = Path("config/codex/plugins/ryo-workflows")
PLUGIN_TARGET = "~/plugins/ryo-workflows/"
SKILL_NAMES = ("export-editable-typst-figures", "writing-typst-research-reports")


def manifest_rows():
    return [
        tuple(line.split("\t"))
        for line in (ROOT / "manifest/base.tsv").read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


class TypstSkillDistributionTests(unittest.TestCase):
    def test_manifest_deploys_every_skill_resource_in_local_context(self):
        rows = set(manifest_rows())
        for name in SKILL_NAMES:
            skill = ROOT / PLUGIN_SOURCE / "skills" / name
            with self.subTest(skill=name):
                self.assertTrue((skill / "SKILL.md").is_file())
            for resource in sorted(path for path in skill.rglob("*") if path.is_file()):
                relative = resource.relative_to(ROOT / PLUGIN_SOURCE)
                with self.subTest(resource=str(relative)):
                    expected = (
                        str(resource.relative_to(ROOT)),
                        PLUGIN_TARGET + str(relative),
                        "0644",
                        "local",
                    )
                    self.assertTrue(expected in rows, f"Missing local deployment row for {relative}")

    def test_deployed_plugin_discovers_skill_with_resolvable_references(self):
        with tempfile.TemporaryDirectory(prefix="typst-skill-distribution-", dir="/tmp") as directory:
            deployed = Path(directory)
            for source, target, _, context in manifest_rows():
                if context not in {"local", "always"} or not target.startswith(PLUGIN_TARGET):
                    continue
                destination = deployed / target.removeprefix(PLUGIN_TARGET)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / source, destination)

            metadata = json.loads((deployed / ".codex-plugin/plugin.json").read_text())
            for name in SKILL_NAMES:
                entrypoint = deployed / metadata["skills"] / name / "SKILL.md"
                with self.subTest(skill=name):
                    self.assertTrue(entrypoint.is_file(), "The deployed plugin cannot discover the skill")
                for document in entrypoint.parent.rglob("*.md"):
                    for target in re.findall(r"\[[^\]]+\]\(([^\s)]+)\)", document.read_text()):
                        if target.startswith(("https:", "http:", "#")):
                            continue
                        with self.subTest(skill=name, document=document.name, reference=target):
                            reference = document.parent / target.partition("#")[0]
                            self.assertTrue(reference.resolve().is_relative_to(deployed.resolve()))
                            self.assertTrue(reference.is_file())


if __name__ == "__main__":
    unittest.main()
