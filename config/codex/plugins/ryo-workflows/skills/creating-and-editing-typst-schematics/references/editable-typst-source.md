# Typst source for hand editing

Use the explicitly adopted JSON selected variant’s current state as the starting composition and deliver a publication-quality, figure-specific Typst source that a person can adjust directly. Preserve the scientific contract, composition and explicit fixed constraints while refining the visual design as described in [Layout mockups](layout-mockups.md#adoption-and-production).
Retain the original JSON unchanged as provenance; the ordinary delivered figure should compile without it.
A JSON-backed renderer is useful for intermediate comparison or an explicitly requested data-driven workflow.

## Arrange the editing surface

Put the following near the start of the source, in the order a person is likely to edit them:

1. Figure width, independent text/line scale, named palette, and text/line sizes.
2. Shared layout references and named curve sections or endpoints.
3. Positions and dimensions of repeated objects, grouped by scientific region.
4. Label positions, with literal Typst text/math at an obvious drawing site.

Use a small number of local drawing helpers for repeated objects.
A spiral can expose center, radius, turns, winding and starting angle; a box can expose position and dimensions.
Write one readable record or call per object, with comments for the region and editable fields.
Choose editable control points or a parametric construction according to the object's meaning and the edits a person is likely to make. Refine curves and repeated shapes while preserving meaningful features and connections. When the user explicitly fixes geometry or its exact shape carries scientific meaning, retain it and compare the reconstructed path with the saved controls at the required precision.

Keep helpers and the layer-by-layer drawing body below the editing settings.
Use direct calls for scientifically distinct items instead of a generic shape-type or label-ID dispatcher.
Write mathematics as Typst content, such as `[$E(k) prop k^(-5/3)$]`, and preserve user text as safely escaped literal content.
Give the palette useful names. Preserve explicitly fixed colors and scientifically meaningful mappings; otherwise adjust colors for hierarchy, consistency and contrast, including colors edited in the mockup.

## Coordinates and dependencies

When using Schemock coordinates in CeTZ, convert its top-left, y-down coordinates using y_up = frame_height - y_down, applying group offsets once and converting both rectangle corners; choose a meaningful shared anchor.
Use a manageable physical or normalized scale and derive related positions from common boundaries, centers or spacing.
Separate schematic drawing coordinates from measured k, energy, time or other scientific values.
Refine positions, curves and spacing for legibility and coherence, including manually adjusted positions, without changing the scientific contract, adopted composition or explicitly fixed geometry. Avoid arbitrary rounding or fitting that damages meaningful features.
Use the agreed receiving aspect ratio and sufficient outer padding; adjust draft padding when publication-size layout requires it without changing the adopted composition.
Codex chooses physical output dimensions and scale for the receiving context; the mockup does not expose these as user controls.
When producing a fitted standalone figure, include the agreed outer padding in the figure body and use zero additional page margin by default to avoid adding it twice.
An imported figure still inherits the receiving document's page margins; these are separate from the figure's own padding.

Keep the normal source self-contained apart from declared packages and genuinely necessary assets such as supplied images or scientific data.
A coordinate list exported by the mockup is not, by itself, a reason to require a separate runtime JSON file.
Keep page/font defaults confined to standalone output; an imported figure inherits the receiving document's typography.

## Verify the handoff

Compile the source alone in a temporary directory without the composition JSON.
Compare required meaning and composition with the adopted layout and previous successful output; separately assess visual hierarchy, labels, arrows, contrast and grayscale distinctions at the intended size. Record physical dimensions, substantive visible changes and their reasons, any coordinate conversion, and reconstruction tolerance where exact geometry is required.
Exercise a representative manual edit, such as moving/resizing one repeated object or changing its winding; check that the intended object changes and unrelated objects stay intact.
Compile affected receiving contexts and check dimensions, surrounding text and page counts.
Report the locations for ordinary edits and any necessary external assets.
