# Schemock layout and editing handoff

## Fixed application and format

Use [Schemock v0.1.0](https://github.com/ryo-ARAKI/schemock/releases/tag/v0.1.0) and format v2 with desktop Google Chrome.
Download `schemock-v0.1.0.html`, `schemock-v0.1.0-data.tar.gz` and `SHA256SUMS` from the [fixed release](https://github.com/ryo-ARAKI/schemock/releases/tag/v0.1.0); verify SHA-256 before use:

- HTML: `a98d9700a911e22c5c1a6d3171ec0725895bdc6415433cba0dba3e26812e8d5d`
- Data archive: `41c46b4e04b04763e41b7d47037dae2c64e49d84b592320c0385181ec44871a1`

Do not automatically fetch the latest version or modify the app per figure.
After download, opening the HTML and JSON needs no network, server, login or installation.
The archive contains the complete [format specification](https://github.com/ryo-ARAKI/schemock/blob/v0.1.0/docs/data-format-v2.md), schemas, [agent workflow](https://github.com/ryo-ARAKI/schemock/blob/v0.1.0/docs/agent-workflow.md), migration instructions and runnable examples.
Use the versioned format and app documentation as the authority for JSON and editor behavior; the app and format versions are distinct. This skill owns publication refinements and the final Typst handoff.

## Propose and exchange

First establish scientific meaning, relationships, directions, containment, qualitative versus measured quantities, required labels, assets, and receiving size and language.
For supported content, prepare 2–3 meaningfully different compositions as variants in one v2 JSON and static PNG previews rendered from that same data with the app; retain a 20 draft-unit outer padding unless the composition requires otherwise. With the release HTML, open the JSON, select each variant and use **PNGを保存**; confirm the saves. The `npm run preview` command in the app's agent workflow requires the Schemock source checkout and is not included in the data archive.
The app supports node/edge rectangles with flat groups and qualitative spectrum paths, regions and labels.
For images, set shapes or other unsupported primitives, explain the limitation and agree on either a hybrid draft (Schemock for representable parts plus complete previews combining the other content) or static previews of the complete composition. Show 2–3 meaningful complete alternatives, retain the actual scientific relationships and assets, and accept changes through supplied files or feedback. In a hybrid draft, update the combined preview after relevant edits and identify the matching JSON and assets. Temporary draft sources may be used to render these previews. Do not silently substitute boxes or patch the editor. Identify the adopted complete composition, including any constituent JSON and assets, and retain the same adoption and refinement checkpoints before production.

The person opens JSON in the fixed app and can move/resize objects and groups, edit text, line breaks and colors, adjust routes and all curve control points, delete elements and dependencies, undo/redo and reset the selected variant.
The agent can make local changes during this process as well as add or replace elements, alter structure or membership, and recompose dimensions.
Editing does not establish scientific correctness.

1. The person saves an intermediate JSON and manually supplies the latest saved file and requested change; a download request alone does not confirm a completed save or delivery.
2. Preserve its original bytes. Validate the entire document against v2, then compare figure ID, structural revision, coordinate frame, all variant IDs/titles and initial states, retained IDs, memberships, connections and path structures, deletions, text, colors, full numeric precision and every control point with the previous handoff. An app load alone is not this comparison.
3. Make only the requested change from that latest JSON. Save a separately named JSON and PNG previews, with a changed-ID/property list. Preserve unrelated edits and deletion absences in every variant; never reconstruct missing work from screenshots or an older handoff.
4. For a local update retain figure ID, `base_revision` and every `initial`; apply with **保存状態を復元** as one undoable operation. For a structural update retain figure and surviving IDs, increment/change `base_revision`, deliberately reconcile initial/current, add new objects to both and preserve unchanged initial entries and current deletions; use **新しい図を開く**. History does not cross this boundary.
5. If editing continued after handoff, obtain the latest saved JSON and reconcile the requested delta again before replacing anything. Cancel or save unfinished work; there is no automatic merge. Unfinished fields and provisional IME text are not transferred in JSON.

Repeat direct edits and agent updates as needed. The [roundtrip examples](../assets/examples/roundtrip/README.md) exercise both families; fixtures are technical evidence, not a person's approval.

## Adoption and production

Before final production obtain explicit human adoption and identify the complete draft and its assets. For Schemock include figure, revision, selected variant and snapshot ID or file hash. Intermediate JSON and exports do not constitute adoption.
Use the adopted composition, and any selected Schemock variant's `current`, as the starting point, preserving deleted objects as absent, all adopted text, scientific relationships, grouping, reading path and explicit fixed constraints. Propose and obtain agreement before removing, rewording or moving adopted text outside the figure, including titles and supplemental prose. Its coordinates, shapes, colors, line breaks and curve controls are design inputs rather than automatically fixed final geometry; this applies to manual edits too. Preserve a shape, proportion, color or path feature when it carries scientific meaning or the user explicitly fixed it. Do not infer that every difference between snapshots is a fixed constraint.
Before final production, assess the adopted mockup at the intended receiving size and present a concise, figure-specific refinement proposal. Identify each target, proposed change and reason: consider object and curve geometry, repeated motifs, visual hierarchy, alignment, whitespace, labels, colors and grayscale legibility. Explicitly identify scientific features and user constraints to retain. If the receiving size is unknown, state a practical assumption. Include alternatives or a comparison when a material choice warrants it; do not prescribe decorative changes merely to differ from the mockup.
For first-time Typst production from the adopted mockup, discuss the proposal and obtain the user's agreement on the intended refinements before writing the final source. Incorporate their choices, including items to leave unchanged. Preserve the adopted draft, assets and any JSON unchanged as provenance. Then build editable Typst manually; ordinary compilation needs no application or coordinate snapshot. Record substantive visible differences and their reasons, as well as physical dimensions and any coordinate conversion used. An existing Typst figure's local revision follows the requested delta without repeating this checkpoint.
Show proposed changes to the reading path, grouping, panel structure or scientifically meaningful encoding beside the adopted draft and obtain agreement before applying them. If a new issue arises during production, ask when its resolution would change those decisions or when intent or scientific meaning is unclear. Routine adjustments within the agreed refinements do not need another checkpoint.
Compile standalone and in receiving contexts; inspect page count, physical dimensions, extracted labels and rendered pages at publication size while preserving the receiving document settings.
See [editable Typst source](editable-typst-source.md) and [Typst recipes](typst-recipes.md).

## Legacy data

Both old families use schema version 1, so never infer the family from that number.
Use the app's **旧JSONを移行**, explicitly select the family and preserve the original; save to a different filename and open the resulting v2 JSON separately.
If initial states are missing, supply the matching complete original JSON or known old HTML as directed by the [migration guide](https://github.com/ryo-ARAKI/schemock/blob/v0.1.0/docs/migration-v1.md); unsupported or mismatched input must be rejected, not guessed.
