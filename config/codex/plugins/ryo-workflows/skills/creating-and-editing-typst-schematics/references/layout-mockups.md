# Layout mockups

## Comparison and handoff

Use the [self-contained HTML starter](../assets/layout-mockup.html) as a diagram-specific draft, rewriting its initial scene, labels, and necessary rendering code for the current request.
Its two generic examples compare a horizontal process with a vertical process; they are not alternative scientific hypotheses.
Generate 2–3 meaningfully different compositions for a new figure and export static previews from the same states.
Static images are the primary comparison medium because terminal chat may not render interactive content.
Save the HTML so the user can open it in an ordinary offline browser; no chat API, network resource, profile, server, or local storage is required.
Do not expand the starter into an arbitrary scientific JSON language or a general drawing application.

The user directly edits positions, widths/heights, whole-group position/size, label text/newlines/position/basic size, and existing connection waypoints and labels.
They can drag shapes, labels, and selected connection points, or select an object and enter values in the form.
Group scaling is affine for child geometry and label offsets; text size remains separately editable.
Codex handles element/image/shape additions or deletion, equation typesetting, image replacement/cropping, group membership, connection topology, specialized drawing, and new compositions.
Do not make small Codex-mediated placement requests the main editing path.

**Back / Forward** undo and redo successful edits in chronological order across variants, including form edits, one complete drag, group resizing, variant switching, reset, and JSON loading.
A new change clears redo; failed or canceled operations, selection alone, unchanged submissions, and exports do not add history.
History stays in the current tab and is not exported; restored states need a new JSON export.
Ctrl+Z and Ctrl+Y invoke the same Back/Forward actions outside input fields. While focus is in text/number inputs, textareas, selects, or editable content, preserve native editing shortcuts; ignore IME composition and modified Alt/Shift combinations.
Keep these controls in generated drafts so users can experiment without losing the preceding layout.

**Reset** restores only the selected variant's entire initial state, including text, leaving other variants' edits intact.
**Confirm** exports the selected variant and all current/initial variant states in one versioned JSON file.
A successful native file write is reported after `close`; the download fallback reports a request and asks the user to check the file, since browsers do not expose download completion to the page.
A canceled/failed write leaves the state intact and is never reported as completion.
Any later edit is unconfirmed and needs another export.
The user attaches the saved file or specifies its location; exporting does not send it to Codex or finish Typst production.
Keep the user's exported file unchanged as the accepted composition revision before cleanup.
Do not pass the review checkpoint based on a screenshot, browser-local state, or an agent's fixture export.

## Version 1 editing snapshot

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
   Copy their current geometry, dimensions, text, font sizes, label positions, and waypoints verbatim unless that object/property is the requested change.
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
Choose a physical unit and increment for the actual receiving dimensions; no universal snap grid is appropriate.
Use a shared origin, row/column reference, common dimensions and pitch to derive related coordinates, rather than rounding each child independently.
Preserve containment and ordering; derive endpoints again from the tidy boxes.
CeTZ uses y upward, so explicitly convert with `y_cetz = canvas_height - y_down` after unit conversion.
For a rectangle convert BOTH corners; do not accidentally reflect horizontally or apply the group offset twice.
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
