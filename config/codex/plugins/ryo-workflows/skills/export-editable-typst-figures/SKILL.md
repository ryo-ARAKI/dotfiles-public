---
name: export-editable-typst-figures
description: Use when packaging editable Typst figures for another location or maintaining a portable bundle's dependencies, provenance, relocation, or recipient integration; figure creation and visual revision belong to creating-and-editing-typst-figures.
---

# Distribute Editable Typst Figures

Create or maintain a bundle that recipients can edit and compile without access to the original report repository.
For extraction or packaging alone, reproduce the authoritative appearance.
Ordinary figure creation or visual revision belongs to [Create and Edit Typst Figures](../creating-and-editing-typst-figures/SKILL.md), including work inside an existing bundle.
Reading that skill's technical references does not require its unrelated procedures or a new extraction.

## Bundle Contract

- Keep ordinary Typst source editable and support `typst compile`, with local rendering/editing dependencies and necessary asset-regeneration helpers.
  Use bundle-relative loading paths without source-repository symlinks.
- Preserve original generation/extraction history and separate it from current inputs and new verification.
  Record unknown identities as gaps rather than inferred revisions.
- Work on a distribution copy, preserving source report/simulation inputs and user edits.
  Use the shared [Data and Verification](../creating-and-editing-typst-figures/references/data-and-verification.md) contract for scientific preservation and candidate updates.
- Preserve existing condition definitions, selector interfaces, and practical provenance formats.
  Extraction alone does not authorize a schema or plotting API migration.
- Cleanup covers run-created temporary artifacts; deletion of pre-existing bundles requires authorization for that location.
  Copy to a recipient repository only when requested; the skill grants no installation, Git, deployment, or external-write authority.

## Read for This Operation

| Operation | Reference |
| --- | --- |
| New extraction, dependency or inclusion change | [Extraction and Portability](references/data-and-provenance.md#extraction-and-portability) |
| Missing source repository or revision | [Unavailable Upstream Materials](references/data-and-provenance.md#unavailable-upstream-materials) |
| CSV storage change | [Storage and Scientific Data Changes](references/data-and-provenance.md#storage-and-scientific-data-changes) |
| Provenance maintenance or output update | [Provenance Records](references/data-and-provenance.md#provenance-records) and [Stage, Verify, and Update](references/data-and-provenance.md#stage-verify-and-update) |
| Requested visual revision or panel export | Relevant [Presentation and Layout](../creating-and-editing-typst-figures/references/presentation-and-layout.md) sections and feature-specific checks |

For record edits, consult [Provenance Examples](references/provenance-examples.md); existing formats and loader keys need not migrate.
Maintenance does not require a new extraction or unrelated upstream investigation.

## Completion

Deliver editable source, data, settings, required helpers, and validated affected outputs under the destination's tracking policy.
Verify relocation for new bundles or changed organization/loading/export paths, and recipient inclusion when that integration is affected.
Report bundle location, direct compilation/inclusion instructions, applicable selector/batch commands and meanings, checked identities, rendering environment, and unverified provenance or integration limits.
