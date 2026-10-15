---
name: dotfiles-deploy
description: Generate managed dotfiles, select host overlays, or prepare and apply a scoped local or remote deployment. Not for ordinary source edits or configuration reviews.
---

# Dotfiles Deploy Workflow

## Scope

Use this when generating configuration, selecting overlays, or applying the user's dotfiles stack. A configuration review or ordinary source edit alone does not require deployment steps.

## Source And Generation

- Use the selected source checkouts or worktrees, not an assumed primary checkout. Include applicable overlays in order: base, private, host; check local-only fragments when they affect generation.
- Read the relevant README section when generation or deployment behavior is unclear. Inspect generated output for the requested targets; generation alone does not authorize writing deployed files.
- Edit managed sources rather than generated live files. Compare the candidate with the deployed target before apply; preserve unrelated app-managed settings instead of replacing them with a partial generated configuration.

## Apply

- For a remote target, establish the intended account, home, and checkout type before constructing commands. Select host manifests with explicit `--host-name`; avoid accidental local expansion inside SSH commands.
- Dry-run the requested targets. Apply only with authorization for those targets, then dry-run the same targets again to verify convergence. Service reloads and remote deployment need their own applicable authorization.

## Scoped Dry-run Examples

Substitute the selected checkouts and target filter; check that the reported targets match the request. These are alternatives, not a sequence. Run the remote-context example on the intended host.

```text
./install --dry-run --context local --private <private-checkout> --only <target>
./install --dry-run --context remote --private <private-checkout> --hosts <hosts-checkout> --host-name <host> --only <target>
```
