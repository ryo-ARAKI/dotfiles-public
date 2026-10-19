# Report Composition

## Figure Selection and Display Requirements

Assign each figure, table, and section a research question and a comparison role that the other material does not already provide.
Use figures for trends and method comparisons; consult [Conditions and Tables](writing-and-tables.md#conditions-and-tables) when deciding whether exact values or definitions need a table.
Cite retained figures from the body in an order the reader can follow, explaining their contribution and supported conditional answer.
Combine or omit redundant displays when the question remains answered, respecting the latest user edits and prior decisions to remove analyses.
Omission from the body does not by itself justify moving a figure to an appendix.
Give an appendix figure its own supporting role and check for redundant panels already shown in the body.
When a brief textual statement supplies the needed information, do not add a figure.
Omitting a display from the report does not authorize untracking or deleting its source, data, or standalone output.

Before requesting a figure change, identify the required conditions, series and their provenance, displayed points, horizontal-axis meaning, quantity symbols and units, comparison directions, reference values, ranges, interval endpoints, receiving dimensions, and formats from the existing inputs.
Choose a representation and panel grouping for the comparison and readability, without fixing the number of figures or panels from a previous report.
Judge information density at the receiving dimensions; split crowded overlays or panels while retaining required conditions, series, and readable labels.
Discrete condition comparisons do not automatically describe a continuous field suitable for contours or interpolation.
Keep negative values, zero, small differences, and required endpoints visible where the comparison depends on them.
A shorter report or aligned layout does not justify changing scientific quantities, selection, aggregation, or normalization.

## Cooperation with Figure Creation and Packaging

For existing figures used as-is, include and explain them using their current outputs and definitions.
Validate the body, caption, and receiving size without starting extraction, redistribution, or relocation checks.

When a figure needs creation, addition, or revision, pass the question and display requirements above to [Create and Edit Typst Figures](../../creating-and-editing-typst-figures/SKILL.md).
Use the existing manuscript and plotting code; a portable bundle is not a prerequisite.
Receive the verified affected outputs, condition/point coverage evidence, identities, limitations, and caption ingredients referenceable through existing quantity, condition, and series definitions, then check their integration into the report.
Use [Presentation and Layout](../../creating-and-editing-typst-figures/references/presentation-and-layout.md) for drawing and exports, including connection choices in [Appearance and Series](../../creating-and-editing-typst-figures/references/presentation-and-layout.md#appearance-and-series).
[Data and Verification](../../creating-and-editing-typst-figures/references/data-and-verification.md) owns input preservation and output updates.
Read only relevant sections; reference reading does not activate the other skill's entire workflow.
If guidance or a definition is unavailable, identify the dependent operation and continue independent report work.

Use [Export Editable Typst Figures](../../export-editable-typst-figures/SKILL.md) only when creating or maintaining a portable set of source, data, settings, and helpers is requested.
Its [Data and Provenance](../../export-editable-typst-figures/references/data-and-provenance.md) owns extraction, dependencies, provenance, relocation, and recipient integration.
Report PDF validation, figure-output validation, and portability/integration checks are separate claims scoped to the affected artifacts.

## Captions and Receiving Context

Compose contextual captions from the figure's authoritative quantity, unit, condition, and series definitions, using its referenceable ingredients rather than a second hand-maintained mapping.
Identify the meanings of rows, columns, panel identifiers, markers, line styles, and insets, using explicit shared references where appropriate; keep legend samples consistent with the actual data display.
Put long explanations and redundant drawing titles in the body or caption and define shared conditions once with an explicit cross-reference.
Do not repeat unchanged defaults, series counts, or every scanned value associated with markers in each caption.
Reference an existing settings table or an earlier caption for shared definitions, keeping changed conditions and figure-specific meanings explicit.
For example, “Shared settings and marker-to-τ mappings follow the caption of Figure …; here the horizontal axis varies k.”
Retain the independently necessary quantities, units, and series information in standalone outputs when report captions permit shorter report labels.
Use existing caller settings or wrappers to distinguish report and standalone display without imposing a new API.
If those displays cannot be separated within scope, resolve the affected output requirement before removing standalone information.
Apply paper and placement rules to the manuscript while preserving the dimensions and export conventions of standalone figures and panels.

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
Continue independent work and preserve the jointly affected successful artifacts and records if one required output fails.
After a change to a final loaded input or metadata, rerun affected checks before updating successful identities; reuse unaffected evidence when its inputs, target tree, and material environment assumptions remain unchanged.

Check meaning as well as compilation: question/answer support, saved numbers and conditions, consistent quantity symbols and definitions across body/equations/axes/legends/captions, units, statistic names and scope, comparison direction, coverage, and body/caption/panel references.
Distinguish notation-only changes from coordinate conversions; confirm conversion conventions and affected coordinates through [Display Quantities and Axes](../../creating-and-editing-typst-figures/references/presentation-and-layout.md#display-quantities-and-axes).
For presentation-only changes, compare scientific input bytes before and after and reconcile displayed values and selections with the saved source; hashes alone do not establish numerical correctness.
Check page count and dimensions with `pdfinfo`, extract text with `pdftotext` for omissions and unresolved references, and render with `pdftoppm` or equivalent for visual inspection.
Inspect at the intended reading size for text and tick legibility, legend correspondence, clipping, excessive whitespace, missing content, and figure/table placement.
Confirm required points, interval bounds, and zero lines in the rendered figure as well as the selected records.
When placement changes can propagate to later pages, inspect every page; a successful compile or a first-page preview does not cover that effect.
Validate affected standalone outputs through the figure workflow when figure changes affect them, keeping their labels and scientific information intact.
Update only authorized deliverables after the relevant checks pass, and report unperformed checks and environment limitations explicitly.
