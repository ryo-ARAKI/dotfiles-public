---
name: creating-and-editing-typst-schematics
description: Use when creating, revising, or reviewing scientific Typst schematics, including hierarchy, processes, flows, sets, qualitative spectra/profiles, and image composites; numerical data plots, report composition, and portable packaging have separate skills.
---

# Create and Edit Typst Schematics

Turn scientific relationships into readable, hand-editable Typst figures while preserving their meaning and the receiving document's settings.
Qualitative curves belong here; measured or computed data plots use the numerical figure skill.

## Scope and mode

- **New figure:** establish meaning and receiving conditions; offer 2–3 distinct compositions as static PNG previews. For figures Schemock can represent, also supply format-v2 JSON for direct browser edits and wait for the user's adopted composition before final Typst production. For unsupported content, agree on a hybrid or static-draft route as described in [Layout mockups](references/layout-mockups.md).
- **Revision:** use the latest source, output, and user edits to identify the requested delta and any source/output mismatch.
  Local corrections need no new composition proposals or browser round trip.
- **Read-only review:** inspect source, scientific meaning and rendered output; return evidence and gaps without changing delivered files.
  Compile candidates only in temporary locations.

Use existing specifications or notes to identify the question, required elements, relationships/directions, containment, correspondences, legend encodings, qualitative versus measured quantities, supplied assets/provenance, receiving dimensions, language, and formats.
Ask only result-changing missing information, one question at a time, and continue independent parts.
Do not invent a direction, causal claim, area interpretation, missing image, or mathematical definition.
For new proposals, omit in-figure titles and supplemental prose unless requested; retain axis/region/relation labels, equations and legends needed to read the diagram. Preserve text present in an adopted mockup, including titles and supplemental prose; propose any removal, rewording or move outside the figure and obtain agreement before making it.
Use fixed default outer padding for mockups; Codex handles aspect-ratio requests, recomposition and output dimensions without adding browser controls for them. Final production may adjust padding for the receiving layout.

## Read for the operation

| Need | Source |
| --- | --- |
| Choose a composition, shape language, visual emphasis, colors and spacing, or check scientific meaning | [Diagram design](references/diagram-design.md) |
| Proposals, browser editing, snapshot validation, redraw, coordinate cleanup | [Layout mockups](references/layout-mockups.md); the fixed Schemock release when used |
| Generating source for a person to edit | [Editable Typst source](references/editable-typst-source.md) |
| Drawing, package choice, anchors, curves, images, standalone/import boundary | [Typst recipes](references/typst-recipes.md) and its four runnable examples |
| Numerical plots in a mixed figure | [Create and Edit Typst Figures](../creating-and-editing-typst-figures/SKILL.md) for the numerical portion |
| Argument, contextual captions, or page composition | [Writing Typst Research Reports](../writing-typst-research-reports/SKILL.md) |
| Requested extraction or portable bundle | [Export Editable Typst Figures](../export-editable-typst-figures/SKILL.md) |

Read only the relevant references; reading does not activate another workflow.

## Completion

For a new figure, the flow is scientific brief → composition proposals → user edits or feedback ⇄ agent updates → explicitly adopted composition → agreement on publication refinements → hand-editable Typst → receiving-size verification. When Schemock is used, the exchange and adoption contracts are in [Layout mockups](references/layout-mockups.md); a saved or exported file is neither a transfer nor proof of adoption.
Before first producing Typst from an adopted mockup, propose concrete publication refinements with their reasons and agree them interactively with the user. Preserve adopted text except for agreed changes, scientific meaning, deleted elements as absent, explicit constraints, and the adopted composition's grouping and reading path. Show changes to the reading path, grouping, panel structure, or scientifically meaningful encoding beside the adopted draft and obtain agreement before applying them; ask when intent cannot be determined. An existing Typst figure's local revision follows the requested delta without a new refinement proposal or adoption checkpoint.

For creation and revision, verify required elements/relationships, standalone compilation, and affected receiving contexts.
Inspect PDF page count/dimensions, extracted labels and rendered pages at publication size; compare meaning and composition with the adopted draft when available and assess visual hierarchy and legibility at the intended size.
Deliver editable text, mathematics and strokes, grouped settings, semantic names, region-wise placements and small helpers for repeated shapes. Keep any accepted draft and supplied JSON as provenance; ordinary compilation needs no coordinate snapshot.
Use the receiving document's typography without changing its page/text settings, numbering, bibliography or slide progression.

Stage candidates separately and preserve successful artifacts and user edits when dependencies, saving, snapshot validation, legibility or inclusion fail.
Report dependent work as incomplete; do not silently downgrade packages or update environments.
For read-only review, apply the relevant meaning, compilation and rendering checks without changing delivered files.
Report source/input identities, package versions and check date where applicable, compiler/fonts, rendered contexts, checks and gaps.
