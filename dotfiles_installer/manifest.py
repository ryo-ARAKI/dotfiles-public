from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ManifestEntry:
    layer: str
    source: str
    target: str
    mode: str
    when: str


def load_manifest(path: Path, layer: str) -> list[ManifestEntry]:
    entries: list[ManifestEntry] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        source, target, mode, when = raw_line.split("\t")
        entries.append(ManifestEntry(layer, source, target, mode, when))
    return entries
