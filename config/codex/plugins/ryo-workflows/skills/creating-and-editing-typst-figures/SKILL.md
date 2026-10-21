---
name: creating-and-editing-typst-figures
description: Use when creating, revising, or performing a read-only review of scientific Typst figures in reports, standalone sources, or existing editable bundles; portable packaging belongs to export-editable-typst-figures, and report prose, captions, or page composition belongs to writing-typst-research-reports.
---

# Create and Edit Typst Figures

Make the requested scientific comparison readable while keeping the correspondence between inputs and displayed quantities verifiable.
Work with the existing plotting code and data definitions; creating a portable bundle is a separate requested result.

## Establish the Figure Contract

Read the request, applicable guidance, current source and inputs, and latest user edits.
Identify the question, required conditions and series, points and interval endpoints, quantities and units, reference values, receiving dimensions, and output formats.
For a new figure, establish expected coverage from the supplied inputs rather than an imagined previous PDF.
For a revision, distinguish the requested delta from any saved-output/source mismatch.
For a read-only review, inspect the relevant plotting sources and scientific data; check displayed values, points, interval endpoints, series, and legends within the requested scope.
Return findings with source/data evidence and leave sources and delivered outputs unchanged.
If compilation is necessary, use disposable outputs without replacing delivered artifacts.

A figure request alone does not authorize simulations, estimation, bootstrap, or confidence-interval generation.
Use saved inputs or explicitly supplied new data within the authorized scope.
A missing definition blocks the dependent claim or transformation; continue independent work.

## Read for This Operation

| Operation | Reference |
| --- | --- |
| Read-only scientific figure review | [Data and Verification](references/data-and-verification.md) and checks for the requested display features; return findings only |
| New figure, revision baseline, supplied data, or output update | [Data and Verification](references/data-and-verification.md) |
| Axes, units, appearance, legends, overlays, or caption ingredients | Relevant sections of [Presentation and Layout](references/presentation-and-layout.md) |
| Panel selection or export interface | [Panel Selection and Batch Export](references/presentation-and-layout.md#panel-selection-and-batch-export) and its feature-specific checks |
| Requested portable bundle or dependency relocation | [Export Editable Typst Figures](../export-editable-typst-figures/SKILL.md) |

Reading a reference does not activate another skill's entire workflow.
Apply only checks for affected features; ordinary plotting and font edits need no extraction or relocation check.
Preserve existing condition definitions, selectors, storage, and record formats without adding a required schema or shared runtime.

## Return Verified Outputs

For authorized creation or revision, generate candidates and validate the affected output set through [Stage, Verify, and Update](references/data-and-verification.md#stage-verify-and-update).
Return verified figures and referenceable caption ingredients for authorized edits; for read-only review, return evidence-backed findings and concrete verification gaps.
The report owns contextual captions, figure selection, argument, and page composition through [Writing Typst Research Reports](../writing-typst-research-reports/SKILL.md).
Report input identities, changes, checks actually performed, environment, and concrete gaps using the existing recording mechanism.
Preserve successful artifacts and records on failure; this skill adds no environment, Git, deployment, or external-write authority.
