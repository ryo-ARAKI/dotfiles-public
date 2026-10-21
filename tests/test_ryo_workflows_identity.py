import importlib.util
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/skill_audits/ryo_workflows/identity.py"
spec = importlib.util.spec_from_file_location("workflow_identity", SCRIPT)
identity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(identity)


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="identity-test-", dir="/tmp")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.observed = self.root / "plugin"
        for relative, entry in identity.public_entries(ROOT).items():
            target = self.observed / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / entry["source"], target)
            target.chmod(entry["mode"])
        self.leaf = self.observed / "skills/dotfiles-deploy/SKILL.md"

    def test_matching_payload_and_distinct_evidence_layers(self):
        result = identity.compare(ROOT, self.observed)
        self.assertTrue(result["file_identity_matches"])
        self.assertEqual(len(result["source"]["resources"]), 19)
        self.assertEqual(result["catalog_visibility"], "unverified")
        self.assertEqual(result["actual_loaded_resources"], "unverified")
        self.assertEqual(len(result["source"]["head"]), 40)
        self.assertNotEqual(result["source"]["payload_sha256"], result["source"]["metadata_version"])

    def test_same_metadata_version_does_not_hide_changed_content(self):
        self.leaf.write_text("changed")
        result = identity.compare(ROOT, self.observed)
        self.assertFalse(result["file_identity_matches"])
        self.assertEqual(result["source"]["metadata_version"], result["observed"]["metadata_version"])
        self.assertIn(str(self.leaf.relative_to(self.observed)), result["differences"]["modified"])

    def test_missing_unexpected_and_empty_directory(self):
        self.leaf.unlink()
        (self.observed / "unexpected.txt").write_text("never collect this content")
        (self.observed / "unknown-directory").mkdir()
        result = identity.compare(ROOT, self.observed)
        self.assertFalse(result["file_identity_matches"])
        self.assertIn(str(self.leaf.relative_to(self.observed)), result["differences"]["missing"])
        self.assertIn("unexpected.txt", result["differences"]["unexpected"])
        self.assertIn("unknown-directory", result["differences"]["unexpected"])
        self.assertNotIn("sha256", result["observed"]["resources"]["unexpected.txt"])

    def test_symlinks_are_not_followed_even_when_dangling(self):
        for target in [self.root / "absent", ROOT / "README.md"]:
            with self.subTest(target=target):
                self.leaf.unlink()
                self.leaf.symlink_to(target)
                result = identity.compare(ROOT, self.observed)
                self.assertFalse(result["file_identity_matches"])
                info = result["observed"]["resources"][str(self.leaf.relative_to(self.observed))]
                self.assertEqual(info["type"], "symlink")
                self.assertNotIn("sha256", info)

    def test_directory_symlink_and_nonregular_resource(self):
        shutil.rmtree(self.leaf.parent)
        self.leaf.parent.symlink_to(ROOT / identity.PLUGIN / "skills/dotfiles-deploy", target_is_directory=True)
        result = identity.compare(ROOT, self.observed)
        self.assertFalse(result["file_identity_matches"])
        self.assertIn("skills/dotfiles-deploy", result["differences"]["wrong_types"])
        self.leaf.parent.unlink()
        self.leaf.parent.mkdir()
        self.leaf.mkdir()
        result = identity.compare(ROOT, self.observed)
        self.assertIn(str(self.leaf.relative_to(self.observed)), result["differences"]["wrong_types"])

    def test_mode_is_separate_from_content(self):
        self.leaf.chmod(0o600)
        result = identity.compare(ROOT, self.observed)
        self.assertFalse(result["file_identity_matches"])
        self.assertEqual(result["source"]["payload_sha256"], result["observed"]["payload_sha256"])
        self.assertTrue(result["differences"]["mode_mismatches"])

    def test_overlay_requires_exact_hash_mode_and_origin(self):
        self.leaf.write_text("approved private override")
        relative = str(self.leaf.relative_to(self.observed))
        overlay = {"files": {relative: {"sha256": identity.digest(self.leaf), "mode": "0644", "origin": "approved-fixture@revision"}}}
        result = identity.compare(ROOT, self.observed, overlay)
        self.assertTrue(result["file_identity_matches"])
        self.assertIn(relative, result["approved_overlays"])
        self.leaf.write_text("unapproved second override")
        self.assertFalse(identity.compare(ROOT, self.observed, overlay)["file_identity_matches"])
        del overlay["files"][relative]["origin"]
        with self.assertRaises(ValueError):
            identity.compare(ROOT, self.observed, overlay)

    def test_approved_addition_and_unapproved_override_are_distinct(self):
        addition = self.observed / "skills/private/SKILL.md"
        addition.parent.mkdir(); addition.write_text("fixture private skill"); addition.chmod(0o644)
        overlay = {"files": {"skills/private/SKILL.md": {"sha256": identity.digest(addition), "mode": "0644", "origin": "fixture"}}}
        self.assertTrue(identity.compare(ROOT, self.observed, overlay)["file_identity_matches"])
        self.leaf.write_text("unexpected override")
        self.assertFalse(identity.compare(ROOT, self.observed, overlay)["file_identity_matches"])

    def test_unsafe_overlay_paths_are_rejected(self):
        for name in ["../outside", "/absolute", "a/../b", "a//b", "a\\b"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                identity.compare(ROOT, self.observed, {"files": {name: {"sha256": "a" * 64, "mode": "0644", "origin": "fixture"}}})

    def test_cli_exit_codes_distinguish_match_mismatch_and_invalid_overlay(self):
        command = [sys.executable, '-B', str(SCRIPT), '--source-repo', str(ROOT),
                   '--observed-root', str(self.observed)]
        matched = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(matched.returncode, 0, matched.stderr)
        self.assertTrue(json.loads(matched.stdout)['file_identity_matches'])
        self.leaf.write_text('changed')
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
        overlay = self.root / 'invalid.json'
        overlay.write_text('{"files": {"invalid": 12}}')
        invalid = subprocess.run(command + ['--expected-overlay', str(overlay)], capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)
        self.assertNotIn('Traceback', invalid.stderr)

    def test_observed_root_symlink_is_rejected(self):
        alias = self.root / "alias"
        alias.symlink_to(self.observed, target_is_directory=True)
        self.assertFalse(identity.compare(ROOT, alias)["file_identity_matches"])


if __name__ == "__main__":
    unittest.main()
