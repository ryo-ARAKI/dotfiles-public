"""Compose the shared editor/prompt settings with optional private fragments."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    tomllib = None

from dotfiles_installer.manifest import ManifestEntry


FRAGMENTS = {
    "~/.config/starship.toml": "config/starship.private.toml",
    "~/.config/Code/User/settings.json": "config/Code/User/settings.private.json",
}
_JSON_STRING = r'"(?:[^"\\]|\\.)*"'


@dataclass(frozen=True)
class SettingsPlan:
    content: bytes
    fragment: str


def fragment_for(entry: ManifestEntry) -> str | None:
    # Full private/host manifest files retain their normal override precedence.
    return FRAGMENTS.get(entry.target) if entry.layer == "base" else None


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON setting")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("Non-finite JSON setting")


def load_jsonc(text: str) -> dict:
    """Accept VS Code comments/trailing commas without altering quoted strings."""
    text = re.sub(
        _JSON_STRING + r'|//[^\n]*|/\*[\s\S]*?\*/',
        lambda match: match[0] if match[0].startswith('"') else " ",
        text,
    )
    text = re.sub(
        _JSON_STRING + r'|,(?=\s*[}\]])',
        lambda match: match[0] if match[0].startswith('"') else "",
        text,
    )
    data = json.loads(text, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    if not isinstance(data, dict):
        raise ValueError("Settings must be a JSON object")
    return data


def _merge(base: dict, private: dict) -> dict:
    result = dict(base)
    for key, value in private.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            # Arrays are replaced as a unit, matching whole-setting overrides.
            result[key] = value
    return result


def _toml_value(value) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{ " + ", ".join(
            f"{json.dumps(key, ensure_ascii=False)} = {_toml_value(item)}"
            for key, item in value.items()
        ) + " }"
    raise ValueError("Unsupported TOML setting type")


def plan_private_settings(
    entry: ManifestEntry, *, base_root: Path, private_root: Path | None,
) -> SettingsPlan | None:
    fragment = fragment_for(entry)
    if fragment is None or private_root is None:
        return None
    private_path = private_root / fragment
    if not private_path.exists():
        return None
    if fragment.endswith(".toml") and tomllib is None:
        raise ValueError("Starship private settings require Python 3.11 or newer (tomllib)")
    try:
        public_text = (base_root / entry.source).read_text(encoding="utf-8")
        private_text = private_path.read_text(encoding="utf-8")
        if fragment.endswith(".toml"):
            data = _merge(tomllib.loads(public_text), tomllib.loads(private_text))
            content = "\n".join(
                f"{json.dumps(key, ensure_ascii=False)} = {_toml_value(value)}"
                for key, value in data.items()
            ) + "\n"
            tomllib.loads(content)
        else:
            data = _merge(load_jsonc(public_text), load_jsonc(private_text))
            content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    except (ValueError, TypeError, OSError):
        # Parser errors may contain private values. Report only managed paths.
        raise ValueError(f"Cannot compose settings: {entry.source} + {fragment}") from None
    return SettingsPlan(content.encode("utf-8"), fragment)
