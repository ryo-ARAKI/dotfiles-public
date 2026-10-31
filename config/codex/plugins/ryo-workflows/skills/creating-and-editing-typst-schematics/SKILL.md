---
name: creating-and-editing-typst-schematics
description: Use when creating, revising, or reviewing scientific Typst schematics, including hierarchy, processes, flows, sets, qualitative spectra/profiles, and image composites; numerical data plots, report composition, and portable packaging have separate skills.
---

# Create and Edit Typst Schematics

Turn scientific relationships into readable, hand-editable Typst figures while preserving their meaning and the receiving document's settings.
Qualitative curves belong here; measured or computed data plots use the numerical figure skill.

## Scope and mode

- **New figure:** establish meaning and receiving conditions; offer 2–3 distinct compositions as static previews and self-contained editable HTML, then wait for the user's exported composition before final Typst production.
- **Revision:** use the latest source, output, and user edits to identify the requested delta and any source/output mismatch.
  Local corrections need no new composition proposals or browser round trip.
- **Read-only review:** inspect source, scientific meaning and rendered output; return evidence and gaps without changing delivered files.
  Compile candidates only in temporary locations.

Use existing specifications or notes to identify the question, required elements, relationships/directions, containment, correspondences, legend encodings, qualitative versus measured quantities, supplied assets/provenance, receiving dimensions, language, and formats.
Ask only result-changing missing information, one question at a time, and continue independent parts.
Do not invent a direction, causal claim, area interpretation, missing image, or mathematical definition.
Omit in-figure titles and supplemental prose unless requested; retain axis/region/relation labels, equations and legends needed to read the diagram.
Use fixed default outer padding; Codex handles aspect-ratio requests, recomposition and output dimensions without adding browser controls for them.

## Read for the operation

| Need | Source |
| --- | --- |
| Choose a composition, shape language, visual emphasis, colors and spacing, or check scientific meaning | [Diagram design](references/diagram-design.md) |
| Proposals, browser editing, snapshot validation, redraw, coordinate cleanup | [Layout mockups](references/layout-mockups.md); [node/edge starter](assets/layout-mockup.html) or [spectrum starter](assets/spectrum-layout-mockup.html) |
| Generating source for a person to edit | [Editable Typst source](references/editable-typst-source.md) |
| Drawing, package choice, anchors, curves, images, standalone/import boundary | [Typst recipes](references/typst-recipes.md) and its four runnable examples |
| Numerical plots in a mixed figure | [Create and Edit Typst Figures](../creating-and-editing-typst-figures/SKILL.md) for the numerical portion |
| Argument, contextual captions, or page composition | [Writing Typst Research Reports](../writing-typst-research-reports/SKILL.md) |
| Requested extraction or portable bundle | [Export Editable Typst Figures](../export-editable-typst-figures/SKILL.md) |

Read only the relevant references; reading does not activate another workflow.

## Completion

The flow is scientific brief → composition proposals → direct browser edits → user's versioned JSON → hand-editable Typst → receiving-size verification.
For a new composition, retain the supplied unrounded snapshot unchanged and validate its figure/revision, initial states and retained IDs/relationships before adoption.
Exporting does not transmit the file to Codex; the user attaches it or supplies its location.
Fixture exports prove test behavior, never a person's agreement.
Preserve text, colors, deletions and unaffected geometry on redraw; show composition-changing cleanup beside the accepted draft and wait for the affected adjustment.

Verify required elements/relationships, standalone compilation, and affected receiving contexts.
Inspect PDF page count/dimensions, extracted labels and rendered pages at publication size; compare with the accepted draft at the agreed aspect ratio.
Deliver editable text, mathematics and strokes, grouped settings, semantic names, region-wise placements and small helpers for repeated shapes.
Keep the accepted JSON as provenance; ordinary compilation needs no coordinate snapshot.
Use the receiving document's typography without changing its page/text settings, numbering, bibliography or slide progression.

Stage candidates separately and preserve successful artifacts and user edits when dependencies, saving, snapshot validation, legibility or inclusion fail.
Report dependent work as incomplete; do not silently downgrade packages or update environments.
Report source/input identities, chosen package versions and check date, compiler/fonts, rendered contexts, checks and gaps.
