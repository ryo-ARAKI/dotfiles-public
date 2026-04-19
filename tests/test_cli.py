import subprocess
import unittest
from pathlib import Path


class InstallCliTests(unittest.TestCase):
    def test_only_filter_limits_output(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            ["./install", "--dry-run", "--context", "local", "--only", "vimrc"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip().splitlines(), ["base: home/.vimrc -> ~/.vimrc"])


if __name__ == "__main__":
    unittest.main()
