from dotfiles_installer.manifest import ManifestEntry


LAYER_ORDER = {"base": 0, "private": 1, "host": 2}


def matches_context(entry: ManifestEntry, context: str) -> bool:
    return entry.when in {"always", context}


def build_plan(entries: list[ManifestEntry], context: str) -> dict[str, ManifestEntry]:
    plan: dict[str, ManifestEntry] = {}
    for entry in entries:
        if not matches_context(entry, context):
            continue
        current = plan.get(entry.target)
        if current is None or LAYER_ORDER[entry.layer] >= LAYER_ORDER[current.layer]:
            plan[entry.target] = entry
    return plan
