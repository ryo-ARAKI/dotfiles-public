"""Offline regressions for CR-001..004; no LLM or active plugin access."""
import copy
import errno
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'scripts/skill_audits/ryo_workflows'
SCRIPT = ROOT / 'config/codex/plugins/ryo-workflows/skills/extrip-to-ics/scripts/build_ics.py'
AUDITED = '737ba2926d72ad51dccfc0cf6b26cd4d2994a44d'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evaluation = load('correction_eval', TOOLS / 'run_eval.py')
ics = load('correction_ics', SCRIPT)


def complete_preflight(root):
    plan = evaluation.prepare(ROOT, root / 'evaluation')
    # Source-only unit fixture: this flag does not certify compiled/inspected PDFs.
    plan['compiled_fixtures'] = True
    plugin = root / 'target/plugin'
    for name, entry in evaluation.identity.public_entries(ROOT).items():
        path = plugin / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / entry['source'], path)
        path.chmod(entry['mode'])
    disabled = root / 'disabled'
    disabled.mkdir()
    record = root / 'synthetic-evidence.txt'
    record.write_text('Synthetic declarations, not runtime enforcement evidence.')
    reference = {'path': str(record), 'sha256': evaluation.sha256(record)}
    evidence = {key: reference for key in ('isolation_evidence', 'runtime_evidence',
                'authentication_evidence', 'budget_evidence', 'permissions_evidence',
                'execution_authorization')}
    evidence.update(disposable_root=str(root), authentication_method='runner-native-no-copy',
        budget={'max_runs': 9, 'max_output_tokens': 200},
        runtime={key: 'synthetic' for key in ('client_version', 'client_binary_sha256',
                 'requested_model', 'effective_model', 'normal_effort', 'planning_effort')},
        target={'plugin_root': str(plugin), 'readable_roots': [str(plugin)],
            'catalog': [{'name': name, 'path': str(plugin / 'skills' / name / 'SKILL.md'),
                         'sha256': evaluation.sha256(plugin / 'skills' / name / 'SKILL.md')}
                        for name in evaluation.SKILLS]},
        disabled={'readable_roots': [str(disabled)], 'catalog': []})
    return plan, evidence


class EvaluationCorrectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='stage3-cr-', dir='/tmp')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.plan, self.evidence = complete_preflight(self.root)

    def blockers(self):
        return evaluation.preflight(self.plan, self.evidence)['blockers']

    def readable_fixture_root(self, mode):
        if mode == 'disabled':
            return self.root / 'disabled'
        # Keep the valid public payload unchanged, so its identity check cannot
        # mask a missed prohibited resource in another declared readable root.
        extra = self.root / 'target/extra'
        extra.mkdir(exist_ok=True)
        roots = self.evidence['target']['readable_roots']
        if str(extra) not in roots:
            roots.append(str(extra))
        return extra

    def test_cr001_valid_target_and_unrelated_control_fixture_pass(self):
        (self.root / 'disabled/anonymous.txt').write_text('Unrelated synthetic fixture\n')
        self.assertEqual(self.blockers(), [])

    def test_cr001_renamed_current_and_audited_resources_are_rejected(self):
        resource = 'skills/creating-and-editing-typst-figures/SKILL.md'
        historical = subprocess.check_output(['git', 'show', f'{AUDITED}:{evaluation.identity.PLUGIN / resource}'], cwd=ROOT)
        for body in ((ROOT / evaluation.identity.PLUGIN / resource).read_bytes(), historical):
            with self.subTest(sha256=hashlib.sha256(body).hexdigest()):
                (self.root / 'disabled/old-skill.txt').write_bytes(body)
                self.assertIn('disabled_readable_target_content', self.blockers())

    def test_cr001_uncataloged_known_entrypoints_are_rejected(self):
        for mode in ('target', 'disabled'):
            root = self.readable_fixture_root(mode)
            for name in ('ryo-workflows-router', 'extrip-to-ics'):
                with self.subTest(mode=mode, name=name):
                    path = root / 'skills' / name / 'SKILL.md'
                    # The legitimate target entrypoint must remain untouched.
                    if path.exists():
                        path = root / 'extra' / name / 'SKILL.md'
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(f'---\nname: "{name}"\ndescription: synthetic entrypoint\n---\nchanged body\n')
                    self.assertIn('disabled_readable_target_entrypoint' if mode == 'disabled' else
                                  'uncataloged_target_entrypoint', self.blockers())
                    path.unlink()

    def test_cr001_renamed_oracle_is_rejected_in_both_modes(self):
        for mode in ('target', 'disabled'):
            with self.subTest(mode=mode):
                path = self.readable_fixture_root(mode) / 'anonymous.txt'
                shutil.copyfile(TOOLS / 'oracles.json', path)
                self.assertIn('readable_evaluator_oracle', self.blockers())
                path.unlink()

    def test_cr001_audited_support_resource_is_rejected(self):
        resource = 'skills/extrip-to-ics/scripts/build_ics.py'
        body = subprocess.check_output(['git', 'show', f'{AUDITED}:{evaluation.identity.PLUGIN / resource}'], cwd=ROOT)
        (self.root / 'disabled/anonymous.py').write_bytes(body)
        self.assertIn('disabled_readable_target_content', self.blockers())

    def test_cr001_renamed_entrypoint_with_changed_body_is_rejected(self):
        for mode in ('target', 'disabled'):
            for newline in ('\n', '\r\n'):
                with self.subTest(mode=mode, newline=newline):
                    path = self.readable_fixture_root(mode) / 'anonymous.txt'
                    path.write_bytes('---\nname: ryo-workflows-router\ndescription: synthetic\n---\nunknown body\n'.replace('\n', newline).encode())
                    self.assertIn('disabled_readable_target_entrypoint' if mode == 'disabled' else
                                  'uncataloged_target_entrypoint', self.blockers())
                    path.unlink()

    def test_cr001_target_cannot_read_extra_audited_resource_copy(self):
        resource = 'skills/extrip-to-ics/scripts/build_ics.py'
        body = subprocess.check_output(['git', 'show', f'{AUDITED}:{evaluation.identity.PLUGIN / resource}'], cwd=ROOT)
        extra = self.root / 'target/extra'
        extra.mkdir()
        (extra / 'anonymous.txt').write_bytes(body)
        self.evidence['target']['readable_roots'].append(str(extra))
        self.assertIn('target_readable_unapproved_resource', self.blockers())

    def test_cr001_historical_hashes_match_the_audited_git_resources(self):
        snapshot = json.loads((TOOLS / 'audited_skill_hashes.json').read_text())
        self.assertEqual(snapshot['source_revision'], AUDITED)
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', AUDITED, '--',
            str(evaluation.identity.PLUGIN / 'skills')], cwd=ROOT).decode().splitlines()
        expected = {}
        for path in paths:
            body = subprocess.check_output(['git', 'show', f'{AUDITED}:{path}'], cwd=ROOT)
            expected[str(Path(path).relative_to(evaluation.identity.PLUGIN))] = hashlib.sha256(body).hexdigest()
        self.assertEqual(snapshot['resources'], expected)

    def test_cr002_every_run_records_exact_prompt_bytes_and_hash(self):
        for run in self.plan['runs']:
            with self.subTest(run=run['run_id']):
                expected = (evaluation.prompt_for(run['case_id'], run['mode']) + '\n').encode('utf-8')
                self.assertEqual(Path(run['prompt_path']).read_bytes(), expected)
                self.assertEqual(run['prompt_utf8'].encode('utf-8'), expected)
                self.assertEqual(run['prompt_sha256'], hashlib.sha256(expected).hexdigest())
        self.assertEqual(self.blockers(), [])

    def test_cr002_modified_or_missing_prompts_are_rejected(self):
        for mode in ('implicit', 'explicit', 'disabled'):
            run = next(r for r in self.plan['runs'] if r['case_id'] == 'B-02' and r['mode'] == mode)
            path = Path(run['workspace']).parent / 'prompt.txt'
            original = path.read_bytes()
            for body in (original + b'x', original.rstrip(b'\n') + b'\r\n', None):
                with self.subTest(mode=mode, body=body):
                    if body is None:
                        path.unlink()
                    else:
                        path.write_bytes(body)
                    self.assertIn('prompt_identity:' + run['run_id'], self.blockers())
                    path.write_bytes(original)

    def test_cr002_prompt_swap_is_rejected_even_with_updated_record_hash(self):
        run = self.plan['runs'][0]
        explicit = next(r for r in self.plan['runs'] if r['mode'] == 'explicit')
        body = (Path(explicit['workspace']).parent / 'prompt.txt').read_bytes()
        (Path(run['workspace']).parent / 'prompt.txt').write_bytes(body)
        run.update(prompt_sha256=hashlib.sha256(body).hexdigest(), prompt_utf8=body.decode())
        self.assertIn('prompt_identity:' + run['run_id'], self.blockers())

    def test_cr002_original_group_and_missing_prompt_metadata_are_rejected(self):
        self.plan['original_prompts_sha256'] = '0' * 64
        self.assertIn('original_prompt_group_identity', self.blockers())
        for field in ('prompt_path', 'prompt_sha256', 'prompt_utf8'):
            with self.subTest(field=field):
                run = self.plan['runs'][0]
                value = run.pop(field, None)
                self.assertIn('prompt_identity:' + run['run_id'], self.blockers())
                run[field] = value

    def test_cr002_hash_mode_and_prompt_path_mismatches_are_rejected(self):
        original = copy.deepcopy(self.plan['runs'][0])
        explicit = next(r for r in self.plan['runs'] if r['mode'] == 'explicit')
        for changes in ({'prompt_sha256': '0' * 64}, {'mode': 'explicit'},
                        {'prompt_path': explicit['prompt_path']}, {'mode': 'unknown'},
                        {'case_id': 'P-03'}, {'prompt_revision': 'changed'}):
            with self.subTest(changes=changes):
                self.plan['runs'][0] = dict(original, **changes)
                self.assertIn('prompt_identity:B-02-implicit', self.blockers())
        self.plan['runs'][0] = original

    def test_cr002_rehashed_original_prompt_group_still_cannot_change(self):
        original = copy.deepcopy(evaluation.original_prompts())
        original['prompts']['B-02'] += 'changed'
        original['prompts_sha256'] = hashlib.sha256(json.dumps(original['prompts'],
            ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
        local = self.root / 'changed-originals'
        local.mkdir()
        (local / 'original_prompts.json').write_text(json.dumps(original))
        with patch.object(evaluation, 'HERE', local), self.assertRaisesRegex(ValueError, 'immutable original prompt group changed'):
            evaluation.original_prompts()

    def executed_result(self):
        result = copy.deepcopy(self.plan['runs'][0])
        reference = self.evidence['runtime_evidence']
        result.update(execution='executed-and-passed', runtime_version='synthetic',
                      client_binary_sha256='synthetic', effective_model='synthetic',
                      normal_effort='medium', planning_effort='medium',
                      catalog_evidence=reference, effective_config_evidence=reference,
                      selection='selected', loaded_resources=[dict(reference, evidence=reference)])
        return result

    def test_cr004_valid_result_with_observed_resource_and_usage_passes(self):
        result = self.executed_result()
        result['usage'].update(output_tokens=12, evidence=self.evidence['runtime_evidence'])
        self.assertTrue(evaluation.validate_result(result))

    def test_cr004_malformed_result_structures_are_invalid(self):
        mutations = [{}, {'loaded_resources': ['bad']}, {'loaded_resources': [None]},
                     {'loaded_resources': None}, {'usage': None}, {'usage': []},
                     {'loaded_resources': [{'path': 42, 'sha256': 'x', 'evidence': {}}]},
                     {'catalog_evidence': {'path': [], 'sha256': 'x'}},
                     {'effective_config_evidence': {'path': '\x00', 'sha256': 'x'}},
                     {'timing': []}, {'artifact_hashes': []}, {'observations': [None]},
                     {'unverified': None}, {'usage': {'output_tokens': []}},
                     {'loaded_resources': [{'path': 'x', 'sha256': 'x', 'evidence': None}]}]
        for changes in mutations:
            with self.subTest(changes=changes):
                result = self.executed_result()
                result.update(changes)
                if not changes:
                    result = None
                self.assertFalse(evaluation.validate_result(result))

    def test_cr002_result_record_rejects_changed_or_missing_prompt(self):
        result = self.executed_result()
        path = Path(result['prompt_path'])
        path.write_bytes(b'Altered task\n')
        self.assertFalse(evaluation.validate_result(result))
        path.unlink()
        self.assertFalse(evaluation.validate_result(result))

    def test_cr004_numeric_and_evidence_shapes_are_checked(self):
        for changes in ({'usage': {'cost': float('inf')}}, {'usage': {'input_tokens': True}},
                        {'usage': {'source': []}}, {'timing': {'task_wall_seconds': []}},
                        {'artifact_hashes': {'figure.pdf': None}}):
            with self.subTest(changes=changes):
                result = dict(self.executed_result(), **changes)
                self.assertFalse(evaluation.validate_result(result))

    def test_cr004_large_json_integer_does_not_raise_overflow(self):
        result = self.executed_result()
        result['usage'].update(cost=10 ** 1000, evidence=self.evidence['runtime_evidence'])
        self.assertTrue(evaluation.validate_result(result))

    def test_cr004_cli_invalid_record_has_controlled_error(self):
        for changes in ({'loaded_resources': ['bad']}, {'usage': None},
                        {'catalog_evidence': {'path': 42, 'sha256': 'bad'}}):
            with self.subTest(changes=changes):
                result = self.executed_result()
                result.update(changes)
                path = self.root / 'result.json'
                path.write_text(json.dumps(result))
                completed = subprocess.run([sys.executable, '-B', str(TOOLS / 'run_eval.py'),
                                            'check-result', str(path)], capture_output=True, text=True)
                self.assertEqual(completed.returncode, 2)
                self.assertIn('Invalid evaluation result record', completed.stderr)
                self.assertNotIn('Traceback', completed.stderr)

    def test_cr004_cli_rejects_invalid_json_and_null_root(self):
        for body in ('null', '[null]', '{'):
            with self.subTest(body=body):
                path = self.root / 'result.json'
                path.write_text(body)
                completed = subprocess.run([sys.executable, '-B', str(TOOLS / 'run_eval.py'),
                                            'check-result', str(path)], capture_output=True, text=True)
                self.assertEqual(completed.returncode, 2)
                self.assertIn('Invalid evaluation result record', completed.stderr)
                self.assertNotIn('Traceback', completed.stderr)


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
