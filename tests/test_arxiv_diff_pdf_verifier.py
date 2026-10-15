import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "config/codex/plugins/ryo-workflows/skills/creating-arxiv-diff-pdfs/scripts/verify_diff_pdf.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_diff_pdf", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load verifier module")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class VerifierUnitTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(
            SCRIPT.is_file(),
            "verify_diff_pdf.py does not exist",
        )
        self.verifier = load_verifier()

    def test_parse_pdfinfo_returns_positive_page_count(self):
        self.assertEqual(self.verifier.parse_pdfinfo("Title: x\nPages: 77\n"), 77)

    def test_parse_pdfinfo_rejects_missing_or_zero_pages(self):
        for text in ("Title: x\n", "Pages: 0\n"):
            with self.subTest(text=text):
                with self.assertRaises(self.verifier.VerificationError):
                    self.verifier.parse_pdfinfo(text)

    def test_inspection_pages_cover_first_middle_last(self):
        self.assertEqual(self.verifier.inspection_pages(77), [1, 39, 77])
        self.assertEqual(self.verifier.inspection_pages(46), [1, 23, 46])
        self.assertEqual(self.verifier.inspection_pages(1), [1])


    def test_classify_log_separates_fatal_and_expected_duplicate_warnings(self):
        self.assertTrue(hasattr(self.verifier, "classify_log"), "classify_log not implemented")
        text = (
            "! LaTeX Error: Broken.\n"
            "Package natbib Warning: Citation x multiply defined.\n"
            "LaTeX Warning: Label LastBibItem multiply defined.\n"
        )
        errors, warnings = self.verifier.classify_log(text)
        self.assertTrue(any("LaTeX Error" in item for item in errors))
        self.assertEqual(len(warnings), 2)

    def test_classify_log_fails_unresolved_summaries_but_not_duplicate_summary(self):
        self.assertTrue(hasattr(self.verifier, "classify_log"), "classify_log not implemented")
        errors, warnings = self.verifier.classify_log(
            "LaTeX Warning: There were undefined references.\n"
            "Package natbib Warning: There were multiply defined citations.\n"
        )
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(warnings), 1)




class VerifierCliTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "verify_diff_pdf.py does not exist")
        self.verifier = load_verifier()

    @staticmethod
    def write_tool(directory: Path, name: str, body: str) -> None:
        path = directory / name
        path.write_text("#!/usr/bin/python3\n" + body, encoding="utf-8")
        path.chmod(0o755)

    def make_fake_tools(self, directory: Path) -> None:
        self.write_tool(directory, "pdfinfo", 'print("Pages: 7")\n')
        self.write_tool(
            directory,
            "qpdf",
            'print("No syntax or stream encoding errors found")\n',
        )
        self.write_tool(
            directory,
            "pdftoppm",
            "import pathlib, sys\n"
            "pathlib.Path(sys.argv[-1] + '.png').write_bytes(b'png')\n",
        )

    def test_cli_writes_success_report_and_three_images(self):
        self.assertTrue(hasattr(self.verifier, "main"), "main not implemented")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tool_dir = root / "tools"
            tool_dir.mkdir()
            self.make_fake_tools(tool_dir)
            pdf = root / "candidate.pdf"
            log = root / "candidate.log"
            output_dir = root / "verification"
            pdf.write_bytes(b"pdf")
            log.write_text("Output written on candidate.pdf (7 pages).\n", encoding="utf-8")

            exit_code = self.verifier.main(
                ["--pdf", str(pdf), "--log", str(log), "--output-dir", str(output_dir)],
                env={"PATH": f"{tool_dir}{os.pathsep}{os.environ['PATH']}"},
            )

            self.assertEqual(exit_code, 0)
            report = json.loads((output_dir / "verification.json").read_text())
            self.assertEqual(report["page_count"], 7)
            self.assertEqual(report["inspection_pages"], [1, 4, 7])
            self.assertEqual(len(report["rendered_images"]), 3)
            self.assertEqual(report["errors"], [])

    def test_cli_reports_missing_pdf(self):
        self.assertTrue(hasattr(self.verifier, "main"), "main not implemented")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "candidate.log"
            log.write_text("clean\n", encoding="utf-8")
            output_dir = root / "verification"
            exit_code = self.verifier.main(
                ["--pdf", str(root / "missing.pdf"), "--log", str(log), "--output-dir", str(output_dir)]
            )
            self.assertNotEqual(exit_code, 0)
            report = json.loads((output_dir / "verification.json").read_text())
            self.assertTrue(any("PDF file not found" in item for item in report["errors"]))

    def test_cli_reports_missing_external_commands(self):
        self.assertTrue(hasattr(self.verifier, "main"), "main not implemented")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pdf = root / "candidate.pdf"
            log = root / "candidate.log"
            output_dir = root / "verification"
            pdf.write_bytes(b"pdf")
            log.write_text("clean\n", encoding="utf-8")
            exit_code = self.verifier.main(
                ["--pdf", str(pdf), "--log", str(log), "--output-dir", str(output_dir)],
                env={"PATH": ""},
            )
            self.assertNotEqual(exit_code, 0)
            report = json.loads((output_dir / "verification.json").read_text())
            self.assertTrue(any("required command not found" in item for item in report["errors"]))

    def test_cli_reports_fatal_log(self):
        self.assertTrue(hasattr(self.verifier, "main"), "main not implemented")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pdf = root / "candidate.pdf"
            log = root / "candidate.log"
            output_dir = root / "verification"
            pdf.write_bytes(b"pdf")
            log.write_text("! LaTeX Error: Broken.\n", encoding="utf-8")
            exit_code = self.verifier.main(
                ["--pdf", str(pdf), "--log", str(log), "--output-dir", str(output_dir)]
            )
            self.assertNotEqual(exit_code, 0)
            report = json.loads((output_dir / "verification.json").read_text())
            self.assertTrue(any("LaTeX Error" in item for item in report["errors"]))
if __name__ == "__main__":
    unittest.main()
