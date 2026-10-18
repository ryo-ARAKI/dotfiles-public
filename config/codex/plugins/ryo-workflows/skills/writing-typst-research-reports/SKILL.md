---
name: writing-typst-research-reports
description: Write, revise, or review Typst research reports, connecting research questions and scientific evidence with prose, tables, figures, and page composition. Excludes application documents, slides, and standalone figure-bundle maintenance.
---

# Write Typst Research Reports

Make the report's questions, evidence, and conditional answers easy to follow within its scientific and formatting contracts.
Use for new reports, authorized revisions, or requested reviews; ordinary proofreading in other document types is outside this skill.

## Establish the Task

- Read the request, applicable repository guidance, manuscript, inherited template, and relevant saved results before choosing changes.
  Distinguish established findings from additional results and identify the questions the report should answer.
- For a review, return findings with locations, evidence, and suggested improvements; leave manuscript sources and delivered outputs unchanged.
  For writing or revision, edit within the authorized scope.
- Inherit the existing template and basic formatting.
  Only for a new manuscript with no specified paper size, default to A4 portrait; margins, font sizes, figure counts, and page targets come from the document's requirements.
  Keep shared template settings at their source of truth; fitting content or stabilizing PDF bytes alone does not justify manuscript overrides of `set page/text/par/figure/document` or equivalent rules.
- Preserve saved values, conditions, units, reference definitions, comparison scope, and statistical meanings.
  A writing request alone does not authorize simulation, estimation, bootstrap, or confidence-interval generation.
  Resolve result-changing gaps in definitions or evidence before completing the affected claim; continue independently supported work.

## Read for the Changed Material

| Work | Reference |
| --- | --- |
| Argument, prose, equations, conditions, or tables | [Writing and Tables](references/writing-and-tables.md) |
| Figure selection, report display requirements, captions, placement, or rendered-document validation | [Report Composition](references/report-composition.md) |

Read the relevant sections and combine them when a change crosses these concerns.
The composition reference explains conditional cooperation with `export-editable-typst-figures`; that skill is not required for ordinary report work.

## Verify and Report

Validate affected sources and rendered outputs using [Report Validation](references/report-composition.md#report-validation) before replacing successful deliverables.
Report the changes or review findings, supporting evidence, preserved contracts, checks actually performed, and concrete gaps or unverified outputs.
Separate missing tools, packages, or fonts from manuscript errors, and preserve existing successful artifacts on failure.
The skill supplies no additional authority for environment installation, distribution, or Git operations.
