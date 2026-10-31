# Typst recipes

## Current packages and selection

At every implementation/drawing operation, check the official distribution for the stable latest versions of directly adopted libraries, then record the checked date and pinned versions.
A local cache or this dated record is not evidence of the latest release at a future use.
The official pages checked **2026-10-31** list [CeTZ 0.5.3](https://typst.app/universe/package/cetz/), [Fletcher 0.5.8](https://typst.app/universe/package/fletcher/), and [Physica 0.9.8](https://typst.app/universe/package/physica/).
The examples directly depend only on CeTZ 0.5.3 (compiler requirement 0.15.0); they were compiled with Typst 0.15.1.
CeTZ 0.5.3's own `src/deps.typ` uses the internal formatting helper oxifmt 1.0.0; it is a transitive dependency, not an independently selected drawing library.
Fletcher 0.5.8 uses CeTZ 0.3.4 internally; using the latest Fletcher does not make its transitive CeTZ the latest CeTZ.
Do not edit vendor code or silently downgrade direct dependencies to unify versions.
Test content-boundary composition if combining libraries, or prefer a working current-version method with fewer dependencies.
Environment/package/font installation and updates require the applicable authority.

| Method | Choose when / tradeoff |
| --- | --- |
| Typst standard shapes, grid, mathematics | Simple boxes or formula alignment; minimal dependency cost, less convenient freeform anchors/paths. |
| CeTZ 0.5.3 | Freeform paths, border anchors, repeated symbols, clips, annotated compositions; explicit geometry makes relationships inspectable. |
| Fletcher 0.5.8 | A node/edge graph with many routed branches benefits from declarative graph relations; weigh its internal CeTZ boundary before mixing canvases. |
| Physica 0.9.8 | A needed scientific notation is clearer with its helpers; basic labels and equations in these examples use standard Typst math. |

The iteration example uses CeTZ alone: four fixed nodes and a return route need no graph-layout layer, and all four examples can share one direct dependency without a common drawing API.
The multiscale example uses native path clipping rather than white masking, and generic particles/curves rather than third-party images.
The flow example uses separate labeled lines rather than a historical curve construction or extra arrow library.
The decomposition example uses ordinary shapes and explicit region labels; no measured area or estimated information value is implied.

## Examples and meaning contracts

Each source exports `schematic(unit: ..., label-size: ...)` and also compiles directly.
No private source, image, bibliography, or template is required.
The only commonality is the simple example entrypoint; drawing code remains local in each file.

| Source | Contract to verify | Example receiving size |
| --- | --- | --- |
| [multiscale.typ](../assets/examples/multiscale.typ) | Micro/meso/macro; undirected magnification correspondence, dashed model scope, cropped swirls; links are not transport. | 76.8 × 43.2 mm, 7 pt labels |
| [iterative-selection.typ](../assets/examples/iterative-selection.typ) | Candidates → select → update; return to candidates and conditional stop; accepted-fixture cleanup preserves text and alignment. | 76.8 × 43.2 mm, 7 pt labels |
| [cascade-and-flows.typ](../assets/examples/cascade-and-flows.typ) | Qualitative profile separate from rightward solid transport and leftward dashed feedback; no measured axes. | 76.8 × 43.2 mm, 7 pt labels |
| [information-decomposition.typ](../assets/examples/information-decomposition.typ) | A-only/shared/B-only membership corresponds to three components; area and heights are schematic. | 76.8 × 43.2 mm, 7 pt labels |

These are verified example conditions, not mandatory typography for real figures.
Use the receiving document's fonts and choose label size for that document.
Standalone wrappers use available Noto Sans and Noto Sans CJK JP; standard Typst math uses its installed math fallback.
For a simple check, from the examples directory:

```fish
typst compile multiscale.typ /tmp/multiscale.pdf
pdfinfo /tmp/multiscale.pdf
pdftotext /tmp/multiscale.pdf -
pdftoppm -scale-to 1400 -png -singlefile /tmp/multiscale.pdf /tmp/multiscale
```

## Anchors, curves, layers, and crops

Name rectangles and use border anchors such as `"stage-1.east"`; resizing should not leave endpoints at stale manual coordinates.
Route loop edges outside the main reading path and keep labels tied to the intended line.
An undirected correspondence gets no arrowhead; line style and explicit text distinguish different flows.
Use CeTZ's [official manual](https://cetz-package.github.io/docs/) for current API details, remembering that y increases upward.
Use a few interpretable control points for curves and inspect the actual terminal tangent and arrowhead direction.
For a saved multi-segment cubic path, merge the matching Bezier segments into one stroked path to preserve joins and dash continuity.
Preserve the draft's filled/open arrowhead form and its size relative to stroke width; a library's default arrow mark need not match an SVG marker.
Keep quantitative curves in the numerical figure workflow.

Draw region backgrounds first, then connections and shapes, then associated labels as appropriate for the intended occlusion.
Do not hide unwanted segments with white paint when native clipping or a routed path expresses the geometry.
CeTZ path `clip` handles the generic multiscale swirls; it does not justify assuming raster/PDF content is clipped in the same way.
For an actual image crop use Typst's native clipped box viewport or an image with explicit width/height/fit, verify the rendered crop, and retain the source/provenance.
Compose imported image/content inside a named region, keeping a precise callout anchor and enough scientific context; supplied images can remain raster assets while text/arrows stay editable.
Never substitute a missing scientific image silently.

## Standalone and receiving hosts

Import the function, rather than `include` the standalone page content:

```typst
#import "multiscale.typ": schematic
#figure(schematic(unit: 0.8mm, label-size: 7pt))
```

The source's top-level page and font setup belongs to standalone module content.
The exported body sizes its own labels locally and inherits the host font; it does not set page, body text, numbering, bibliography, or slide progression.
Do not move document-wide settings into the function.
For slides, increase physical unit and label size together after checking the actual available height.
The validation hosts place all four functions in a 2 × 2 grid with a 6 mm gutter:
A4 portrait, 20 mm margins, 10 pt body, unit 0.8 mm / 7 pt labels; and 320 × 180 mm, 10 mm margins, 20 pt body, unit 1.1 mm / 9.5 pt labels.
Both must remain one page with surrounding host text at its original font/size and the original page dimensions.
Inspect their rendered pages as well as standalone outputs; extracted text and context assertions alone do not establish legibility or fit.
