from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dotfiles_installer.codex_runtime import CodexRuntimePlan
from dotfiles_installer.codex_runtime import apply_codex_runtime
from dotfiles_installer.codex_runtime import plan_codex_runtime


PUBLIC_FRAGMENT = Path("config/codex/config.public.toml")
PRIVATE_FRAGMENT = Path("config/codex/config.private.toml")
PRIVATE_LOCAL_FRAGMENT = Path("config/codex/config.private.local.toml")
TARGET_PATH = Path("~/.codex/config.toml")


@dataclass(frozen=True)
class CodexConfigPlan:
    content: str
    source_label: str
    target_path: Path
    target_label: str
    runtime_plan: CodexRuntimePlan


def _read_required_fragment(path: Path) -> str:
    if not path.exists():
        raise ValueError(f"Codex config fragment not found: {path}")
    return path.read_text(encoding="utf-8")


def plan_codex_config(
    base_root: Path,
    private_root: Path | None,
    *,
    home_root: Path | None = None,
    context: str = "local",
) -> CodexConfigPlan:
    public_path = base_root / PUBLIC_FRAGMENT
    fragments = [_read_required_fragment(public_path)]
    source_label = str(PUBLIC_FRAGMENT)
    if private_root is not None:
        private_path = private_root / PRIVATE_FRAGMENT
        fragments.append(_read_required_fragment(private_path))
        source_label = f"{source_label} + {PRIVATE_FRAGMENT}"
        private_local_path = private_root / PRIVATE_LOCAL_FRAGMENT
        if context == "local" and private_local_path.exists():
            fragments.append(_read_required_fragment(private_local_path))
            source_label = f"{source_label} + {PRIVATE_LOCAL_FRAGMENT}"
    content = "\n\n".join(fragment for fragment in fragments if fragment)
    expanded_home = home_root if home_root is not None else Path.home()
    target_path = expanded_home / ".codex" / "config.toml"
    runtime_plan = plan_codex_runtime(
        content,
        target_path=target_path,
        source_label=source_label,
        target_label=str(TARGET_PATH),
    )
    return CodexConfigPlan(
        content,
        source_label,
        target_path,
        str(TARGET_PATH),
        runtime_plan,
    )


def plan_codex_profile(
    content: str,
    *,
    target_path: Path,
    source_label: str,
    target_label: str,
) -> CodexRuntimePlan:
    return plan_codex_runtime(
        content,
        target_path=target_path,
        source_label=source_label,
        target_label=target_label,
    )


def apply_codex_config(plan: CodexConfigPlan, *, backup_root: Path, dry_run: bool) -> str:
    return apply_codex_runtime(plan.runtime_plan, backup_root=backup_root, dry_run=dry_run)
