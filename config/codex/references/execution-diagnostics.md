# Execution Diagnostics

Read this document when diagnosing execution-environment failures or host-job
liveness. Resolve prerequisites and gather evidence before changing state.
Keep observations separate from inference and report unresolved evidence.

## Runner, network, and target failures

A runner or environment failure before the target command starts says nothing
about the command, file, test, or data. For example,
`bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` is a runner
startup failure, not evidence of a failing target test.

On the first runner failure, rerun the same bounded operation once through the
nearest scoped escalated equivalent. After that known failure in a turn, use
scoped escalation directly for necessary operations of the same class. Retry
necessary network-blocked commands with scoped escalation. Report whether the
target command actually ran; do not turn a failed launch into a target failure.

Keep escalation requests bounded to the necessary operation. Suggest a reusable
approval prefix only when short and non-destructive; never use a shell,
interpreter, one-off argument string, or complex compound command as the prefix.
Escalation does not resolve missing action/target authority; apply the common
authority rules before changing state.

Use one or two meaningful fallbacks only for operation-specific failures.
After any fallback edit, re-read the target and inspect the resulting diff.
If evidence remains unresolved, report the limitation instead of treating a
fallback's exit status as proof of the intended result.

## Host-job liveness

Negative `screen`, `tmux`, `ps`, or `/proc` results are inconclusive when the
environment may not see the host PID namespace. Declare a host job stopped
only from an explicit terminal record or reliable host-visible absence with no
progress over a workload-appropriate interval. Otherwise report liveness as
uncertain. Prefer fresh user-supplied host observations or reliable host-visible
evidence over a sandbox's process inventory.
