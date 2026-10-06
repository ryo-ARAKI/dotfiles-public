import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from dotfiles_installer.codex_runtime import apply_codex_runtime
from dotfiles_installer.codex_runtime import plan_codex_runtime


class CodexRuntimeTests(unittest.TestCase):
    def test_retains_hook_feature_and_managed_values_win(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "config.toml"
            target.write_text('[features]\nhooks = true\n', encoding="utf-8")
            for managed, expected in (
                ('model = "managed"\n', {"hooks": True}),
                ('[features]\nother_managed = true\n', {"other_managed": True, "hooks": True}),
                ('[features]\nhooks = false\n', {"hooks": False}),
            ):
                with self.subTest(managed=managed):
                    plan = plan_codex_runtime(managed, target_path=target, source_label="x", target_label="target")
                    self.assertEqual(tomllib.loads(plan.content)["features"], expected)
                    self.assertEqual("features.hooks" in plan.preserved_keys, "hooks = false" not in managed)

    def test_hook_feature_rejects_invalid_types_and_unknown_flags(self) -> None:
        for existing, error in (
            ('features = true\n', "type conflict"),
            ('[features]\nhooks = "true"\n', "type conflict"),
            ('[features.hooks]\nenabled = true\n', "type conflict"),
            ('[features]\nunknown_flag = true\n', "Unclassified existing Codex setting"),
        ):
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "config.toml"
                target.write_text(existing, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, error):
                    plan_codex_runtime('model = "managed"\n', target_path=target, source_label="x", target_label="target")

    def test_retains_hook_state_with_redacted_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "config.toml"
            target.write_text(
                'model = "old"\n[hooks.state."private-hook@example"]\n'
                'enabled = false\ntrusted_hash = "synthetic-hash"\n',
                encoding="utf-8",
            )
            plan = plan_codex_runtime('model = "managed"\n', target_path=target, source_label="x", target_label="target")
            self.assertEqual(tomllib.loads(plan.content)["hooks"]["state"]["private-hook@example"],
                             {"enabled": False, "trusted_hash": "synthetic-hash"})
            self.assertEqual(set(plan.preserved_keys), {"hooks.state.*.enabled", "hooks.state.*.trusted_hash"})
            self.assertEqual(apply_codex_runtime(plan, backup_root=root / "backup", dry_run=False), "applied")
            fresh = plan_codex_runtime('model = "managed"\n', target_path=target, source_label="x", target_label="target")
            self.assertEqual(apply_codex_runtime(fresh, backup_root=root / "backup", dry_run=True), "nochange")

    def test_managed_hook_state_wins_without_dropping_other_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "config.toml"
            target.write_text('[hooks.state.example]\nenabled = true\ntrusted_hash = "synthetic-hash"\n', encoding="utf-8")
            plan = plan_codex_runtime('[hooks.state.example]\nenabled = false\n', target_path=target, source_label="x", target_label="target")
            self.assertEqual(tomllib.loads(plan.content)["hooks"]["state"]["example"],
                             {"enabled": False, "trusted_hash": "synthetic-hash"})

    def test_hook_state_rejects_unknown_fields_and_executable_hooks(self) -> None:
        for existing in (
            '[hooks.state."private-hook@example"]\ncommand = "synthetic-secret"\n',
            '[hooks]\nSessionStart = []\n',
        ):
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "config.toml"
                target.write_text(existing, encoding="utf-8")
                with self.assertRaises(ValueError) as caught:
                    plan_codex_runtime('model = "managed"\n', target_path=target, source_label="x", target_label="target")
                self.assertIn("Unclassified existing Codex setting", str(caught.exception))
                self.assertNotIn("private-hook@example", str(caught.exception))
                self.assertNotIn("synthetic-secret", str(caught.exception))

    def test_hook_state_rejects_invalid_table_and_value_types(self) -> None:
        for existing in (
            'hooks = "not-a-table"\n',
            '[hooks]\nstate = false\n',
            '[hooks.state]\n"private-hook@example" = false\n',
            '[hooks.state."private-hook@example"]\nenabled = "false"\n',
            '[hooks.state."private-hook@example"]\ntrusted_hash = 42\n',
            '[hooks.state."private-hook@example".enabled]\nnested = true\n',
        ):
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "config.toml"
                target.write_text(existing, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "type conflict") as caught:
                    plan_codex_runtime('model = "managed"\n', target_path=target, source_label="x", target_label="target")
                self.assertNotIn("private-hook@example", str(caught.exception))

    def test_retains_allowlisted_state_and_managed_values_win(self) -> None:
        existing = "\n".join([
            'model = "old-model"', '[plugins."plug@example"]', 'enabled = true',
            '[mcp_servers.synthetic]', 'command = "tool"',
            'env = { TOKEN = "synthetic-secret" }', '[marketplaces.synthetic]',
            'source = "fixture"', '[projects."/tmp/synthetic"]',
            'trust_level = "trusted"', '[notice.model_migrations]',
            '"old-model" = "new-model"', '[tui.model_availability_nux]',
            '"gpt-6-luna" = 42', '[desktop]', 'followUpQueueMode = "queue"', '',
        ])
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "home/.codex/config.toml"
            target.parent.mkdir(parents=True)
            target.write_text(existing, encoding="utf-8")
            managed = 'model = "managed-model"\n[plugins."plug@example"]\nenabled = false\n'
            plan = plan_codex_runtime(managed, target_path=target, source_label="fixture", target_label="target")
            result = tomllib.loads(plan.content)
            self.assertEqual(result["model"], "managed-model")
            self.assertFalse(result["plugins"]["plug@example"]["enabled"])
            self.assertEqual(result["mcp_servers"]["synthetic"]["env"]["TOKEN"], "synthetic-secret")
            self.assertEqual(result["projects"]["/tmp/synthetic"]["trust_level"], "trusted")
            self.assertEqual(result["tui"]["model_availability_nux"]["gpt-6-luna"], 42)
            self.assertIn("mcp_servers.*.command", " ".join(plan.preserved_keys))

    def test_unknown_setting_and_type_conflict_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "config.toml"
            target.write_text('mystery = "value"\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unclassified existing Codex setting: mystery"):
                plan_codex_runtime('model = "managed"\n', target_path=target, source_label="x", target_label="target")
            target.write_text('[plugins.X]\nenabled = true\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "type conflict"):
                plan_codex_runtime('plugins = "not-a-table"\n', target_path=target, source_label="x", target_label="target")
            target.write_text("model = 42\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "type conflict"):
                plan_codex_runtime('model = "managed"\n', target_path=target, source_label="x", target_label="target")
            target.write_text('[projects."/tmp/synthetic"]\ntrust_level = true\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "type conflict"):
                plan_codex_runtime('model = "managed"\n', target_path=target, source_label="x", target_label="target")

    def test_invalid_existing_toml_error_does_not_include_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "config.toml"
            target.write_text('secret = "synthetic-secret"\ninvalid = [\n', encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                plan_codex_runtime('model = "managed"\n', target_path=target, source_label="x", target_label="target")
            self.assertNotIn("synthetic-secret", str(caught.exception))

    def test_dry_run_apply_nochange_and_restrictive_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "home/config.toml"
            target.parent.mkdir()
            target.write_text('model = "old"\n', encoding="utf-8")
            target.chmod(0o600)
            backup = root / "backup"
            plan = plan_codex_runtime('model = "new"\n', target_path=target, source_label="x", target_label="target")
            self.assertEqual(apply_codex_runtime(plan, backup_root=backup, dry_run=True), "would_apply")
            self.assertEqual(target.read_text(encoding="utf-8"), 'model = "old"\n')
            self.assertFalse(backup.exists())
            self.assertEqual(apply_codex_runtime(plan, backup_root=backup, dry_run=False), "applied")
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            new_plan = plan_codex_runtime('model = "new"\n', target_path=target, source_label="x", target_label="target")
            self.assertEqual(apply_codex_runtime(new_plan, backup_root=backup, dry_run=False), "nochange")
            self.assertEqual(len([path for path in backup.rglob("*") if path.is_file()]), 1)

    def test_new_managed_config_is_stable_after_first_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "config.toml"
            managed = '# managed profile\nmodel = "managed"\n'
            first_plan = plan_codex_runtime(managed, target_path=target, source_label="x", target_label="target")
            self.assertEqual(apply_codex_runtime(first_plan, backup_root=root / "backup", dry_run=False), "applied")
            second_plan = plan_codex_runtime(managed, target_path=target, source_label="x", target_label="target")
            self.assertEqual(second_plan.content, managed)
            self.assertEqual(apply_codex_runtime(second_plan, backup_root=root / "backup", dry_run=True), "nochange")
            self.assertEqual(target.read_text(encoding="utf-8"), managed)

    def test_stale_plan_and_backup_failure_preserve_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "config.toml"
            target.write_text('model = "old"\n', encoding="utf-8")
            plan = plan_codex_runtime('model = "new"\n', target_path=target, source_label="x", target_label="target")
            target.write_text('model = "changed"\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "changed after planning"):
                apply_codex_runtime(plan, backup_root=root / "backup", dry_run=False)
            fresh = plan_codex_runtime('model = "new"\n', target_path=target, source_label="x", target_label="target")
            with patch("dotfiles_installer.codex_runtime.shutil.copy2", side_effect=OSError("synthetic failure")):
                with self.assertRaises(OSError):
                    apply_codex_runtime(fresh, backup_root=root / "backup", dry_run=False)
            self.assertEqual(target.read_text(encoding="utf-8"), 'model = "changed"\n')

    def test_atomic_replace_failure_keeps_old_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "config.toml"
            target.write_text('model = "old"\n', encoding="utf-8")
            plan = plan_codex_runtime('model = "new"\n', target_path=target, source_label="x", target_label="target")
            with patch("dotfiles_installer.codex_runtime.os.replace", side_effect=OSError("synthetic failure")):
                with self.assertRaises(OSError):
                    apply_codex_runtime(plan, backup_root=root / "backup", dry_run=False)
            self.assertEqual(target.read_text(encoding="utf-8"), 'model = "old"\n')


if __name__ == "__main__":
    unittest.main()
