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

Use figure text for scientific labels: axes, regions, quantities, equations, legend meanings and relationships.
Omit figure-wide titles such as 「3次元乱流のエネルギースペクトル」 and supplemental notes such as 「模式図：曲線の高さ・領域幅・境界位置は定量値を表さない」 unless the user explicitly requests them.
Keep the qualitative/quantitative distinction in the meaning contract or provenance notes; it does not require an extra sentence on the drawing.

## Choose by relationship

| Relationship | Useful composition and checks |
| --- | --- |
| Hierarchy or scale | Aligned levels, explicit correspondence or magnification links, separate scope enclosure; magnification is not time or transport. |
| Process or iteration | A clear main reading path, branch labels, and a routed return edge outside nodes; distinguish exit from update. |
| Qualitative spectra or profiles | Confirm the quantity, axis scale, physical regime, and theoretical annotations; draw editable curves, axes, and region bands. Geometry is not measured data, and a transfer arrow is distinct from the spectrum curve. |
| Flows on a qualitative profile | Distinguish the profile from directed transport and transfer between locations; label each line role without implying measured axes. |
| Overlap and decomposition | Name exclusive/shared regions and components; record schematic area/height interpretation in the meaning contract unless supported by measured values. |
| Images with annotations | Retain provenance and scientific context, crop within a real viewport, and anchor callouts to features rather than page pixels. |

The four [runnable examples](typst-recipes.md#examples-and-meaning-contracts) demonstrate these relationships with generic shapes and no external research inputs.
Past figures inform meaning and author intent; their coordinates, libraries, masking, and curves are candidates to improve rather than prescribed implementations.

If the topic is not yet chosen, offer a few concrete subjects with a recommendation.
Once a subject is chosen, make provisional compositions with explicit assumptions; settle scientific claims before drawing them, and settle receiving dimensions before final-size verification.

For a new composition, show 2–3 alternatives with different grouping or reading paths, not merely different colors.
Supply static previews as the basic comparison medium and a saved, offline HTML for direct adjustment.
Use [Layout mockups](layout-mockups.md) for the editing/review checkpoint.

## Visual form from the author's reference schematics

These defaults abstract design choices in the author's reference figures reviewed for this skill.
Use them when proposing a new figure; a supplied style, the receiving document, and an accepted composition take precedence.
For revisions, apply them within the requested change rather than restyling unrelated objects.
The references vary in typography, palette, and density; their exact colors, coordinates, prose blocks, and drawing techniques are not a fixed house style.

| Observed reference pattern | Transferable design choice |
| --- | --- |
| Particle, fluctuating-field, and macroscopic views in one row | Give comparable views a shared alignment and visual weight; repeat a crop's frame color in its magnification links. |
| Candidate selection beside component redistribution | Mute the alternatives, accent the selected item, and leave room between views for the iteration relation. |
| A spectrum with distinct flows and embedded physical structures | Let the profile organize the composition; separate the main contour, flow arrows, and smaller explanatory drawings by visual role. |
| Large-to-small vortices inside a profile and a highlighted range | Repeat a recognizable motif at different scales; use a background region to group it without enclosing every object. |
| Overlapping sets beside a stacked decomposition | Carry component colors and mathematical symbols across representations; use a brace for the total. |
| A research overview combining a profile, diagrams, and numerical insets | Establish one dominant structure and give supporting insets a readable, subordinate place. |

### Make the scientific object carry the composition

Start with the recognizable geometry of the subject: particles, spirals, a profile, overlapping regions, a decomposition, or equations with highlighted terms.
Give that structure enough area to be understood before reading every label.
Use boxes for actual viewports, scope, discrete steps, or a needed text container; preserve open space around structures that need no enclosure.
Choose a main row, baseline, curve, or set of equation rows as the organizing reference, then place related details around it.
For alternative compositions, change that organization or the relation between overview and detail, while preserving the scientific contract.

### Keep shapes simple and repetition coherent

Use a small family of clear primitives and curves with a common construction for the same kind of object.
Particles can be outlined circles with local vectors; vortices can be open spirals; a range can be a band or brace.
Vary size, orientation, winding, or position only when it helps show scale, direction, or a qualitative distribution.
Keep repeated objects recognizable and avoid adding fine texture or decorative irregularity that disappears at publication size.
Treat object count, packing, and size as schematic unless the contract gives them quantitative meaning.
Use smooth, economical curve sections for continuous profiles and flow paths; inspect their joins and terminal tangents.
An intentional physical transition may need a corner; curve smoothing must not change the supplied meaning or accepted shape.

### Establish visual emphasis with line roles and color

Choose the first thing the reader should notice: the main profile, a selected candidate, a flow, or the correspondence between views.
Give it stronger contrast or line weight than supporting boundaries and guides.
A useful starting hierarchy is a clear main contour or relation, lighter local detail, and quiet region fills; keep axes and necessary labels readable.
Use a small set of line weights by role, with consistent arrowhead shape and size within each role.
Do not make every outline, guide, and arrow equally heavy, or enlarge arrowheads until they obscure their endpoints.

Use black or a dark neutral for general text and structural lines, with a limited set of role colors for selection, flows, components, or correspondence.
Repeat a role's color in its associated label, outline, connector, or equation highlight when that helps the reader follow it.
Across a set diagram, a bar, and a formula, preserve the same component mapping.
Use lighter or muted fills under dark text and line work; reserve stronger color for the emphasis that matters.
Prefer flat fills and clear outlines; use shading when it explains a physical shape or belongs to a supplied scientific image.
Choose colors for contrast against the actual background and neighboring fills, including small colored labels.
The reference figures use different colors for similar physical roles: do not prescribe a universal red/blue mapping or copy a low-contrast accent merely because an old figure used it.
Retain labels, line styles, or shapes that make essential distinctions readable without hue.

### Use spacing and labels to expose relationships

Align comparable panels, repeated stages, and bars by shared centers, baselines, or boundaries.
Keep spacing within a group visibly closer than spacing between independent groups, while reserving clear corridors for connectors and return loops.
Leave space for labels and arrowheads when allocating the canvas; do not fill every opening with another object.
Choose frame shape and corner treatment consistently for the same role; use an enclosure only where its grouping or scope helps.
Attach short scientific labels directly to their region or line when the association is clear; use an external label and precise leader when the interior is crowded.
Keep label offsets and text sizes coherent by role, using the receiving document's typography and readable mathematics.
Place rotated text only where it clarifies an axis or sloping feature, and verify it at the receiving size.
If text does not fit, simplify the composition or move the label before shrinking it below a readable size.

### Integrate detail without losing the main structure

For image panels and numerical insets, reserve a real area and a quiet boundary so their internal detail does not compete with the main relation.
Crop to the relevant feature while retaining scientific context; keep corresponding views aligned when they are meant to be compared.
Place a small physical sketch near the part of a profile it explains, with enough separation to distinguish the sketch from the profile and flow paths.
For equation-based processes, highlight the relevant terms and connect those terms across rows; keep formulas legible instead of turning each entire equation into a generic node.
Reuse component colors across insets and equations only when the meanings match.
When the main structure loses prominence or an inset becomes unreadable, reduce secondary detail or propose separate panels before reducing all text and strokes.
Extract these compositional choices from dense historical overview figures while retaining the current default to omit figure-wide titles and supplemental prose.

## Receiving-size review

Choose the actual intended width and height before judging density.
Compare drafts at that aspect ratio; inspect both enlarged detail and publication-size placement.
Avoid routing through unrelated labels, visually merging distinct arrows, or hiding content with white rectangles.
Use a true clip for image crops and visible gaps or appropriate layering for crossings.
Let line roles survive grayscale and use labels where color alone would be ambiguous.

At the intended size, check that the main structure and emphasized relation are identifiable before reading the small annotations.
Check that repeated motifs remain recognizable, secondary fills recede, component mappings stay consistent, and panel gaps separate groups without disconnecting related items.
Inspect the smallest labels and arrowheads, light colored text, and detailed insets; enlarged previews alone can conceal their loss of contrast or legibility.

Check every required entity, relationship, direction, membership, correspondence, loop, and legend against the input contract.
Check arrowheads and endpoints, label associations, missing glyphs, mathematical meaning, overlap, and clipping.
A compilation or text-extraction pass alone does not verify these properties.
Record intentional differences from a prior figure or accepted draft and keep unresolved scientific claims separate from layout defects.
