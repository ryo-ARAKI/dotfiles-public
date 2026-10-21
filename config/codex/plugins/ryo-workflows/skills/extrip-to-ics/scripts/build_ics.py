"""Render reviewed travel events as iCalendar files; Python standard library only."""

import argparse
from datetime import date, datetime, timezone
import json
import errno
import os
from pathlib import Path
import re
import stat
import tempfile
import warnings
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


class PublicationError(OSError):
    """A failed C1 batch. Successful operation records are separate from observations."""

    def __init__(self, report, cause):
        self.report = report
        for key, value in report.items():
            setattr(self, key, value)
        super().__init__(getattr(cause, 'errno', None) or errno.EIO, _report_message(report))


class PublicationCleanupWarning(UserWarning):
    """All outputs were published, but run-owned temporary cleanup was incomplete."""

    def __init__(self, report):
        self.report = report
        for key, value in report.items():
            setattr(self, key, value)
        super().__init__(_report_message(report))


def _report_message(report):
    return (f'C1 phase={report["phase"]}; batch_completed={str(report["batch_completed"]).lower()}; '
            f'published={json.dumps(report["published_names"])}; failed={report["failed_name"]}; '
            f'failed_publication_attempted={str(report["failed_publication_attempted"]).lower()}; '
            f'unattempted={json.dumps(report["unattempted_names"])}; '
            f'uncertain={json.dumps(report["uncertain_names"])}; '
            f'observed={json.dumps(report["observed_states"], sort_keys=True)}; '
            f'cleanup={json.dumps(report["cleanup_errors"])}; staging_dir={report["staging_dir"]}; '
            'atomic no-clobber requires same-filesystem hard-link support when overwrite=False')


def _check_output_directory(path):
    # Inspect the specified path without resolving away aliases. A trusted directory
    # without noncooperating writers is required; these checks do not eliminate races.
    if '..' in path.parts:
        raise ValueError('output path must not contain lexical .. components')
    absolute = path.absolute()
    for component in (*reversed(absolute.parents), absolute):
        try:
            info = component.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode):
            raise ValueError(f'output path symlink is not allowed: {component}')
        if not stat.S_ISDIR(info.st_mode):
            raise NotADirectoryError(errno.ENOTDIR, 'output path component is not a directory', str(component))


def _check_target(path, overwrite):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(info.st_mode):
        raise ValueError(f'output target symlink is not allowed: {path.name}')
    if not stat.S_ISREG(info.st_mode):
        raise OSError(errno.EINVAL, 'output target must be a regular file', str(path))
    if not overwrite:
        raise FileExistsError(errno.EEXIST, 'choose another directory or explicitly use --overwrite', str(path))
    return stat.S_IMODE(info.st_mode)


def _write_stage(path, body):
    # The directory is private (0700). New file permissions retain the caller's
    # normal umask. Apply replacement permission bits after content verification.
    with path.open('xb') as stream:
        if stream.write(body) != len(body):
            raise OSError(errno.EIO, 'short staging write')


def _publish_one(stage, final, overwrite):
    if overwrite:
        os.replace(stage, final)
    else:
        # Atomic create-if-absent. Never fall back to streaming into a final file.
        os.link(stage, final)


def _cleanup_staging(staging, names):
    errors = []
    for name in names:
        try:
            (staging / name).unlink(missing_ok=True)
        except OSError as error:
            errors.append(f'{name}:{type(error).__name__}:{error.errno}')
    try:
        # Do not recursively remove unexpected files, even inside this private dir.
        staging.rmdir()
    except OSError as error:
        errors.append(f'directory:{type(error).__name__}:{error.errno}')
    return tuple(errors)


def _observe_outputs(output_dir, payloads):
    states = {}
    for name, body in payloads.items():
        try:
            _check_output_directory(output_dir)
            path = output_dir / name
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                states[name] = 'symlink'
            elif not stat.S_ISREG(info.st_mode):
                states[name] = 'nonregular'
            else:
                states[name] = 'new-content' if path.read_bytes() == body else 'other-content'
        except FileNotFoundError:
            states[name] = 'absent'
        except (OSError, ValueError):
            states[name] = 'unavailable'
    return states


def generate(events, output_dir, combined='trips.ics', overwrite=False):
    # Validate and construct every complete payload before touching output paths.
    validate(events)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*\.ics', combined):
        raise ValueError('combined: expected a simple .ics filename')
    groups = {}
    for event in events:
        groups.setdefault(event['group'], []).append(event)
    payloads = {group + '.ics': calendar(items).encode('utf-8') for group, items in groups.items()}
    if combined in payloads:
        raise ValueError('combined filename collides with a group filename')
    payloads[combined] = calendar(events).encode('utf-8')
    output_dir = Path(output_dir)
    _check_output_directory(output_dir)
    modes = {name: _check_target(output_dir / name, overwrite) for name in payloads}
    output_dir.mkdir(parents=True, exist_ok=True)
    _check_output_directory(output_dir)

    staging, published, failed_name = None, [], None
    phase, failure, cleanup_errors = 'staging', None, ()
    try:
        staging = Path(tempfile.mkdtemp(prefix='.extrip-to-ics-', dir=output_dir))
        for name, body in payloads.items():
            failed_name = name
            _write_stage(staging / name, body)
            if (staging / name).read_bytes() != body:
                raise OSError(errno.EIO, 'staged content verification failed')
            if modes[name] is not None:
                (staging / name).chmod(modes[name])
        for name in payloads:
            failed_name = name
            phase = 'pre-publication'
            _check_output_directory(output_dir)
            _check_target(output_dir / name, overwrite)
            phase = 'publication'
            _publish_one(staging / name, output_dir / name, overwrite)
            published.append(name)  # Record only an operation that returned success.
        failed_name = None
    except (OSError, ValueError) as error:
        failure = error
    finally:
        if staging is not None:
            try:
                cleanup_errors = _cleanup_staging(staging, payloads)
            except OSError as error:
                cleanup_errors = (f'{type(error).__name__}:{error.errno}',)

    if failure or cleanup_errors:
        observed = _observe_outputs(output_dir, payloads)
        uncertain = [name for name in published if observed[name] != 'new-content']
        if failure and phase == 'publication':
            # The failing operation has no successful return record. Inspection
            # may observe new content, but is not proof of who published it.
            uncertain.append(failed_name)
        names = list(payloads)
        # The failed file has its own record, even when its precheck prevented
        # invocation. Keep subsequent files separate from that failed file.
        unattempted = names[len(published) + 1:] if phase in ('pre-publication', 'publication') and failure else names if failure else []
        report = dict(phase=phase if failure else 'cleanup', published_names=tuple(published),
                      failed_name=failed_name, failed_publication_attempted=bool(failure and phase == 'publication'),
                      unattempted_names=tuple(unattempted),
                      batch_completed=len(published) == len(payloads),
                      uncertain_names=tuple(uncertain), observed_states=observed,
                      cleanup_errors=cleanup_errors, staging_dir=str(staging) if cleanup_errors else None)
        if failure:
            raise PublicationError(report, failure) from failure
        warnings.warn(PublicationCleanupWarning(report), stacklevel=2)
    return {name: body.count(b'BEGIN:VEVENT\r\n') for name, body in payloads.items()}


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
