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
Managed settings use the standard service tier (`service_tier = "default"`).

| Selection | Model | Normal / planning effort | Remaining work |
| --- | --- | --- | --- |
| `quick` | `gpt-6-luna` | medium / medium | Narrow routine steps with clear targets and acceptance checks |
| `default` with explicit high overrides | `gpt-6.1-sol` | high / high | Local fix with a known cause and approach; routine reviews still keep `reviewer` |
| `default` (no `--profile`) | `gpt-6.1-sol` | xhigh / max | Ordinary investigation, implementation, and verification requiring existing specifications |
| `deep` | `gpt-6.1-sol` | max / max | Difficult judgment, competing hypotheses, design tradeoffs, or numerical validity; reviews keep `reviewer` with max overrides |
| `subagent` profile | `gpt-6-luna` | medium / medium | Bounded delegated work within granted authority |
| Spawned defaults | `gpt-6-luna` | medium normal; planning effort must be checked in the launch environment | Defaults specify the spawned model and normal effort, not a separate planning value |
| `reviewer` role/profile | `gpt-6.1-sol` | high / high; max / max overrides for difficult reviews | Independent read-only review of requirements, diffs, and evidence |
| Explicit Sol ultra selection, after support checks | Verify the available Sol model ID | Verify both effective efforts | Meaningful independent parts make parallel work useful |
| Astra, with task-specific approval | Verify the available Astra model ID | Record both effective efforts | Compare against a concrete Sol max limitation for a stated purpose |

Recommend max from the start when difficult judgment is already apparent; an
xhigh failure is not a prerequisite. Gather missing evidence first. Permission,
network, or runner failures alone do not justify higher effort. Large amounts
of routine editing alone do not justify max or ultra; start with max for one
tightly coupled hard problem. A planning phase alone does not justify a max
recommendation; distinguish that recommendation from the profile's configured
planning effort. The xhigh default reflects usage and user preference, not
measured optimality; quality differences and usage-limit multipliers between
efforts are unverified.

For ultra, explain the proposed independent parts and benefit, check the
installed client's availability and selection method, and keep model selection
separate from delegation authority. Do not assume CLI, API, and UI support are
identical. Sol max with sequential work is an alternative when parallel work
cannot help or is not authorized. If max or ultra is unavailable, report that
and an available alternative without switching to Astra or implying the
requested setting succeeded.

Astra is normally avoided because of its larger usage-limit cost. Explain the
specific Sol max limitation and comparison purpose before seeking explicit
approval for that task; a profile name does not establish approval.

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
2. Record profile, actual model ID, normal and planning efforts, the next
   unresolved judgment explaining the recommendation, and delegation authority
   separately in the handoff. Record the deployed config root, paths, effective
   values, required overrides, and unresolved checks in `launch_config_check`.
3. If deployed values differ or are unknown, use explicit model and both effort
   overrides as needed. An old deployed `deep` may still select Astra; never
   recommend that bare profile based only on the current managed source.
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
# Local correction with both efforts explicit.
codex -m gpt-6.1-sol -c 'model_reasoning_effort="high"' -c 'plan_mode_reasoning_effort="high"'
# Deep investigation, including with an old Astra deep profile.
codex --profile deep -m gpt-6.1-sol -c 'model_reasoning_effort="max"' -c 'plan_mode_reasoning_effort="max"'
# Difficult review retains verified reviewer permissions.
codex --profile reviewer -m gpt-6.1-sol -c 'model_reasoning_effort="max"' -c 'plan_mode_reasoning_effort="max"'
```

Public guidance: [Models](https://learn.chatgpt.com/docs/models) and
[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
Check current official guidance when resolving public product behavior;
these links do not establish availability in a particular client or account.
