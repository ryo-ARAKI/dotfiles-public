import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = "/usr/bin:/bin"


class NvmPathTests(unittest.TestCase):
    def run_shell(self, shell, home, command='printf "%s" "$PATH"', *,
                  path=BASE_PATH, reload=False):
        source = ROOT / ("home/.bashrc_remote" if shell == "bash" else
                         "config/fish/conf.d/90-interactive-init.fish")
        command = f'source "{source}" || exit; ' * (2 if reload else 1) + command
        # Fish functions must not count as an installed Codex executable.
        if shell == "fish":
            command = 'function codex; end; ' + command
        options = ["--noprofile", "--norc"] if shell == "bash" else ["--no-config"]
        result = subprocess.run([shell, *options, "-c", command],
                                env=dict(os.environ, HOME=str(home), PATH=path),
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def add_version(self, home, version, executables=("node", "codex")):
        bin_dir = home / ".nvm/versions/node" / version / "bin"
        bin_dir.mkdir(parents=True)
        for name in executables:
            executable = bin_dir / name
            executable.write_text("#!/bin/sh\nexit 0\n")
            executable.chmod(0o755)
        return bin_dir

    def test_discovers_latest_complete_version_and_reloads_without_duplicates(self):
        for shell in ("bash", "fish"):
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp)
                self.add_version(home, "v9.9.0")
                selected = self.add_version(home, "v24.12.0")
                self.add_version(home, "v25.0.0", ("node",))
                self.add_version(home, "v26.0.0", ("codex",))
                output = self.run_shell(
                    shell, home, 'command -v codex; command -v node; printf "%s" "$PATH"',
                    reload=True,
                )
                self.assertEqual(output.splitlines(), [str(selected / "codex"),
                                 str(selected / "node"), f"{selected}:{BASE_PATH}"])

    def test_no_nvm_leaves_path_unchanged(self):
        for shell in ("bash", "fish"):
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as tmp:
                self.assertEqual(self.run_shell(shell, Path(tmp)), BASE_PATH)

    def test_existing_codex_takes_priority(self):
        for shell in ("bash", "fish"):
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp)
                existing = self.add_version(home, "v20.19.3")
                self.add_version(home, "v24.12.0")
                path = f"{existing}:{BASE_PATH}"
                self.assertEqual(self.run_shell(shell, home, path=path), path)
