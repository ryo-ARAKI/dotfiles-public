"""Render reviewed travel events as iCalendar files; Python standard library only."""

import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import urlencode
import uuid


def escape(value):
    return value.replace('\\', '\\\\').replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\\n').replace(';', '\\;').replace(',', '\\,')


def fold(line):
    parts, current = [], ''
    for char in line:
        if len((current + char).encode('utf-8')) > 75:
            parts.append(current)
            current = ' '
        current += char
    return '\r\n'.join(parts + [current])


def required(event, key):
    value = event.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{key}: nonempty string required')
    return value


def validate(events):
    if not isinstance(events, list) or not events:
        raise ValueError('events: nonempty array required')
    seen = set()
    for event in events:
        if not isinstance(event, dict):
            raise ValueError('event must be an object')
        for key in ('id', 'group', 'summary', 'description', 'source', 'map_query', 'start', 'end'):
            required(event, key)
        if event['id'] in seen:
            raise ValueError(f'duplicate event id: {event["id"]}')
        seen.add(event['id'])
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', event['group']):
            raise ValueError('group: use only letters, numbers, underscores and hyphens')
        if type(event.get('all_day')) is not bool:
            raise ValueError('all_day: boolean required')
        if event['all_day']:
            for key in ('start', 'end'):
                if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', event[key]):
                    raise ValueError(f'{key}: expected YYYY-MM-DD')
            start, end = (date.fromisoformat(event[key]) for key in ('start', 'end'))
        else:
            start, end = (datetime.fromisoformat(event[key]) for key in ('start', 'end'))
            if start.utcoffset() is None or end.utcoffset() is None:
                raise ValueError('timed events need explicit UTC offsets, normally +09:00')
        if end <= start:
            raise ValueError('end must be later than start; all-day end is exclusive')


def calendar(events):
    validate(events)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//EXTrip to ICS//JA', 'CALSCALE:GREGORIAN']
    for event in events:
        uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'extrip:' + event['id'])) + '@extrip-to-ics.local'
        url = 'https://www.google.com/maps/search/?' + urlencode({'api': '1', 'query': event['map_query']})
        kind = ';VALUE=DATE' if event['all_day'] else ''
        def moment(value):
            if event['all_day']:
                return date.fromisoformat(value).strftime('%Y%m%d')
            return datetime.fromisoformat(value).astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        lines += ['BEGIN:VEVENT', 'UID:' + uid, 'DTSTAMP:' + stamp,
                  'DTSTART' + kind + ':' + moment(event['start']),
                  'DTEND' + kind + ':' + moment(event['end']),
                  'SUMMARY:' + escape(event['summary']), 'LOCATION:' + escape(url), 'URL:' + url,
                  'DESCRIPTION:' + escape(event['description'] + '\n出典：' + event['source']),
                  'END:VEVENT']
    lines.append('END:VCALENDAR')
    return '\r\n'.join(fold(line) for line in lines) + '\r\n'


def generate(events, output_dir, combined='trips.ics', overwrite=False):
    # Validate the whole batch and all destination names before any writes.
    validate(events)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*\.ics', combined):
        raise ValueError('combined: expected a simple .ics filename')
    groups = {}
    for event in events:
        groups.setdefault(event['group'], []).append(event)
    payloads = {group + '.ics': calendar(items) for group, items in groups.items()}
    if combined in payloads:
        raise ValueError('combined filename collides with a group filename')
    payloads[combined] = calendar(events)
    output_dir = Path(output_dir)
    if not overwrite:
        for name in payloads:
            if (output_dir / name).exists():
                raise FileExistsError(f'{output_dir / name} exists; choose another directory or explicitly use --overwrite')
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, body in payloads.items():
        with (output_dir / name).open('wb' if overwrite else 'xb') as stream:
            stream.write(body.encode('utf-8'))
    return {name: body.count('BEGIN:VEVENT\r\n') for name, body in payloads.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='UTF-8 JSON object containing an events array')
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--combined', default='trips.ics')
    parser.add_argument('--overwrite', action='store_true', help='replace existing output files intentionally')
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('input must be an object containing events')
        result = generate(data.get('events'), args.output_dir, args.combined, args.overwrite)
    except (ValueError, OSError) as error:
        parser.exit(2, f'Error: {error}\n')
    for name, count in result.items():
        print(f'{args.output_dir / name}: {count} events')


if __name__ == '__main__':
    main()
