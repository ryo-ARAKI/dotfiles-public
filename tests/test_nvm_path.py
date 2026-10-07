import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NvmPathTests(unittest.TestCase):
    def run_shell(self, shell, home):
        source = ROOT / ("home/.bashrc_remote" if shell == "bash" else
                         "config/fish/conf.d/90-interactive-init.fish")
        # Fish functions must not count as an installed Codex executable.
        command = f'source "{source}"; command -v codex; command -v node'
        if shell == "fish":
            command = 'function codex; end; ' + command
        env = dict(os.environ, HOME=str(home), PATH="/usr/bin:/bin")
        return subprocess.run([shell, "--noprofile", "--norc", "-c", command]
                              if shell == "bash" else [shell, "--no-config", "-c", command],
                              env=env, text=True, capture_output=True)

    def add_version(self, home, version, codex=True):
        bin_dir = home / ".nvm/versions/node" / version / "bin"
        bin_dir.mkdir(parents=True)
        for name in (["node", "codex"] if codex else ["node"]):
            executable = bin_dir / name
            executable.write_text("#!/bin/sh\nexit 0\n")
            executable.chmod(0o755)
        return bin_dir

    def test_discovers_latest_version_with_node_and_codex(self):
        for shell in ("bash", "fish"):
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp)
                self.add_version(home, "v9.9.0")
                self.add_version(home, "v20.19.3")
                selected = self.add_version(home, "v24.12.0")
                self.add_version(home, "v25.0.0", codex=False)
                result = self.run_shell(shell, home)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.splitlines(),
                                 [str(selected / "codex"), str(selected / "node")])

    def test_no_nvm_leaves_path_unchanged(self):
        for shell in ("bash", "fish"):
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as tmp:
                source = ROOT / ("home/.bashrc_remote" if shell == "bash" else
                                 "config/fish/conf.d/90-interactive-init.fish")
                result = subprocess.run([shell, "--norc" if shell == "bash" else "--no-config", "-c", f'source "{source}"; printf "%s" "$PATH"'],
                                        env=dict(os.environ, HOME=tmp, PATH="/usr/bin:/bin"),
                                        text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "/usr/bin:/bin")

    def test_existing_codex_takes_priority_and_repeated_source_is_idempotent(self):
        for shell in ("bash", "fish"):
            with self.subTest(shell=shell), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp)
                existing = self.add_version(home, "v20.19.3")
                self.add_version(home, "v24.12.0")
                source = ROOT / ("home/.bashrc_remote" if shell == "bash" else
                                 "config/fish/conf.d/90-interactive-init.fish")
                path = f"{existing}:/usr/bin:/bin"
                result = subprocess.run([shell, "--norc" if shell == "bash" else "--no-config", "-c", f'source "{source}"; source "{source}"; printf "%s" "$PATH"'],
                                        env=dict(os.environ, HOME=tmp, PATH=path),
                                        text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, path)
