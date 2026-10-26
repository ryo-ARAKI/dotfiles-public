"""Refresh the enabled local workflow plugin through Codex's installer."""
import json
import os
import subprocess
import tomllib
from pathlib import Path

PLUGIN_NAME = "ryo-workflows"
PLUGIN_TARGET = "~/plugins/ryo-workflows/"


def _files(root: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and not {".git", "__pycache__"}.intersection(path.relative_to(root).parts)
    }


def refresh_workflows_cache(home: Path, *, dry_run: bool) -> str:
    """Only refresh an already-enabled plugin registered from our local payload."""
    marketplace_path = home / ".agents/plugins/marketplace.json"
    config_path = home / ".codex/config.toml"
    if not marketplace_path.is_file() or not config_path.is_file():
        return "plugin cache skipped: no local registration or Codex config"
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    marketplace_name = marketplace["name"]
    plugin_id = f"{PLUGIN_NAME}@{marketplace_name}"
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    if config.get("plugins", {}).get(plugin_id, {}).get("enabled") is not True:
        return f"plugin cache skipped: {plugin_id} is not enabled"
    deployed = home / "plugins" / PLUGIN_NAME
    registered = any(
        plugin.get("name") == PLUGIN_NAME
        and plugin.get("source", {}).get("source") == "local"
        and (home / plugin["source"]["path"]).resolve() == deployed.resolve()
        for plugin in marketplace.get("plugins", [])
    )
    if not registered:
        return "plugin cache skipped: workflow plugin is not registered from the deployed directory"
    command = ["codex", "plugin", "add", plugin_id, "--json"]
    if dry_run:
        return "would refresh plugin cache: " + " ".join(command)
    result = subprocess.run(
        command, check=True, capture_output=True, text=True, timeout=60,
        env=dict(os.environ, CODEX_HOME=str(home / ".codex")),
    )
    installed = json.loads(result.stdout)
    cache = Path(installed["installedPath"]).resolve()
    expected_parent = (home / ".codex/plugins/cache" / marketplace_name / PLUGIN_NAME).resolve()
    if installed.get("pluginId") != plugin_id or cache.parent != expected_parent:
        raise ValueError("Codex returned an unexpected plugin cache target")
    source_files, cache_files = _files(deployed), _files(cache)
    if not source_files or source_files != cache_files:
        raise ValueError(f"plugin cache differs from deployed files: {cache}")
    return f"plugin cache verified: {plugin_id} ({len(source_files)} files); start a new Codex session"
