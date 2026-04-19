import unittest

from dotfiles_installer.context import detect_context


class DetectContextTests(unittest.TestCase):
    def test_explicit_context_wins(self) -> None:
        self.assertEqual(detect_context("remote", {}), "remote")

    def test_ssh_environment_means_remote(self) -> None:
        self.assertEqual(detect_context(None, {"SSH_CONNECTION": "1 2 3 4"}), "remote")

    def test_ssh_tty_environment_means_remote(self) -> None:
        self.assertEqual(detect_context(None, {"SSH_TTY": "/dev/pts/0"}), "remote")

    def test_no_ssh_environment_means_local(self) -> None:
        self.assertEqual(detect_context(None, {}), "local")


if __name__ == "__main__":
    unittest.main()
