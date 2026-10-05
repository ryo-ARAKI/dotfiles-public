import os
import tempfile
import subprocess
import tomllib
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
            reviewer_profile_path = home / ".codex" / "reviewer.config.toml"
            rules_path = home / ".codex" / "rules" / "default.rules"
            self.assertTrue(config_path.exists())
            self.assertTrue(quick_profile_path.exists())
            self.assertTrue(deep_profile_path.exists())
            self.assertTrue(reviewer_profile_path.exists())
            self.assertTrue(rules_path.exists())
            public_fragment = (repo_root / "config" / "codex" / "config.public.toml").read_text(encoding="utf-8")
            private_fragment = (private_repo / "config" / "codex" / "config.private.toml").read_text(encoding="utf-8")
            private_local_fragment = (private_repo / "config" / "codex" / "config.private.local.toml").read_text(
                encoding="utf-8"
            )
            quick_profile = (repo_root / "config" / "codex" / "quick.config.toml").read_text(encoding="utf-8")
            deep_profile = (repo_root / "config" / "codex" / "deep.config.toml").read_text(encoding="utf-8")
            reviewer_profile = (repo_root / "config" / "codex" / "reviewer.config.toml").read_text(encoding="utf-8")
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
            self.assertEqual(reviewer_profile_path.read_text(encoding="utf-8"), reviewer_profile)
            generated_config = tomllib.loads(config_text)
            self.assertEqual(generated_config["agents"]["reviewer"]["config_file"], "reviewer.config.toml")
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

    def test_only_quick_updates_only_that_profile_and_retains_its_runtime_state(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            codex_home = home / ".codex"
            codex_home.mkdir(parents=True)
            profile = codex_home / "quick.config.toml"
            profile.write_text(
                'model = "old-model"\n[notice.model_migrations]\n"old-model" = "new-model"\n',
                encoding="utf-8",
            )
            profile.chmod(0o600)
            env = dict(os.environ)
            env["HOME"] = str(home)
            result = subprocess.run(
                ["./install", "--yes", "--context", "local", "--only", "quick.config.toml"],
                cwd=repo_root, env=env, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(profile.stat().st_mode & 0o777, 0o600)
            generated = tomllib.loads(profile.read_text(encoding="utf-8"))
            self.assertEqual(generated["model"], "gpt-6-luna")
            self.assertEqual(generated["notice"]["model_migrations"]["old-model"], "new-model")
            self.assertIn("applied: base: config/codex/quick.config.toml", result.stdout)
            self.assertNotIn("config.toml -> ~/.codex/config.toml", result.stdout)
            backups = list((home / ".dotfiles-backup").rglob("quick.config.toml"))
            self.assertEqual(len(backups), 1)
            rerun = subprocess.run(
                ["./install", "--yes", "--context", "local", "--only", "quick.config.toml"],
                cwd=repo_root, env=env, capture_output=True, text=True, check=False,
            )
            self.assertEqual(rerun.returncode, 0, msg=rerun.stderr)
            self.assertIn("nochange: base: config/codex/quick.config.toml", rerun.stdout)
            self.assertEqual(len(list((home / ".dotfiles-backup").rglob("quick.config.toml"))), 1)

    def test_codex_profile_preflight_stops_before_generic_writes(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            codex_home = home / ".codex"
            codex_home.mkdir(parents=True)
            (home / ".bashrc").write_text("keep this\n", encoding="utf-8")
            (codex_home / "quick.config.toml").write_text('unknown_setting = "synthetic-secret"\n', encoding="utf-8")
            env = dict(os.environ)
            env["HOME"] = str(home)
            result = subprocess.run(
                ["./install", "--yes", "--context", "local"],
                cwd=repo_root, env=env, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unclassified existing Codex setting: unknown_setting", result.stderr)
            self.assertNotIn("synthetic-secret", result.stderr)
            self.assertEqual((home / ".bashrc").read_text(encoding="utf-8"), "keep this\n")

    def test_dry_run_redacts_retained_profile_values_and_does_not_write(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            codex_home = home / ".codex"
            codex_home.mkdir(parents=True)
            profile = codex_home / "quick.config.toml"
            before = 'model = "old-model"\n[mcp_servers.synthetic]\ncommand = "fixture"\nenv = { TOKEN = "synthetic-secret" }\n'
            profile.write_text(before, encoding="utf-8")
            env = dict(os.environ)
            env["HOME"] = str(home)
            result = subprocess.run(
                ["./install", "--dry-run", "--context", "local", "--only", "quick.config.toml"],
                cwd=repo_root, env=env, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertNotIn("synthetic-secret", result.stdout + result.stderr)
            self.assertIn("existing settings retained: mcp_servers.*.command, mcp_servers.*.env.TOKEN", result.stdout)
            self.assertEqual(profile.read_text(encoding="utf-8"), before)
            self.assertFalse((home / ".dotfiles-backup").exists())

    def test_local_remote_profile_overlay_retention_and_reapply(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            private = root / "private"
            hosts = root / "hosts"
            for layer in (private, hosts):
                (layer / "manifest").mkdir(parents=True)
                (layer / "config" / "codex").mkdir(parents=True)
            (private / "manifest/private.tsv").write_text(
                "config/codex/quick-private.config.toml\t~/.codex/quick.config.toml\t0644\talways\n"
                "config/codex/deep-private.config.toml\t~/.codex/deep.config.toml\t0644\tlocal\n",
                encoding="utf-8",
            )
            (hosts / "manifest/synthetic-host.tsv").write_text(
                "config/codex/quick-host.config.toml\t~/.codex/quick.config.toml\t0644\talways\n",
                encoding="utf-8",
            )
            (private / "config/codex/config.private.toml").write_text(
                '[projects."/tmp/synthetic-private"]\ntrust_level = "trusted"\n', encoding="utf-8"
            )
            (private / "config/codex/config.private.local.toml").write_text(
                '[mcp_servers.local-fragment]\ncommand = "local fixture"\n', encoding="utf-8"
            )
            profile = 'model = "gpt-6-luna"\nmodel_reasoning_effort = "medium"\nplan_mode_reasoning_effort = "medium"\ndeveloper_instructions = "private selected"\n'
            (private / "config/codex/quick-private.config.toml").write_text(profile, encoding="utf-8")
            (hosts / "config/codex/quick-host.config.toml").write_text(profile.replace("private selected", "host selected"), encoding="utf-8")
            (private / "config/codex/deep-private.config.toml").write_text(
                'model = "gpt-6-astra"\nmodel_reasoning_effort = "high"\nplan_mode_reasoning_effort = "xhigh"\n'
                '[projects."/tmp/synthetic-private-trust"]\ntrust_level = "trusted"\n', encoding="utf-8"
            )
            homes = {}
            for context in ("local", "remote"):
                home = root / context
                codex_home = home / ".codex"
                codex_home.mkdir(parents=True)
                homes[context] = home
                (codex_home / "config.toml").write_text(
                    f'[mcp_servers.{context}-fixture]\ncommand = "fixture"\nenv = {{ TOKEN = "{context}-synthetic-secret" }}\n',
                    encoding="utf-8",
                )
                (codex_home / "quick.config.toml").write_text(
                    'model = "old-model"\n[notice.model_migrations]\n"old-model" = "new-model"\n',
                    encoding="utf-8",
                )
                (codex_home / "deep.config.toml").write_text(
                    'model = "old-model"\n[projects."/tmp/synthetic-target-trust"]\ntrust_level = "trusted"\n',
                    encoding="utf-8",
                )

            def invoke(context: str, *extra: str) -> subprocess.CompletedProcess[str]:
                env = dict(os.environ, HOME=str(homes[context]))
                command = ["./install", "--context", context, "--private", str(private)]
                if context == "remote":
                    command.extend(["--hosts", str(hosts), "--host-name", "synthetic-host"])
                return subprocess.run(command + list(extra), cwd=repo_root, env=env, capture_output=True, text=True, check=False)

            dry = invoke("local", "--dry-run", "--only", "quick.config.toml")
            self.assertEqual(dry.returncode, 0, msg=dry.stderr)
            self.assertNotIn("local-synthetic-secret", dry.stdout + dry.stderr)
            local_config_before = (homes["local"] / ".codex/config.toml").read_text(encoding="utf-8")
            self.assertEqual(invoke("local", "--yes").returncode, 0)
            local = tomllib.loads((homes["local"] / ".codex/config.toml").read_text(encoding="utf-8"))
            self.assertIn("local-fixture", local["mcp_servers"])
            self.assertIn("local-fragment", local["mcp_servers"])
            self.assertEqual(local["mcp_servers"]["local-fixture"]["env"]["TOKEN"], "local-synthetic-secret")
            local_profile = tomllib.loads((homes["local"] / ".codex/quick.config.toml").read_text(encoding="utf-8"))
            self.assertEqual(local_profile["developer_instructions"], "private selected")
            self.assertEqual(local_profile["notice"]["model_migrations"]["old-model"], "new-model")
            local_deep = tomllib.loads((homes["local"] / ".codex/deep.config.toml").read_text(encoding="utf-8"))
            self.assertIn("/tmp/synthetic-private-trust", local_deep["projects"])
            self.assertIn("/tmp/synthetic-target-trust", local_deep["projects"])
            backup_root = homes["local"] / ".dotfiles-backup"
            codex_backup_count = sum(1 for path in backup_root.rglob("*") if path.is_file() and path.name in {"config.toml", "quick.config.toml"})
            rerun = invoke("local", "--yes")
            self.assertEqual(rerun.returncode, 0, msg=rerun.stderr)
            self.assertIn("nochange: codex:", rerun.stdout)
            self.assertEqual(
                sum(1 for path in backup_root.rglob("*") if path.is_file() and path.name in {"config.toml", "quick.config.toml"}),
                codex_backup_count,
            )
            remote_dry = invoke("remote", "--dry-run", "--only", "quick.config.toml")
            self.assertEqual(remote_dry.returncode, 0, msg=remote_dry.stderr)
            self.assertNotIn("remote-synthetic-secret", remote_dry.stdout + remote_dry.stderr)
            self.assertEqual(invoke("remote", "--yes").returncode, 0)
            remote = tomllib.loads((homes["remote"] / ".codex/config.toml").read_text(encoding="utf-8"))
            self.assertIn("remote-fixture", remote["mcp_servers"])
            self.assertNotIn("local-fragment", remote["mcp_servers"])
            remote_profile = tomllib.loads((homes["remote"] / ".codex/quick.config.toml").read_text(encoding="utf-8"))
            self.assertEqual(remote_profile["developer_instructions"], "host selected")
            self.assertEqual(remote_profile["notice"]["model_migrations"]["old-model"], "new-model")
            remote_deep = tomllib.loads((homes["remote"] / ".codex/deep.config.toml").read_text(encoding="utf-8"))
            self.assertNotIn("/tmp/synthetic-private-trust", remote_deep.get("projects", {}))
            self.assertIn("/tmp/synthetic-target-trust", remote_deep["projects"])
            remote_backup_root = homes["remote"] / ".dotfiles-backup"
            remote_codex_backup_count = sum(
                1 for path in remote_backup_root.rglob("*")
                if path.is_file() and path.name in {"config.toml", "quick.config.toml", "deep.config.toml"}
            )
            remote_rerun = invoke("remote", "--yes")
            self.assertEqual(remote_rerun.returncode, 0, msg=remote_rerun.stderr)
            self.assertIn("nochange: host: config/codex/quick-host.config.toml", remote_rerun.stdout)
            self.assertEqual(
                sum(
                    1 for path in remote_backup_root.rglob("*")
                    if path.is_file() and path.name in {"config.toml", "quick.config.toml", "deep.config.toml"}
                ),
                remote_codex_backup_count,
            )
            self.assertNotEqual((homes["local"] / ".codex/config.toml").read_text(encoding="utf-8"), local_config_before)

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

    @unittest.skipUnless(
        os.environ.get("DOTFILES_PRIVATE_ROOT") and os.environ.get("DOTFILES_HOSTS_ROOT"),
        "requires DOTFILES_PRIVATE_ROOT and DOTFILES_HOSTS_ROOT",
    )
    def test_dgx_ollama_overlay_selection_with_real_companion_roots(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        private_root = Path(os.environ["DOTFILES_PRIVATE_ROOT"]).resolve()
        hosts_root = Path(os.environ["DOTFILES_HOSTS_ROOT"]).resolve()

        def run_dry(context: str, only: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [
                    "./install",
                    "--dry-run",
                    "--context",
                    context,
                    "--private",
                    str(private_root),
                    "--hosts",
                    str(hosts_root),
                    "--host-name",
                    "dgx",
                    "--only",
                    only,
                ],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

        local_launcher = run_dry("local", "95-codex-dgx.fish")
        self.assertEqual(local_launcher.returncode, 0, msg=local_launcher.stderr)
        self.assertRegex(
            local_launcher.stdout,
            r"(?m)^(?:would apply|nochange): private: config/fish/conf\.d/95-codex-dgx\.fish -> ~/\.config/fish/conf\.d/95-codex-dgx\.fish$",
        )
        self.assertNotIn(": host:", local_launcher.stdout)

        remote_launcher = run_dry("remote", "95-codex-dgx.fish")
        self.assertEqual(remote_launcher.returncode, 0, msg=remote_launcher.stderr)
        self.assertRegex(
            remote_launcher.stdout,
            r"(?m)^(?:would apply|nochange): host: config/fish/conf\.d/95-codex-dgx\.fish -> ~/\.config/fish/conf\.d/95-codex-dgx\.fish$",
        )
        self.assertNotIn(": private:", remote_launcher.stdout)

        remote_hook = run_dry("remote", "codex-dgx-refresh")
        self.assertEqual(remote_hook.returncode, 0, msg=remote_hook.stderr)
        self.assertNotIn("codex-dgx-refresh", remote_hook.stdout)

        for legacy_path in (
            "gptoss.config.toml",
            "dgx.config.toml",
            "model-catalogs/gpt-oss.json",
        ):
            with self.subTest(legacy_path=legacy_path):
                legacy = run_dry("local", legacy_path)
                self.assertEqual(legacy.returncode, 0, msg=legacy.stderr)
                self.assertEqual(
                    legacy.stdout.strip(),
                    "Dry run summary: applied=0 skipped=0 nochange=0 overridden=0",
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
