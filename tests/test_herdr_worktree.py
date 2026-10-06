import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'bin/herdr-worktree'


class HerdrWorktreeTests(unittest.TestCase):
    def test_primary_and_linked_worktrees_use_primary_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repo with spaces'
            root.mkdir()
            def git(*args):
                return subprocess.run(['git', '-C', str(root), *args], check=True,
                                      capture_output=True, text=True)
            git('init')
            git('-c', 'user.name=Test', '-c', 'user.email=test@example.com',
                'commit', '--allow-empty', '-m', 'initial')
            linked = Path(tmp) / 'linked'
            git('worktree', 'add', '-b', 'linked', str(linked))
            fakebin = Path(tmp) / 'bin'
            fakebin.mkdir()
            fake = fakebin / 'herdr'
            fake.write_text('#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n')
            fake.chmod(0o755)
            env = dict(os.environ, PATH=str(fakebin) + os.pathsep + os.environ['PATH'])
            import json
            for cwd in (root, linked):
                result = subprocess.run([str(SCRIPT), 'feature/test', '--no-focus'],
                                        cwd=cwd, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), [
                    'worktree', 'create', '--cwd', str(root), '--branch', 'feature/test',
                    '--path', str(root / '.worktrees/feature/test'), '--no-focus'])
            for branch in ('../escape', '-bad'):
                result = subprocess.run([str(SCRIPT), branch], cwd=root, env=env,
                                        capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')
            result = subprocess.run([str(SCRIPT), 'valid', '--path', '/tmp/elsewhere'],
                                    cwd=root, env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
