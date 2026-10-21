"""Publication failure regressions independent of workflow audit tools."""
import errno
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'config/codex/plugins/ryo-workflows/skills/extrip-to-ics/scripts/build_ics.py'
spec = importlib.util.spec_from_file_location('correction_ics', SCRIPT)
ics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ics)


def event(group):
    return dict(id=group, group=group, summary='new-' + group, description='synthetic',
                source='synthetic.md', map_query='Tokyo station', all_day=False,
                start='2026-12-31T23:50:00+09:00', end='2027-01-01T01:10:00+09:00')


class PublicationCorrectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='stage3-cr-ics-', dir='/tmp')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.events = [event('a'), event('b')]
        self.out = self.root / 'output'
        self.out.mkdir()
        for name in ('a.ics', 'b.ics', 'trips.ics'):
            (self.out / name).write_bytes(b'old-' + name.encode())

    def precheck_failure(self, checker):
        original = getattr(ics, checker)
        publish = ics._publish_one
        published = []
        def record(stage, final, overwrite):
            publish(stage, final, overwrite)
            published.append(final.name)
        def fail(path, *args):
            if published == ['a.ics'] and (checker == '_check_output_directory' or path.name == 'b.ics'):
                raise OSError(errno.EIO, 'pre-publication check')
            return original(path, *args)
        return patch.object(ics, checker, fail), patch.object(ics, '_publish_one', record), published

    def test_cr003_path_and_target_failures_before_invocation_are_not_uncertain(self):
        for checker in ('_check_target', '_check_output_directory'):
            with self.subTest(checker=checker):
                check, publish, calls = self.precheck_failure(checker)
                with check, publish, self.assertRaises(ics.PublicationError) as caught:
                    ics.generate(self.events, self.out, overwrite=True)
                error = caught.exception
                self.assertEqual(calls, ['a.ics'])
                self.assertEqual(error.published_names, ('a.ics',))
                self.assertEqual(error.failed_name, 'b.ics')
                self.assertEqual(error.phase, 'pre-publication')
                self.assertFalse(error.failed_publication_attempted)
                self.assertNotIn('b.ics', error.uncertain_names)
                self.assertEqual(error.unattempted_names, ('trips.ics',))
                self.assertEqual((self.out / 'b.ics').read_bytes(), b'old-b.ics')
                self.assertEqual((self.out / 'trips.ics').read_bytes(), b'old-trips.ics')

    def test_cr003_no_clobber_conflict_before_invocation_is_not_uncertain(self):
        output = self.root / 'fresh'
        publish = ics._publish_one
        def concurrent_target(stage, final, overwrite):
            publish(stage, final, overwrite)
            if final.name == 'a.ics':
                (output / 'b.ics').write_bytes(b'concurrent complete target')
        with patch.object(ics, '_publish_one', concurrent_target), self.assertRaises(ics.PublicationError) as caught:
            ics.generate(self.events, output)
        self.assertEqual(caught.exception.uncertain_names, ())
        self.assertFalse(caught.exception.failed_publication_attempted)
        self.assertEqual(caught.exception.unattempted_names, ('trips.ics',))
        self.assertEqual((output / 'b.ics').read_bytes(), b'concurrent complete target')
        self.assertFalse((output / 'trips.ics').exists())

    def test_cr003_replace_and_link_after_effect_failures_remain_uncertain(self):
        for overwrite in (True, False):
            with self.subTest(overwrite=overwrite):
                output = self.out if overwrite else self.root / 'fresh'
                publish = ics._publish_one
                def ambiguous(stage, final, overwrite):
                    publish(stage, final, overwrite)
                    if final.name == 'b.ics':
                        raise OSError(errno.EIO, 'after publication')
                with patch.object(ics, '_publish_one', ambiguous), self.assertRaises(ics.PublicationError) as caught:
                    ics.generate(self.events, output, overwrite=overwrite)
                self.assertTrue(caught.exception.failed_publication_attempted)
                self.assertEqual(caught.exception.phase, 'publication')
                self.assertEqual(caught.exception.published_names, ('a.ics',))
                self.assertEqual(caught.exception.uncertain_names, ('b.ics',))
                self.assertEqual(caught.exception.observed_states['b.ics'], 'new-content')
                self.assertEqual(caught.exception.unattempted_names, ('trips.ics',))

    def test_cr003_cli_precheck_failure_reports_no_attempt_and_no_batch_success(self):
        source = self.root / 'events.json'
        source.write_text(json.dumps({'events': self.events}))
        check, publish, _ = self.precheck_failure('_check_target')
        stderr, stdout = io.StringIO(), io.StringIO()
        with check, publish, patch.object(sys, 'argv', [str(SCRIPT), str(source), '--output-dir', str(self.out), '--overwrite']), patch('sys.stderr', stderr), patch('sys.stdout', stdout):
            with self.assertRaises(SystemExit) as caught:
                ics.main()
        self.assertEqual(caught.exception.code, 2)
        self.assertEqual(stdout.getvalue(), '')
        self.assertIn('phase=pre-publication', stderr.getvalue())
        self.assertIn('failed_publication_attempted=false', stderr.getvalue())
        self.assertIn('uncertain=[]', stderr.getvalue())
        self.assertIn('batch_completed=false', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
