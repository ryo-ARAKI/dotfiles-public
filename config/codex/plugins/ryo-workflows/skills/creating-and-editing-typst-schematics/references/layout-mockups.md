# Layout mockups

## Comparison and handoff

Choose the draft primitives from the figure: use the [node/edge starter](../assets/layout-mockup.html) for processes and the [spectrum starter](../assets/spectrum-layout-mockup.html) for qualitative curves, axes, region bands, and annotations.
Rewrite its initial scene, labels, and necessary rendering code for the current request; do not reduce a curve-based figure to boxes simply because the first starter uses rectangles.
The node/edge starter's two generic examples compare a horizontal process with a vertical process; they are not alternative scientific hypotheses.
Generate 2–3 meaningfully different compositions for a new figure and export static previews from the same states.
Static images are the primary comparison medium because terminal chat may not render interactive content.
Save the HTML so the user can open it in an ordinary offline browser; no chat API, network resource, profile, server, or local storage is required.
Do not expand the starter into an arbitrary scientific JSON language or a general drawing application.

The user directly edits positions, widths/heights, whole-group position/size, label text/newlines/position/basic size, and existing connection waypoints and labels, plus fill/stroke/text colors.
They can drag shapes, labels, and selected connection points, or select an object and enter values in the form.
Group scaling is affine for child geometry and label offsets; text size remains separately editable.
Codex handles element/image/shape additions or deletion, equation typesetting, image replacement/cropping, group membership, connection topology, specialized drawing, and new compositions.
Do not make small Codex-mediated placement requests the main editing path.

**Back / Forward** undo and redo successful edits in chronological order across variants, including form edits, one complete drag, group resizing, variant switching, reset, and JSON loading.
A new change clears redo; failed or canceled operations, selection alone, unchanged submissions, and exports do not add history.
History stays in the current tab and is not exported; restored states need a new JSON export.
Ctrl+Z and Ctrl+Y invoke the same Back/Forward actions outside input fields. While focus is in text/number inputs, textareas, selects, or editable content, preserve native editing shortcuts; ignore IME composition and modified Alt/Shift combinations.
Keep these controls in generated drafts so users can experiment without losing the preceding layout.

**Reset** restores only the selected variant's entire initial state, including text and colors, leaving other variants' edits intact.
**Confirm** exports the selected variant and all current/initial variant states in one versioned JSON file.
A successful native file write is reported after `close`; the download fallback reports a request and asks the user to check the file, since browsers do not expose download completion to the page.
A canceled/failed write leaves the state intact and is never reported as completion.
Any later edit is unconfirmed and needs another export.
The user attaches the saved file or specifies its location; exporting does not send it to Codex or finish Typst production.
Keep the user's exported file unchanged as the accepted composition revision before cleanup.
Do not pass the review checkpoint based on a screenshot, browser-local state, or an agent's fixture export.

## Color selection

Both starters offer the 18 [Typst predefined colors](https://typst.app/docs/reference/visualize/color/#predefined-colors), with names, RGB values, and a preview swatch (checked 2026-10-31).
Select an object, choose its fill, stroke, or text color as applicable, then press Apply.
Color edits participate in the same history, per-variant reset, JSON export/import, and PNG rendering as geometry edits.
Preserve these controls in generated drafts.
The initial-color option restores the object's generated color, including existing custom colors; it preserves the original appearance and permits older snapshots without color overrides to load.
The initial/reset states and figure/revision identity checks remain exact.

Store selected colors as Typst names in the object's `fill` or `stroke` field; label text color uses `fill`.
The node/edge starter adds optional `fill`/`stroke` on elements and groups, `stroke` on connections, and `fill` on labels.
The spectrum starter makes existing path `stroke` and region `fill` editable and adds optional label `fill`.
Accept only predefined names or the exact original value for that object/property; preserve custom initial colors without accepting arbitrary CSS from imported JSON.
Resolve names through the embedded RGB table when rendering SVG and arrowheads: browser CSS names such as `green`, `gray`, and `purple` differ from Typst's values, and `eastern` is not a CSS color name.
Keep both standalone HTML palettes aligned when updating the official list.

Verify either starter offline with the same regression, using a separate output directory for each run:

```fish
node scripts/check-mockup-colors.mjs (command -v google-chrome) assets/layout-mockup.html /tmp/node-colors-check
node scripts/check-mockup-colors.mjs (command -v google-chrome) assets/spectrum-layout-mockup.html /tmp/spectrum-colors-check
```

## Qualitative spectrum drafts

The spectrum starter uses three compositions of the same three-dimensional turbulence concept: background bands, external callouts, and a separate scale-transfer strip.
It is a qualitative high-Reynolds-number Kolmogorov picture, not a numerical spectrum or an assertion that all turbulent flows have that shape.
Multiple separate spiral paths below the spectrum indicate a spread of eddy sizes in each region, decreasing toward high wavenumber. Their drawn radii and counts are illustrative, not a calibrated inverse-wavenumber scale or an energy-density encoding; mixed winding is a visual depiction, not an assertion about measured vorticity.
When placing scale glyphs under a curve, verify their full outlines lie below the actual path and above the horizontal axis, within the appropriate region, without crossing annotations or one another.
Keep such scale glyphs separate from the spectrum and transfer paths so users can reposition them without deforming the scientific curve.
The inertial-range relation and the distinction between small-k energy input and large-k dissipation follow [David Tong's fluid dynamics notes, figure 35 and equation 6.16](https://www.damtp.cam.ac.uk/user/tong/fluids/fluids.pdf) (checked 2026-10-31).
No data, Reynolds number, numerical tick spacing, fitted range, or exact region boundary is implied.
Its `k^(−5/3)` draft label is plain editable text; typeset the mathematics in the final Typst figure.

Selecting a path reveals draggable endpoints and cubic control points; dragging the path translates all its points.
Users can also enter point coordinates, move/resize region bands, and edit labels, with Back/Forward for each completed operation.
Curve handles and tangent guides are editing aids and are omitted from PNG previews.
Free adjustments do not enforce a theoretical slope or physical constraints: recheck the meaning and the relation to the guide line before finalization.

This is a separate figure-specific version-1 snapshot, not an extension that the node/edge starter can import.
It retains the same figure/revision/variant/coordinate identity and initial-state checks, with three bounded collections:

- `paths[]`: stable ID, fixed `type` (`cubic` or `polyline`), point count, width, dash and direction; editable `stroke` and `points[]` in canvas coordinates. A cubic chain has one start followed by groups of two control points and one endpoint.
- `regions[]`: stable ID; editable fill and x/y/width/height for rectangular background or under-axis bands.
- `labels[]`: stable ID; editable canvas x/y, text/newlines, font size, and text fill.

Validate against this scene's exact initial structure before adopting an export. Preserve path IDs and every control point on redraw; convert all control points as well as endpoints when transferring to CeTZ.
The final spectrum curve must remain a path, and the transfer arrow must remain a distinct editable object.

Run the dependency-free browser regression with installed Node and Chrome; the output directory holds test-only snapshots and PNGs, not user acceptance:

```fish
mkdir -p /tmp/spectrum-editor-check
node scripts/check-spectrum-mockup.mjs (command -v google-chrome) assets/spectrum-layout-mockup.html /tmp/spectrum-editor-check
```

## Node/edge version 1 editing snapshot

The starter's `INITIAL` object is also its concrete, deliberately limited example of this handoff contract.
Coordinates are draft units with a top-left origin, x rightward and y downward; the canvas is 960 × 540 in this example.
Adapt canvas constants and the renderer together for another diagram.

| Field | Meaning |
| --- | --- |
| `schema_version`, `figure_id`, `base_revision` | Format version, figure identity, and exact generated scene revision. |
| `selected_variant_id`, `coordinate_system` | Selected composition and explicit origin/axis directions/canvas/unit. |
| `variants[]` | Stable `id`, title, independent `initial` and `current` states. |
| `elements[]` | Stable `id`, `group_id` or null, x/y, positive width/height. Element x/y is local to its group. |
| `groups[]` | Stable `id`, canvas x/y and positive width/height. This starter uses one flat group level. |
| `labels[]` | Stable `id`, `owner_id` or null, local or canvas x/y, text including newlines, positive `fontSize`. |
| `connections[]` | Stable `id`, `from`/`to` element and cardinal anchor, directed flag, canvas-space waypoints. Connection labels are independent labels. |
| `constraints[]` | Declared alignment, equal gap, common dimension, and containment intent retained for coordinate cleanup. They do not silently constrain free browser edits. |
| `snapshot` | Export ID and timestamp; not scientific provenance, delivery acknowledgment, or proof of human approval in a test. |

An anchor is computed from the current world rectangle; moving or resizing cannot reverse a relation.
Waypoints and free labels retain their canvas positions during element or group changes.
Group movement adds the group offset exactly once; group resizing scales child local geometry and local label offsets about the group's top-left corner.
It does not change membership, relation endpoints/direction, or basic text size.

Validate before adopting: supported version, exact figure/revision and coordinate system, unique IDs (including variants), finite bounded coordinates, positive dimensions and text sizes, existing owners/groups/anchors, unchanged topology and initial reset states, and retained constraints.
The starter rejects snapshots for other scenes or structural revisions atomically and keeps existing edits on malformed JSON or failed validation.
Treat text as text (`textContent`), never HTML, executable JavaScript, or automatically interpolated Typst source.
When embedding a snapshot into a regenerated HTML, serialize it as data and escape `<` as `\u003c` so a literal `</script>` label cannot end the script element.
Use a replacement callback when updating the seed so label text such as `$&` is not interpreted as a replacement pattern.
Codex must apply the same identity checks before using a handed-over file; do not merely trust that the browser previously accepted it.

## Codex redraw with preserved edits

Start from the LAST file the user supplied, not from the original HTML or remembered positions.
Preserve the original snapshot separately.
For an authorized structural change, generate a new revision and update the HTML's initial/current objects deliberately:

1. Match retained elements, labels, groups, and connections by stable ID.
   Copy their current geometry, dimensions, text, font sizes, colors, label positions, and waypoints verbatim unless that object/property is the requested change.
2. Retain the previous reset state for unchanged objects, so merely redrawing does not discard the original reset contract.
   Add intentional new objects to both initial/current states; define new IDs for replacements.
   Update relationship declarations for intentional structural changes.
3. Reconcile deletions, owners, and endpoint references explicitly.
   Never transfer an old element's edits silently onto a different replacement.
4. Bump `base_revision` and inspect the old/new states for every unaffected ID.
   Old-revision imports must still be rejected by the new HTML; migration is this explicit Codex operation, not permissive browser loading.

Test a redraw by adding one generic element to both states in a temporary HTML and verifying the other objects exactly retain their edits.
This is a handoff exercise, not a shared rendering runtime or automatic scientific converter.

## From accepted geometry to Typst

Retain the unrounded file and record its figure/revision, selected variant, and export ID.
A figure-local Typst renderer can read the retained JSON as data and draw the selected state directly; keep its primitive handlers explicit rather than building a general scientific converter.
Preserving already usable coordinates without snapping is valid. Record a zero cleanup displacement instead of rounding merely to produce a tidy-looking coordinate list.
Compare geometry with literal labels first, then inspect the intended math/font substitutions separately so typesetting differences do not hide layout shifts.
Choose a physical unit and increment for the actual receiving dimensions; no universal snap grid is appropriate.
Use a shared origin, row/column reference, common dimensions and pitch to derive related coordinates, rather than rounding each child independently.
Preserve containment and ordering; derive endpoints again from the tidy boxes.
CeTZ uses y upward, so explicitly convert with `y_cetz = canvas_height - y_down` after unit conversion.
For a rectangle convert BOTH corners; do not accidentally reflect horizontally or apply the group offset twice.
Preserve exported fill/stroke/text colors and resolve predefined names with the matching Typst color constants; carry any original custom colors as explicit RGB values.
Copy text and line breaks literally, with appropriate Typst escaping or content construction; never evaluate JSON as Typst code.

The [iteration example](../assets/examples/iterative-selection.typ) demonstrates the starter's horizontal fixture at 96 × 54 tidy units:

| Accepted draft geometry (960 × 540) | Tidy geometry (96 × 54, y still downward here) |
| --- | --- |
| Group x/y = 50.3/60.2, width/height = 700.4/310.6 | 5/6, 70/31 |
| Child x = 30, 250, 470, scaled by 700.4/700 | Common local start 3, pitch 22 |
| Child y = 90 scaled by 310.6/310 | Shared local row top 9 |
| Width = 180 scaled by 700.4/700; height = 90 scaled by 310.6/310 | Shared width 18, height 9 |
| Edge-label x/y = 279.8/281.2 | 28/28.1 (CeTZ 28/25.9) |
| Waypoints = (280.2,195.1), (290.4,195.1) | (28,19.5), (29,19.5), derived from the shared row center |

The example's `候補 α`/`Candidates` and `選択へ`/`select` line breaks correspond to the edited test fixture.
The starter uses centered SVG text at 30.9 draft units, which becomes about 7 pt at this 76.8 mm publication width; keep separately edited text sizes when transferring a real snapshot.
These fixture exports are verification inputs, not a claim of user approval.
Compare accepted PNG and Typst at the same 16:9 canvas ratio, excluding standalone page margins.
Record the chosen physical scale, rounding increments, maximum shifts, text and relation preservation, and any intentional typesetting difference.
If cleanup causes a visible composition change, show both images and wait for the affected user adjustment instead of adopting a different layout.
