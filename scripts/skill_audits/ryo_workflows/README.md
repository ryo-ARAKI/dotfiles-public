# Ryo Workflows source audit tools

These standard-library tools are repository maintenance resources, outside the public plugin manifest. They neither deploy resources nor launch an LLM. Run from the repository root with Python 3.10 or later. Keep evidence outside both plugin roots and use disposable `/tmp` workspaces without reservation content or credentials.

## Public and observed resource identity

```sh
python3 -B scripts/skill_audits/ryo_workflows/identity.py --source-repo . --observed-root /tmp/skill-audit/target/plugin --output /tmp/skill-audit/identity.json
```

The manifest defines the expected public paths and deployed modes. JSON records the source HEAD and relevant dirty state, manifest/content SHA-256, release label, paths, type, size, mode and mtime. Content identity excludes mtime and modes; file identity also checks deployed modes, missing/additional resources and unexpected types. Source files can have different checkout modes from the deployed `0644` mode. Unexpected files are inventoried without reading their contents; symlink resources are not followed. Do not point this tool at unrelated configuration or a credentials directory.

Exit status is `0` for a match, `1` for a comparison mismatch and `2` for invalid inputs or an operational error. `--output` creates a new evidence file exclusively. No source or observed resource is modified. Filesystem observations are a point-in-time check, without malicious-race protection.

Optional `--expected-overlay` takes an independently approved JSON file:

```json
{"files":{"skills/private/SKILL.md":{"sha256":"<64 lowercase hex characters>","mode":"0644","origin":"approved-private-revision-and-path"}}}
```

Each declared addition or replacement must have an exact hash, mode and approval origin. This file records a prior approval; generating it does not grant approval. Never read or modify active private overlays to populate a test fixture. A release label is separate from content identity. Matching resources do not prove catalog visibility, skill selection, or actual loaded resources; those fields remain unverified.

## Focused evaluation preparation

```sh
python3 -B scripts/skill_audits/ryo_workflows/run_eval.py prepare --source-repo . --destination /tmp/skill-audit/evaluation --compile-fixtures
```

The destination must not exist. `--compile-fixtures` uses the installed Typst executable and fonts, without installing packages. Omitting it prepares source-only fixtures and leaves a blocking PDF prerequisite. The focused matrix contains nine runs: B-02 implicit/explicit/disabled, then B-01, B-03 and N-01 implicit/disabled. Preserve `original_prompts.json`: it contains the exact twelve Stage 1 P/N/B prompts and their historical source hash. Implicit and disabled prompts are identical; only explicit invocation adds the skill prefix. Stage 2 M-001 through M-008 revisions remain separate acceptance metadata. P-02, P-06 and supplemental X cases are designed but not prepared or executed here.

Each run has `input/`, `prompt.txt` and `result-template.json`; the plan records source and fixture hashes. Every run records `prompt_path`, `prompt_utf8` (including its final LF), `prompt_sha256`, and `original_prompts_sha256`. Preparation writes those exact UTF-8 bytes. Preflight and result validation require the file bytes, recorded text and SHA-256 to match the original case and mode; the original group is pinned to the Stage 1 digest. Missing or modified prompts, changed hashes and explicit/implicit/disabled mismatches are invalid. Regenerate older plans/templates that lack these fields; intentional prompt changes require a separately identified evaluation revision. Treat `TASK.md` as a common fixture clarification across modes. `oracles.json` is evaluator-only and is never copied into `input/`. Figure fixtures preserve four independent condition tuples. B-02 intentionally contains an upper-interval error and swapped legend labels; B-01 and B-03 use the correct figure. Compile and visually inspect baseline PDFs before comparison.

## Offline preflight and runtime evidence

```sh
python3 -B scripts/skill_audits/ryo_workflows/run_eval.py preflight --plan /tmp/skill-audit/evaluation/plan.json --evidence /tmp/skill-audit/prerequisites.json
```

An empty evidence object safely reports missing prerequisites with exit `2`. A supplied evidence object needs:

- `disposable_root`: an existing task-owned subdirectory of `/tmp`, containing all catalog copies and declared readable roots. Never declare the host home, repository, cache, auth files, or unrelated configuration as an evaluation root.
- `target` and `disabled`: each has `readable_roots` and `catalog` entries (`name`, absolute `path`, `sha256`). `target.plugin_root` identifies the disposable public payload, deployed with manifest modes. The target catalog must expose all six skill entrypoints at matching hashes. The control catalog and all its declared readable roots must exclude the six skills, the old router, and renamed copies of known current or audited skill resources. Known entrypoints outside the supplied catalog and the old router are rejected in both modes. Target skill resources are allowed only at their current manifest paths under `target.plugin_root`. Both modes must exclude evaluator oracles.
- `runtime`: `client_version`, `client_binary_sha256`, `requested_model`, `effective_model`, `normal_effort`, `planning_effort`. Requested and effective model must agree. Collect actual client/config evidence; do not infer it from managed config or a requested CLI option.
- `authentication_method`: `runner-native-no-copy`. A separately authorized runner must enforce this boundary without copying credentials into fixtures.
- `budget`: approved positive `max_runs` covering the plan and positive `max_output_tokens`. Set and enforce provider-specific spending or usage limits separately if required by the approval.
- `isolation_evidence`, `runtime_evidence`, `authentication_evidence`, `budget_evidence`, `permissions_evidence`, `execution_authorization`: each references an existing evidence file as `{"path":"/tmp/...","sha256":"..."}`.

The static readable-root check recognizes current public skill hashes, the 17 resource hashes from audited revision `737ba2926d72ad51dccfc0cf6b26cd4d2994a44d` in [audited_skill_hashes.json](audited_skill_hashes.json), known skill/router directory names and simple `name` frontmatter in the first 8192 bytes, and the current oracle hash or reserved filename `oracles.json`. Hash matching also detects renamed exact copies. This is a check for known evaluation resources, not a general security scanner: transformed/paraphrased copies, unknown historical versions, undeclared roots, runtime mounts, instructions and races need separate enforcement and review.

Preflight validates supplied files and declarations; it does not independently establish sandbox enforcement, live authentication behavior, permissions, model configuration, budget enforcement or authority. An isolated external runner and human review of this evidence remain required before execution. It must prevent model access to evaluator oracles in both modes, and to the source repository, active installations and host catalogs that would contaminate a disabled run. Include filesystem, plugin/catalog and instruction surfaces, not only a different working directory. Static preflight success proves neither runtime isolation nor skill-selection correctness. No execution adapter or LLM command is supplied by this project.

Run only after all execution prerequisites and explicit budget/authorization are established. Keep target and control client/model/efforts, inputs, prompts, output constraints and instrumentation comparable. Capture client version and effective settings, catalog entries, actual read/execute events where supported, artifacts, read-only violations and scientific findings. An unsupported observation stays inconclusive. Do not use model self-reports as selection or visual-inspection evidence.

`check-result RESULT.json` returns `0` only for a completed/inconclusive execution record with an unchanged recorded prompt, referenced configuration/catalog evidence and evidence for any claimed loaded resource or measured usage. Invalid JSON or record structure returns `2` with `Invalid evaluation result record`; the API returns `False` for invalid records. `loaded_resources` must be an array of objects containing resource `path`/`sha256` and an observation `evidence` reference. References use nonempty string paths and lowercase SHA-256 strings. `usage`, `timing` and `artifact_hashes` are objects; token counts are nonnegative integers or `null`, cost/times are finite nonnegative numbers or `null`, artifact values are SHA-256 strings, and `observations`/`unverified` are arrays of strings. Selection is `selected`, `not-selected` or `inconclusive`, and must remain `inconclusive` when actual resource reads cannot be observed. Unexecuted templates cannot pass. This is record validation, not automatic task scoring; independently assess the acceptance oracle and raw execution evidence.

Record usage from actual runner/provider measurements; unavailable values stay `null`, including cost. Separate preflight time from task time. No independent before LLM baseline exists, so an after-only run is an absolute assessment, not evidence of improvement. Stage 3 leaves all LLM runs unexecuted.
