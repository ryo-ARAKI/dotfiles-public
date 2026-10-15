# Data and Provenance

Use the section for the requested operation; [Stage, Verify, and Update](#stage-verify-and-update) governs affected output updates.
TOML recording examples are in [Provenance Examples](provenance-examples.md); keep the bundle's existing format and loader keys.

## Extraction and Portability

For a new extraction, identify the authoritative report invocation and reproduce its observed rendering before applying requested presentation changes.
Standalone previews may use different normalization state, dimensions, fonts, or show rules.
Preserve rendering-sensitive setup, including state and show-rule order, when reproducing the report invocation.
Trace imports, data, images, and generated assets; include the dependencies needed for rendering and editing, and regeneration helpers for separately rendered assets.
Keep ordinary Typst source editable, package version specifications and required assets intact, and loading paths bundle-relative without symlinks back to the source repository.
The bundle requires Typst, its fonts, and packages; it is not a complete offline environment.
Recipients copy the whole bundle and compile its entry point, for example `typst compile figure.typ figure.pdf` from the bundle directory.

Record the source repository, full revision, and original figure/data/normalization paths.
Use the specified revision without mixing in working-tree changes; identify included uncommitted files by their actual hashes separately from the base commit.
Compare extracted inputs with that revision or the captured working-tree contents.
Keep normalization and CSV generating identities and scopes distinct; one artifact's revision does not establish another's origin.

When creating a bundle or changing file organization, loading, or export paths, move only the bundle and verify compilation there.
An edit and recompile in a temporary copy can check direct editability when needed.
When extracting or changing inclusion format, integration code, or material compiler/export assumptions, test a minimal recipient document with the actual compiler and export settings.
Use PDF inclusion only if supported; otherwise generate a supported format such as SVG, and verify that delivered format too.
Standalone compilation does not prove recipient inclusion.

### Unavailable Upstream Materials

For maintenance, use pre-edit local source, inputs, and a fresh compilation as the baseline; preserve extraction history without claiming its upstream equivalence was freshly checked.
Report unavailable repositories/revisions/inputs and the resulting limits.
Local hashes, compilation, and inspection do not verify upstream calculations.
For new extraction, proceed only when available authoritative rendering and inputs suffice; otherwise finish independent work and identify the missing dependency.

## Storage and Scientific Data Changes

Consolidate CSVs only within the requested scope, when compatible schemas and recipient loading or maintenance justify it; keep incompatible schemas separate.
Use a noncolliding identifier column and preserve every original header, cell string, row, column, within-input order, and identifier-to-source mapping, including unplotted data.
Do not parse and rewrite numeric strings, round, average, subsample, or recompute during a storage transformation.
Update loaders while retaining the original selection and aggregation inputs, order, and method.
Verify by splitting on the identifier and removing it to reconstruct every original header, row, and cell string.
Distinguish original-byte hashes from table equality after reserialization; check actual file hashes, row counts, mappings, and normalization.

For an authorized scientific data change, account for its delta against pre-edit inputs rather than requiring reconstruction of the old values.
Record newly supplied data's source and available generation identity; the original extraction identity does not describe its origin.
If normalization changes, preserve original settings as history and record the new settings and generation identity separately.
If data reduction is requested, explain the editing capabilities it removes.

## Provenance Records

Preserve original normalization definitions/values, generation records, and extraction history.
Use the existing practical format (TOML, JSON, Markdown, or similar); record observed identities and verified claims, with unknown revisions/conditions explicitly left as gaps.

| Record | Meaning and update rule |
| --- | --- |
| Extraction | Original repository/revision/paths and exported input snapshot identities; retain during later edits |
| Current data | Actual bundle-relative input paths, SHA-256 hashes, row counts excluding headers, and source identities; update changed-path entries without duplicates |
| Verification | Append scoped observations tied to baseline/inputs, changed source/output identities, rendering environment, checks performed, and gaps |

At extraction or storage change, record encoding, line endings, identifier/column mappings, concatenation order, and cell-preserving rules as applicable.
Preserve calculation conditions, definitions, commands, and generating-code identities; identify values transcribed only from directory names as labels.
Original absolute paths may remain in provenance, but rendering must use local paths.
Hash the original normalization input before appending provenance; do not store a final TOML's hash inside itself.
When provenance shares a loaded normalization or conditions file, metadata-only additions may change that file's bytes and hash, but must preserve its scientific definitions/values and loading behavior.
This allowance does not permit rewriting scientific data cells or historical records; keep original snapshot hashes, and record any needed final shared-file hash outside that file in the existing practical format.
Hashes establish content identity, not numerical correctness.
Recheck historical claims before presenting them as current; reuse unaffected evidence only while its inputs and material environment assumptions remain unchanged.

## Stage, Verify, and Update

Use the authoritative source for extraction and the pre-edit bundle for maintenance.
For presentation changes, keep scientific data bytes, normalization definitions/values, stored conditions, selection, and aggregation unchanged; derived display coordinates do not replace saved data.
Full and standalone outputs share the existing condition definitions wherever stored.
The transformation and feature-specific checks are in [Presentation and Layout](presentation-and-layout.md#feature-specific-verification).

1. Capture the relevant pre-edit source/helper and input identities and normalization settings.
   Freshly compile the baseline; identify any saved-output/source mismatch separately from the requested change.
   Compare baseline and candidates under the same compiler/package/font assumptions except for requested changes; separate other environment differences.
2. Generate every affected delivered figure, panel, and format in a temporary copy.
   Verify the requested delta and preserved scientific inputs/meaning, compile, and inspect the affected rendering at its receiving size.
   For storage-only restructuring, investigate visual differences; for presentation edits, account for intended differences. PDF timestamps are not rendering differences.
3. Prepare the verification append in the temporary copy, recording only performed checks in the existing format, with baseline, environment, changes, validated identities, and unresolved gaps.
   Presentation-only work retains extraction and unchanged-data records; it adds verification without schema or loader migration, updating any needed shared-file identity outside that file.
   If this changes a loaded input file, verify its final loaded scientific definitions/values and rerun affected loader/rendering checks before delivery; do not claim whole-file byte equality for that shared file.
4. Only after the affected set and final inputs pass, update outputs and successful records coherently, following destination tracking policy.
   Hash the actual validated files; subsequent source/input/output edits invalidate affected checks and identities, including metadata edits to loaded files.

If compilation, numeric correspondence, inspection, or a required panel/format fails, preserve previous delivery and successful records.
Keep candidates and diagnostics separately; never replace success hashes with unverified candidates or mark unperformed checks as passed.
A failed/incomplete observation may be recorded explicitly if the existing format supports it; partial success is not success of the affected set.
Repair and rerun affected checks before updating delivery.
Keep temporary checks outside delivery and avoid simulation reruns or full source-repository test suites solely for packaging.
