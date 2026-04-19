import subprocess
import unittest


class InstallCliTests(unittest.TestCase):
    def test_only_filter_limits_output(self) -> None:
        result = subprocess.run(
            ["./install", "--dry-run", "--context", "local", "--only", "vimrc"],
            cwd="/home/ryo/github/dotfiles-public",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn(".vimrc", result.stdout)
        self.assertNotIn(".gitconfig", result.stdout)


if __name__ == "__main__":
    unittest.main()
