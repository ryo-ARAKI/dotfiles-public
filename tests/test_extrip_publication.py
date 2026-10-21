"""C1-F01..F10: disposable fault injection and filesystem behavior."""
import errno
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'config/codex/plugins/ryo-workflows/skills/extrip-to-ics/scripts/build_ics.py'
spec = importlib.util.spec_from_file_location('publication_ics', SCRIPT)
ics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ics)


def event(group, title='new'):
    return dict(id=group, group=group, summary=title + '-' + group, description='synthetic',
                source='synthetic.md', map_query='Tokyo station', all_day=False,
                start='2026-12-31T23:50:00+09:00', end='2027-01-01T01:10:00+09:00')


class C1PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='ics-c1-', dir='/tmp')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.out = self.root / 'output with spaces'
        self.out.mkdir()
        self.events = [event('a'), event('b')]
        self.old = {}
        for name, events in [('a.ics', [event('a', 'old')]), ('b.ics', [event('b', 'old')]),
                             ('trips.ics', [event('a', 'old'), event('b', 'old')])]:
            self.old[name] = ics.calendar(events).encode()
            (self.out / name).write_bytes(self.old[name])
        self.sentinel = self.root / 'outside-sentinel'
        self.sentinel.write_bytes(b'unrelated')
        (self.out / 'unrelated.txt').write_bytes(b'keep')

    def unchanged(self):
        for name, body in self.old.items():
            self.assertEqual((self.out / name).read_bytes(), body)
        self.assertEqual(self.sentinel.read_bytes(), b'unrelated')
        self.assertEqual((self.out / 'unrelated.txt').read_bytes(), b'keep')

    def complete(self, name):
        body = (self.out / name).read_bytes()
        self.assertTrue(body.startswith(b'BEGIN:VCALENDAR\r\n'))
        self.assertTrue(body.endswith(b'END:VCALENDAR\r\n'))
        self.assertIn(b'SUMMARY:new-', body)
        return body

    def no_temporary_resources(self):
        self.assertEqual(set(p.name for p in self.out.iterdir()), set(self.old) | {'unrelated.txt'})

    def test_f01_invalid_event_name_collision_and_payload_fail_before_publication(self):
        for events, combined in [([event('a'), event('b') | {'end': 'invalid'}], 'trips.ics'),
                                 (self.events, '../outside.ics'), (self.events, 'b.ics')]:
            with self.subTest(combined=combined), self.assertRaises(ValueError):
                ics.generate(events, self.out, combined, overwrite=True)
            self.unchanged()
        original = ics.calendar
        calls = []
        def later_payload(events):
            calls.append(events)
            if len(calls) == 2:
                raise ValueError('injected payload failure')
            return original(events)
        with patch.object(ics, 'calendar', later_payload), self.assertRaises(ValueError):
            ics.generate(self.events, self.out, overwrite=True)
        self.unchanged(); self.no_temporary_resources()

    def test_f02_later_stage_write_failure_preserves_all_finals(self):
        original = ics._write_stage
        def injected(path, body):
            self.unchanged()
            self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
            if path.name == 'b.ics':
                raise OSError(errno.ENOSPC, 'injected staging failure')
            return original(path, body)
        with patch.object(ics, '_write_stage', injected), self.assertRaises(ics.PublicationError) as caught:
            ics.generate(self.events, self.out, overwrite=True)
        self.assertEqual(caught.exception.phase, 'staging')
        self.assertEqual(caught.exception.published_names, ())
        self.assertFalse(caught.exception.batch_completed)
        self.unchanged(); self.no_temporary_resources()

    def test_f02_readback_failure_preserves_all_finals(self):
        original = ics._write_stage
        def corrupt(path, body):
            original(path, body)
            if path.name == 'b.ics':
                path.write_bytes(b'incomplete')
        with patch.object(ics, '_write_stage', corrupt), self.assertRaises(ics.PublicationError):
            ics.generate(self.events, self.out, overwrite=True)
        self.unchanged(); self.no_temporary_resources()

    def test_f03_stage_all_and_close_before_same_filesystem_atomic_replacement(self):
        original = ics.os.replace
        replaced = []
        (self.out / 'a.ics').chmod(0o640)
        def observe(source, destination):
            self.assertEqual(destination.read_bytes(), self.old[destination.name])
            self.assertEqual(source.stat().st_dev, destination.parent.stat().st_dev)
            self.assertTrue(source.read_bytes().endswith(b'END:VCALENDAR\r\n'))
            if not replaced:
                self.assertEqual({p.name for p in source.parent.iterdir()}, set(self.old))
                for p in source.parent.iterdir():
                    self.assertTrue(p.read_bytes().endswith(b'END:VCALENDAR\r\n'))
            original(source, destination)
            replaced.append(destination.name)
        with patch.object(ics.os, 'replace', observe):
            result = ics.generate(self.events, self.out, overwrite=True)
        self.assertEqual(result, {'a.ics': 1, 'b.ics': 1, 'trips.ics': 2})
        self.assertEqual(replaced, list(self.old))
        self.assertEqual(stat.S_IMODE((self.out / 'a.ics').stat().st_mode), 0o640)
        for name in result: self.complete(name)
        self.no_temporary_resources()

    def test_f03_write_only_permissions_are_applied_after_staged_verification(self):
        target = self.out / 'a.ics'
        target.chmod(0o200)
        try:
            result = ics.generate(self.events, self.out, overwrite=True)
            self.assertEqual(result['a.ics'], 1)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o200)
        finally:
            target.chmod(0o600)
        self.complete('a.ics')
        self.no_temporary_resources()

    def test_f04_partial_publication_preserves_new_and_untouched_old_files(self):
        original = ics._publish_one
        def injected(stage, final, overwrite):
            if final.name == 'b.ics':
                raise OSError(errno.EIO, 'injected publication failure')
            original(stage, final, overwrite)
        with patch.object(ics, '_publish_one', injected), self.assertRaises(OSError) as caught:
            ics.generate(self.events, self.out, overwrite=True)
        error = caught.exception
        self.assertIsInstance(error, ics.PublicationError)
        self.assertEqual(error.published_names, ('a.ics',))
        self.assertEqual(error.failed_name, 'b.ics')
        self.assertEqual(error.unattempted_names, ('trips.ics',))
        self.assertFalse(error.batch_completed)
        self.complete('a.ics')
        for name in ('b.ics', 'trips.ics'):
            self.assertEqual((self.out / name).read_bytes(), self.old[name])
        self.assertIn('batch_completed=false', str(error))
        self.assertNotIn('synthetic', str(error))
        self.no_temporary_resources()

    def test_f04_ambiguous_operation_records_observation_without_claiming_success(self):
        original = ics._publish_one
        def interrupted(stage, final, overwrite):
            original(stage, final, overwrite)
            if final.name == 'b.ics':
                raise OSError(errno.EIO, 'ambiguous operation')
        with patch.object(ics, '_publish_one', interrupted), self.assertRaises(ics.PublicationError) as caught:
            ics.generate(self.events, self.out, overwrite=True)
        error = caught.exception
        self.assertEqual(error.published_names, ('a.ics',))
        self.assertIn('b.ics', error.uncertain_names)
        self.assertEqual(error.observed_states['b.ics'], 'new-content')
        self.assertEqual(error.unattempted_names, ('trips.ics',))
        self.complete('a.ics'); self.complete('b.ics')

    def test_f05_existing_no_clobber_conflict_has_no_publication(self):
        with self.assertRaises(FileExistsError):
            ics.generate(self.events, self.out)
        self.unchanged(); self.no_temporary_resources()

    def test_f05_publication_time_no_clobber_conflict_is_preserved(self):
        output = self.root / 'fresh'
        original = ics.os.link
        def conflict(stage, final):
            if final.name == 'b.ics': final.write_bytes(b'concurrent complete target')
            original(stage, final)
        with patch.object(ics.os, 'link', conflict), self.assertRaises(ics.PublicationError) as caught:
            ics.generate(self.events, output)
        self.assertEqual(caught.exception.published_names, ('a.ics',))
        self.assertEqual((output / 'b.ics').read_bytes(), b'concurrent complete target')
        self.assertTrue((output / 'a.ics').read_bytes().endswith(b'END:VCALENDAR\r\n'))
        self.assertFalse((output / 'trips.ics').exists())
        self.assertEqual(set(p.name for p in output.iterdir()), {'a.ics', 'b.ics'})

    def test_f06_combined_failure_has_complete_individuals_and_old_combined(self):
        original = ics._publish_one
        def injected(stage, final, overwrite):
            if final.name == 'trips.ics': raise OSError('injected combined publication failure')
            original(stage, final, overwrite)
        with patch.object(ics, '_publish_one', injected), self.assertRaises(ics.PublicationError) as caught:
            ics.generate(self.events, self.out, overwrite=True)
        self.complete('a.ics'); self.complete('b.ics')
        self.assertEqual((self.out / 'trips.ics').read_bytes(), self.old['trips.ics'])
        self.assertEqual(caught.exception.published_names, ('a.ics', 'b.ics'))
        self.assertEqual(caught.exception.failed_name, 'trips.ics')
        self.assertEqual(caught.exception.unattempted_names, ())
        self.no_temporary_resources()

    def test_f07_leaf_and_dangling_symlinks_are_rejected_in_both_modes(self):
        target = self.out / 'b.ics'; target.unlink()
        for dangling in (False, True):
            target.symlink_to(self.root / 'missing' if dangling else self.sentinel)
            for overwrite in (False, True):
                with self.subTest(dangling=dangling, overwrite=overwrite), self.assertRaises((OSError, ValueError)):
                    ics.generate(self.events, self.out, overwrite=overwrite)
                self.assertTrue(target.is_symlink())
                self.assertEqual(self.sentinel.read_bytes(), b'unrelated')
                self.assertEqual((self.out / 'a.ics').read_bytes(), self.old['a.ics'])
            target.unlink()

    def test_f07_output_directory_and_relevant_parent_symlinks_are_rejected(self):
        alias = self.root / 'alias'; alias.symlink_to(self.out, target_is_directory=True)
        for output in (alias, alias / 'nested'):
            for overwrite in (False, True):
                with self.subTest(output=output, overwrite=overwrite), self.assertRaises((OSError, ValueError)):
                    ics.generate(self.events, output, overwrite=overwrite)
        self.unchanged()
        self.assertFalse((self.out / 'nested').exists())

    def test_f07_nonregular_targets_and_lexical_traversal_are_rejected(self):
        target = self.out / 'b.ics'; target.unlink(); target.mkdir()
        with self.assertRaises((OSError, ValueError)): ics.generate(self.events, self.out, overwrite=True)
        self.assertEqual((self.out / 'a.ics').read_bytes(), self.old['a.ics'])
        target.rmdir(); os.mkfifo(target)
        with self.assertRaises((OSError, ValueError)): ics.generate(self.events, self.out, overwrite=True)
        self.assertTrue(stat.S_ISFIFO(target.lstat().st_mode))
        with self.assertRaises(ValueError): ics.generate(self.events, self.root / 'x' / '..' / 'y', overwrite=True)
        self.assertFalse((self.root / 'x').exists())

    def test_f07_hardlink_target_replacement_does_not_modify_external_inode(self):
        target = self.out / 'a.ics'; target.unlink(); os.link(self.sentinel, target)
        ics.generate(self.events, self.out, overwrite=True)
        self.complete('a.ics')
        self.assertEqual(self.sentinel.read_bytes(), b'unrelated')
        self.assertNotEqual(target.stat().st_ino, self.sentinel.stat().st_ino)

    def test_f08_cleanup_failure_after_partial_publication_is_reported(self):
        original = ics._publish_one
        def injected(stage, final, overwrite):
            if final.name == 'b.ics': raise OSError('injected publish failure')
            original(stage, final, overwrite)
        with patch.object(ics, '_publish_one', injected), patch.object(ics, '_cleanup_staging', side_effect=OSError('injected cleanup failure')):
            with self.assertRaises(ics.PublicationError) as caught:
                ics.generate(self.events, self.out, overwrite=True)
        self.complete('a.ics')
        self.assertTrue(caught.exception.cleanup_errors)
        self.assertTrue(Path(caught.exception.staging_dir).is_dir())
        self.assertEqual((self.out / 'unrelated.txt').read_bytes(), b'keep')

    def test_f08_cleanup_failure_after_complete_batch_warns_without_rollback(self):
        with patch.object(ics, '_cleanup_staging', side_effect=OSError('injected cleanup failure')):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                result = ics.generate(self.events, self.out, overwrite=True)
        self.assertEqual(result['trips.ics'], 2)
        self.assertEqual(len(caught), 1)
        self.assertTrue(caught[0].message.batch_completed)
        self.assertTrue(caught[0].message.cleanup_errors)
        for name in result: self.complete(name)

    def test_f08_unrelated_file_inside_private_staging_is_not_removed(self):
        original = ics._write_stage
        added = []
        def inject(path, body):
            original(path, body)
            if not added:
                extra = path.parent / 'unrelated.keep'; extra.write_bytes(b'keep'); added.append(extra)
        with patch.object(ics, '_write_stage', inject), warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always'); ics.generate(self.events, self.out, overwrite=True)
        self.assertTrue(caught)
        self.assertEqual(added[0].read_bytes(), b'keep')
        for name in self.old: self.complete(name)

    def test_f09_cli_publication_failure_is_nonzero_and_reports_partial_state(self):
        source = self.root / 'events.json'; source.write_text(json.dumps({'events': self.events}))
        original = ics._publish_one
        def injected(stage, final, overwrite):
            if final.name == 'b.ics': raise OSError('injected publication failure')
            original(stage, final, overwrite)
        arguments = [str(SCRIPT), str(source), '--output-dir', str(self.out), '--overwrite']
        stderr = io.StringIO(); stdout = io.StringIO()
        with patch.object(sys, 'argv', arguments), patch.object(ics, '_publish_one', injected), patch('sys.stderr', stderr), patch('sys.stdout', stdout):
            with self.assertRaises(SystemExit) as caught: ics.main()
        self.assertEqual(caught.exception.code, 2)
        self.assertIn('batch_completed=false', stderr.getvalue())
        self.assertIn('a.ics', stderr.getvalue()); self.assertIn('b.ics', stderr.getvalue())
        self.assertIn('trips.ics', stderr.getvalue()); self.assertEqual(stdout.getvalue(), '')

    def test_f10_unsupported_no_clobber_fails_without_final_streaming_fallback(self):
        output = self.root / 'unsupported'
        with patch.object(ics.os, 'link', side_effect=OSError(errno.EOPNOTSUPP, 'unsupported')):
            with self.assertRaises(ics.PublicationError) as caught: ics.generate(self.events, output)
        self.assertEqual(caught.exception.published_names, ())
        self.assertEqual(list(output.iterdir()), [])
        self.assertIn('no-clobber', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
