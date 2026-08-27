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

    def test_codex_function_uses_ollama_launch_profile_for_ollama_120b(self) -> None:
        argv = self.run_codex_function("exec --oss --local-provider ollama -m gpt-oss:120b -C .")

        self.assertIn("--profile", argv)
        self.assertIn("ollama-launch", argv)
        self.assertEqual(
            argv[1:-2],
            ["exec", "--oss", "--local-provider", "ollama", "-m", "gpt-oss:120b", "-C", "."],
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

    def test_codex_function_preserves_openai_model_and_profile_arguments(self) -> None:
        argv = self.run_codex_function("exec --profile deep -m gpt-5.4 prompt")

        self.assertEqual(argv[1:], ["exec", "--profile", "deep", "-m", "gpt-5.4", "prompt"])

    def run_codex_function(self, codex_args: str) -> list[str]:
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
            (home / ".codex").mkdir()
            (home / ".codex" / "ollama-launch.config.toml").write_text("model = \"gpt-oss:120b\"\n", encoding="utf-8")
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
