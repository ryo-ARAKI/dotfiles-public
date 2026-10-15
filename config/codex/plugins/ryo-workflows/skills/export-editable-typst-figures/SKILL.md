---
name: export-editable-typst-figures
description: Use when packaging editable Typst figures from reports for conference slides or papers, or maintaining those bundles, their presentation, provenance, and panel exports.
---

# Distribute Editable Typst Figures

## Purpose

Create or maintain a bundle that recipients can edit and compile without access to the original report repository.
Support requested presentation, data, and export changes while preserving scientific meaning and traceable provenance.

## Invariants

- Keep ordinary Typst source editable and support `typst compile`; include all local rendering/editing dependencies and necessary asset-regeneration helpers, using relative loading paths without source-repository symlinks.
- Preserve scientific quantities, stored conditions, selection, aggregation, and normalization except for explicitly requested scientific changes.
  Presentation changes retain scientific data bytes and normalization definitions/values; display transformations do not replace saved data.
- Preserve original generation/extraction history; distinguish current inputs and new verification from historical claims, and record unknown identities as gaps.
- Share existing condition definitions and series meanings across full figures, standalone panels, legends, and exporters.
  Preserve their existing storage location and selection interface unless changing them is requested.
- Work on a distribution copy, preserving original report/simulation data and user edits.
  Validate affected outputs before replacing delivery and its success records; preserve prior successes on failure.
- Cleanup covers run-created temporary artifacts; deleting pre-existing bundles requires authorization for that location.
  Copy to a recipient repository only when requested; the skill grants no installation, Git, or external-write authority.

## Read for This Operation

Read only the relevant sections; combine them for changes affecting several features.

| Operation | Reference |
| --- | --- |
| New extraction or dependency/inclusion changes | [Extraction and Portability](references/data-and-provenance.md#extraction-and-portability); [Unavailable Upstream Materials](references/data-and-provenance.md#unavailable-upstream-materials) when needed |
| Scientific data or storage changes | [Storage and Scientific Data Changes](references/data-and-provenance.md#storage-and-scientific-data-changes) and [Provenance Records](references/data-and-provenance.md#provenance-records) |
| Fonts, notation, display quantities, or composition | Relevant sections of [Presentation and Layout](references/presentation-and-layout.md) and its [Feature-Specific Verification](references/presentation-and-layout.md#feature-specific-verification) |
| Panel selection or batch export | [Panel Selection and Batch Export](references/presentation-and-layout.md#panel-selection-and-batch-export) and applicable [Feature-Specific Verification](references/presentation-and-layout.md#feature-specific-verification) |

For affected output updates, follow [Stage, Verify, and Update](references/data-and-provenance.md#stage-verify-and-update).
For TOML record edits, consult [Provenance Examples](references/provenance-examples.md); existing formats and loader keys need not migrate.
Maintenance does not require a new extraction or unrelated data/provenance investigation.

## Completion

Deliver the editable source and validated affected outputs, with coherent identities and scoped verification records under the destination's tracking policy.
Report bundle location, direct compilation/inclusion instructions, applicable selector/batch commands and meanings, checks performed, rendering environment, and unverified provenance or integration limits.
