# dotfiles-public

Public base layer for my personal dotfiles.

This repository holds the configuration files that I am comfortable publishing.
It is designed to work together with two companion repositories:

- `dotfiles-public`: shareable base configuration
- `dotfiles-private`: personal overlay for non-public or machine-specific settings
- `dotfiles-hosts`: host-specific overrides for machines such as `h200`, `Reshiram`, and `Zekrom`

The installer in this repository reads manifest files and applies the selected files to their real locations under `$HOME`.

## What Is Public Here

This repository is meant for settings that are either reusable as-is or easy to understand and adapt:

- shell startup files such as `.bashrc`, `.profile`, `.screenrc`, `.tmux.conf`, `.vimrc`
- shared `fish` configuration
- shared terminal and desktop config such as Terminator and Projecteur
- the installer itself, its manifest format, and tests

Settings that contain private information or strong host-specific assumptions are kept out of this repository and belong in `dotfiles-private` or `dotfiles-hosts`.

## Repository Topology

The intended layer order is:

```text
base < private < host
```

In other words:

- `dotfiles-public` provides the base layer
- `dotfiles-private` overrides the base layer when the same target path appears in both manifests
- `dotfiles-hosts` is reserved for per-host overrides on top of the first two layers

Current implementation status:

- `dotfiles-public` is fully wired into `./install`
- `dotfiles-private` is supported through `--private /path/to/dotfiles-private`
- `dotfiles-hosts` is supported through `--hosts /path/to/dotfiles-hosts`

## Directory Layout

```text
.
├── install
├── manifest/
│   └── base.tsv
├── home/
│   ├── .bashrc
│   ├── .bashrc_remote
│   ├── .profile
│   ├── .gitconfig
│   ├── .latexmkrc
│   ├── .vimrc
│   ├── .screenrc
│   └── .tmux.conf
├── config/
│   ├── fcitx5/
│   ├── fish/
│   ├── gh/
│   ├── terminator/
│   ├── Projecteur/
│   └── xbindkeys/
├── dotfiles_installer/
│   ├── apply.py
│   ├── context.py
│   ├── manifest.py
│   ├── planner.py
│   └── reporting.py
└── tests/
```

The rough split is:

- `home/`: files that normally live directly under `$HOME`
- `config/`: files that normally live under `$HOME/.config`
- `manifest/`: source-to-target mapping rules
- `dotfiles_installer/`: installer logic
- `tests/`: `unittest` coverage for manifest parsing, planning, context detection, apply logic, and CLI behavior

Notable tracked config beyond the original shell files includes:

- `home/.latexmkrc` for LaTeX build defaults
- `config/fish/fish_plugins` for `fisher` plugin declarations
- `config/fcitx5/config` for local IME behavior
- `config/gh/config.yml` for GitHub CLI defaults and aliases

## Manifest Format

The installer uses a tab-separated manifest with four columns:

```text
source<TAB>target<TAB>mode<TAB>when
```

Example:

```text
home/.bashrc	~/.bashrc	0644	always
home/.bashrc_remote	~/.bashrc	0644	remote
config/fish/config.fish	~/.config/fish/config.fish	0644	always
```

Column meanings:

- `source`: path inside the repository
- `target`: destination path on the target machine
- `mode`: file mode to apply after installation
- `when`: one of `always`, `local`, or `remote`

## How `install` Works

`./install` is a manifest-driven installer. It does not hardcode file placement rules in the script beyond reading the manifests and applying the selected entries.

The current behavior is:

1. Detect execution context as `local` or `remote`
2. Load `manifest/base.tsv`
3. Optionally load `dotfiles-private/manifest/private.tsv` when `--private` is given
4. Optionally load `dotfiles-hosts/manifest/<host>.tsv` when `--hosts` is given
5. Resolve conflicts by layer precedence
6. Build the final plan
7. For each selected file:
   show a short preview or diff
   ask for confirmation unless `--yes` is used
   back up the current file if it exists
   install the new file and set the requested mode
8. Print a summary at the end

### Context Detection

Context detection is based on:

- `--context local|remote` when explicitly supplied
- otherwise `SSH_CONNECTION` or `SSH_TTY`
- otherwise `local`

That makes it possible to keep separate local and remote bash entry points:

- local: `home/.bashrc -> ~/.bashrc`
- remote: `home/.bashrc_remote -> ~/.bashrc`

### Host Detection

Host overlay loading is opt-in and only happens when `--hosts` is provided.

Host manifest selection is based on:

- `--host-name <name>` when explicitly supplied
- otherwise `socket.gethostname()`

That means:

- `--hosts /path/to/dotfiles-hosts --host-name h200` loads `manifest/h200.tsv`
- `--hosts /path/to/dotfiles-hosts` loads `manifest/<current-hostname>.tsv`

If `--hosts` is given and the resolved host manifest does not exist, `./install` exits with an error instead of silently ignoring the host layer.

### Backup Behavior

Existing files are copied to:

```text
~/.dotfiles-backup/<timestamp>/
```

before they are overwritten.

### Preview and Summary Behavior

Interactive runs show a short unified diff before asking for confirmation.

Run summaries track:

- `applied`
- `skipped`
- `nochange`
- `overridden`

Dry runs do not write anything. They report what would be applied and show overridden lower-layer entries when relevant.

## Command Reference

### Dry-run the local base layer

```bash
./install --dry-run --context local
```

### Dry-run local with private overlay

```bash
./install --dry-run --context local --private ~/github/dotfiles-private
```

### Dry-run remote with private overlay

```bash
./install --dry-run --context remote --private ~/github/dotfiles-private
```

### Dry-run remote with private and host overlays

```bash
./install --dry-run --context remote \
  --private ~/github/dotfiles-private \
  --hosts ~/github/dotfiles-hosts \
  --host-name h200
```

### Apply interactively on a remote machine

```bash
./install --context remote --private ~/github/dotfiles-private
```

### Apply interactively with private and host overlays

```bash
./install --context remote \
  --private ~/github/dotfiles-private \
  --hosts ~/github/dotfiles-hosts
```

### Apply without prompting

```bash
./install --yes --context remote --private ~/github/dotfiles-private
```

### Apply without prompting with private and host overlays

```bash
./install --yes --context remote \
  --private ~/github/dotfiles-private \
  --hosts ~/github/dotfiles-hosts
```

### Limit the run to one file family

```bash
./install --dry-run --context local --only vimrc
./install --dry-run --context remote --only fish/conf.d
```

`--only` matches by substring against either the manifest source path or the target path.

Additional option notes:

- `--private`: path to the `dotfiles-private` repository root
- `--hosts`: path to the `dotfiles-hosts` repository root
- `--host-name`: optional host manifest name override; defaults to the current hostname
- `--host-name` requires `--hosts`
- `--hosts` fails if `manifest/<resolved-host>.tsv` does not exist

## Daily Workflow

### Update local config and sync it into this repo

Typical flow:

1. edit the actual config file under `$HOME`
2. copy the updated content into the matching file in this repository
3. update `manifest/base.tsv` if you added a new file
4. run a dry-run
5. run tests
6. commit

### Add a new public file

1. decide whether the file belongs in `home/` or `config/`
2. add the file to this repository
3. add one row to `manifest/base.tsv`
4. choose the correct `when` value
5. run:

```bash
./install --dry-run --context local --only <pattern>
python3 -m unittest discover -s tests -v
```

### Move a file to the private layer

If a file should no longer be public:

1. remove it from `dotfiles-public`
2. add it to `dotfiles-private`
3. add or update the row in `dotfiles-private/manifest/private.tsv`
4. verify with:

```bash
./install --dry-run --context local --private ~/github/dotfiles-private
```

## Public vs Private vs Host-Specific

Use this rule of thumb:

- `dotfiles-public`
  Settings that are safe to publish and broadly reusable
- `dotfiles-private`
  Personal settings, private values, or config with strong path assumptions
- `dotfiles-hosts`
  Overrides that should apply only to one named host

Examples of things that belong in `dotfiles-private`:

- `~/.shell_env`
- `~/.config/starship.toml`
- `fish` aliases or abbreviations that depend on personal paths
- editor settings that assume local executables or local tooling layout

Examples of things that may eventually belong in `dotfiles-hosts`:

- hostname-specific environment variables
- GPU or CUDA toolchain setup that differs by machine
- shell config that should exist on `h200` but not elsewhere

## Remote Hosts

The current operational target set is:

- `h200`
- `Reshiram`
- `Zekrom`

Today, these hosts share the same base and private layers by default.
Host-specific manifests in `dotfiles-hosts` are opt-in and are only loaded when `--hosts` is provided.

For now, the recommended remote workflow is:

1. log into the remote machine
2. clone or update `dotfiles-public` under `~/github/dotfiles-public`
3. clone or update `dotfiles-private` under `~/github/dotfiles-private`
4. clone or update `dotfiles-hosts` under `~/github/dotfiles-hosts`
5. run:

```bash
./install --dry-run --context remote \
  --private ~/github/dotfiles-private \
  --hosts ~/github/dotfiles-hosts \
  --host-name "$(hostname)"
./install --context remote \
  --private ~/github/dotfiles-private \
  --hosts ~/github/dotfiles-hosts \
  --host-name "$(hostname)"
```

## Verification

The current test suite is plain `unittest`:

```bash
python3 -m unittest discover -s tests -v
```

Useful spot checks:

```bash
./install --dry-run --context local
./install --dry-run --context remote --private ~/github/dotfiles-private
./install --dry-run --context remote --private ~/github/dotfiles-private --hosts ~/github/dotfiles-hosts --host-name h200
```

## Safety Notes

- Interactive runs show diffs before confirmation, but they assume text files encoded as UTF-8.
- `--yes` skips prompts. Use it only after a dry-run you trust.
- `docs/` is intentionally not part of the normal committed content in this repository during design/plan work.
- `--hosts` is strict: if the resolved host manifest is missing, the command exits with an error.

## Current Limitations

- diff rendering is text-oriented and not designed for binary files
- the test suite does not yet exhaustively cover every interactive branch or mode-only diff case

## Related Repositories

- `dotfiles-public`: public base layer
- `dotfiles-private`: private overlay
- `dotfiles-hosts`: host-specific overlay stubs
