import importlib.util
import json
import shutil
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'scripts/skill_audits/ryo_workflows'
spec = importlib.util.spec_from_file_location('workflow_eval', TOOLS / 'run_eval.py')
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


class EvaluationTests(unittest.TestCase):
    def test_original_prompts_match_historical_stage1(self):
        original = evaluation.original_prompts()
        baseline = ROOT / 'config/codex/docs/skill-audits/ryo-workflows/stage1/03_baseline.md'
        self.assertEqual(original['prompts'], evaluation.extract_prompts(baseline.read_text()))
        self.assertEqual(len(original['prompts']), 12)
        self.assertEqual(evaluation.sha256(baseline), original['source_sha256'])

    def test_explicit_prefix_is_the_only_prompt_change(self):
        implicit = evaluation.prompt_for('B-02', 'implicit')
        self.assertEqual(evaluation.prompt_for('B-02', 'disabled'), implicit)
        self.assertEqual(evaluation.prompt_for('B-02', 'explicit'),
                         '$creating-and-editing-typst-figures を使って、' + implicit)

    def test_focused_plan_has_nine_runs_and_no_oracle_in_inputs(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as folder:
            plan = evaluation.prepare(ROOT, Path(folder) / 'evaluation')
            self.assertEqual(len(plan['runs']), 9)
            self.assertEqual(plan['runs'][0]['case_id'], 'B-02')
            for run in plan['runs']:
                workspace = Path(run['workspace'])
                self.assertFalse((workspace / 'oracle.json').exists())
                self.assertTrue((workspace / 'TASK.md').exists())
                self.assertEqual(run['execution'], 'designed-but-unexecuted')
                self.assertIsNone(run['usage']['input_tokens'])
            result = evaluation.preflight(plan, {})
            self.assertFalse(result['prerequisites_satisfied'])
            self.assertFalse(result['llm_executed'])
            self.assertIn('budget', result['blockers'])
            self.assertIn('isolation_evidence', result['blockers'])

    def test_fixture_mutation_blocks_preflight(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as folder:
            plan = evaluation.prepare(ROOT, Path(folder) / 'evaluation')
            Path(plan['runs'][0]['workspace'], 'TASK.md').write_text('changed')
            self.assertIn('fixture_identity:B-02-implicit', evaluation.preflight(plan, {})['blockers'])

    def test_disabled_copy_is_detected_by_content_not_only_name(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as folder:
            path = Path(folder) / 'renamed.txt'
            path.write_bytes((ROOT / 'config/codex/plugins/ryo-workflows/skills/dotfiles-deploy/SKILL.md').read_bytes())
            problems = evaluation.catalog_problems([], [Path(folder)], ROOT, disabled=True)
            self.assertTrue(problems)

    def test_catalog_must_match_all_six_entrypoint_paths_and_hashes(self):
        problems = evaluation.catalog_problems([], [], ROOT, disabled=False)
        self.assertIn('target_catalog_missing_skills', problems)
        problems = evaluation.catalog_problems([{'name': 'extrip-to-ics', 'path': '/absent', 'sha256': 'bad'}], [], ROOT, disabled=True)
        self.assertIn('disabled_catalog_target', problems)

    def test_catalog_cannot_hash_paths_outside_declared_readable_roots(self):
        path = ROOT / 'config/codex/plugins/ryo-workflows/skills/extrip-to-ics/SKILL.md'
        with tempfile.TemporaryDirectory(dir='/tmp') as folder:
            entry = {'name': 'extrip-to-ics', 'path': str(path), 'sha256': evaluation.sha256(path)}
            problems = evaluation.catalog_problems([entry], [Path(folder)], ROOT, disabled=False)
        self.assertIn('catalog_path_outside_readable_roots', problems)

    def test_preflight_does_not_scan_unbounded_catalog_roots(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as folder:
            plan = evaluation.prepare(ROOT, Path(folder) / 'evaluation')
            evidence = {'target': {'readable_roots': [str(ROOT)]}}
            result = evaluation.preflight(plan, evidence)
            self.assertIn('disposable_root', result['blockers'])
            self.assertIn('target_readable_root_boundary', result['blockers'])

    def test_preflight_checks_supplied_complete_evidence_without_executing(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as folder:
            root = Path(folder)
            plan = evaluation.prepare(ROOT, root / 'evaluation')
            # Simulate the compiler flag only; this unit test does not certify PDFs.
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
            record.write_text('Unit-test declarations, not live runner evidence.')
            reference = {'path': str(record), 'sha256': evaluation.sha256(record)}
            evidence = {key: reference for key in ('isolation_evidence', 'runtime_evidence',
                        'authentication_evidence', 'budget_evidence', 'permissions_evidence',
                        'execution_authorization')}
            evidence.update(disposable_root=folder, authentication_method='runner-native-no-copy',
                budget={'max_runs': 9, 'max_output_tokens': 200},
                runtime={key: 'synthetic' for key in ('client_version', 'client_binary_sha256',
                         'requested_model', 'effective_model', 'normal_effort', 'planning_effort')},
                target={'plugin_root': str(plugin), 'readable_roots': [str(plugin)],
                    'catalog': [{'name': name, 'path': str(plugin / 'skills' / name / 'SKILL.md'),
                                 'sha256': evaluation.sha256(plugin / 'skills' / name / 'SKILL.md')}
                                for name in evaluation.SKILLS]},
                disabled={'readable_roots': [str(disabled)], 'catalog': []})
            result = evaluation.preflight(plan, evidence)
            self.assertTrue(result['prerequisites_satisfied'], result['blockers'])
            self.assertFalse(result['llm_executed'])
            evidence['runtime']['effective_model'] = 'different'
            self.assertIn('effective_model_mismatch', evaluation.preflight(plan, evidence)['blockers'])
            leaked = disabled / 'renamed.txt'
            shutil.copyfile(plugin / 'skills/extrip-to-ics/SKILL.md', leaked)
            self.assertIn('disabled_readable_target_content', evaluation.preflight(plan, evidence)['blockers'])

    def test_selection_and_usage_claims_need_observation_evidence(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as folder:
            path = Path(folder) / 'evidence.txt'
            path.write_text('synthetic runtime evidence')
            reference = {'path': str(path), 'sha256': evaluation.sha256(path)}
            result = evaluation.result_template('B-02', 'implicit')
            prompt = Path(folder) / 'prompt.txt'
            prompt.write_bytes(result['prompt_utf8'].encode('utf-8'))
            result['prompt_path'] = str(prompt)
            result.update(execution='executed-and-passed', runtime_version='synthetic',
                          client_binary_sha256='synthetic', effective_model='synthetic',
                          normal_effort='medium', planning_effort='medium',
                          catalog_evidence=reference, effective_config_evidence=reference)
            self.assertTrue(evaluation.validate_result(result))
            result['selection'] = 'selected'
            self.assertFalse(evaluation.validate_result(result))
            result['selection'] = 'inconclusive'
            result['usage']['output_tokens'] = 12
            self.assertFalse(evaluation.validate_result(result))

    def test_result_requires_runtime_evidence_and_does_not_invent_usage(self):
        result = evaluation.result_template('B-02', 'implicit')
        self.assertEqual(result['selection'], 'inconclusive')
        self.assertFalse(evaluation.validate_result(result))
        self.assertEqual(result['loaded_resources'], [])
        self.assertIsNone(result['usage']['cost'])


if __name__ == '__main__':
    unittest.main()
