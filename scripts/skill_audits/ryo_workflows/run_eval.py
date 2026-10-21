"""Prepare focused evaluations and validate supplied preflight evidence; never launch an LLM."""

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('audit_identity', HERE / 'identity.py')
identity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(identity)
sha256 = identity.digest
SKILLS = ('dotfiles-deploy', 'creating-arxiv-diff-pdfs', 'creating-and-editing-typst-figures',
          'export-editable-typst-figures', 'writing-typst-research-reports', 'extrip-to-ics')
ENTRYPOINTS = set(SKILLS) | {'ryo-workflows-router'}
ORIGINAL_PROMPTS_SHA256 = 'aa6ea58c2c85635c8857590fc5a5f956cc8cfd8cc00d6593889b888c19a6deb9'


def extract_prompts(text):
    prompts = {}
    for case in range(1, 7):
        section = text.split(f'### P-{case:02d} /', 1)[1].split('\n### ', 1)[0]
        prompts[f'P-{case:02d}'] = re.search(r'^> (.+)$', section, re.MULTILINE)[1]
    for line in text.splitlines():
        match = re.match(r'\| ([NB]-\d\d) [^|]+\| `([^`]+)`', line)
        if match:
            prompts[match[1]] = match[2]
    return prompts


def original_prompts():
    result = json.loads((HERE / 'original_prompts.json').read_text(encoding='utf-8'))
    canonical = json.dumps(result['prompts'], ensure_ascii=False, sort_keys=True).encode('utf-8')
    if hashlib.sha256(canonical).hexdigest() != result['prompts_sha256'] or result['prompts_sha256'] != ORIGINAL_PROMPTS_SHA256:
        raise ValueError('immutable original prompt group changed')
    return result


def cases():
    return json.loads((HERE / 'cases.json').read_text(encoding='utf-8'))


def prompt_for(case, mode):
    if mode not in ('explicit', 'implicit', 'disabled'):
        raise ValueError('unknown evaluation mode')
    prompts = original_prompts()['prompts']
    if case not in prompts:
        raise ValueError('unknown evaluation case')
    text = prompts[case]
    if mode == 'explicit':
        owner = cases()['owners'].get(case)
        if not owner:
            raise ValueError('negative cases do not force an explicit skill')
        return '$' + owner + ' を使って、' + text
    return text


def tree_manifest(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('evaluation inputs must not contain symlinks')
        if path.is_file():
            result[str(path.relative_to(root))] = sha256(path)
    return result


def result_template(case, mode):
    prompt = prompt_for(case, mode) + '\n'
    return {'case_id': case, 'mode': mode, 'prompt_revision': 'stage1-immutable',
            'original_prompts_sha256': original_prompts()['prompts_sha256'],
            'prompt_utf8': prompt, 'prompt_sha256': hashlib.sha256(prompt.encode('utf-8')).hexdigest(),
            'acceptance_revision': cases()['acceptance_revision'],
            'runtime_version': None, 'client_binary_sha256': None,
            'requested_model': None, 'effective_model': None,
            'normal_effort': None, 'planning_effort': None, 'effective_config_evidence': None,
            'catalog_evidence': None, 'loaded_resources': [],
            'usage': {'source': 'unavailable', 'input_tokens': None, 'output_tokens': None, 'cost': None},
            'timing': {'preflight_seconds': None, 'task_wall_seconds': None},
            'selection': 'inconclusive', 'execution': 'designed-but-unexecuted',
            'failure_class': None, 'artifact_hashes': {}, 'observations': [], 'unverified': []}


def prepare(repo, destination, compile_fixtures=False):
    resolved = destination.resolve()
    if not resolved.is_relative_to('/tmp') or resolved == Path('/tmp'):
        raise ValueError('evaluation destination must be a disposable subdirectory of /tmp')
    destination.mkdir(parents=True, exist_ok=False)
    runs = []
    for case, modes in cases()['focused'].items():
        for mode in modes:
            run_id = f'{case}-{mode}'
            root = destination / run_id
            workspace = root / 'input'
            shutil.copytree(HERE / 'fixtures' / cases()['fixtures'][case], workspace)
            if compile_fixtures and case != 'N-01':
                subprocess.run(['typst', 'compile', 'figure.typ', 'figure.pdf'], cwd=workspace, check=True, timeout=30)
                if case == 'B-03':
                    subprocess.run(['typst', 'compile', 'report.typ', 'report.pdf'], cwd=workspace, check=True, timeout=30)
            result = result_template(case, mode)
            prompt_path = root / 'prompt.txt'
            prompt_path.write_bytes(result['prompt_utf8'].encode('utf-8'))
            result.update(run_id=run_id, workspace=str(workspace.absolute()), fixture_manifest=tree_manifest(workspace),
                          prompt_path=str(prompt_path.absolute()))
            (root / 'result-template.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
            runs.append(result)
    source = identity.compare(repo, repo / identity.PLUGIN)['source']
    plan = {'source': source, 'runs': runs, 'compiled_fixtures': compile_fixtures,
            'original_prompts_sha256': original_prompts()['prompts_sha256'],
            'llm_executed': False, 'repo': str(repo.absolute())}
    (destination / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
    return plan


def known_entrypoint(path):
    """Recognize only known directory names or simple skill frontmatter names."""
    if path.name == 'SKILL.md' and path.parent.name in ENTRYPOINTS:
        return path.parent.name
    # Read a bounded header, not arbitrary fixture bodies or general YAML.
    with path.open('rb') as stream:
        header = stream.read(8192).decode('utf-8', errors='replace').replace('\r\n', '\n')
    if not header.startswith('---\n'):
        return None
    header = re.split(r'^---\s*$', header, flags=re.MULTILINE)[1]
    match = re.search(r'^name:[ \t]*[\'\"]?([a-z0-9-]+)[\'\"]?[ \t]*(?:#.*)?$', header, re.MULTILINE)
    return match[1] if match and match[1] in ENTRYPOINTS else None


def catalog_problems(catalog, readable_roots, repo, disabled, plugin_root=None):
    problems = []
    current = {name: sha256(repo / identity.PLUGIN / name) for name in identity.public_entries(repo)
               if name.startswith('skills/')}
    audited = json.loads((HERE / 'audited_skill_hashes.json').read_text(encoding='utf-8'))
    known = set(current.values()) | set(audited['resources'].values())
    oracle_hash = sha256(HERE / 'oracles.json')
    allowed = {str((Path(plugin_root) / name).resolve()): digest for name, digest in current.items()} if plugin_root else {}
    catalog_paths = {(entry.get('name'), str(Path(entry.get('path', '/nonexistent')).resolve())) for entry in catalog}
    names = {entry.get('name') for entry in catalog}
    if disabled and (names.intersection(SKILLS) or 'ryo-workflows-router' in names):
        problems.append('disabled_catalog_target')
    if not disabled and not set(SKILLS).issubset(names):
        problems.append('target_catalog_missing_skills')
    for entry in catalog:
        path = Path(entry.get('path', '/nonexistent'))
        if not any(path.resolve().is_relative_to(root.resolve()) for root in readable_roots):
            problems.append('catalog_path_outside_readable_roots')
            continue
        if path.is_symlink() or not path.is_file() or sha256(path) != entry.get('sha256'):
            problems.append('catalog_path_hash_mismatch')
        elif not disabled and entry.get('name') in SKILLS:
            expected = repo / identity.PLUGIN / 'skills' / entry['name'] / 'SKILL.md'
            if sha256(path) != sha256(expected):
                problems.append('catalog_source_mismatch')
        if disabled and entry.get('sha256') in known:
            problems.append('disabled_catalog_content')
    for root in readable_roots:
        if not root.is_dir() or root.is_symlink():
            problems.append('uninspectable_readable_root')
            continue
        for path in root.rglob('*'):
            if path.is_symlink():
                problems.append('readable_root_symlink')
            elif path.is_file():
                digest = sha256(path)
                if digest == oracle_hash or path.name == 'oracles.json':
                    problems.append('readable_evaluator_oracle')
                if disabled and digest in known:
                    problems.append('disabled_readable_target_content')
                elif not disabled and digest in known and allowed.get(str(path.resolve())) != digest:
                    problems.append('target_readable_unapproved_resource')
                name = known_entrypoint(path)
                if name and (disabled or name == 'ryo-workflows-router' or (name, str(path.resolve())) not in catalog_paths):
                    problems.append('disabled_readable_target_entrypoint' if disabled else 'uncataloged_target_entrypoint')
    return sorted(set(problems))


def evidence_exists(item):
    if (not isinstance(item, dict) or not valid_path_string(item.get('path')) or
            not valid_sha256(item.get('sha256'))):
        return False
    path = Path(item['path'])
    return path.is_file() and not path.is_symlink() and sha256(path) == item['sha256']


def valid_path_string(value):
    return isinstance(value, str) and bool(value) and '\x00' not in value


def valid_sha256(value):
    return isinstance(value, str) and re.fullmatch(r'[a-f0-9]{64}', value) is not None


def prompt_matches(run):
    if (not isinstance(run.get('case_id'), str) or run['case_id'] not in original_prompts()['prompts'] or
            run.get('mode') not in ('explicit', 'implicit', 'disabled') or
            run.get('prompt_revision') != 'stage1-immutable' or
            run.get('original_prompts_sha256') != ORIGINAL_PROMPTS_SHA256 or
            not valid_path_string(run.get('prompt_path'))):
        return False
    if run['mode'] == 'explicit' and run['case_id'] not in cases()['owners']:
        return False
    expected = (prompt_for(run['case_id'], run['mode']) + '\n').encode('utf-8')
    if (run.get('prompt_utf8') != expected.decode('utf-8') or
            run.get('prompt_sha256') != hashlib.sha256(expected).hexdigest()):
        return False
    if 'run_id' in run and run['run_id'] != run['case_id'] + '-' + run['mode']:
        return False
    path = Path(run['prompt_path'])
    return path.is_file() and not path.is_symlink() and path.read_bytes() == expected


def preflight(plan, evidence):
    """Check supplied evidence, not runner enforcement; authorization never follows from a timeout."""
    if not isinstance(plan, dict) or not isinstance(evidence, dict):
        raise ValueError('plan and evidence must be objects')
    blockers = []
    repo = Path(plan['repo'])
    if plan.get('original_prompts_sha256') != original_prompts()['prompts_sha256']:
        blockers.append('original_prompt_group_identity')
    if identity.compare(repo, repo / identity.PLUGIN)['source']['payload_sha256'] != plan['source']['payload_sha256']:
        blockers.append('source_identity')
    for run in plan['runs']:
        if not prompt_matches(run):
            blockers.append('prompt_identity:' + run['run_id'])
        if tree_manifest(Path(run['workspace'])) != run['fixture_manifest']:
            blockers.append('fixture_identity:' + run['run_id'])
    if not plan['compiled_fixtures']:
        blockers.append('baseline_pdfs_unprepared')
    for key in ('isolation_evidence', 'runtime_evidence', 'authentication_evidence',
                'budget_evidence', 'permissions_evidence', 'execution_authorization'):
        if not evidence_exists(evidence.get(key)):
            blockers.append(key)
    budget = evidence.get('budget', {})
    if not (isinstance(budget.get('max_runs'), int) and budget['max_runs'] >= len(plan['runs']) and
            isinstance(budget.get('max_output_tokens'), int) and budget['max_output_tokens'] > 0):
        blockers.append('budget')
    runtime = evidence.get('runtime', {})
    for key in ('client_version', 'client_binary_sha256', 'requested_model', 'effective_model',
                'normal_effort', 'planning_effort'):
        if not runtime.get(key) or runtime[key] == 'unknown':
            blockers.append(key)
    if runtime.get('requested_model') != runtime.get('effective_model'):
        blockers.append('effective_model_mismatch')
    if evidence.get('authentication_method') != 'runner-native-no-copy':
        blockers.append('authentication_boundary')
    disposable = Path(evidence.get('disposable_root', '/nonexistent')).absolute()
    bounded = (disposable.resolve().is_relative_to(Path('/tmp').resolve()) and
               disposable.resolve() != Path('/tmp').resolve() and
               disposable.is_dir() and not disposable.is_symlink())
    if not bounded:
        blockers.append('disposable_root')
    for mode in ('target', 'disabled'):
        catalog = evidence.get(mode, {})
        roots = [Path(value) for value in catalog.get('readable_roots', [])]
        if not roots:
            blockers.append(mode + '_readable_roots')
        if not bounded or any(not root.resolve().is_relative_to(disposable.resolve()) for root in roots):
            blockers.append(mode + '_readable_root_boundary')
        else:
            blockers.extend(catalog_problems(catalog.get('catalog', []), roots, repo, disabled=mode == 'disabled',
                                             plugin_root=catalog.get('plugin_root')))
    target_root = evidence.get('target', {}).get('plugin_root')
    if (not target_root or not bounded or
            not Path(target_root).resolve().is_relative_to(disposable.resolve()) or
            not identity.compare(repo, Path(target_root))['file_identity_matches']):
        blockers.append('target_resource_identity')
    return {'prerequisites_satisfied': not blockers, 'blockers': sorted(set(blockers)),
            'llm_executed': False,
            'scope': 'Offline validation of supplied evidence. Independently review runner enforcement before execution.'}


def validate_result(result):
    if not isinstance(result, dict):
        return False
    # Validate the externally supplied shapes before accessing nested fields.
    loaded = result.get('loaded_resources', [])
    usage = result.get('usage', {})
    timing = result.get('timing', {})
    artifacts = result.get('artifact_hashes', {})
    if (not isinstance(loaded, list) or not all(isinstance(item, dict) for item in loaded) or
            not isinstance(usage, dict) or not isinstance(timing, dict) or not isinstance(artifacts, dict)):
        return False
    if 'source' in usage and not isinstance(usage['source'], str):
        return False
    for key in ('observations', 'unverified'):
        values = result.get(key, [])
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            return False
    for key in ('input_tokens', 'output_tokens'):
        value = usage.get(key)
        if value is not None and (type(value) is not int or value < 0):
            return False
    for value in (usage.get('cost'), timing.get('preflight_seconds'), timing.get('task_wall_seconds')):
        if value is not None and (type(value) not in (int, float) or value < 0 or
                                  (type(value) is float and not math.isfinite(value))):
            return False
    if not all(isinstance(key, str) and valid_sha256(value) for key, value in artifacts.items()):
        return False
    if 'evidence' in usage and not evidence_exists(usage['evidence']):
        return False
    if not prompt_matches(result):
        return False
    if result.get('execution') not in ('executed-and-passed', 'executed-and-failed', 'inconclusive'):
        return False
    if not all(isinstance(result.get(key), str) and result[key] for key in
               ('runtime_version', 'client_binary_sha256', 'effective_model', 'normal_effort', 'planning_effort')):
        return False
    if not all(evidence_exists(result.get(key)) for key in ('catalog_evidence', 'effective_config_evidence')):
        return False
    if result.get('selection') not in ('selected', 'not-selected', 'inconclusive'):
        return False
    if result.get('selection') != 'inconclusive' and not loaded:
        return False
    if any(usage.get(key) is not None for key in ('input_tokens', 'output_tokens', 'cost')):
        if not evidence_exists(usage.get('evidence')):
            return False
    return all(evidence_exists(item.get('evidence')) and evidence_exists(item) for item in loaded)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare_parser = commands.add_parser('prepare')
    prepare_parser.add_argument('--source-repo', type=Path, required=True)
    prepare_parser.add_argument('--destination', type=Path, required=True)
    prepare_parser.add_argument('--compile-fixtures', action='store_true')
    preflight_parser = commands.add_parser('preflight')
    preflight_parser.add_argument('--plan', type=Path, required=True)
    preflight_parser.add_argument('--evidence', type=Path, required=True)
    record_parser = commands.add_parser('check-result')
    record_parser.add_argument('result', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            result = prepare(args.source_repo, args.destination, args.compile_fixtures)
            print(json.dumps({'runs_prepared': len(result['runs']), 'llm_executed': False}))
            return 0
        if args.command == 'preflight':
            result = preflight(json.loads(args.plan.read_text()), json.loads(args.evidence.read_text()))
            print(json.dumps(result, indent=2))
            return 0 if result['prerequisites_satisfied'] else 2
        try:
            record = json.loads(args.result.read_text())
        except json.JSONDecodeError as error:
            parser.exit(2, f'Invalid evaluation result record: {error}\n')
        if not validate_result(record):
            parser.exit(2, 'Invalid evaluation result record\n')
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(2, f'Evaluation preparation error: {type(error).__name__}: {error}\n')


if __name__ == '__main__':
    raise SystemExit(main())
