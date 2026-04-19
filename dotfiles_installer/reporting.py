from __future__ import annotations

from difflib import unified_diff
from pathlib import Path

from dotfiles_installer.manifest import ManifestEntry


def read_text_if_exists(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def summarize_plan_line(entry: ManifestEntry, prefix: str = "") -> str:
    return f"{prefix}{entry.layer}: {entry.source} -> {entry.target}"


def summarize_overridden_line(entry: ManifestEntry) -> str:
    return f"overridden: {entry.layer}: {entry.source} -> {entry.target}"


def summarize_generated_line(label: str, source: str, target: str, *, status: str) -> str:
    return f"{status}: {label}: {source} -> {target}"


def render_text_diff(target_label: str, source_label: str, current_text: str | None, source_text: str) -> str:
    if current_text is None:
        current_lines: list[str] = []
        header = [f"New file: {target_label}"]
        from_label = "/dev/null"
    else:
        current_lines = current_text.splitlines(keepends=True)
        header = []
        from_label = target_label
    source_lines = source_text.splitlines(keepends=True)
    diff = list(
        unified_diff(
            current_lines,
            source_lines,
            fromfile=from_label,
            tofile=source_label,
            lineterm="",
        )
    )
    if not diff:
        return "\n".join([*header, "No content changes"]) if header else "No content changes"
    return "\n".join([*header, *diff]) if header else "\n".join(diff)


def summarize_run(applied: int, skipped: int, nochange: int, overridden: int, dry_run: bool) -> str:
    label = "Dry run summary" if dry_run else "Summary"
    return f"{label}: applied={applied} skipped={skipped} nochange={nochange} overridden={overridden}"
