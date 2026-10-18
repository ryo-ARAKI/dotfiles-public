import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "config/codex/plugins/ryo-workflows/skills/extrip-to-ics/scripts/build_ics.py"
spec = importlib.util.spec_from_file_location("build_ics", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def unfold(body):
    return body.replace('\r\n ', '')


def uids(body):
    return {line for line in unfold(body).split('\r\n') if line.startswith('UID:')}


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
        properties = dict(line.split(':', 1) for line in unfold(body).split('\r\n') if ':' in line)
        self.assertEqual(properties['LOCATION'], properties['URL'])
        self.assertEqual(parse_qs(urlsplit(properties['URL']).query), {'api': ['1'], 'query': ['東京駅']})
        self.assertIn('出典：trip-a.md', properties['DESCRIPTION'])
        self.assertIn(r'注記\,例\;確認\\済み', properties['DESCRIPTION'])

    def test_all_day_end_is_exclusive(self):
        body = module.calendar([self.event(all_day=True, start='2026-11-04', end='2026-11-06')])
        self.assertIn('DTSTART;VALUE=DATE:20261104\r\n', body)
        self.assertIn('DTEND;VALUE=DATE:20261106\r\n', body)

    def test_folding_and_stable_uid(self):
        summary = '日本語' * 60
        body = module.calendar([self.event(summary=summary)])
        self.assertTrue(all(len(line.encode()) <= 75 for line in body.split('\r\n')))
        self.assertNotIn('\n', body.replace('\r\n', ''))
        self.assertIn('SUMMARY:' + summary + '\r\n', unfold(body))
        changed = self.event(summary='変更', description='座席変更',
                             start='2026-11-04T09:00:00+09:00', end='2026-11-04T11:00:00+09:00')
        self.assertEqual(uids(body), uids(module.calendar([changed])))
        self.assertNotEqual(uids(body), uids(module.calendar([self.event(id='another-booking')])))

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
            original = {path.name: path.read_bytes() for path in output.iterdir()}
            with self.assertRaises(FileExistsError):
                module.generate([self.event(summary='変更')], output, 'trips.ics')
            with self.assertRaises(ValueError):
                module.generate([self.event(), self.event(id='other', group='trip-b', end='invalid')], output, 'bad.ics')
            self.assertEqual(original, {path.name: path.read_bytes() for path in output.iterdir()})
            module.generate([self.event(summary='変更')], output, 'trips.ics', overwrite=True)
            for name, previous in original.items():
                current = (output / name).read_bytes().decode()
                self.assertIn('SUMMARY:変更\r\n', current)
                self.assertEqual(uids(previous.decode()), uids(current))

    def test_destination_names_are_checked_before_creating_output(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'output'
            for combined in ['trip-a.ics', '../outside.ics']:
                with self.subTest(combined=combined), self.assertRaises(ValueError):
                    module.generate([self.event()], output, combined)
                self.assertFalse(output.exists())

    def test_cli_generates_separate_and_combined_calendars_across_new_year(self):
        events = [
            self.event(start='2026-12-31T23:50:00+09:00', end='2027-01-01T01:10:00+09:00'),
            self.event(id='trip-a-hotel', all_day=True, start='2027-01-01', end='2027-01-03',
                       summary='ホテル例', map_query='ホテル例 京都市の住所'),
            self.event(id='trip-b-outbound', group='trip-b', source='trip-b.md'),
        ]
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'events.json'
            source.write_text(json.dumps({'events': events}, ensure_ascii=False), encoding='utf-8')
            original = source.read_bytes()
            output = Path(folder) / 'output'
            result = subprocess.run([sys.executable, str(SCRIPT), str(source), '--output-dir', str(output)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = {'trip-a.ics': 2, 'trip-b.ics': 1, 'trips.ics': 3}
            self.assertEqual({path.name for path in output.iterdir()}, set(expected))
            bodies = {}
            for name, count in expected.items():
                body = (output / name).read_bytes().decode('utf-8')
                bodies[name] = unfold(body)
                self.assertEqual(body.count('BEGIN:VEVENT\r\n'), count)
                self.assertTrue(body.startswith('BEGIN:VCALENDAR\r\n'))
                self.assertTrue(body.endswith('END:VCALENDAR\r\n'))
                self.assertIn(f'{name}: {count} events', result.stdout)
            self.assertEqual(uids(bodies['trips.ics']), uids(bodies['trip-a.ics']) | uids(bodies['trip-b.ics']))
            self.assertIn('DTSTART:20261231T145000Z\r\n', bodies['trip-a.ics'])
            self.assertIn('DTEND:20261231T161000Z\r\n', bodies['trip-a.ics'])
            self.assertIn('DTEND;VALUE=DATE:20270103\r\n', bodies['trip-a.ics'])
            urls = [line.removeprefix('URL:') for line in bodies['trip-a.ics'].split('\r\n') if line.startswith('URL:')]
            self.assertEqual([parse_qs(urlsplit(url).query)['query'][0] for url in urls],
                             ['東京駅', 'ホテル例 京都市の住所'])
            self.assertEqual(source.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
