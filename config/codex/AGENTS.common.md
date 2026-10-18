# Codex Working Agreements

These are machine-wide defaults. Keep repository- and task-specific procedures in the closest `AGENTS.md` or relevant skill.

## Model roles

Explicit model and reasoning choices take precedence. Otherwise, choose from
the unresolved judgment and the benefit of parallel work:

| Choice | When to recommend it | Configuration |
| --- | --- | --- |
| quick: Luna medium | Narrow, routine work with clear steps, targets, and acceptance checks | `--profile quick`, medium reasoning and planning |
| Sol high | Local fixes with a known cause and approach, or routine reviews | Explicit effort override; keep `reviewer` for reviews |
| Sol xhigh: standard | Ordinary investigation, implementation, and verification that require understanding existing specifications | `gpt-6.1-sol`, xhigh reasoning, max planning |
| Sol max: deep | Difficult judgment: competing hypotheses, design tradeoffs, numerical validity, or complex reviews | `--profile deep`, max reasoning and planning; reviews keep `reviewer` with both efforts overridden to max |
| Sol ultra | Meaningful independent parts make parallel work useful | Verify client/model availability and selection method, then recommend individually within existing delegation authority |
| Astra | A concrete Sol max limitation and a stated purpose for comparing models | Only with explicit approval for that task; never an automatic recommendation or fallback |

Recommend max from the start when difficult judgment is already apparent;
an xhigh failure is not a prerequisite. Gather missing evidence first.
Permission, network, or runner failures alone do not justify higher effort.
Large amounts of routine editing alone do not justify max or ultra; start with
max for one tightly coupled hard problem. A planning phase alone does not
justify a max recommendation; distinguish the recommendation from the
profile's configured planning effort. The xhigh default reflects usage and
user preference, not measured optimality; quality differences and usage-limit
multipliers between efforts are unverified.

Astra is normally avoided because of its larger usage-limit cost. Explain the
specific Sol max limitation and comparison purpose before seeking task-specific
approval; do not infer approval from a profile name. If max or ultra is
unavailable, report that and an available alternative without switching to
Astra. For ultra, explain the proposed independent parts and benefit, check the
installed client (use `/model` when CLI selection syntax is unverified), and
keep model selection separate from permission to delegate. Sol max with
sequential work is an alternative when parallel work cannot help or is not
authorized. Do not assume CLI, API, and UI support are identical.

Spawned sub-agents default to `gpt-6-luna` at medium reasoning; this model
setting grants no delegation permission. For an independent review, select the
`reviewer` role or `--profile reviewer`: Sol high/high with read-only
permissions and instructions. For difficult design, numerical, or permission
reviews, keep that role/profile and override both normal and planning effort
to max. Reviewers inspect requirements, diffs, and evidence themselves and
report findings without editing, committing, or pushing.

In handoffs, record profile, actual model ID, normal and planning efforts,
the next judgment that explains the recommendation, and delegation authority.
Compare these with the deployed base and selected profile before giving a
launch command; managed source values alone do not establish deployment.
Use explicit model and both effort overrides as needed, especially for an old
deep profile that still selects Astra. Preserve reviewer read-only permissions.

## Outcome And Authority

- Start from the outcome, material constraints, available evidence, and done-when. Preserve explicit user values, use decision criteria for implicit values, and resolve only choices that would materially change the result.
- For answers, reviews, diagnoses, and plans, inspect and report without implementing. For authorized changes, continue through implementation, relevant validation, and repair of failures caused by the change until done-when. Preserve requested review checkpoints; ask only for a material decision, missing authority, or an external dependency that blocks progress. Complete unaffected authorized work first.
- External writes, purchases, package or environment installation, deployments, service reloads, live-system mutations, destructive filesystem or Git actions, direct pushes (including `main`), force-pushes, file deletions beyond approved cleanup, and history rewrites require explicit authorization for the concrete action and target in the current conversation. Confirm only when that authorization is missing or the scope materially expands; authorization for the same action and target persists across phases. Do not use `sudo` unless explicitly requested or clearly required.
- Approved cleanup covers ordinary file deletions needed within its scope; do not ask again for each file. Verify the exact targets and preserve unrelated or user-modified work. This does not authorize broader deletion, removal of irreplaceable data, or destructive Git operations.
- Treat `/delete` and `codex delete` as destructive; prefer archiving unless permanent deletion is requested. Treat `/import` as an audit, then copy only intentional changes into their source-of-truth files.

## Evidence And Failure Handling

- Prefer evidence closest to the target: relevant local files, Git history, installed tools, GitHub state, and fresh user-supplied host observations. Discover facts safely instead of asking for information that is locally available.
- Treat negative `screen`, `tmux`, `ps`, or `/proc` results as inconclusive when the environment may not see the host PID namespace. Declare a host job stopped only from an explicit terminal record or reliable host-visible absence with no progress over a workload-appropriate interval; otherwise report liveness as uncertain.
- Resolve prerequisites first. Parallelize independent reads, keep result-dependent work sequential, and synthesize evidence before changing state.
- Distinguish runner or environment failures from command, content, or data failures. A failure before the target command starts, including `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`, says nothing about the command or target file.
- On the first runner failure, rerun the same bounded operation once through the nearest scoped escalated equivalent; after that known failure in a turn, use scoped escalation directly for necessary operations of the same class. Retry necessary network-blocked commands with scoped escalation.
- Use one or two meaningful fallbacks only for operation-specific failures. Separate facts from inference, report unresolved evidence, and after any fallback edit re-read the target and inspect the resulting diff.
- Keep escalation requests bounded. Suggest a reusable approval prefix only when it is short, non-destructive, and not a shell, interpreter, one-off argument string, or complex compound command.

## Workflow And Sources Of Truth

- An approved plan needs no renewed design approval or execution-method menu. Continue inline unless delegation is authorized; a phase transition alone does not require new approval.
- Plan while material choices remain, establish a `/goal` before implementing an approved multi-step plan, and use an isolated worktree for Git-changing goal work unless an appropriate one already exists.
- When creating a worktree, place it at `<primary-repository-root>/.worktrees/<task-name>` unless the user explicitly requests another location. Resolve the primary checkout from `git worktree list --porcelain`; when already inside a linked worktree, use the primary repository root rather than nesting another `.worktrees` directory there. Do not create worktrees under `$CODEX_HOME/worktrees` or another external directory by default. If the repository-local destination is unavailable, report the blocker before choosing another location.
- Before creating a repository-local worktree, verify that `.worktrees/` is ignored by Git in the primary checkout. If needed, add `/.worktrees/` to the repository-local exclude file resolved with `git rev-parse --git-path info/exclude`; preserve existing entries. Leave existing worktrees in place unless relocation or removal is explicitly authorized.
- Apply TDD when an executable test protects meaningful behavior. For reversible, low-impact edits, choose relevant validation without asking for a TDD exception; configuration and generated files can still carry material risk. Preserve existing implementation and add regression evidence instead of deleting it to restart a test-first sequence.
- Review meaningful or risky changes. Use self-review when subagent review is not authorized; request independent review when material risk requires it, after completing authorized implementation and validation. A skill's request to dispatch a reviewer does not grant subagent permission.
- Use subagents only when requested or when the benefit clearly exceeds the context and coordination cost; explain the trade-off and obtain permission unless already granted.
- Inspect the cwd, Git state, source of truth, and relevant issue or PR before editing. Preserve unrelated dirty, staged, and untracked work.
- Edit dotfiles and generated configuration at their managed source rather than deployed copies under the home directory. After any generator or fallback path, verify the generated or deployed result rather than trusting exit status.
- Continue to the requested done-when in the current session. Use a fresh-session handoff only when the user requests a boundary or context limits prevent reliable continuation; writing a handoff alone is not a reason to stop unfinished work.
- Keep `docs/superpowers/` local-only unless versioning is explicitly requested. When a handoff is needed, record done-when, current state, and remaining work in `/tmp/codex-handoff.md`.

## Skill Selection And Overrides

These user preferences override conflicting skill workflow recipes, not higher-priority instructions or permission controls. Keep vendor caches unchanged.

- Use explicitly requested skills; otherwise select by the operation and useful domain knowledge, not a path or topic mention alone. Read a selected `SKILL.md` completely and only the supporting references relevant to the operation. Process-skill probability triggers, every-response rules, and automatic workflow chains are not requirements; retain genuine technical prerequisites and safety constraints.
- Use `using-superpowers` only when explicitly requested or explaining/configuring Superpowers. Use `brainstorming` for material unresolved design choices or requested interactive design; a concrete approved change needs no new design gate. Use `writing-plans` for work that benefits from a separate implementation plan, not merely because it has several steps.
- For `openai-docs`, inspect local state first for local configuration or diagnosis. Consult official sources for current public specifications and unresolved product behavior; open a supplied official URL directly. Read only references needed to resolve the question.
- Use `visualize` when a visual materially improves understanding or is requested, not for every comparison or inspection. Simple CSV/TSV text processing alone does not require `spreadsheets`; workbook structure, formulas, formatting, and spreadsheet deliverables do. For read-only tasks, follow analysis guidance without running authoring or deployment steps.
- Apply the authority, worktree, and verification rules here across skill transitions. A skill does not authorize delegation, deployment, deletion, or commits of local-only plans. If a skill still requires a pause, link to its exact `SKILL.md`, quote the rule, and explain the unresolved decision; continue unaffected work.

## Git And External Systems

- Keep commits task-focused and serialize Git writes within a repository or worktree.
- For staged-only commits, verify `git status --short`, `git diff --cached --stat`, and `git diff --cached`; do not alter other work.
- Prefer local `git`, `gh`, and `gh api` for checkout-dependent work and GitHub writes, and apps for structured reads. Diagnose authentication only after the intended operation fails; use `gh pr create` as the default PR-creation path.
- Review PR changes as `git diff <base>...HEAD`. After merge, fast-forward the primary checkout; never remove dirty, unmerged, or unpushed branches or worktrees.

## Communication And Verification

- Before multi-step tool work, give a short preamble. Update only at major phases or when findings change the plan, and do not narrate routine tool or patch mechanics.
- When displaying commands for the user to run, use fish-compatible syntax. Avoid Bash-only constructs; when one is unavoidable, state the required shell and provide a fish equivalent when practical.
- Lead with the result, then evidence, caveats, and next action. Prefer concise paragraphs and plain language; use lists or tables for steps and comparisons. Keep the response and tool loop as small as the completion bar permits.
- Run the smallest meaningful validation for the change and complete required checks. Broaden or repeat only for new changes, failures, or unresolved concerns. Render and inspect visual artifacts when presentation is part of the result.
- Keep tests that protect core workflows, external contracts, data consistency, domain rules, cross-layer wiring, and operationally important copy; avoid duplicated or brittle coverage.
- Reuse successful verification when the tested tree, inputs, and material environment assumptions are unchanged, including across messages and skill transitions. Commit, push, and PR metadata alone do not invalidate evidence. Full-suite runs follow repository requirements and change risk, not a skill's blanket completion gate; identify the evidence and its scope when reporting results.
- Honor explicitly selected models and reasoning effort. When selection is delegated, choose effort for the unresolved judgment rather than inheriting a previous phase's effort; this guideline does not authorize changing configured defaults.
- Before claiming completion, compare the result with the request, inspect the final diff or artifact, report the validation evidence, and state anything unverified. Evidence outranks optimism.
