import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CodexDgxLauncherTests(unittest.TestCase):
    def test_local_launcher_is_a_bare_visible_model_abbreviation(self) -> None:
        launcher = ROOT / "config" / "fish" / "conf.d" / "95-codex-dgx.fish"

        result = subprocess.run(
            [
                "fish",
                "--no-config",
                "-ic",
                f'source "{launcher}"; abbr --show | string match -- "*codex-dgx*"',
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "abbr -a -- codex-dgx 'codex --oss --local-provider ollama -m gpt-oss:120b'",
        )


if __name__ == "__main__":
    unittest.main()
