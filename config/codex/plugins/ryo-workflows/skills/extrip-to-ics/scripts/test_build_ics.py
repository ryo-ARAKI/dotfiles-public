import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('build_ics', Path(__file__).with_name('build_ics.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CalendarTests(unittest.TestCase):
    def event(self, **changes):
        event = dict(id='trip-a-outbound', group='trip-a', summary='のぞみ1号 東京→京都',
                     start='2026-11-04T08:39:00+09:00', end='2026-11-04T10:50:00+09:00',
                     map_query='東京駅', description='5号車10番E席\n注記,例;確認\\済み',
                     source='trip-a.md', all_day=False)
        return event | changes

    def test_japan_time_and_maps(self):
        body = module.calendar([self.event()])
        self.assertIn('DTSTART:20261103T233900Z\r\n', body)
        self.assertIn('DTEND:20261104T015000Z\r\n', body)
        unfolded = body.replace('\r\n ', '')
        self.assertIn('LOCATION:https://www.google.com/maps/search/?api=1&query=', unfolded)
        self.assertIn('出典：trip-a.md', unfolded)
        self.assertIn(r'注記\,例\;確認\\済み', unfolded)

    def test_all_day_end_is_exclusive(self):
        body = module.calendar([self.event(all_day=True, start='2026-11-04', end='2026-11-06')])
        self.assertIn('DTSTART;VALUE=DATE:20261104\r\n', body)
        self.assertIn('DTEND;VALUE=DATE:20261106\r\n', body)

    def test_folding_and_stable_uid(self):
        body = module.calendar([self.event(summary='日本語' * 60)])
        self.assertTrue(all(len(line.encode()) <= 75 for line in body.split('\r\n')))
        self.assertNotIn('\n', body.replace('\r\n', ''))
        uid = lambda s: next(x for x in s.split('\r\n') if x.startswith('UID:'))
        self.assertEqual(uid(body), uid(module.calendar([self.event(summary='変更')])) )

    def test_rejects_bad_or_ambiguous_events(self):
        for changes in [dict(start='2026-11-04T08:39:00'), dict(end='2026-11-04T08:00:00+09:00'),
                        dict(all_day=True, start='2026-11-04', end='2026-11-04'),
                        dict(group='../outside'), dict(map_query=''), dict(source='')]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                module.calendar([self.event(**changes)])
        with self.assertRaises(ValueError):
            module.calendar([self.event(), self.event()])

    def test_output_collision_and_validation_do_not_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            module.generate([self.event()], output, 'trips.ics')
            original = (output / 'trip-a.ics').read_bytes()
            with self.assertRaises(FileExistsError):
                module.generate([self.event(summary='変更')], output, 'trips.ics')
            self.assertEqual(original, (output / 'trip-a.ics').read_bytes())
            with self.assertRaises(ValueError):
                module.generate([self.event(), self.event(id='other', group='trip-b', end='invalid')], output, 'bad.ics')
            self.assertFalse((output / 'trip-b.ics').exists())


if __name__ == '__main__':
    unittest.main()
