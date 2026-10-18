# Report Composition

## Figure Selection and Display Requirements

Choose figures by the question and comparison they support, and cite them from the body in an order the reader can follow.
Select curves, points, tables, or other representations according to the quantity's meaning; discrete condition comparisons do not automatically describe a continuous field suitable for contours.
Before changing composition, identify the required conditions, displayed points, quantities, units, comparison directions, reference values, ranges, and interval endpoints from the existing inputs.
Distinguish repeated displays of a point from independent comparisons so aggregation does not silently change coverage.

Choose panel grouping, shared legends, insets, or overlays by readability at the intended publication dimensions, rather than a fixed figure count or panel arrangement.
Overlays need distinguishable conditions and series; an inset needs a clear relation to the full range and enough space to resolve the small difference it is intended to show.
Keep negative values, zero, small differences, and required endpoints visible where the comparison depends on them.
Do not unify ranges, normalize values, drop points, or replace statistical quantities merely to make panels align or shorten the report.
If a requested display transformation is scientifically equivalent, confirm its definition and scope before implementation; an unresolved conflict blocks that transformation.

For report figures, prioritize axes, units, readable ticks, concise meaningful legends, and necessary panel identifiers.
Use mathematical quantity labels and powers of ten when appropriate, and require legend samples to match the actual lines and markers.
Move long explanations and redundant titles into the body or caption.
State shared explanations once and map rows, columns, panel identifiers, conditions, and insets explicitly, using cross-references for details already defined elsewhere.

## Cooperation with Editable Figure Bundles

For existing figures used as-is, include and explain them without starting extraction, redistribution, or an unrelated upstream audit.
For ordinary figures without a bundle, work with the existing manuscript and plotting code; conversion into a bundle is not a prerequisite.
Standalone bundle maintenance belongs to `export-editable-typst-figures`, outside this report skill's scope.

When a report needs bundle changes, first establish the report's purpose, required comparisons and conditions, displayed quantities and units, and receiving dimensions.
Then use the available figure skill for bundle implementation and verification, and integrate the verified outputs into the report for a whole-document check.
The technical sources of truth remain [Presentation and Layout](../../export-editable-typst-figures/references/presentation-and-layout.md) for legends, axes, ticks, fonts, quantity transformations, panel composition and exports, and [Data and Provenance](../../export-editable-typst-figures/references/data-and-provenance.md) for extraction, dependencies, portability, provenance and delivery updates.
Consult only the sections relevant to the bundle change; keep their code examples, transformation procedures, and feature-specific verification there.
If that skill is unavailable, continue independent report work and identify any bundle operation needing its technical guidance.

Apply report paper and placement rules to the manuscript, preserving the dimensions and export conventions of standalone figures and panels.
When report captions allow shorter labels, keep independently necessary quantities, units, conditions, and series information in standalone outputs.
Use existing caller settings or wrappers to distinguish report and standalone display; a new shared API is not assumed.
If those displays cannot be separated within the authorized change, identify the affected outputs and scope decision before removing standalone information.
Report PDF validation and bundle portability/export validation are separate claims, each scoped to the changed artifacts.

## Page Composition

Use the template's normal flow and automatic figure/table placement as the starting point.
If automatic placement moves a table ahead of its definitions or separates evidence from its introduction, use normal-flow placement where it restores the reading order.
Judge existing deliberate section breaks in context; added forced page breaks are not a report-shortening strategy.
To reduce whitespace, inspect figure height, unbreakable groups, table width, caption length, float behavior, and the order and amount of explanation together.
Revise grouping, split an oversized figure or table, or simplify repeated explanations while preserving evidence and readable text at the receiving size.
Removing a page break or setting placement to `auto` alone does not establish that the page is well composed.
Keep the inherited page and text settings while resolving the content and layout that produce the gap.

## Report Validation

Capture the relevant source/input identities and existing successful outputs before editing; use the existing specification or index instead of imposing a new schema.
Compile candidate PDFs to a temporary location so compilation or inspection failure leaves successful PDFs and their records intact.
Use the project's normal Typst command and dependencies; verify relative imports and references rather than bypassing missing files with absolute paths or source-repository symlinks.
For an unresolved definition, missing evidence, numeric mismatch, or broken reference, identify the affected part and required repair and keep it incomplete.

Check meaning as well as compilation: question/answer support, saved numbers and conditions, units, statistic names and scope, comparison direction, coverage, and body/caption/panel references.
For presentation-only changes, compare scientific input bytes before and after and reconcile displayed values and selections with the saved source; hashes alone do not establish numerical correctness.
Check page count and dimensions with `pdfinfo`, extract text with `pdftotext` for omissions and unresolved references, and render with `pdftoppm` or equivalent for visual inspection.
Inspect at the intended reading size for text and tick legibility, legend correspondence, clipping, excessive whitespace, missing content, and figure/table placement.
Confirm required points, interval bounds, and zero lines in the rendered figure as well as the selected records.
When placement changes can propagate to later pages, inspect every page; a successful compile or a first-page preview does not cover that effect.
Validate affected standalone outputs through the figure workflow when bundle changes affect them, keeping their labels and scientific information intact.
Update only authorized deliverables after the relevant checks pass, and report unperformed checks and environment limitations explicitly.
