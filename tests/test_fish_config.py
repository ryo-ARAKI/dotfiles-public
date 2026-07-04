import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FishConfigTests(unittest.TestCase):
    def test_interactive_init_guards_starship_initialization(self) -> None:
        config = (ROOT / "config" / "fish" / "conf.d" / "90-interactive-init.fish").read_text(encoding="utf-8")

        self.assertIn("if command -v starship >/dev/null", config)
        self.assertLess(config.index("if command -v starship >/dev/null"), config.index("starship init fish | source"))

    def test_codex_function_injects_gpt_oss_catalog_for_ollama_120b(self) -> None:
        argv = self.run_codex_function("exec --oss --local-provider ollama -m gpt-oss:120b prompt")

        self.assertIn("-c", argv)
        self.assertIn(
            'model_catalog_json="/home/ryo/.codex/model-catalogs/gpt-oss.json"',
            argv,
        )

    def test_codex_function_does_not_duplicate_existing_model_catalog_config(self) -> None:
        argv = self.run_codex_function(
            'exec --oss --local-provider=ollama --model=gpt-oss:120b -c model_catalog_json=/tmp/catalog.json prompt'
        )

        self.assertEqual(argv.count("-c"), 1)
        self.assertIn('model_catalog_json=/tmp/catalog.json', argv)
        self.assertNotIn('model_catalog_json="/home/ryo/.codex/model-catalogs/gpt-oss.json"', argv)

    def test_codex_function_does_not_duplicate_equals_model_catalog_config(self) -> None:
        argv = self.run_codex_function(
            "exec --oss --local-provider=ollama --model=gpt-oss:120b --config=model_catalog_json=/tmp/catalog.json prompt"
        )

        self.assertNotIn("-c", argv)
        self.assertIn("--config=model_catalog_json=/tmp/catalog.json", argv)
        self.assertNotIn('model_catalog_json="/home/ryo/.codex/model-catalogs/gpt-oss.json"', argv)

    def test_codex_function_leaves_normal_invocations_unchanged(self) -> None:
        argv = self.run_codex_function("--version")

        self.assertNotIn("-c", argv)
        self.assertEqual(argv[-1], "--version")

    def test_codex_function_restores_gpt_oss_settings_for_ollama_resume_session(self) -> None:
        session_id = "019f2d8c-5a50-73b2-ab85-dacf3e186f28"
        argv = self.run_codex_function(
            f"resume {session_id}",
            session_id=session_id,
            session_text=(
                '{"type":"session_meta","payload":{"model_provider":"ollama"}}\n'
                '{"type":"turn_context","payload":{"model":"gpt-oss:120b"}}\n'
            ),
        )

        self.assertIn("resume", argv)
        self.assertIn(session_id, argv)
        self.assertIn("--profile", argv)
        self.assertIn("dgx", argv)
        self.assertIn("--oss", argv)
        self.assertIn("--local-provider", argv)
        self.assertIn("ollama", argv)
        self.assertIn("-m", argv)
        self.assertIn("gpt-oss:120b", argv)

    def test_codex_function_restores_missing_flags_for_partial_gpt_oss_resume(self) -> None:
        session_id = "019f2d8c-5a50-73b2-ab85-dacf3e186f28"
        argv = self.run_codex_function(
            f"resume {session_id} --model gpt-oss:120b",
            session_id=session_id,
            session_text=(
                '{"type":"session_meta","payload":{"model_provider":"ollama"}}\n'
                '{"type":"turn_context","payload":{"model":"gpt-oss:120b"}}\n'
            ),
        )

        self.assertIn("--model", argv)
        self.assertIn("gpt-oss:120b", argv)
        self.assertIn("--oss", argv)
        self.assertIn("--local-provider", argv)
        self.assertIn("ollama", argv)

    def test_codex_function_does_not_restore_gpt_oss_when_resume_model_is_overridden(self) -> None:
        session_id = "019f2d8c-5a50-73b2-ab85-dacf3e186f28"
        argv = self.run_codex_function(
            f"resume {session_id} --model gpt-5.5",
            session_id=session_id,
            session_text=(
                '{"type":"session_meta","payload":{"model_provider":"ollama"}}\n'
                '{"type":"turn_context","payload":{"model":"gpt-oss:120b"}}\n'
            ),
        )

        self.assertIn("--model", argv)
        self.assertIn("gpt-5.5", argv)
        self.assertNotIn("--oss", argv)
        self.assertNotIn("--local-provider", argv)
        self.assertNotIn("gpt-oss:120b", argv)

    def test_codex_function_uses_cd_for_last_resume_session_matching(self) -> None:
        session_id = "019f2d8c-5a50-73b2-ab85-dacf3e186f28"
        target_cwd = "/tmp/codex-target-cwd"
        current_cwd = str(ROOT)
        argv = self.run_codex_function(
            f"-C {target_cwd} resume --last",
            session_id=session_id,
            session_text=(
                f'{{"type":"session_meta","payload":{{"cwd":"{target_cwd}","model_provider":"ollama"}}}}\n'
                '{"type":"turn_context","payload":{"model":"gpt-oss:120b"}}\n'
            ),
            extra_session_texts=[
                (
                    f'{{"type":"session_meta","payload":{{"cwd":"{current_cwd}","model_provider":"openai"}}}}\n'
                    '{"type":"turn_context","payload":{"model":"gpt-5.5"}}\n'
                ),
            ],
        )

        self.assertIn("-C", argv)
        self.assertIn(target_cwd, argv)
        self.assertIn("--oss", argv)
        self.assertIn("--local-provider", argv)
        self.assertIn("ollama", argv)
        self.assertIn("gpt-oss:120b", argv)

    def test_codex_function_does_not_restore_last_resume_from_other_cwd(self) -> None:
        session_id = "019f2d8c-5a50-73b2-ab85-dacf3e186f28"
        argv = self.run_codex_function(
            "resume --last",
            session_id=session_id,
            session_text=(
                '{"type":"session_meta","payload":{"cwd":"/tmp/other-cwd","model_provider":"ollama"}}\n'
                '{"type":"turn_context","payload":{"model":"gpt-oss:120b"}}\n'
            ),
        )

        self.assertIn("resume", argv)
        self.assertIn("--last", argv)
        self.assertNotIn("--oss", argv)
        self.assertNotIn("--local-provider", argv)
        self.assertNotIn("gpt-oss:120b", argv)

    def test_codex_function_treats_last_resume_prompt_as_prompt(self) -> None:
        session_id = "019f2d8c-5a50-73b2-ab85-dacf3e186f28"
        current_cwd = str(ROOT)
        prompt = "continue from here"
        argv = self.run_codex_function(
            f'resume --last "{prompt}"',
            session_id=session_id,
            session_text=(
                f'{{"type":"session_meta","payload":{{"cwd":"{current_cwd}","model_provider":"ollama"}}}}\n'
                '{"type":"turn_context","payload":{"model":"gpt-oss:120b"}}\n'
            ),
        )

        self.assertIn("--last", argv)
        self.assertIn(prompt, argv)
        self.assertIn("--oss", argv)
        self.assertIn("--local-provider", argv)
        self.assertIn("ollama", argv)
        self.assertIn("gpt-oss:120b", argv)

    def test_codex_function_restores_gpt_oss_settings_for_named_resume_session(self) -> None:
        session_id = "019f2d8c-5a50-73b2-ab85-dacf3e186f28"
        session_name = "local oss session"
        argv = self.run_codex_function(
            f'resume \"{session_name}\"',
            session_id=session_id,
            session_name=session_name,
            session_text=(
                '{"type":"session_meta","payload":{"model_provider":"ollama"}}\n'
                '{"type":"turn_context","payload":{"model":"gpt-oss:120b"}}\n'
            ),
        )

        self.assertIn(session_name, argv)
        self.assertIn("--oss", argv)
        self.assertIn("--local-provider", argv)
        self.assertIn("ollama", argv)
        self.assertIn("gpt-oss:120b", argv)

    def test_codex_function_restores_date_like_named_resume_session(self) -> None:
        session_id = "019f2d8c-5a50-73b2-ab85-dacf3e186f28"
        session_name = "2026-07-04"
        argv = self.run_codex_function(
            f'resume "{session_name}"',
            session_id=session_id,
            session_name=session_name,
            session_text=(
                '{"type":"session_meta","payload":{"model_provider":"ollama"}}\n'
                '{"type":"turn_context","payload":{"model":"gpt-oss:120b"}}\n'
            ),
        )

        self.assertIn(session_name, argv)
        self.assertIn("--oss", argv)
        self.assertIn("--local-provider", argv)
        self.assertIn("ollama", argv)
        self.assertIn("gpt-oss:120b", argv)

    def test_codex_function_resolves_named_resume_before_filename_matching(self) -> None:
        session_id = "019f2d8c-5a50-73b2-ab85-dacf3e186f28"
        session_name = "2026"
        argv = self.run_codex_function(
            f'resume "{session_name}"',
            session_id=session_id,
            session_name=session_name,
            session_text=(
                '{"type":"session_meta","payload":{"model_provider":"openai"}}\n'
                '{"type":"turn_context","payload":{"model":"gpt-5.5"}}\n'
            ),
            extra_session_texts=[
                (
                    '{"type":"session_meta","payload":{"model_provider":"ollama"}}\n'
                    '{"type":"turn_context","payload":{"model":"gpt-oss:120b"}}\n'
                ),
            ],
        )

        self.assertIn(session_name, argv)
        self.assertNotIn("--oss", argv)
        self.assertNotIn("--local-provider", argv)
        self.assertNotIn("gpt-oss:120b", argv)

    def test_codex_function_ignores_noninteractive_last_resume_sessions_by_default(self) -> None:
        session_id = "019f2d8c-5a50-73b2-ab85-dacf3e186f28"
        current_cwd = str(ROOT)
        argv = self.run_codex_function(
            "resume --last",
            session_id=session_id,
            session_text=(
                f'{{"type":"session_meta","payload":{{"cwd":"{current_cwd}","source":"cli","model_provider":"openai"}}}}\n'
                '{"type":"turn_context","payload":{"model":"gpt-5.5"}}\n'
            ),
            extra_session_texts=[
                (
                    f'{{"type":"session_meta","payload":{{"cwd":"{current_cwd}","originator":"codex_exec","source":"exec","model_provider":"ollama"}}}}\n'
                    '{"type":"turn_context","payload":{"model":"gpt-oss:120b"}}\n'
                ),
            ],
        )

        self.assertIn("resume", argv)
        self.assertIn("--last", argv)
        self.assertNotIn("--oss", argv)
        self.assertNotIn("--local-provider", argv)
        self.assertNotIn("gpt-oss:120b", argv)

    def test_codex_function_does_not_restore_gpt_oss_for_non_resume_subcommands(self) -> None:
        session_id = "019f2d8c-5a50-73b2-ab85-dacf3e186f28"
        argv = self.run_codex_function(
            f"exec resume {session_id}",
            session_id=session_id,
            session_text=(
                '{"type":"session_meta","payload":{"model_provider":"ollama"}}\n'
                '{"type":"turn_context","payload":{"model":"gpt-oss:120b"}}\n'
            ),
        )

        self.assertIn("exec", argv)
        self.assertIn("resume", argv)
        self.assertIn(session_id, argv)
        self.assertNotIn("--oss", argv)
        self.assertNotIn("--local-provider", argv)
        self.assertNotIn("gpt-oss:120b", argv)

    def run_codex_function(
        self,
        codex_args: str,
        *,
        session_id: str | None = None,
        session_text: str | None = None,
        session_name: str | None = None,
        extra_session_texts: list[str] | None = None,
    ) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            home = temp_root / "home"
            bin_dir = temp_root / "bin"
            functions_dir = home / ".config" / "fish" / "functions"
            wrapper = home / ".config" / "fish" / "codex-pty-wrapper.py"
            output_path = temp_root / "argv.txt"
            codex_function = functions_dir / "codex.fish"

            functions_dir.mkdir(parents=True)
            bin_dir.mkdir()
            wrapper.parent.mkdir(parents=True, exist_ok=True)
            codex_function.write_text(
                (ROOT / "config" / "fish" / "functions" / "codex.fish").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (bin_dir / "codex").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            (bin_dir / "codex").chmod(0o755)
            wrapper.write_text(
                "#!/bin/sh\nfor arg do printf '%s\\n' \"$arg\"; done > \"$CODEX_ARGV_CAPTURE\"\n",
                encoding="utf-8",
            )
            wrapper.chmod(0o755)
            if session_id is not None and session_text is not None:
                session_dir = home / ".codex" / "sessions" / "2026" / "07" / "04"
                session_dir.mkdir(parents=True)
                session_path = session_dir / f"rollout-2026-07-04T23-33-20-{session_id}.jsonl"
                session_path.write_text(session_text, encoding="utf-8")
                os.utime(session_path, (1, 1))
                if session_name is not None:
                    (home / ".codex" / "session_index.jsonl").write_text(
                        f'{{"id":"{session_id}","thread_name":"{session_name}","updated_at":"2026-07-04T23:33:20Z"}}\n',
                        encoding="utf-8",
                    )
                for index, extra_session_text in enumerate(extra_session_texts or [], start=1):
                    extra_session_path = session_dir / f"rollout-2026-07-04T23-33-2{index}-extra-{index}.jsonl"
                    extra_session_path.write_text(extra_session_text, encoding="utf-8")
                    os.utime(extra_session_path, (index + 1, index + 1))

            env = dict(os.environ)
            env["HOME"] = str(home)
            env["PATH"] = f"{bin_dir}:{env['PATH']}"
            env["CODEX_ARGV_CAPTURE"] = str(output_path)

            result = subprocess.run(
                ["fish", "-ic", f"source {codex_function}; codex {codex_args}"],
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            return output_path.read_text(encoding="utf-8").splitlines()


if __name__ == "__main__":
    unittest.main()
