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

For authorized scientific changes or supplied new data, use [Supplied Data and Scientific Changes](../../creating-and-editing-typst-figures/references/data-and-verification.md#supplied-data-and-scientific-changes).
Keep the new source identity separate from the original extraction identity in the bundle's records.
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

Follow the shared [Stage, Verify, and Update](../../creating-and-editing-typst-figures/references/data-and-verification.md#stage-verify-and-update) for candidate generation, final loaded inputs, and preservation on partial failure.
Use the authoritative source invocation for extraction and the identified local pre-edit bundle for maintenance.
Apply the following bundle-specific conditions in addition to those common checks.

- New extraction compares source-revision or captured working-tree inputs and the observed rendering with the candidate bundle.
  Use [Extraction and Portability](#extraction-and-portability) for dependencies, relocation, editability, and affected recipient integration.
  Storage changes also require lossless table reconstruction as described above.
- Prepare the verification append in the temporary copy using [Provenance Records](#provenance-records).
  Keep original extraction history, current input identities, and this verification separate.
  Presentation-only edits retain extraction and unchanged-data records without schema or loader migration.
- If provenance shares a loaded input file, preserve its scientific definitions and loading behavior and verify the final loaded file through the common procedure.
  Preserve historical snapshot hashes and record any needed final shared-file identity outside that file.
- Update the affected delivery and successful records only after all required outputs and bundle-specific checks pass.
  Record unavailable upstream comparison and recipient checks as gaps; local success does not establish upstream calculation correctness.

Keep temporary checks outside delivery and avoid simulation reruns or full source-repository test suites solely for packaging.
