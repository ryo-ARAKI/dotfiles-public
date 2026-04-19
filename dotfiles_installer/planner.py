from dotfiles_installer.manifest import ManifestEntry


LAYER_ORDER = {"base": 0, "private": 1, "host": 2}


def matches_context(entry: ManifestEntry, context: str) -> bool:
    return entry.when in {"always", context}


def match_specificity(entry: ManifestEntry, context: str) -> int:
    return 1 if entry.when == context else 0


def build_plan(entries: list[ManifestEntry], context: str) -> dict[str, ManifestEntry]:
    plan: dict[str, ManifestEntry] = {}
    for entry in entries:
        if not matches_context(entry, context):
            continue
        current = plan.get(entry.target)
        if current is None:
            plan[entry.target] = entry
            continue
        current_layer = LAYER_ORDER[current.layer]
        entry_layer = LAYER_ORDER[entry.layer]
        if entry_layer > current_layer:
            plan[entry.target] = entry
            continue
        if entry_layer == current_layer and match_specificity(entry, context) > match_specificity(current, context):
            plan[entry.target] = entry
    return plan
