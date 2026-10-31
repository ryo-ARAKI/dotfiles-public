"""Run both self-contained drafts offline in real Chrome through a test-only CDP pipe.

SCHEMATIC_PLUGIN_ROOT can point at an actual manifest copy. Set
SCHEMATIC_EVIDENCE_DIR to retain downloads/screenshots in fresh case directories.
Installed Node >=22 and Chrome/Chromium are optional for ordinary suites.
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = Path(os.environ.get('SCHEMATIC_PLUGIN_ROOT', ROOT / 'config/codex/plugins/ryo-workflows'))
ASSETS = PLUGIN / 'skills/creating-and-editing-typst-schematics/assets'
CHROME = next((shutil.which(n) for n in ('google-chrome', 'chromium', 'chromium-browser') if shutil.which(n)), None)


@unittest.skipUnless(CHROME and shutil.which('node'), 'installed Chrome and Node required')
class MockupBrowserTests(unittest.TestCase):
    def check_draft(self, check, spectrum=False):
        html = ASSETS / ('spectrum-layout-mockup.html' if spectrum else 'layout-mockup.html')
        self.assertTrue(html.is_file(), html)
        name = check + ('-spectrum' if spectrum else '-node')
        evidence = os.environ.get('SCHEMATIC_EVIDENCE_DIR')
        if evidence:
            Path(evidence).mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='schematic-browser-', dir='/tmp') as tmp:
            out = Path(tempfile.mkdtemp(prefix=name + '-', dir=evidence)) if evidence else Path(tmp)
            runner = ROOT / 'tests' / f'schematic_{check}.mjs'
            result = subprocess.run(['node', str(runner), CHROME, str(html), str(out)],
                                    text=True, capture_output=True, timeout=110)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            print(result.stdout.strip())

    def test_browser_edit_download_reload_and_protection(self):
        self.check_draft('node')

    def test_spectrum_curve_editing_history_and_handoff(self):
        self.check_draft('spectrum', spectrum=True)

    def test_node_input_precision_colors_and_export(self):
        self.check_draft('colors')

    def test_spectrum_input_precision_colors_and_export(self):
        self.check_draft('colors', spectrum=True)

    def test_node_dependent_deletion_empty_state_and_reset(self):
        self.check_draft('deletion')

    def test_spectrum_deletion_empty_state_and_reset(self):
        self.check_draft('deletion', spectrum=True)


if __name__ == '__main__':
    unittest.main()
