# Typst source for hand editing

Use the accepted mockup as the layout input and deliver a figure-specific Typst source that a person can adjust directly.
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
Keep a control-point representation for an individually deformed object; recover parametric construction only when it reproduces the accepted geometry.
Compare every recovered path against the saved control points, allowing only their recorded precision.

Keep helpers and the layer-by-layer drawing body below the editing settings.
Use direct calls for scientifically distinct items instead of a generic shape-type or label-ID dispatcher.
Write mathematics as Typst content, such as `[$E(k) prop k^(-5/3)$]`, and preserve user text as safely escaped literal content.
Preserve exported fill/stroke/text colors while giving the palette useful names.

## Coordinates and dependencies

For CeTZ, use rightward X and upward Y, normally with the axes' intersection or another meaningful shared anchor as the origin.
Use a manageable physical or normalized scale and derive related positions from common boundaries, centers or spacing.
Separate schematic drawing coordinates from measured k, energy, time or other scientific values.
Preserve the accepted positions; neat source does not justify arbitrary coordinate rounding, curve fitting or layout shifts.
Keep the Codex-selected aspect ratio and the mockup's fixed default outer padding; preserve any extra whitespace needed for that ratio.
Codex chooses physical output dimensions and scale for the receiving context; the mockup does not expose these as user controls.
When producing a fitted standalone figure, include the agreed outer padding in the figure body and use zero additional page margin by default to avoid adding it twice.
An imported figure still inherits the receiving document's page margins; these are separate from the figure's own padding.

Keep the normal source self-contained apart from declared packages and genuinely necessary assets such as supplied images or scientific data.
A coordinate list exported by the mockup is not, by itself, a reason to require a separate runtime JSON file.
Keep page/font defaults confined to standalone output; an imported figure inherits the receiving document's typography.

## Verify the handoff

Compile the source alone in a temporary directory without the composition JSON.
Compare the rendered figure with the accepted layout and previous successful output, recording any numerical reconstruction tolerance and intended typesetting differences.
Exercise a representative manual edit, such as moving/resizing one repeated object or changing its winding; check that the intended object changes and unrelated objects stay intact.
Compile affected receiving contexts and check dimensions, surrounding text and page counts.
Report the locations for ordinary edits and any necessary external assets.
