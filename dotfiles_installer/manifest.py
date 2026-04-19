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
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        parts = raw_line.split("\t")
        if len(parts) != 4:
            raise ValueError(
                f"Malformed manifest row in {path} at line {line_number}: expected 4 tab-separated columns, got {len(parts)}"
            )
        source, target, mode, when = parts
        entries.append(ManifestEntry(layer, source, target, mode, when))
    return entries
