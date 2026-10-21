# Worktree And Git Procedures

Read this document before creating a worktree or using the Git procedures
below. The common Working Agreements own authority, isolation, preservation,
and verification policy. Resolve execution-environment failures using
[execution diagnostics](execution-diagnostics.md).

## Inspect and isolate

Inspect cwd, Git state, the managed source, and any relevant issue or PR before
editing. Preserve unrelated dirty, staged, and untracked work. Check
`git worktree list --porcelain` for an appropriate existing worktree before
creating another. Inspect the selected worktree's own branch and status.

```fish
pwd
git status --short
git branch --show-current
git worktree list --porcelain
git remote -v
```

Resolve the primary checkout from the worktree list, even when currently in a
linked worktree. The default destination is
`<primary-repository-root>/.worktrees/<task-name>`; do not nest `.worktrees`
under a linked checkout or use `$CODEX_HOME/worktrees` or another external
directory by default. Use another location only when explicitly requested.
If the repository-local destination is unavailable, report the blocker before
choosing another location. Leave existing worktrees in place unless relocation
or removal is explicitly authorized.

Before creating the worktree, verify `.worktrees/` is ignored in the primary
checkout. If needed, append `/.worktrees/` to the repository-local exclude file
resolved by `git rev-parse --git-path info/exclude`, preserving existing entries.
For example, after substituting the primary checkout identified above:

```fish
set -l task_primary /path/to/primary-checkout
git -C "$task_primary" check-ignore -q .worktrees/
if test $status -ne 0
    set -l task_exclude (git -C "$task_primary" rev-parse --path-format=absolute --git-path info/exclude)
    # Inspect the resolved path and existing entries before appending.
    cat "$task_exclude"
    printf '\n%s\n' '/.worktrees/' >> "$task_exclude"
    git -C "$task_primary" check-ignore -q .worktrees/
end
```

Confirm that check succeeded before creation. Use a platform worktree tool when
it can honor the required destination and ref; otherwise use Git. For example,
after choosing a task name, unused branch, and base ref:

```fish
set -l task_name my-task
git -C "$task_primary" worktree add "$task_primary/.worktrees/$task_name" -b "codex/$task_name" HEAD
git -C "$task_primary/.worktrees/$task_name" status --short
```

`HEAD` here is the primary checkout's HEAD; choose the intended base explicitly
when it differs. Verify the created path and branch, then work from that path.

## Commits, PRs, and merge follow-up

Keep commits task-focused and serialize Git writes within a repository or
worktree. For a staged-only commit, inspect all three before committing; do not
alter other work:

```fish
git status --short
git diff --cached --stat
git diff --cached
```

Prefer local `git`, `gh`, and `gh api` for checkout-dependent work and GitHub
writes, and apps for structured reads. Diagnose authentication only after the
intended operation fails. Use `gh pr create` as the default PR creation path.
Review PR changes as `git diff <base>...HEAD`; for uncommitted implementation,
also inspect the working/staged diff and new files. After merge, fast-forward
the primary checkout. Never remove dirty, unmerged, or unpushed branches or
worktrees.

## Dotfiles sources

Edit managed sources rather than deployed home-directory copies and inspect
generated or deployed output. For concrete generation and deployment steps,
identify the selected source checkout and read its repository README and Codex
README. Use the existing `dotfiles-deploy` skill when available. Local-only
plugins may be absent in remote context; the selected checkout's documentation
remains the source of procedures. Report missing prerequisites rather than
inventing a generation or deployment command.
