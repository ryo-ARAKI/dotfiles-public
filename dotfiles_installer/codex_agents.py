from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from dotfiles_installer.reporting import read_text_if_exists


COMMON_FRAGMENT = Path("config/codex/AGENTS.common.md")
LOCAL_EXTRA_FRAGMENT = Path("config/codex/AGENTS.local.extra.md")
TARGET_PATH = Path("~/.codex/AGENTS.md")
TARGET_MODE = 0o644


@dataclass(frozen=True)
class CodexAgentsPlan:
    content: str
    source_label: str
    target_path: Path
    target_label: str


def _read_required_fragment(path: Path) -> str:
    if not path.exists():
        raise ValueError(f"Codex AGENTS fragment not found: {path}")
    return path.read_text(encoding="utf-8")


def plan_codex_agents(
    private_root: Path | None,
    *,
    home_root: Path | None = None,
    context: str = "local",
) -> CodexAgentsPlan:
    if private_root is None:
        raise ValueError("dotfiles-private is required to generate Codex AGENTS.md")

    common_path = private_root / COMMON_FRAGMENT
    fragments = [_read_required_fragment(common_path)]
    source_label = str(COMMON_FRAGMENT)

    local_extra_path = private_root / LOCAL_EXTRA_FRAGMENT
    if context == "local" and local_extra_path.exists():
        fragments.append(local_extra_path.read_text(encoding="utf-8"))
        source_label = f"{source_label} + {LOCAL_EXTRA_FRAGMENT}"

    content = "\n\n".join(fragment for fragment in fragments if fragment)
    expanded_home = home_root if home_root is not None else Path.home()
    return CodexAgentsPlan(
        content=content,
        source_label=source_label,
        target_path=expanded_home / ".codex" / "AGENTS.md",
        target_label=str(TARGET_PATH),
    )


def apply_codex_agents(plan: CodexAgentsPlan, *, backup_root: Path, dry_run: bool) -> str:
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
