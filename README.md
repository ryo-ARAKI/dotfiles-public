# dotfiles-public

Public base layer for personal dotfiles.

## Install

```bash
./install --dry-run --context local
./install --dry-run --context local --only vimrc
./install --dry-run --context remote --private /home/ryo/github/dotfiles-private
./install --yes --context remote --private /home/ryo/github/dotfiles-private
```

Use `--only` to limit output to matching targets or source paths, and `--yes` to apply changes without prompting.

## Layer order

`base < private < host`
