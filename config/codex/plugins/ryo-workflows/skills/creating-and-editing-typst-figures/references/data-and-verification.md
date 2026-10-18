# Data and Verification

Use this contract for new scientific figures and revisions, inside a manuscript, standalone source, or existing portable bundle.
Read [Presentation and Layout](presentation-and-layout.md#feature-specific-verification) only for the affected visual or export features.

## Inputs and Baselines

Treat the latest user-edited source and saved inputs as the starting point.
Capture the relevant source/helper identities, scientific input hashes, definitions, conditions, selection, aggregation, normalization, stored intervals, and existing successful outputs and records before editing.
Use the existing specification or recording method; ordinary plotting does not require a provenance TOML or second hand-maintained condition inventory.
For an existing figure, freshly compile the relevant baseline when needed to establish source/output correspondence.
Identify a saved-output/source mismatch separately from the requested change and compare under the same compiler/package/font assumptions except for authorized changes.
For a new figure without a prior output, derive the expected series, condition tuples, points, units, reference values, and interval endpoints from the actual inputs and definitions.
A candidate made from the new code is not independent evidence of fidelity to an old figure.

Presentation changes preserve scientific data bytes, stored conditions, selection, aggregation, normalization definitions/values, and interval estimates.
Derived display coordinates leave saved values intact.
Reconcile selected keys and numerical coordinates as well as file hashes; hashes prove content identity, not numerical correctness.
For merged panels or overlays, compare each expected condition tuple and its multiplicity, series, points, and interval endpoints; matching totals alone is insufficient.
A display offset changes drawing positions while retaining access to the unshifted quantities and conditions.
Preserve existing data/condition/series definitions as the common source for rendering, legends, selectors, exporters, and caption ingredients.

## Supplied Data and Scientific Changes

Distinguish newly supplied data from presentation changes and account for its authorized delta against pre-edit inputs.
Record its source and available generation identity separately from the old inputs and extraction history; leave unknown origins explicit.
Preserve unchanged cells and conditions, and validate the expected added or replaced records rather than demanding equality with the old dataset.
For an authorized normalization change, retain previous settings as history and identify the new settings and generation source.
A plotting request or supplied dataset does not authorize rerunning simulations, estimation, bootstrap, or interval generation.
Simple arithmetic to verify saved-value correspondence is distinct from recomputing scientific estimators or uncertainty.
For storage transformations in portable bundles, use the lossless reconstruction procedure in [Storage and Scientific Data Changes](../../export-editable-typst-figures/references/data-and-provenance.md#storage-and-scientific-data-changes).

## Stage, Verify, and Update

1. Establish the applicable baseline or new-figure expectations from [Inputs and Baselines](#inputs-and-baselines).
   Stage source changes and generate candidates in a temporary area, preserving the original inputs, user edits, and successful deliverables.
   If concurrent edits change the baseline, reread and reconcile them before any overwrite.
2. Generate every affected required figure, panel, and format into that area.
   Verify the requested delta, scientific input preservation or authorized data delta, condition-level numerical correspondence, compilation, and rendering at the receiving size.
   Use the applicable [Feature-Specific Verification](presentation-and-layout.md#feature-specific-verification) rows.
   For storage-only restructuring, investigate visual differences; for presentation edits, account for intended differences.
   PDF timestamps are not rendering differences.
3. Prepare records of checks actually performed, tying observations to input/source/output identities, baseline, environment, changes, and gaps in the existing format.
   Verify the final inputs that the renderer actually reads, including loaded metadata after any recording edit.
   A metadata-only edit in a loaded conditions/normalization file may change its bytes while preserving scientific values; check loading and rerun affected rendering rather than claiming whole-file byte equality.
   Keep a final shared-file hash outside that file to avoid a self-hash cycle.
4. Update only the authorized deliverables and successful records coherently after the entire affected set and final loaded inputs pass, following destination tracking policy.
   Hash the actual validated files.
   Reuse valid checks while their target tree, inputs, and material environment assumptions remain unchanged.
   Subsequent source, input, metadata, or output edits invalidate affected checks and identities; rerun only that scope.

## Failure and Scope

| Finding | Action and preserved result |
| --- | --- |
| Missing statistic, quantity definition, units, storage convention, or reference | Hold the dependent claim or conversion, record the missing evidence, and continue independent work. |
| Missing/duplicated condition, wrong coordinate or interval, clipping, or unreadable output | Keep the affected figure and dependent inclusion incomplete; retain previous successful outputs and records. |
| Compile failure or one required panel/format fails | Hold the jointly affected output set; retain successful delivery and success hashes, and keep candidates and diagnostics separately. |
| Compiler, package, or font unavailable | Report the environment limitation separately from source errors and leave the affected checks unverified; installation requires authorization. |
| User or another session changes the target | Reconcile with the latest source and preserve those edits instead of restoring an old snapshot. |

Execute the candidate generation and update decision before reporting a preservation check as passed.
Partial success is not success of the affected set, and unperformed checks stay explicit.
An incomplete attempt may be recorded separately when the existing format supports it; failed candidates never replace successful identities.
Cleanup covers run-created temporary artifacts; pre-existing outputs, data, or source deletion needs the corresponding authority.
