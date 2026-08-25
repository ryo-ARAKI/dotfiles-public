import os
import tempfile
import subprocess
import unittest
from pathlib import Path


class InstallCliTests(unittest.TestCase):
    def test_install_generates_codex_config_from_public_and_private_fragments(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            private_repo = temp_root / "private"
            home = temp_root / "home"
            private_repo.mkdir()
            (private_repo / "manifest").mkdir()
            (private_repo / "config" / "codex").mkdir(parents=True)
            home.mkdir()

            (private_repo / "manifest" / "private.tsv").write_text("", encoding="utf-8")
            (private_repo / "config" / "codex" / "config.private.toml").write_text(
                '\n[projects."/tmp/private-project"]\ntrust_level = "trusted"\n',
                encoding="utf-8",
            )
            (private_repo / "config" / "codex" / "config.private.local.toml").write_text(
                '\n[plugins."ryo-workflows@ryo-private"]\nenabled = true\n',
                encoding="utf-8",
            )

            env = dict(os.environ)
            env["HOME"] = str(home)
            result = subprocess.run(
                ["./install", "--yes", "--context", "local", "--private", str(private_repo)],
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            config_path = home / ".codex" / "config.toml"
            quick_profile_path = home / ".codex" / "quick.config.toml"
            deep_profile_path = home / ".codex" / "deep.config.toml"
            rules_path = home / ".codex" / "rules" / "default.rules"
            self.assertTrue(config_path.exists())
            self.assertTrue(quick_profile_path.exists())
            self.assertTrue(deep_profile_path.exists())
            self.assertTrue(rules_path.exists())
            public_fragment = (repo_root / "config" / "codex" / "config.public.toml").read_text(encoding="utf-8")
            private_fragment = (private_repo / "config" / "codex" / "config.private.toml").read_text(encoding="utf-8")
            private_local_fragment = (private_repo / "config" / "codex" / "config.private.local.toml").read_text(
                encoding="utf-8"
            )
            quick_profile = (repo_root / "config" / "codex" / "quick.config.toml").read_text(encoding="utf-8")
            deep_profile = (repo_root / "config" / "codex" / "deep.config.toml").read_text(encoding="utf-8")
            expected_rules = (repo_root / "config" / "codex" / "rules" / "default.rules").read_text(encoding="utf-8")
            config_text = config_path.read_text(encoding="utf-8")
            self.assertEqual(
                config_text,
                f"{public_fragment}\n\n{private_fragment}\n\n{private_local_fragment}",
            )
            self.assertNotIn("[profiles.", config_text)
            self.assertNotIn("profile = \"", config_text)
            self.assertEqual(quick_profile_path.read_text(encoding="utf-8"), quick_profile)
            self.assertEqual(deep_profile_path.read_text(encoding="utf-8"), deep_profile)
            self.assertEqual(rules_path.read_text(encoding="utf-8"), expected_rules)

    def test_remote_install_excludes_private_local_codex_fragment(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            private_repo = temp_root / "private"
            home = temp_root / "home"
            private_repo.mkdir()
            (private_repo / "manifest").mkdir()
            (private_repo / "config" / "codex").mkdir(parents=True)
            home.mkdir()

            (private_repo / "manifest" / "private.tsv").write_text("", encoding="utf-8")
            (private_repo / "config" / "codex" / "config.private.toml").write_text(
                '\n[projects."/tmp/private-project"]\ntrust_level = "trusted"\n',
                encoding="utf-8",
            )
            (private_repo / "config" / "codex" / "config.private.local.toml").write_text(
                '\n[plugins."ryo-workflows@ryo-private"]\nenabled = true\n',
                encoding="utf-8",
            )

            env = dict(os.environ)
            env["HOME"] = str(home)
            result = subprocess.run(
                ["./install", "--yes", "--context", "remote", "--private", str(private_repo)],
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            config_text = (home / ".codex" / "config.toml").read_text(encoding="utf-8")
            self.assertIn('[projects."/tmp/private-project"]', config_text)
            self.assertNotIn("ryo-workflows@ryo-private", config_text)

    def test_install_generates_codex_agents_from_common_and_local_fragments(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            private_repo = temp_root / "private"
            home = temp_root / "home"
            private_repo.mkdir()
            (private_repo / "manifest").mkdir()
            (private_repo / "config" / "codex").mkdir(parents=True)
            home.mkdir()

            (private_repo / "manifest" / "private.tsv").write_text("", encoding="utf-8")
            (private_repo / "config" / "codex" / "config.private.toml").write_text("", encoding="utf-8")
            (private_repo / "config" / "codex" / "AGENTS.common.md").write_text("# Common\n", encoding="utf-8")
            (private_repo / "config" / "codex" / "AGENTS.local.extra.md").write_text(
                "## Local\n",
                encoding="utf-8",
            )

            env = dict(os.environ)
            env["HOME"] = str(home)
            result = subprocess.run(
                ["./install", "--yes", "--context", "local", "--private", str(private_repo), "--only", "AGENTS.md"],
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual((home / ".codex" / "AGENTS.md").read_text(encoding="utf-8"), "# Common\n\n\n## Local\n")
            self.assertIn(
                "applied: codex-agents: config/codex/AGENTS.common.md + config/codex/AGENTS.local.extra.md -> ~/.codex/AGENTS.md",
                result.stdout,
            )

    def test_dry_run_reports_codex_config_generation_without_writing(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            home.mkdir()

            env = dict(os.environ)
            env["HOME"] = str(home)
            result = subprocess.run(
                ["./install", "--dry-run", "--context", "local"],
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("would apply: codex: config/codex/config.public.toml -> ~/.codex/config.toml", result.stdout)
            self.assertIn(
                "would apply: base: config/codex/quick.config.toml -> ~/.codex/quick.config.toml",
                result.stdout,
            )
            self.assertIn(
                "would apply: base: config/codex/deep.config.toml -> ~/.codex/deep.config.toml",
                result.stdout,
            )
            self.assertFalse((home / ".codex" / "config.toml").exists())
            self.assertFalse((home / ".codex" / "quick.config.toml").exists())
            self.assertFalse((home / ".codex" / "deep.config.toml").exists())

    def test_only_filter_limits_output(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ)
            env["HOME"] = tmp
            result = subprocess.run(
                ["./install", "--dry-run", "--context", "local", "--only", "vimrc"],
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.strip().splitlines(),
            ["would apply: base: home/.vimrc -> ~/.vimrc", "Dry run summary: applied=0 skipped=0 nochange=0 overridden=0"],
        )

    def test_dry_run_reports_overridden_entries(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            private_repo = temp_root / "private"
            home = temp_root / "home"
            private_repo.mkdir()
            (private_repo / "manifest").mkdir()
            (private_repo / "home").mkdir()
            home.mkdir()

            (private_repo / "manifest" / "private.tsv").write_text(
                "home/.vimrc_private\t~/.vimrc\t0644\talways\n",
                encoding="utf-8",
            )
            (private_repo / "home" / ".vimrc_private").write_text("private\n", encoding="utf-8")

            env = dict(os.environ)
            env["HOME"] = str(home)
            result = subprocess.run(
                [
                    "./install",
                    "--dry-run",
                    "--context",
                    "local",
                    "--private",
                    str(private_repo),
                    "--only",
                    "vimrc",
                ],
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("would apply: private: home/.vimrc_private -> ~/.vimrc", result.stdout)
            self.assertIn("overridden: base: home/.vimrc -> ~/.vimrc", result.stdout)
            self.assertIn("Dry run summary: applied=0 skipped=0 nochange=0 overridden=1", result.stdout)

    def test_host_name_requires_hosts_option(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            ["./install", "--dry-run", "--host-name", "h200"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--host-name requires --hosts", result.stderr)

    def test_hosts_option_fails_when_host_manifest_is_missing(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            hosts_repo = temp_root / "hosts"
            home = temp_root / "home"
            hosts_repo.mkdir()
            (hosts_repo / "manifest").mkdir()
            home.mkdir()

            env = dict(os.environ)
            env["HOME"] = str(home)
            result = subprocess.run(
                [
                    "./install",
                    "--dry-run",
                    "--hosts",
                    str(hosts_repo),
                    "--host-name",
                    "h200",
                ],
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Host manifest not found", result.stderr)


    def test_dry_run_supports_binary_manifest_entries(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            private_repo = temp_root / "private"
            home = temp_root / "home"
            private_repo.mkdir()
            (private_repo / "manifest").mkdir()
            (private_repo / "config").mkdir()
            home.mkdir()

            (private_repo / "manifest" / "private.tsv").write_text(
                "config/icon.png\t~/.config/example/icon.png\t0644\tlocal\n",
                encoding="utf-8",
            )
            (private_repo / "config" / "icon.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\xff")

            env = dict(os.environ)
            env["HOME"] = str(home)
            result = subprocess.run(
                ["./install", "--dry-run", "--context", "local", "--private", str(private_repo), "--only", "icon.png"],
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("would apply: private: config/icon.png -> ~/.config/example/icon.png", result.stdout)

if __name__ == "__main__":
    unittest.main()
