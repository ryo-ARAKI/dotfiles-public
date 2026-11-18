# Model Selection And Launch Checks

Read this document when recommending a model or effort, constructing a launch
command, or preparing a handoff. The common Working Agreements own explicit
choices, Astra approval conditions, and authority; this document supplies the
selection and configuration details. These are user policies and managed source
values, not evidence of live client/account availability or deployment.

## Roles and selection

Keep profile, actual model ID, normal reasoning effort, and planning effort
separate. Explicit user choices take precedence. Otherwise choose from the
unresolved judgment and the benefit of parallel work, rather than inheriting
the previous phase's effort or using work volume alone.
Managed settings use Standard speed (`service_tier = "default"`). Consider
Fast or Ultrafast when reduced latency is worth the additional usage.
Check the selected model, plan, and client for availability and rates.

| Selection | Model | Normal / planning effort | Remaining work |
| --- | --- | --- | --- |
| `default` (no `--profile`) | `gpt-6.2-sol` | medium / medium | Everyday investigation, writing, visual inspection, computer use, implementation, and verification |
| `quick` | `gpt-6.1-terra` | medium / medium | Short checks, routine edits, and work with readily verifiable results |
| Explicit Sol overrides | `gpt-6.2-sol` | high or xhigh, selected for each mode | Complex investigation or implementation, interpreting specifications, reconciling sources, or preserving technical meaning |
| `deep` | `gpt-6.2-sol` | max / max | Difficult judgment, competing hypotheses, design tradeoffs, or numerical validity; reviews keep `reviewer` with max overrides |
| `subagent` profile | `gpt-6-luna` | medium / medium | Bounded delegated work within granted authority |
| Spawned defaults | `gpt-6-luna` | medium normal; planning effort must be checked in the launch environment | Defaults specify the spawned model and normal effort, not a separate planning value |
| `reviewer` role/profile | `gpt-6.2-sol` | high / high; max / max overrides for difficult reviews | Independent read-only review of requirements, diffs, and evidence |
| Explicit Sol ultra selection, after support checks | `gpt-6.2-sol` | Verify both effective efforts | Independent parts benefit from parallel work and automatic delegation is approved |
| Astra, with task-specific approval | `gpt-6.2-astra` | Record both effective efforts | Evaluate an expected improvement over Sol max against a specified deliverable |

Sol medium is the starting point for everyday work. Use Terra medium for
short, readily verifiable tasks where latency or usage matters. Select normal
and planning effort by error impact, remaining judgment, verifiability, and
rework cost. Consider high or xhigh when interpreting competing specifications,
when investigation repeats without narrowing hypotheses, or when changes could
affect surrounding contracts or scientific meaning. State the reason for any
recommended model or effort switch during a task.

Recommend max from the start when difficult judgment is already apparent; an
xhigh failure is not a prerequisite. Gather missing evidence first. Permission,
network, or runner failures alone do not justify a different model or higher
effort. Large amounts of routine editing alone do not justify max or ultra;
start with max for one tightly coupled hard problem. A planning phase alone
does not justify max. Quality differences, latency, and usage-limit multipliers
between models and efforts remain unverified for the user's actual tasks.

Ultra reasoning can automatically delegate work. Select it only with explicit
authorization for that delegation on the task. Explain the independent parts
and expected benefit, and verify support and selection in the installed client.
Use Sol max when the difficult work is tightly coupled or delegation is outside
the approved scope. If max or ultra is unavailable, report the available Sol
options. Ultrafast is a service tier that changes generation speed and usage.

Astra requires task-specific approval because of its larger usage cost. Before
seeking approval, state the concrete limitation expected with Sol max, the
improvement expected from Astra, and the deliverable or outcome to compare.
Use the applicable Work or Codex usage guidance for subscription usage and
credits. API token prices apply to API billing.

Reviewers inspect requirements, diffs, and evidence themselves and report
findings without editing, committing, or pushing. Keep the `reviewer` role or
profile and its read-only permissions and instructions. For difficult design,
numerical, or permission reviews, override both normal and planning effort to
max. Do not substitute `deep` for the reviewer profile.

## Launch and handoff checks

1. Identify the launch environment and its actual `CODEX_HOME` (normally
   `~/.codex`). Inspect the deployed base config and the selected standalone
   profile, including its permissions and instructions. Confirm named profiles
   exist. Loading order is base config, selected profile, then explicit CLI
   overrides. Compare these with managed source values; source edits alone do
   not establish deployment.
   The deployed base may retain the previous session's model, effort, or service
   tier selections. Differences from managed defaults are expected runtime state,
   not by themselves a deployment error; do not reset them merely to match source.
2. Record profile, actual model ID, normal and planning efforts, the next
   unresolved judgment explaining the recommendation, and delegation authority
   separately in the handoff. Record the deployed config root, paths, effective
   values, required overrides, and unresolved checks in `launch_config_check`.
3. If deployed values differ or are unknown, use explicit model and both effort
   overrides as needed. Do not infer the deployed profile's values from the
   managed source.
4. For reviews, verify read-only reviewer permissions and instructions first.
   If missing or unverified, report that prerequisite and wait for configuration
   verification instead of substituting `deep`.
5. Verify ultra syntax and support in the installed client before using an ultra
   CLI override. When CLI syntax is unverified, inspect `/model` and its supported
   More reasoning options. Otherwise give a verified Sol launch command and
   mark ultra and its effective efforts unverified until checked.

Run the following examples from the intended checkout, after confirming the
named profile exists and, for review, remains read-only. `default` means no
`--profile` argument; `-C` may select the intended cwd when needed.

```fish
# Complex investigation with both efforts explicit; use xhigh when warranted.
codex -m gpt-6.2-sol -c 'model_reasoning_effort="high"' -c 'plan_mode_reasoning_effort="high"'
# Deep investigation with both efforts explicit.
codex --profile deep -m gpt-6.2-sol -c 'model_reasoning_effort="max"' -c 'plan_mode_reasoning_effort="max"'
# Difficult review retains verified reviewer permissions.
codex --profile reviewer -m gpt-6.2-sol -c 'model_reasoning_effort="max"' -c 'plan_mode_reasoning_effort="max"'
```

Public guidance includes [Models](https://learn.chatgpt.com/docs/models),
[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), and
[Fast and Ultrafast](https://learn.chatgpt.com/docs/agent-configuration/speed).
Check current official guidance when resolving public product behavior;
these links do not establish availability in a particular client or account.
