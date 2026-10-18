from __future__ import annotations

from pathlib import Path

from dotfiles_installer.codex_runtime import CodexFilePlan, plan_codex_file


COMMON_FRAGMENT = Path("config/codex/AGENTS.common.md")
LOCAL_EXTRA_FRAGMENT = Path("config/codex/AGENTS.local.extra.md")
TARGET_PATH = Path("~/.codex/AGENTS.md")


def _read_required_fragment(path: Path) -> str:
    if not path.exists():
        raise ValueError(f"Codex AGENTS fragment not found: {path}")
    return path.read_text(encoding="utf-8")


def plan_codex_agents(
    private_root: Path | None,
    *,
    base_root: Path | None = None,
    home_root: Path | None = None,
    context: str = "local",
) -> CodexFilePlan:
    if private_root is None and base_root is None:
        raise ValueError("dotfiles-private is required to generate Codex AGENTS.md")

    # Older private checkouts may still carry a complete common override.
    common_root = private_root if private_root is not None and (private_root / COMMON_FRAGMENT).exists() else base_root
    if common_root is None:
        common_root = private_root
    common_path = common_root / COMMON_FRAGMENT
    fragments = [_read_required_fragment(common_path)]
    source_label = str(COMMON_FRAGMENT)

    local_extra_path = private_root / LOCAL_EXTRA_FRAGMENT if private_root is not None else None
    if context == "local" and local_extra_path is not None and local_extra_path.exists():
        fragments.append(local_extra_path.read_text(encoding="utf-8"))
        source_label = f"{source_label} + {LOCAL_EXTRA_FRAGMENT}"

    content = "\n\n".join(fragment for fragment in fragments if fragment)
    expanded_home = home_root if home_root is not None else Path.home()
    return plan_codex_file(
        content=content,
        source_label=source_label,
        target_path=expanded_home / ".codex" / "AGENTS.md",
        target_label=str(TARGET_PATH),
    )
