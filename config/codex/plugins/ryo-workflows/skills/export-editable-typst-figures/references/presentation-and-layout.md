# Presentation and Layout

Read only the sections for the changed features, and use [Stage, Verify, and Update](data-and-provenance.md#stage-verify-and-update) before updating delivery.
For extraction/packaging alone, reproduce the original appearance; the improvement defaults below apply when figure creation or presentation adjustment is requested.
Explicit user choices and publication requirements take precedence.
Choose dimensions, panel count, palette, fonts, and stroke widths for the destination; no report-specific page format or arrangement is mandatory.
Code blocks are independent explanatory fragments, not a shared template or mandatory bundle interface.
Adapt them to the existing renderer; package-specific APIs are examples for the named version.

## Figure Information and Caption Ingredients

Keep visible figure information focused on axis symbols, units, ticks, short legends, and panel letters.
Keep titles, long condition descriptions, detailed method/quantity explanations, and reproducibility IDs out of the drawing.
Retain internal IDs and provenance in source, comments, or provenance records, separate from reader-facing information.

The figure's `.typ` retains referenceable parameters, quantity definitions/units, conditions, and series mappings needed to write a caption, rather than finished caption text.
Reuse the existing authoritative data, condition, and series definitions: expose or reference them through the figure's existing interface, without hand-copying values or maintaining a second active mapping.
Adapt exported values, functions, compiler metadata, or source references to the bundle; do not require a new variable name, schema, or migration.
The data flow is existing data/condition definitions → drawing and referenceable parameter information → a contextual caption composed by the receiving report.
Standalone figures also retain access to these ingredients; do not restore explanatory prose inside the drawing to make them self-contained.
If quantities, units, or conditions are unknown, report the missing information rather than filling it in by inference.

## Appearance and Series

Keep figure-specific dimensions, fonts, strokes, colors, and notation easy to edit in ordinary source; judge readability at the receiving size.
Preserve scientific data bytes, stored conditions, selection, aggregation, normalization, and stored confidence intervals while changing appearance.
Do not run simulations, estimation, bootstrap, or confidence-interval generation for presentation work.
Distinguish categories such as methods from ordered quantities such as time or parameter values when choosing visual channels.
For ordered quantities, use an appropriate colormap such as plasma, with a consistent value-to-color mapping and domain across compared figures.
Show the mapping with a short legend or colorbar; identify what each visual channel encodes and keep it consistent across curves, markers, annotations, and legends.
Verify sign, component-to-column correspondence, and units before renaming quantities.
Align legend line and marker centers, matching actual series colors, line styles, and symbols.
Use short, meaningful method names and retain their definitions as caption ingredients.
Choose legend placement and wrapping for the requested composition rather than requiring a centered, single-row legend.
Check text, line, and marker discrimination at publication size; keep guides subdued enough not to obscure data.
Hollow markers have transparent interiors, not white-filled interiors: the background and overlapping data must remain visible through them.

Choose curves, points, or tables according to the comparison readers need to make.
Use contours primarily for spatial/field visualization; do not mechanically convert condition or method comparisons to contour plots.

### Existing or Requested Default Emphasis

Apply default checks only when default emphasis exists or is requested; do not add it to other figures.
Determine membership from stored scientific conditions before unit conversion, logarithms, or display offsets.
Retain all specified defaults and their expected multiplicity for each relevant method/panel; totals alone can hide missing and duplicated conditions.
Match every relevant key, with equality/tolerance appropriate to storage semantics; do not substitute a nearby point for a missing default.
Record intentionally absent defaults as part of the expected specification.
Keep marker/legend meaning, point counts, and error bars consistent. No particular colors, shapes, fills, or one-point multiplicity are universal.

## Display Quantities and Axes

Before changing a displayed quantity, confirm its formula, units, storage convention, and applicable series from observed inputs/settings.
Do not infer elapsed time from sample counts without knowing the convention, or normalize already nondimensional coordinates again.
Distinguish notation-only changes from unit, coordinate, or scale conversions.
Use mathematical notation for variables by default, and powers of ten rather than forms such as `1e+05`; display `10^0` as `1`.
Notation-only changes preserve numerical positions, scientific meaning, and scale.
Changing a label alone is not a conversion.
Apply the confirmed transformation exactly once to coordinates, error bounds, theory, ticks/labels, limits, and annotations that represent the target quantity and exist in the figure.
Preserve other quantities; update affected condition information in caption ingredients only when it expresses that quantity.

This linear y-axis example assumes stored lengths have been confirmed to be millimetres and displays metres.
It does not change x coordinates, stored conditions, or raw data; the plotting API must receive the derived coordinates and corresponding unit label.

```typst
#let to-display(y) = y / 1000
#let raw-y = (1000, 2000)
#let display-y = raw-y.map(to-display)
#let y-ticks = raw-y.map(y => (to-display(y), [#to-display(y)]))
#let y-limits = (0, 3000).map(to-display)
```

For nonlinear conversion, transform the applicable error endpoints rather than assuming a symmetric error remains symmetric.
For log axes, distinguish package-managed scaling from manually logged coordinates; do not apply both.
Check finite coordinates and positive log inputs. Where offsets exist, use quantity conversion, then log coordinates if applicable, then presentation offsets; offsets do not redefine scientific values or theory.
Pair numeric tick positions with labels without changing the scale to obtain a preferred label, such as `1` instead of `10^0`.

### Package-Specific Tick Fonts

Text, math, and generated ticks may follow different rendering paths.
For Lilaq 0.6.0, the following applies a text-font wrapper to tick labels; choose installed destination fonts and retain needed language fallbacks.
It changes text-content ticks; automatically formatted math ticks may also need an equation font rule, and an already matching font produces no visible change.
This fragment was checked with Typst 0.15.1 and Lilaq 0.6.0; recheck APIs in a different environment.

```typst
#import "@preview/lilaq:0.6.0" as lq
#show: lq.show_(lq.tick-label, it => text(font: "New Computer Modern Math")[#it])
```

## Composition and Standalone Information

Preserve existing data/condition selection and share rendering logic between full and standalone outputs; let callers control dimensions and visibility.
Use the requested panel arrangement rather than assuming two rows or two columns.
Respect the caller's paper, margins, and body settings; figure code must not change manuscript-wide settings.
Resolve fit through placement or panel splitting, without casually enlarging paper, shrinking margins, or scaling down the entire composition.
Keep explanatory prose in captions rather than adding it to the drawing to solve layout problems.
Suppress repeated labels only when the composition still identifies quantities, units, and series, with conditions available as caption ingredients.
Restore independently necessary axis/legend information for standalone outputs while keeping explanations in caption ingredients.
Different centers/ranges can require numerical tick labels even when numeric widths match.
Omitting a panel from one composition does not remove its data or existing standalone output unless that removal is requested.

When alignment is requested, distinguish common numeric endpoints, equal numeric widths, and equal physical drawing-frame widths.
Frame alignment alone retains numeric ranges; check actual frame edges because tick-label widths can shift them inside outer boxes.
For requested equal numeric widths on linear axes, find each needed interval including existing error bounds/theory and padding, use `D = max(high_i-low_i)`, and expand around each own center `c_i = (high_i+low_i)/2` to `[c_i-D/2, c_i+D/2]`.
This does not require common endpoints or zero symmetry, and the additive rule does not apply unconditionally to log axes.
Reject empty/non-finite intervals; finite constant series need positive finite padding appropriate to their scale.

Comparison bands and layer order apply only when those elements exist or are requested.
If a band represents another panel's interval, use that final interval consistently and keep it visible without obscuring the data.
Choose stacking to preserve the intended comparison: backgrounds behind data or markers over error bars/theory are examples, not fixed z-index requirements.
When splitting layers, reuse the same precomputed values rather than changing counts or aggregating twice.

### Overlay and Insets

Combine series only on axes with the same meaning, units, and comparable scales.
Use line style, width, opacity, color, and symbols to preserve discrimination; split panels when overlays become crowded at publication size.
Do not drop series, conditions, data points, or error ranges to achieve a compact composition.

Distinguish two inset purposes:

- **Magnification of the same quantity:** mark the target region on the main plot with a frame or background tint.
  If using a tint, match it to the entire inset background.
  The marked bounds and inset display limits must agree; keep main-plot data visible.
- **A different quantity:** use axes for the specified quantity and retain its definition, conditions, and relation to the main plot as caption ingredients.
  Do not automatically draw a magnification-region frame for an unrelated quantity.

Omit labels/annotations clearly redundant with the parent panel, retaining necessary axis symbols and units.
Keep insets compact without making the figure unnecessarily tall, and keep explanatory sentences out of them.

## Panel Selection and Batch Export

Apply interface checks when adding or changing panel selection or batch export; ordinary presentation maintenance only regenerates affected delivered panels.
Keep one authoritative condition definition in its existing location, including external bundled files, and use it for full rendering, selected rendering, and the exporter.
Preserve existing selectors, ordering, filenames, and unselected compilation behavior unless changing them is requested; report any changed mapping.
Each selected output retains its data, normalization, necessary axis/legend information, and access to caption ingredients under the requested presentation changes.

For a new interface, `--input panel=1` with array-order one-based selectors is one possible design, not a migration requirement.
The following illustrates deriving a compiler-exposed map from one condition list; labels and filenames are illustrative, not required schema keys.
Real records retain their scientific conditions and references, and may be loaded from a bundled external file instead.

```typst
#let conditions = (
  (label: [A], filename: "panel-a.pdf"),
  (label: [B], filename: "panel-b.pdf"),
)
#let panel-export-map = conditions.enumerate().map(((i, condition)) => (
  selector: i + 1, condition: condition,
))
#metadata(panel-export-map) <panel-export-map>
```

An exporter may read compiler metadata using the environment's supported extraction API or read the same external condition source directly.
Do not parse source text or hand-maintain a second active condition list; recorded provenance mappings are identified snapshots.
Use meaningful, unique filenames consistent with the bundle's convention and document selector meanings, output location, commands, and overwrite behavior.
Validate selections against the actual interface; for one-based single-integer selection, reject zero, out-of-range values, and lists. Named or other existing selectors keep their own validation rules.

Provide a batch exporter when batch export is requested, reusing an existing one where suitable.
Resolve bundle paths independently of the caller's working directory, quote paths, and stop on compilation failure.
An executable POSIX `export-panels.sh` with `set -eu` and an optional output directory is an example, not a prerequisite for single-panel export.

## Feature-Specific Verification

For packaging alone, check fidelity to the original appearance rather than enforcing presentation improvements.
Compile and inspect every affected delivered output at its receiving size, preserving scientific data bytes, normalization definitions/values, stored conditions/confidence intervals, selection, and aggregation for presentation changes.
Capture input hashes and compare selected points/conditions and error endpoints with the baseline; do not regenerate estimates or intervals.
Verify standalone output and document inclusion separately when affected; rasterize the necessary outputs and inspect them at publication size.
Apply only the rows for features that exist and are affected; a font-only edit does not require conversion, CSV reconstruction, upstream calculations, or selector-interface tests.

| Changed feature | Additional checks |
| --- | --- |
| Fonts, labels, or appearance | Applicable text/math/ticks, powers of ten with `10^0` shown as `1` at unchanged positions, page count, clipping, and readability; preserve required language fallbacks |
| Series, legends, or markers | Ordered color domain/value mapping consistent across compared figures and matching legend/colorbar; legend line/marker centers and actual series styles; hollow interiors transparent over a colored background and overlapping data |
| Caption ingredients or visible information | Exact quantities/units/parameters/conditions/series meanings obtainable from the figure's existing definitions, sufficient for a report-side caption without duplicated values/mappings; no explanatory prose or internal IDs in the drawing, including standalone outputs |
| Equivalent display quantity or axis scale | Confirmed formula/units and target scope; numerical correspondence of affected coordinates, error bounds, existing theory, ticks, limits, and annotations; unchanged other quantities; no double conversion |
| Default emphasis | Raw-key membership and each expected condition's multiplicity; marker/legend meaning without inventing defaults |
| Ranges, bands, or overlays | Requested endpoint/width/frame goal, required content/padding, band-to-interval correspondence and visibility, intended overlap order; comparable quantities/units/scales, distinguishable styles/widths/opacities, no missing series/conditions/points/error ranges |
| Insets | Magnification bounds equal the marked main region, matching whole-inset background when tinted, and main data visible; different-quantity axes and caption ingredients without a spurious zoom frame; necessary symbols/units retained and redundant labels omitted |
| Composition or standalone visibility | Requested arrangement and frame alignment, independent axis/legend information and caption ingredients, caller's paper/margins/body settings respected, fit and readability at intended size |
| Selection or batch-export interface | Valid/invalid selectors under the existing contract, exact selector-condition-filename correspondence, unique filenames, preserved full output; for batch changes, every expected panel and relocation/from-outside invocation with spaced output paths |

If formula/units/conditions are unknown, report the gap and stop the dependent change rather than guess.
Invalid coordinates, missing required defaults, clipping, and missing standalone information fail the affected check; repair and rerun it.
Separate missing-font/compiler effects from intended presentation changes, and do not install dependencies without authorization.
For partial failure or unverified outputs, preserve delivery and success records as required by [Stage, Verify, and Update](data-and-provenance.md#stage-verify-and-update).
Keep verification candidates and diagnostics separately under `/tmp`, outside delivery; failed candidates never replace delivered files or successful records.
