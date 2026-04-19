import shutil
from pathlib import Path

from dotfiles_installer.manifest import ManifestEntry


def apply_entry(entry: ManifestEntry, repo_root: Path, backup_root: Path) -> Path:
    source_path = repo_root / entry.source
    target_path = Path(entry.target).expanduser()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path = backup_root / target_path.relative_to(target_path.anchor)
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        shutil.copy2(target_path, backup_path)
    shutil.copy2(source_path, target_path)
    target_path.chmod(int(entry.mode, 8))
    return backup_path
