import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dotfiles_installer.plugin_cache import refresh_workflows_cache


class PluginCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        (self.home / '.codex').mkdir()
        (self.home / '.codex/config.toml').write_text(
            '[plugins."ryo-workflows@ryo-private"]\nenabled = true\n')
        market = self.home / '.agents/plugins/marketplace.json'
        market.parent.mkdir(parents=True)
        market.write_text(json.dumps({'name': 'ryo-private', 'plugins': [{
            'name': 'ryo-workflows',
            'source': {'source': 'local', 'path': './plugins/ryo-workflows'},
        }]}))
        self.source = self.home / 'plugins/ryo-workflows'
        (self.source / 'skills/example').mkdir(parents=True)
        (self.source / 'skills/example/SKILL.md').write_text('new skill')
        self.cache = self.home / '.codex/plugins/cache/ryo-private/ryo-workflows/v1'

    def install(self, *args, **kwargs):
        shutil.copytree(self.source, self.cache, dirs_exist_ok=True)
        return subprocess.CompletedProcess(args[0], 0, json.dumps({
            'pluginId': 'ryo-workflows@ryo-private', 'installedPath': str(self.cache),
        }), '')

    @patch('dotfiles_installer.plugin_cache.subprocess.run')
    def test_refresh_replaces_stale_content_and_checks_installed_files(self, run):
        self.cache.mkdir(parents=True)
        run.side_effect = self.install
        result = refresh_workflows_cache(self.home, dry_run=False)
        self.assertIn('verified', result)
        self.assertEqual(run.call_args.kwargs['env']['CODEX_HOME'], str(self.home / '.codex'))
        self.assertEqual((self.cache / 'skills/example/SKILL.md').read_text(), 'new skill')
        self.assertEqual(run.call_args.args[0],
                         ['codex', 'plugin', 'add', 'ryo-workflows@ryo-private', '--json'])

    @patch('dotfiles_installer.plugin_cache.subprocess.run')
    def test_dry_run_and_disabled_or_unregistered_plugin_do_not_install(self, run):
        self.assertIn('would refresh', refresh_workflows_cache(self.home, dry_run=True))
        (self.home / '.codex/config.toml').write_text(
            '[plugins."ryo-workflows@ryo-private"]\nenabled = false\n')
        self.assertIn('skipped', refresh_workflows_cache(self.home, dry_run=False))
        (self.home / '.codex/config.toml').write_text('')
        (self.home / '.agents/plugins/marketplace.json').unlink()
        self.assertIn('skipped', refresh_workflows_cache(self.home, dry_run=False))
        run.assert_not_called()

    @patch('dotfiles_installer.plugin_cache.subprocess.run')
    def test_stale_or_extra_cache_file_is_reported(self, run):
        for error in ('stale', 'extra'):
            with self.subTest(error=error):
                def broken(*args, **kwargs):
                    result = self.install(*args, **kwargs)
                    if error == 'stale':
                        (self.cache / 'skills/example/SKILL.md').write_text('old')
                    else:
                        (self.cache / 'skills/retired').mkdir(parents=True, exist_ok=True)
                        (self.cache / 'skills/retired/SKILL.md').write_text('retired')
                    return result
                run.side_effect = broken
                with self.assertRaisesRegex(ValueError, 'cache differs'):
                    refresh_workflows_cache(self.home, dry_run=False)

    @patch('dotfiles_installer.plugin_cache.subprocess.run')
    def test_failed_command_is_reported(self, run):
        run.side_effect = subprocess.CalledProcessError(1, ['codex'], stderr='install failed')
        with self.assertRaises(subprocess.CalledProcessError):
            refresh_workflows_cache(self.home, dry_run=False)


class PluginCacheCliTests(unittest.TestCase):
    def test_help_works_without_tomllib(self):
        import sys
        repo = Path(__file__).resolve().parents[1]
        result = subprocess.run([
            sys.executable, "-c",
            "import runpy, sys; sys.modules['tomllib'] = None; "
            "sys.argv = ['install', '--help']; runpy.run_path('install', run_name='__main__')",
        ], cwd=repo, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--dry-run', result.stdout)

    setUp = PluginCacheTests.setUp

    def test_cli_refresh_scope_dry_run_and_failure(self):
        import os
        import sys

        repo = Path(__file__).resolve().parents[1]
        binary = self.home / 'bin/codex'
        binary.parent.mkdir()
        binary.write_text(f'#!{sys.executable}\n' + '''import json, os, shutil, sys
from pathlib import Path
home = Path.home()
with (home / 'calls').open('a') as stream:
    stream.write(json.dumps(sys.argv[1:]) + '\\n')
if (home / 'fail').exists():
    sys.exit(7)
source = home / 'plugins/ryo-workflows'
cache = home / '.codex/plugins/cache/ryo-private/ryo-workflows/v1'
shutil.copytree(source, cache, dirs_exist_ok=True)
print(json.dumps({'pluginId': 'ryo-workflows@ryo-private', 'installedPath': str(cache)}))
''')
        binary.chmod(0o755)
        env = dict(os.environ, HOME=str(self.home), PATH=str(binary.parent) + os.pathsep + os.environ['PATH'])

        def install(*args):
            return subprocess.run([sys.executable, str(repo / 'install'), '--yes', *args],
                                  cwd=repo, env=env, capture_output=True, text=True)

        result = install('--context', 'local', '--only', 'plugins/ryo-workflows/')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('plugin cache verified', result.stdout)
        calls = (self.home / 'calls').read_text()
        for args in (
            ('--context', 'local', '--only', 'plugins/ryo-workflows/', '--dry-run'),
            ('--context', 'remote', '--only', 'plugins/ryo-workflows/'),
            ('--context', 'local', '--only', 'rules/default.rules'),
        ):
            with self.subTest(args=args):
                result = install(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((self.home / 'calls').read_text(), calls)
        (self.home / 'fail').touch()
        result = install('--context', 'local', '--only', 'plugins/ryo-workflows/')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Plugin cache refresh failed', result.stderr)
        self.assertTrue((self.source / 'skills/extrip-to-ics/SKILL.md').is_file())


if __name__ == '__main__':
    unittest.main()
