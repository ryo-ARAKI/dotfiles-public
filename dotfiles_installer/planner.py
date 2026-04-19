from dataclasses import dataclass

from dotfiles_installer.manifest import ManifestEntry

LAYER_ORDER = {"base": 0, "private": 1, "host": 2}


@dataclass(frozen=True)
class PlanReport:
    selected: dict[str, ManifestEntry]
    overridden: dict[str, tuple[ManifestEntry, ...]]


def matches_context(entry: ManifestEntry, context: str) -> bool:
    return entry.when in {"always", context}


def match_specificity(entry: ManifestEntry, context: str) -> int:
    return 1 if entry.when == context else 0


def is_better_candidate(candidate: ManifestEntry, current: ManifestEntry, context: str) -> bool:
    candidate_layer = LAYER_ORDER[candidate.layer]
    current_layer = LAYER_ORDER[current.layer]
    if candidate_layer > current_layer:
        return True
    if candidate_layer == current_layer and match_specificity(candidate, context) > match_specificity(current, context):
        return True
    return False


def build_plan_report(entries: list[ManifestEntry], context: str) -> PlanReport:
    selected: dict[str, ManifestEntry] = {}
    overridden: dict[str, list[ManifestEntry]] = {}
    for entry in entries:
        if not matches_context(entry, context):
            continue
        current = selected.get(entry.target)
        if current is None:
            selected[entry.target] = entry
            continue
        if is_better_candidate(entry, current, context):
            overridden.setdefault(entry.target, []).append(current)
            selected[entry.target] = entry
            continue
        overridden.setdefault(entry.target, []).append(entry)
    return PlanReport(
        selected=selected,
        overridden={target: tuple(entries) for target, entries in overridden.items()},
    )


def build_plan(entries: list[ManifestEntry], context: str) -> dict[str, ManifestEntry]:
    return build_plan_report(entries, context).selected
