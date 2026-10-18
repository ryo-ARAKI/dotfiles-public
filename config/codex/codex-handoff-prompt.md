# Codex Handoff Prompt

Use this prompt when preparing a handoff for a fresh Codex session.
Prefer a fresh session at a major phase boundary, such as research to
implementation or implementation to PR/review, when the current thread has
accumulated substantial tool output. Do not wait for context exhaustion, and
do not split a narrow task whose remaining work is cheaper to finish in place.

Write the handoff to `/tmp/codex-handoff.md` by replacing the whole file.
Do not paste the handoff body into chat. After writing the file, reply only
with the saved path, the recommended launch command, a one-sentence selection
reason, and the initial prompt for the next session.

The user will specify one phase:

- `phase=research` for investigation and policy/design decisions
- `phase=issue` for creating or updating an implementation issue before edits
- `phase=implementation` for continuing code or document changes
- `phase=pr` for cleanup, verification, commits, and PR readiness
- `phase=review` for PR review comments, CI failures, and requested changes

If the phase is missing, infer it from the current work. If it is still
ambiguous, choose the narrowest phase that lets the next session act safely.

## Output Contract

Create `/tmp/codex-handoff.md` with this structure:

- `# Codex Handoff`
- `phase:`
- `handoff_path:` with `direct-goal`, `issue-goal`, `issue-only`, `pr`, or
  `review`
- `handoff_reason:`
- `recommended_profile:`
- `recommended_model:` with the actual model ID
- `recommended_reasoning_effort:` for normal execution
- `recommended_plan_reasoning_effort:` for planning mode
- `model_selection_reason:` tied to the next unresolved judgment
- `delegation_authority:` with `not_granted` or the approved split and scope
- `launch_config_check:` with the deployed config root, base/profile values,
  overrides needed, and anything still unverified
- `launch_command:` matching the profile, model, and both efforts
- `recommended_mode:`
- `cwd:`
- `repo:`
- `branch:`
- `worktree:`
- `issue_or_pr:`
- `source_of_truth:`
- `active_goal:`
- `goal_action:` with `create`, `select`, `continue`, or `none`
- `goal:`
- `done_when:`
- `git_state:` with `clean/dirty/staged/untracked`, `base_ref`,
  `ahead_behind`, `last_commit`, `staged_summary`, `okay_to_touch`, and
  `do_not_touch`
- `user_confirmations:` for explicit permissions and constraints
- `current_state:` with `completed`, `confirmed`, and `important_files`
- `decisions:`
- `next:` as a numbered list
- `first_commands:` as a short shell block
- `verification:` with `ran`, `results`, and `still_needed`
- `constraints:`

Target 60-80 lines and keep the file under 100 lines. Prefer concise bullets
and concrete file paths. Write task instructions, not a conversation summary.
Use `unknown` for
unavailable values and `none` for intentionally absent values. Use
`handoff_path` for the route from planning to execution: `direct-goal` when the
next session should create a `/goal` directly from this handoff, `issue-goal`
when the next session should read an issue before creating a `/goal`,
`issue-only` when the next session should create or update the issue and stop,
and `pr` or `review` for those specialized phases. Use `handoff_reason` for why
a fresh session is being used, such as context budget, switching profile, PR
cleanup, or review follow-up. Use `source_of_truth` to name the file or repo
copy to edit and any deployed or generated copies not to edit directly. Make
`constraints` include either an explicit scope boundary or a `do_not_expand`
note.

## Mode Guidance

Separate profile, model, and the two reasoning efforts. Honor explicit user
choices first; otherwise choose from the unresolved judgment and the benefit
of parallel work, rather than inheriting the previous session's effort or
using work volume alone:

| Recommendation | Model | Normal / planning effort | Remaining work |
| --- | --- | --- | --- |
| `quick` | `gpt-6-luna` | medium / medium | Narrow routine steps with clear targets and acceptance checks |
| `default` with high overrides | `gpt-6.1-sol` | high / high | Local fix with a known cause and approach |
| `default` | `gpt-6.1-sol` | xhigh / max | Ordinary investigation, implementation, and verification |
| `deep` | `gpt-6.1-sol` | max / max | Competing hypotheses, difficult design, or numerical validity |
| `reviewer` | `gpt-6.1-sol` | high / high; max / max for difficult review | Independent read-only review |

Recommend max from the start when difficult judgment is already apparent; do
not require an xhigh failure first. Gather missing evidence before increasing
effort. Permission, network, and runner failures alone, routine edit volume,
and a planning phase alone do not justify a higher recommendation. The
configured default planning effort remains max; distinguish it from the
reason for selecting a model or normal effort. The xhigh default reflects
usage and preference, not measured optimality. Effort-specific quality and
usage-limit multipliers are unverified.

Consider Sol ultra only when meaningful independent parts make parallel work
useful. Describe the split and benefit, verify the installed client's model
availability and selection method, and record both actual efforts. Do not
assume CLI, API, and UI support match or infer delegation permission from
ultra. Record `delegation_authority: not_granted` unless the user approved a
split and scope. If ultra is unavailable or parallel work cannot help or is
not authorized, consider available Sol max with sequential work. If max is
unavailable, report the limitation and an available alternative explicitly.
Never imply an unavailable setting succeeded or switch to Astra automatically.

Astra is normally avoided because of its larger usage-limit cost. It requires
a concrete Sol max limitation, a stated comparison purpose, and explicit
approval for the target task. A profile name does not establish that approval.

Before writing `launch_command`, inspect the actual base config and selected
standalone profile under the launch environment's `CODEX_HOME` (normally
`~/.codex`). Record the paths and effective model, normal effort, and planning
effort in `launch_config_check`, along with differences from managed source.
The loading order is base config, selected profile, then explicit CLI
overrides. Source edits alone do not establish deployment. If a deployed
value is different or unknown, explicitly override the model and each
unconfirmed effort; do not recommend a bare old `deep` that still selects
Astra. Confirm named profiles exist. For reviews, confirm the reviewer
profile's read-only permissions and instructions; if missing or unverified,
report the prerequisite and wait for configuration verification rather than
substituting `deep`.

Use `-m`, `-c 'model_reasoning_effort="..."'`, and
`-c 'plan_mode_reasoning_effort="..."'` as needed. For example, these commands
make both efforts explicit even with an older deployment:

```fish
# Local correction; default means no --profile argument.
codex -C <cwd> -m gpt-6.1-sol -c 'model_reasoning_effort="high"' -c 'plan_mode_reasoning_effort="high"'
# Deep investigation, after confirming deep.config.toml exists.
codex -C <cwd> --profile deep -m gpt-6.1-sol -c 'model_reasoning_effort="max"' -c 'plan_mode_reasoning_effort="max"'
# Difficult review keeps the verified read-only reviewer profile.
codex -C <cwd> --profile reviewer -m gpt-6.1-sol -c 'model_reasoning_effort="max"' -c 'plan_mode_reasoning_effort="max"'
```

Only use ultra CLI overrides after verifying their syntax and support in the
installed client. Otherwise give a verified Sol launch command and instruct
the user to inspect `/model` and its More reasoning options before selecting
ultra; mark ultra and its effective efforts as unverified until checked.

Set `recommended_mode:` from the phase:

- `phase=research` -> `/plan`
- `phase=issue` -> `/plan`
- `phase=implementation` -> `/goal`
- `phase=pr` -> `/goal`
- `phase=review` -> `/goal`

Use `/plan` when the next session still needs to settle scope, policy, or user
choices before editing. Use `/review` instead of `/goal` only when the task is
to perform a fresh code review, not to address existing review feedback.

For `/goal`, include concrete `active_goal:`, `goal_action:`, `goal:`, and
`done_when:` fields. Set `goal_action: create` when no active goal exists,
`select` when an existing goal should be chosen, and `continue` when the current
goal should be resumed. For `/goal` work touching Git, use the current
app-managed or user-specified worktree when one exists; otherwise tell the next
session to create or verify an isolated worktree before editing.

Use `handoff_path: direct-goal` when `/plan` has settled enough detail to
implement without creating a GitHub issue. Use `handoff_path: issue-goal` when a
GitHub issue is the durable implementation contract. Both are valid routes:
`/plan` -> `/goal` and `/plan` -> issue -> `/goal`.

Keep `first_commands` limited to confirmation commands such as `pwd`,
`git status`, issue/PR inspection, and targeted file reads. Do not include
implementation commands, destructive commands, or commands that assume the
handoff state is already current.

## Phase Guidance

### `phase=research`

Optimize the handoff for preserving facts and choices before implementation.
Include:

- investigated files, issues, PRs, docs, logs, or official sources
- important design or policy decisions and why they matter
- unresolved questions and user confirmations still needed
- whether the next implementation handoff should be `direct-goal` or
  `issue-goal`
- the smallest implementation scope that follows from the research
- confirmation commands the next session should run before changing files

Do not imply implementation is approved unless the current thread made that
clear.

For Codex plugin or config research, include the source file under
`dotfiles-private`, the generated or deployed copy that must not be edited
directly, and any `codex plugin list --json` check still needed after deploy.

### `phase=issue`

Optimize the handoff for creating or updating a GitHub issue, not for editing
code. Use `handoff_path: issue-only` when the next session should stop after the
issue is ready. Include:

- the repository and issue command or issue number to inspect
- the problem statement, intended outcome, acceptance criteria, and out of scope
- implementation notes that are specific enough for a future `/goal`
- open questions that still need user confirmation before implementation
- the recommended `/new` prompt for the implementation session

The issue should be usable as the durable contract for a later
`handoff_path: issue-goal` implementation handoff. Do not imply implementation
is approved merely because the issue was created.

### `phase=implementation`

Optimize the handoff for immediately continuing edits.
Include:

- exact files or modules likely to change next
- whether implementation should start from this handoff directly or from an
  issue named in `issue_or_pr`
- already implemented pieces
- remaining work in priority order
- local conventions and design constraints to preserve
- targeted checks to run while implementing

Make `next` a concrete implementation checklist. If `handoff_path: issue-goal`
or `issue_or_pr` names an issue, tell the next session to inspect the issue and
resolve any implementation-blocking details with the user before creating the
`/goal`.

For Codex plugin or config changes, include a verification step that checks the
actual Codex-visible state, such as `codex plugin list --json`, after applying
or deploying the dotfiles source.

### `phase=pr`

Optimize the handoff for making a branch merge-ready.
Include:

- PR purpose and closing issue references
- commit/staging intent and intended commit split
- plan/spec/tmp files to keep or delete
- redundant tests to consider pruning and representative tests to keep
- PR body requirements: Summary, Validation, Closes
- verification gates before ready/merge

Make `done_when` describe the merge-ready condition, not just "PR exists".

### `phase=review`

Optimize the handoff for addressing review feedback rigorously.
Include:

- current review/CI state
- unresolved review threads, CI failures, and reviewer replies still needed
- unresolved review comments by file and issue
- for each comment: implement / push back / needs user confirmation
- whether each comment or thread is safe to resolve
- already addressed comments
- tests or logs that reproduce failures
- reply points for reviewers

Do not mark feedback resolved unless code, tests, and replies are actually
handled.

## Exclusions

Do not include:

- long conversation logs
- long diffs
- long command outputs
- private reasoning or hidden chain of thought
- abandoned alternatives that no longer affect the work
- broad background that the next session can rediscover cheaply

## Final Reply Format

After creating `/tmp/codex-handoff.md`, reply in chat with only:

```text
Created /tmp/codex-handoff.md.
Recommended next session:
<launch_command matching recommended_profile, recommended_model, and both reasoning efforts>
<one sentence explaining model_selection_reason and any selection still needing verification>

Initial prompt:
/tmp/codex-handoff.md を読んで、そこに書かれた recommended_mode、phase、handoff_path、goal_action、next に従って作業してください。recommended_mode が /goal なら active_goal と goal_action を確認し、必要なら goal と done_when から /goal を作成または選択してください。handoff_path が issue-goal なら issue_or_pr のissueも確認し、実装を妨げる未確定事項を対話的に詰めてから /goal を作成してください。まずcwd、git状態、source_of_truth、関連issue/PR状態を確認し、巨大出力は要約してください。
```

For `handoff_path: direct-goal`, phrase the initial prompt around creating or
continuing a `/goal` from `/tmp/codex-handoff.md`. For `handoff_path:
issue-goal`, include the issue number and ask the next session to inspect the
issue before creating the `/goal`. For `handoff_path: issue-only`, report the
issue number and the recommended `/new` prompt for the future implementation
session instead of implying that implementation should start immediately.

For `recommended_profile: default`, use `codex -C <cwd>` without `--profile`;
otherwise select the named profile with `--profile`. Include model and both
effort overrides required by `launch_config_check`. Keep `--profile reviewer`
for difficult reviews and set both efforts to max. Give the selection reason
in one short sentence even when the model or effort stays the same.
