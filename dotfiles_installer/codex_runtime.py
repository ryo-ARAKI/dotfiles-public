from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fail closed on Python < 3.11
    tomllib = None


_PRESERVE_TABLES = {"plugins", "mcp_servers", "marketplaces"}
_PRESERVE_SCALARS = {
    ("notice", "hide_rate_limit_model_nudge"),
    ("tui", "screen_reader_detection_done"),
    ("desktop", "followUpQueueMode"),
}
_PRESERVE_MAPS = {
    ("notice", "model_migrations"),
    ("tui", "model_availability_nux"),
}
_PRESERVE_PREFIXES = {("notice",), ("tui",), ("desktop",), ("projects",)}


@dataclass(frozen=True)
class CodexRuntimePlan:
    content: str
    source_label: str
    target_path: Path
    target_label: str
    snapshot: bytes | None
    snapshot_mode: int | None
    preserved_keys: tuple[str, ...]
    changed_keys: tuple[str, ...]


def _loads(text: str, *, what: str) -> dict[str, Any]:
    if tomllib is None:
        raise ValueError("Codex config retention requires Python 3.11 or newer (tomllib)")
    try:
        value = tomllib.loads(text)
    except Exception as exc:
        # Parser exceptions can include source text; never echo config values.
        raise ValueError(f"Cannot safely parse {what}: invalid or duplicate TOML key") from None
    if not isinstance(value, dict):
        raise ValueError(f"Cannot safely parse {what}: expected a TOML table")
    return value


def _allowed_existing(path: tuple[str, ...]) -> bool:
    if not path:
        return False
    if path in _PRESERVE_PREFIXES:
        return True
    if path in _PRESERVE_MAPS:
        return True
    if len(path) == 2 and path[0] == "projects":
        return True
    if len(path) == 3 and path[0] == "projects" and path[2] == "trust_level":
        return True
    if len(path) == 1 and path[0] in _PRESERVE_TABLES:
        return True
    if path[0] in _PRESERVE_TABLES and len(path) >= 2:
        return True
    if len(path) == 2 and path in _PRESERVE_SCALARS:
        return True
    if len(path) >= 3 and path[:2] in _PRESERVE_MAPS:
        return True
    return False


def _display_path(path: tuple[str, ...]) -> str:
    parts = list(path)
    if len(parts) >= 2 and parts[0] in _PRESERVE_TABLES | {"projects"}:
        parts[1] = "*"
    elif len(parts) >= 3 and path[:2] in _PRESERVE_MAPS:
        parts[2] = "*"
    return ".".join(parts)


def _validate_preserved_type(path: tuple[str, ...], value: Any) -> None:
    expected: type | None = None
    if len(path) == 3 and path[0] == "projects" and path[2] == "trust_level":
        expected = str
    elif path in {
        ("notice", "hide_rate_limit_model_nudge"),
        ("tui", "screen_reader_detection_done"),
    }:
        expected = bool
    elif len(path) == 3 and path[:2] == ("notice", "model_migrations"):
        expected = str
    elif len(path) == 3 and path[:2] == ("tui", "model_availability_nux"):
        if type(value) in {bool, int}:
            return
        expected = bool
    elif path == ("desktop", "followUpQueueMode"):
        expected = str
    if expected is not None and type(value) is not expected:
        raise ValueError(f"Codex config type conflict at {_display_path(path)}")


def _merge(managed: Any, existing: Any, path: tuple[str, ...], preserved: set[str]) -> Any:
    if isinstance(managed, dict):
        if existing is not None and not isinstance(existing, dict):
            raise ValueError(f"Codex config type conflict at {_display_path(path)}")
        old = existing if isinstance(existing, dict) else {}
        result: dict[str, Any] = {}
        for key in old:
            child_path = (*path, key)
            if key not in managed and not _allowed_existing(child_path):
                raise ValueError(f"Unclassified existing Codex setting: {_display_path(child_path)}")
        for key, value in managed.items():
            child_path = (*path, key)
            result[key] = _merge(value, old.get(key), child_path, preserved) if key in old else value
        for key, value in old.items():
            if key not in managed:
                child_path = (*path, key)
                if isinstance(value, dict):
                    result[key] = _merge({}, value, child_path, preserved)
                else:
                    if not _allowed_existing(child_path):
                        raise ValueError(f"Unclassified existing Codex setting: {_display_path(child_path)}")
                    if len(child_path) == 1 and child_path[0] in _PRESERVE_TABLES | {"projects", "notice", "tui", "desktop"}:
                        raise ValueError(f"Codex config type conflict at {_display_path(child_path)}")
                    if (len(child_path) == 2 and child_path[0] in _PRESERVE_TABLES | {"projects"}) or child_path in _PRESERVE_MAPS:
                        raise ValueError(f"Codex config type conflict at {_display_path(child_path)}")
                    _validate_preserved_type(child_path, value)
                    result[key] = value
                    preserved.add(_display_path(child_path))
        return result
    if existing is not None and type(existing) is not type(managed):
        raise ValueError(f"Codex config type conflict at {_display_path(path)}")
    return managed


def _toml_key(key: str) -> str:
    if key and all(char.isalnum() or char in "_-" for char in key) and not key[0].isdigit():
        return key
    return json.dumps(key, ensure_ascii=False)


def _toml_value(value: Any) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    raise ValueError("Codex config contains a TOML value this runtime cannot safely serialize")


def _dumps(data: dict[str, Any]) -> str:
    lines: list[str] = []

    def emit(table: dict[str, Any], path: tuple[str, ...], *, header: bool) -> None:
        if header:
            if lines and lines[-1] != "":
                lines.append("")
            lines.append("[" + ".".join(_toml_key(part) for part in path) + "]")
        for key, value in table.items():
            if not isinstance(value, dict):
                lines.append(f"{_toml_key(key)} = {_toml_value(value)}")
        for key, value in table.items():
            if isinstance(value, dict):
                emit(value, (*path, key), header=True)

    emit(data, (), header=False)
    return "\n".join(lines) + "\n"


def plan_codex_runtime(
    content: str,
    *,
    target_path: Path,
    source_label: str,
    target_label: str,
) -> CodexRuntimePlan:
    managed = _loads(content, what="managed config")
    try:
        snapshot = target_path.read_bytes() if target_path.exists() else None
        mode = target_path.stat().st_mode & 0o777 if target_path.exists() else None
    except OSError:
        raise ValueError(f"Cannot safely read Codex target: {target_label}") from None
    existing = _loads(snapshot.decode("utf-8"), what="existing config") if snapshot is not None else {}
    preserved: set[str] = set()
    merged = _merge(managed, existing, (), preserved)
    merged_text = content if snapshot is None else _dumps(merged)
    _loads(merged_text, what="merged config")
    changed: set[str] = set()

    def visit(managed_table: dict[str, Any], old_table: dict[str, Any], prefix: tuple[str, ...] = ()) -> None:
        for key, value in managed_table.items():
            path = (*prefix, key)
            old_value = old_table.get(key, object())
            if isinstance(value, dict):
                visit(value, old_value if isinstance(old_value, dict) else {}, path)
            elif old_value != value:
                changed.add(_display_path(path))

    visit(managed, existing)
    return CodexRuntimePlan(
        merged_text,
        source_label,
        target_path,
        target_label,
        snapshot,
        mode,
        tuple(sorted(preserved)),
        tuple(sorted(changed)),
    )


def apply_codex_runtime(plan: CodexRuntimePlan, *, backup_root: Path, dry_run: bool) -> str:
    try:
        current = plan.target_path.read_bytes() if plan.target_path.exists() else None
        current_mode = plan.target_path.stat().st_mode & 0o777 if plan.target_path.exists() else None
    except OSError:
        raise ValueError(f"Cannot safely recheck Codex target: {plan.target_label}") from None
    if current != plan.snapshot or current_mode != plan.snapshot_mode:
        raise ValueError(f"Codex target changed after planning; replan before applying: {plan.target_label}")
    if current == plan.content.encode("utf-8"):
        return "nochange"
    if dry_run:
        return "would_apply"

    plan.target_path.parent.mkdir(parents=True, exist_ok=True)
    if current is not None:
        backup_path = backup_root / plan.target_path.relative_to(plan.target_path.anchor)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(plan.target_path, backup_path)

    mode = plan.snapshot_mode if plan.snapshot_mode is not None else 0o644
    if plan.snapshot_mode is not None:
        mode &= 0o777  # Existing permissions are preserved, never widened.
    fd, temporary_name = tempfile.mkstemp(prefix=f".{plan.target_path.name}.", dir=plan.target_path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(plan.content.encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(mode)
        os.replace(temporary, plan.target_path)
    except Exception:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    return "applied"
