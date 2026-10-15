import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "config/codex/plugins/ryo-workflows"
MANIFEST = ROOT / "manifest/base.tsv"

EXPECTED_MANIFEST_ROWS = {
    "config/codex/plugins/ryo-workflows/skills/creating-arxiv-diff-pdfs/SKILL.md\t~/plugins/ryo-workflows/skills/creating-arxiv-diff-pdfs/SKILL.md\t0644\tlocal",
    "config/codex/plugins/ryo-workflows/skills/creating-arxiv-diff-pdfs/references/revtex-latexdiff-troubleshooting.md\t~/plugins/ryo-workflows/skills/creating-arxiv-diff-pdfs/references/revtex-latexdiff-troubleshooting.md\t0644\tlocal",
    "config/codex/plugins/ryo-workflows/skills/creating-arxiv-diff-pdfs/scripts/verify_diff_pdf.py\t~/plugins/ryo-workflows/skills/creating-arxiv-diff-pdfs/scripts/verify_diff_pdf.py\t0644\tlocal",
}


class ArxivSkillPluginContractTests(unittest.TestCase):
    def test_manifest_deploys_all_skill_files(self):
        rows = set(MANIFEST.read_text(encoding="utf-8").splitlines())
        self.assertTrue(EXPECTED_MANIFEST_ROWS <= rows)

    def test_readme_lists_the_distributed_skill(self):
        readme = (PLUGIN / "README.md").read_text(encoding="utf-8")
        self.assertIn("creating-arxiv-diff-pdfs", readme)
        self.assertIn("first/middle/last", readme)
        self.assertIn("raw latexdiff", readme)

    def test_plugin_metadata_exposes_arxiv_discovery_terms(self):
        metadata = json.loads(
            (PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        keywords = {keyword.lower() for keyword in metadata["keywords"]}
        self.assertTrue({"arxiv", "latex", "pdf"} <= keywords)
        self.assertIn("arXiv", metadata["interface"]["longDescription"])
        self.assertIn(
            "Create an arXiv version diff PDF",
            metadata["interface"]["defaultPrompt"],
        )

    def test_skill_entrypoint_and_support_files_exist(self):
        skill = PLUGIN / "skills/creating-arxiv-diff-pdfs"
        for relative in (
            "SKILL.md",
            "references/revtex-latexdiff-troubleshooting.md",
            "scripts/verify_diff_pdf.py",
        ):
            with self.subTest(relative=relative):
                self.assertTrue((skill / relative).is_file())


if __name__ == "__main__":
    unittest.main()
