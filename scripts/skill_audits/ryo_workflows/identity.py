"""Read-only public plugin identity comparison; never proves catalog selection or load."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess

PLUGIN = Path('config/codex/plugins/ryo-workflows')
TARGET = '~/plugins/ryo-workflows/'


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            value.update(block)
    return value.hexdigest()


def safe_relative(value):
    if not isinstance(value, str):
        raise ValueError('plugin-relative paths must be strings')
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or '..' in path.parts or
            str(path) != value or '\\' in value or '\n' in value):
        raise ValueError('expected a canonical plugin-relative path')
    return value


def public_entries(repo):
    entries = {}
    for line in (repo / 'manifest/base.tsv').read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        source, target, mode, when = line.split('\t')
        is_source = Path(source).is_relative_to(PLUGIN)
        if not (is_source or target.startswith(TARGET)):
            continue
        if not is_source or not target.startswith(TARGET) or when != 'local':
            raise ValueError('unexpected public plugin manifest mapping')
        relative = safe_relative(target.removeprefix(TARGET))
        if Path(source) != PLUGIN / relative or relative in entries:
            raise ValueError('inconsistent or duplicate plugin mapping')
        entries[relative] = {'source': source, 'mode': int(mode, 8)}
    if not entries:
        raise ValueError('public plugin manifest is empty')
    return entries


def inventory(root, hashed_paths):
    """Do not follow links or read unexpected file contents (which may be private)."""
    resources = {}

    def visit(path, relative):
        info = path.lstat()
        kind = ('symlink' if stat.S_ISLNK(info.st_mode) else
                'directory' if stat.S_ISDIR(info.st_mode) else
                'regular' if stat.S_ISREG(info.st_mode) else 'other')
        item = {'type': kind, 'mode': f'{stat.S_IMODE(info.st_mode):04o}',
                'size': info.st_size, 'mtime_ns': info.st_mtime_ns}
        if kind == 'regular' and relative in hashed_paths:
            item['sha256'] = digest(path)
        resources[relative] = item
        if kind == 'directory':
            for child in sorted(path.iterdir()):
                visit(child, f'{relative}/{child.name}' if relative else child.name)

    try:
        visit(root, '')
    except FileNotFoundError:
        if not resources:
            return {'': {'type': 'missing'}}
        raise
    return resources


def content_id(resources):
    lines = [f'{value["sha256"]}  {name}\n' for name, value in sorted(resources.items()) if 'sha256' in value]
    return hashlib.sha256(''.join(lines).encode('utf-8')).hexdigest()


def directories(paths):
    result = {''}
    for name in paths:
        result.update(str(parent) for parent in PurePosixPath(name).parents if str(parent) != '.')
    return result


def metadata_version(root, resources):
    if resources.get('.codex-plugin/plugin.json', {}).get('type') != 'regular':
        return None
    try:
        return json.loads((root / '.codex-plugin/plugin.json').read_text(encoding='utf-8')).get('version')
    except (ValueError, OSError):
        return None


def compare(repo, observed_root, overlay=None):
    repo, observed_root = Path(repo).absolute(), Path(observed_root).absolute()
    entries = public_entries(repo)
    source_root = repo / PLUGIN
    source = inventory(source_root, entries)
    expected = {}
    source_problems = []
    for name, entry in entries.items():
        item = source.get(name, {})
        if item.get('type') != 'regular':
            source_problems.append(name)
        else:
            expected[name] = {'sha256': item['sha256'], 'mode': f'{entry["mode"]:04o}'}
    source_dirs = directories(entries)
    source_problems.extend(name for name, item in source.items()
                           if name not in entries and not (name in source_dirs and item['type'] == 'directory'))
    if overlay is not None and not isinstance(overlay, dict):
        raise ValueError('overlay must be an object')
    overlays = (overlay or {}).get('files', {})
    if not isinstance(overlays, dict):
        raise ValueError('overlay files must be an object')
    for name, item in overlays.items():
        safe_relative(name)
        if (not isinstance(item, dict) or not isinstance(item.get('origin'), str) or not item['origin'].strip() or
                not isinstance(item.get('sha256'), str) or
                not re.fullmatch(r'[0-9a-f]{64}', item['sha256']) or
                not isinstance(item.get('mode'), str) or
                not re.fullmatch(r'0[0-7]{3}', item['mode'])):
            raise ValueError('overlay requires an exact SHA-256, mode, and approval origin')
        expected[name] = {'sha256': item['sha256'], 'mode': item['mode']}
    observed = inventory(observed_root, expected)
    expected_dirs = directories(expected)
    differences = {key: [] for key in ('missing', 'unexpected', 'modified', 'wrong_types', 'mode_mismatches')}
    for name, item in observed.items():
        if name in expected:
            if item['type'] != 'regular':
                differences['wrong_types'].append(name)
            else:
                if item['sha256'] != expected[name]['sha256']:
                    differences['modified'].append(name)
                if item['mode'] != expected[name]['mode']:
                    differences['mode_mismatches'].append(name)
        elif name in expected_dirs:
            if item['type'] != 'directory':
                differences['wrong_types'].append(name)
        else:
            differences['unexpected'].append(name)
    differences['missing'] = sorted(set(expected) - observed.keys())
    git = lambda *args: subprocess.check_output(['git', *args], cwd=repo, text=True, stderr=subprocess.DEVNULL).strip()
    return {
        'schema_version': 1,
        'source': {'repo': str(repo), 'head': git('rev-parse', 'HEAD'),
                   'status': git('status', '--porcelain=v1', '--', str(PLUGIN), 'manifest/base.tsv'),
                   'manifest_sha256': digest(repo / 'manifest/base.tsv'),
                   'payload_sha256': content_id(source), 'metadata_version': metadata_version(source_root, source),
                   'resources': {name: source[name] for name in entries if name in source},
                   'problems': sorted(set(source_problems))},
        'observed': {'root': str(observed_root), 'payload_sha256': content_id(observed),
                     'metadata_version': metadata_version(observed_root, observed), 'resources': observed},
        'approved_overlays': overlays, 'differences': differences,
        'file_identity_matches': not source_problems and not any(differences.values()),
        'catalog_visibility': 'unverified', 'actual_loaded_resources': 'unverified',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-repo', type=Path, required=True)
    parser.add_argument('--observed-root', type=Path, required=True)
    parser.add_argument('--expected-overlay', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            output = args.output.resolve()
            if any(output.is_relative_to(root.resolve()) for root in [args.source_repo / PLUGIN, args.observed_root]):
                raise ValueError('identity output must be outside both plugin roots')
        overlay = json.loads(args.expected_overlay.read_text(encoding='utf-8')) if args.expected_overlay else None
        result = compare(args.source_repo, args.observed_root, overlay)
        body = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            with args.output.open('x', encoding='utf-8') as stream:
                stream.write(body)
        else:
            print(body, end='')
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(2, f'Identity error: {type(error).__name__}: {error}\n')
    return 0 if result['file_identity_matches'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
