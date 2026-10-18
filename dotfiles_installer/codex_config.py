from __future__ import annotations

from pathlib import Path

from dotfiles_installer.codex_runtime import CodexFilePlan
from dotfiles_installer.codex_runtime import plan_codex_runtime


PUBLIC_FRAGMENT = Path("config/codex/config.public.toml")
PRIVATE_FRAGMENT = Path("config/codex/config.private.toml")
PRIVATE_LOCAL_FRAGMENT = Path("config/codex/config.private.local.toml")
TARGET_PATH = Path("~/.codex/config.toml")


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
) -> CodexFilePlan:
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
    return plan_codex_runtime(
        content,
        target_path=target_path,
        source_label=source_label,
        target_label=str(TARGET_PATH),
    )
