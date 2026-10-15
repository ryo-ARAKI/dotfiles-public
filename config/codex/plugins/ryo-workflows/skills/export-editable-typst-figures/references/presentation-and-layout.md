# Presentation and Layout

Read only the sections for the changed features, and use [Stage, Verify, and Update](data-and-provenance.md#stage-verify-and-update) before updating delivery.
Code blocks are independent explanatory fragments, not a shared template or mandatory bundle interface.
Adapt them to the existing renderer; package-specific APIs are examples for the named version.

## Appearance and Series

Keep figure-specific dimensions, fonts, strokes, colors, and notation easy to edit in ordinary source; judge readability at the receiving size.
Preserve scientific quantities, selected data, normalization, and aggregation while changing appearance.
Identify what each visual channel encodes, and keep that mapping consistent across affected curves, markers, annotations, and legends.
Verify sign, component-to-column correspondence, and units before renaming quantities.
Use distinguishable legend samples for the actual series and strokes; choose placement and wrapping for the requested composition rather than requiring a centered, single-row legend.

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
Changing a label alone is not a conversion.
Apply the confirmed transformation exactly once to coordinates, error bounds, theory, ticks/labels, limits, and annotations that represent the target quantity and exist in the figure.
Preserve other quantities; a condition title changes only when it expresses that quantity.

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
Suppress repeated labels only when the full composition still identifies quantities, units, conditions, and series; restore independently necessary information in standalone outputs.
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

## Panel Selection and Batch Export

Apply interface checks when adding or changing panel selection or batch export; ordinary presentation maintenance only regenerates affected delivered panels.
Keep one authoritative condition definition in its existing location, including external bundled files, and use it for full rendering, selected rendering, and the exporter.
Preserve existing selectors, ordering, filenames, and unselected compilation behavior unless changing them is requested; report any changed mapping.
Each selected output retains its data, normalization, and necessary scientific information under the requested presentation changes.

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

Compile and inspect every affected delivered output at its receiving size, preserving scientific data bytes, normalization definitions/values, selection, and aggregation for presentation changes.
Apply only the rows for features that exist and are affected; a font-only edit does not require conversion, CSV reconstruction, upstream calculations, or selector-interface tests.

| Changed feature | Additional checks |
| --- | --- |
| Fonts, labels, or appearance | Applicable text/math/ticks, scientific notation, series/legend mapping, page count, clipping, and readability; preserve required language fallbacks |
| Equivalent display quantity or axis scale | Confirmed formula/units and target scope; numerical correspondence of affected coordinates, error bounds, existing theory, ticks, limits, and annotations; unchanged other quantities; no double conversion |
| Default emphasis | Raw-key membership and each expected condition's multiplicity; marker/legend meaning without inventing defaults |
| Ranges, bands, or layers | Requested endpoint/width/frame goal, required content/padding, band-to-interval correspondence and visibility, and intended overlap order |
| Composition or standalone visibility | Requested arrangement, actual frame alignment where requested, and independent labels/units/conditions/series information |
| Selection or batch-export interface | Valid/invalid selectors under the existing contract, exact selector-condition-filename correspondence, unique filenames, preserved full output; for batch changes, every expected panel and relocation/from-outside invocation with spaced output paths |

If formula/units are unknown, stop that conversion rather than guess.
Invalid coordinates, missing required defaults, clipping, and missing standalone information fail the affected check; repair and rerun it.
Separate missing-font/compiler effects from intended presentation changes, and do not install dependencies without authorization.
For partial failure or unverified outputs, preserve delivery and success records as required by [Stage, Verify, and Update](data-and-provenance.md#stage-verify-and-update).
