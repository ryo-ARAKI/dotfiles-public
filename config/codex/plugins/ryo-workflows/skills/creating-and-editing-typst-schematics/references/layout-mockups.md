# Schemock layout and editing handoff

## Fixed application and format

Use [Schemock v0.1.0](https://github.com/ryo-ARAKI/schemock/releases/tag/v0.1.0) and format v2 with desktop Google Chrome.
Download `schemock-v0.1.0.html`, `schemock-v0.1.0-data.tar.gz` and `SHA256SUMS` from the [fixed release](https://github.com/ryo-ARAKI/schemock/releases/tag/v0.1.0); verify SHA-256 before use:

- HTML: `a98d9700a911e22c5c1a6d3171ec0725895bdc6415433cba0dba3e26812e8d5d`
- Data archive: `41c46b4e04b04763e41b7d47037dae2c64e49d84b592320c0385181ec44871a1`

Do not automatically fetch the latest version or modify the app per figure.
After download, opening the HTML and JSON needs no network, server, login or installation.
The archive contains the complete [format specification](https://github.com/ryo-ARAKI/schemock/blob/v0.1.0/docs/data-format-v2.md), schemas, [agent workflow](https://github.com/ryo-ARAKI/schemock/blob/v0.1.0/docs/agent-workflow.md), migration instructions and runnable examples.
Use these versioned documents as the detailed contract; the app and format versions are distinct.

## Propose and exchange

First establish scientific meaning, relationships, directions, containment, qualitative versus measured quantities, required labels, assets, and receiving size and language.
Prepare 2–3 meaningfully different compositions as variants in one v2 JSON and static PNG previews rendered from that same data with the app; retain a 20 draft-unit outer padding unless the composition requires otherwise.
The app supports node/edge rectangles with flat groups and qualitative spectrum paths, regions and labels.
For images, set shapes or other unsupported primitives, explain the limitation and agree on a separate representation; do not silently substitute boxes or patch the editor.

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

Before final production obtain explicit human adoption and identify the figure, revision, selected variant and snapshot ID or file hash. Intermediate JSON and exports do not constitute adoption.
Use the adopted variant's `current`, preserving deleted objects as absent, labels/newlines, colors, geometry and all curve controls.
Build editable Typst manually, with no application or JSON dependency at compile time; record coordinate conversion, physical dimensions and intentional typography or cleanup differences.
Show composition-changing cleanup and obtain the affected adjustment before proceeding.
Compile standalone and in receiving contexts; inspect page count, physical dimensions, extracted labels and rendered pages at publication size while preserving the receiving document settings.
See [editable Typst source](editable-typst-source.md) and [Typst recipes](typst-recipes.md).

## Legacy data

Both old families use schema version 1, so never infer the family from that number.
Use the app's **旧JSONを移行**, explicitly select the family and preserve the original; save to a different filename and open the resulting v2 JSON separately.
If initial states are missing, supply the matching complete original JSON or known old HTML as directed by the [migration guide](https://github.com/ryo-ARAKI/schemock/blob/v0.1.0/docs/migration-v1.md); unsupported or mismatched input must be rejected, not guessed.
