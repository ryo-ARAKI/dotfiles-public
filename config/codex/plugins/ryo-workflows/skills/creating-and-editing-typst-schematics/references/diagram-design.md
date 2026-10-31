# Diagram design

## Meaning before geometry

Write down the figure's question and enumerate its required entities and relations using the supplied notes.
For each connection, identify its endpoints, direction (including undirected correspondence), and meaning: transport, selection, iteration, magnification, membership, or comparison.
Separate visual emphasis from physical signs or causality.
Define colors and line styles locally; they have no universal scientific meaning.
Distinguish qualitative distances, areas, heights, and curves from measured quantities.
Measured parts also need authoritative inputs, units, conditions, and the numerical figure skill's checks.

When direction is unknown, leave that relation unresolved and ask one question about it.
When an essential asset or definition is missing, retain a clearly identified draft placeholder only for a requested concept review; do not adopt it into a final figure.
Do not infer quantitative proportions from an old schematic's geometry.

## Choose by relationship

| Relationship | Useful composition and checks |
| --- | --- |
| Hierarchy or scale | Aligned levels, explicit correspondence or magnification links, separate scope enclosure; magnification is not time or transport. |
| Process or iteration | A clear main reading path, branch labels, and a routed return edge outside nodes; distinguish exit from update. |
| Flows on a qualitative profile | Distinguish the profile from directed transport and transfer between locations; label each line role without implying measured axes. |
| Overlap and decomposition | Name exclusive/shared regions and components; state that area/height is schematic unless supported by measured values. |
| Images with annotations | Retain provenance and scientific context, crop within a real viewport, and anchor callouts to features rather than page pixels. |

The four [runnable examples](typst-recipes.md#examples-and-meaning-contracts) demonstrate these relationships with generic shapes and no external research inputs.
Past figures inform meaning and author intent; their coordinates, libraries, masking, and curves are candidates to improve rather than prescribed implementations.

For a new composition, show 2–3 alternatives with different grouping or reading paths, not merely different colors.
Supply static previews as the basic comparison medium and a saved, offline HTML for direct adjustment.
Use [Layout mockups](layout-mockups.md) for the editing/review checkpoint.

## Receiving-size review

Choose the actual intended width and height before judging density.
Compare drafts at that aspect ratio; inspect both enlarged detail and publication-size placement.
Avoid routing through unrelated labels, visually merging distinct arrows, or hiding content with white rectangles.
Use a true clip for image crops and visible gaps or appropriate layering for crossings.
Let line roles survive grayscale and use labels where color alone would be ambiguous.

Check every required entity, relationship, direction, membership, correspondence, loop, and legend against the input contract.
Check arrowheads and endpoints, label associations, missing glyphs, mathematical meaning, overlap, and clipping.
A compilation or text-extraction pass alone does not verify these properties.
Record intentional differences from a prior figure or accepted draft and keep unresolved scientific claims separate from layout defects.
