from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from dotfiles_installer.reporting import read_text_if_exists

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    tomllib = None


PUBLIC_FRAGMENT = Path("config/codex/config.public.toml")
PRIVATE_FRAGMENT = Path("config/codex/config.private.toml")
TARGET_PATH = Path("~/.codex/config.toml")
TARGET_MODE = 0o644


@dataclass(frozen=True)
class CodexConfigPlan:
    content: str
    source_label: str
    target_path: Path
    target_label: str


def _read_required_fragment(path: Path) -> str:
    if not path.exists():
        raise ValueError(f"Codex config fragment not found: {path}")
    return path.read_text(encoding="utf-8")


def _validate_toml(text: str) -> None:
    if tomllib is None:
        return
    tomllib.loads(text)


def plan_codex_config(base_root: Path, private_root: Path | None, *, home_root: Path | None = None) -> CodexConfigPlan:
    public_path = base_root / PUBLIC_FRAGMENT
    fragments = [_read_required_fragment(public_path)]
    source_label = str(PUBLIC_FRAGMENT)

    if private_root is not None:
        private_path = private_root / PRIVATE_FRAGMENT
        fragments.append(_read_required_fragment(private_path))
        source_label = f"{source_label} + {PRIVATE_FRAGMENT}"

    content = "\n\n".join(fragment for fragment in fragments if fragment)
    _validate_toml(content)

    expanded_home = home_root if home_root is not None else Path.home()
    return CodexConfigPlan(
        content=content,
        source_label=source_label,
        target_path=expanded_home / ".codex" / "config.toml",
        target_label=str(TARGET_PATH),
    )


def apply_codex_config(plan: CodexConfigPlan, *, backup_root: Path, dry_run: bool) -> str:
    current_text = read_text_if_exists(plan.target_path)
    if current_text == plan.content:
        return "nochange"
    if dry_run:
        return "would_apply"

    plan.target_path.parent.mkdir(parents=True, exist_ok=True)
    if plan.target_path.exists():
        backup_path = backup_root / plan.target_path.relative_to(plan.target_path.anchor)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(plan.target_path, backup_path)

    plan.target_path.write_text(plan.content, encoding="utf-8")
    plan.target_path.chmod(TARGET_MODE)
    return "applied"
