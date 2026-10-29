# Saved-Result Data Contract

Use this contract for instructions, sender packaging, and receiver validation.
These are required meanings, not a new common schema or directory layout.
Reuse the recipient's existing schema, loader, selector, inventories, and provenance formats.

## Select the Necessary Bundle

Start from the requested analysis, local operations, condition/key sets, accepted versions, and identities of existing recipient inputs.
The normal transfer supports reading saved estimates, arithmetic regrouping, verification, and later plotting without rerunning the simulation or estimator.
Full scientific recomputation requires separately agreed inputs and environment.

Classify candidate files as **include**, **reuse an existing recipient input**, **retain at source for upstream reruns**, or **unneeded for this request**, with reasons and dependencies.
Check the proposed file count, total bytes, and dominant size contributors before assembly; justify any whole-directory inclusion.
Code trees, raw logs, duplicate per-case tables, old failed packages, and PDF/PNG files are not default payloads; include them when the requested checks need them.
Do not reduce individual estimates to displayed means or discard undisplayed saved values used by the same analysis merely because future use seems unlikely.
If the requested scope cannot be supported, report the missing values or dependencies rather than filling estimates or silently narrowing conditions.

## Values, Conditions, and Provenance

Include saved individual IC/member, matching, replicate, sample-size, and directional estimates wherever applicable, summaries for comparison, and the spectra, energies, or diagnostics needed by the requested operations.
Retain the original TOML/JSON sidecars and relevant input metadata rather than replacing them with a lossy summary.
Record applicable conditions from authoritative metadata; distinguish unknown from not applicable:

- Parameters, IC/member identities and counts, actual pair/sample counts, physical times and saved indices, requested and realized lag/time pairs.
- Bands or shell sets, pairing method, difference sign, selection method, seed, and saved selection-index location/identity. A seed cannot replace saved indices for exact selection.
- Estimator name/version, neighborhood count, distance metric, normalization, pooling/transformation order, directional column meanings, units, and normalization coefficients with sources.
- Shared ICs/members, paired versus unpaired replicates, nested versus separate sample-size selections, and weighting. Dependent rows must not be pooled as independent observations.
- Producer commit and dirty state, relevant code hashes, runtime/dependency versions, analysis ID, and source input identities. A commit alone does not prove clean generating code.

Keep different estimator versions and scientific conditions distinct even at equal sample counts.
Each row or unambiguous partition retains its actual producer and input identities, including reused and new rows.
An input-manifest byte hash, analysis signature, and converted JSON hash identify different things.
Preserve directional labels for negative rates and the producer's signed-sum definition.
Define SD, SE, or CI, averaging/variance denominators, and weights; a single replicate has no estimable sample SD.

## Whole Files and Extracted Tables

Copy included original CSV and metadata bytes unchanged, preserving precision, headers, columns, row order, and line endings.
When only part of a large table is needed, keep the original at source and transfer a separately identified derived table with:

- Original analysis ID, source host/path, original file SHA-256, and source retention evidence or its unconfirmed status.
- Exact extraction conditions and a source-row key or row-number mapping for every output row, defining header/row numbering conventions.
- Transformation instructions or a runnable script, including schema adaptations and any changes to numerical strings, precision, columns, order, or line endings.
- Output SHA-256, size, row count, and identities of metadata needed to interpret the selection.

Do not label a derived hash as the original file hash.
At the sender, compare the extraction and required aggregates with the original.
At the receiver, verify included bytes, mappings, conditions, and required arithmetic; independently rerunning extraction from an omitted original remains unverified.
Original retention does not require another full original copy inside every transfer bundle.
Record omitted originals' location, identity, reason for omission, retention evidence, and any operations that still need them.
Do not claim remote retention was confirmed when only drafting instructions or reading local historical records.

## Current Inventory and Historical Evidence

The current inventory describes only the inputs promised for the current scope:

| Information | Contract |
| --- | --- |
| Payload | Relative path, role, bytes, SHA-256, CSV data-row count where applicable, source/analysis identity, and assembly time. Include necessary metadata and verification code. |
| Reused local inputs | Exact relative location, identity/hash, scientific conditions, and required availability. If recipient availability is unknown, prefer a self-contained bundle. |
| Coverage | Planned dataset, delivered subset, accepted subset, missing conditions, and dependencies needed for each promised operation. |
| History | Original delivery manifests, producer verification, and old failed-version references are historical evidence with their original identities. Copy only relevant history, or retain exact references and retention status. |
| Management records | Declare which inventory, verification outputs, or receipt records are outside the payload hash set and why. Avoid circular/self hashes. Account for unexpected files rather than ignoring them silently. |

Keep the current inventory separate from the complete original delivery manifest and its validation history.
Never rewrite the original manifest or its hash to fit a subset.
A subset verifier must not require omitted historical payloads; a full-delivery verifier may still be used on the preserved full delivery.
Provide a package README or existing equivalent with purpose, column meanings/units, selectors, dependencies, verification commands, principal saved results, reproduction limits, and unresolved items.

## Verify the Declared Scope

Use an existing verifier that covers the declared scope; otherwise provide a small package-specific check, preferably standard-library Python for CSV/JSON.
It must resolve package inputs relatively, work after relocation without source-host access for promised local operations, and exit nonzero on a contract violation.
Verify:

1. Required files, sizes, SHA-256, CSV data-row counts, and the declared inventory boundary.
2. Unique keys and exact expected key sets from declared conditions, including missing/unexpected conditions; distinguish planned coverage from accepted completed coverage.
3. Required/nonfinite values under explicit producer missing/censoring rules. Preserve and report invalid entries rather than silently dropping or filling them.
4. Applicable signed sums and summary mean/SD reconstructed from individual values, with tolerance and aggregation definitions. If individual values are unavailable, report which summaries cannot be independently reconstructed.
5. Condition/provenance consistency, new/reused partitions, and identities of required local dependencies.

Verify promised reads, selections, and arithmetic regrouping with source-only inputs unavailable.
Separate included dependencies from omitted upstream originals; if an omitted dependency is needed for a promised operation, that operation is incomplete.
Verification does not establish scientific correctness of the simulation, estimator, or raw inputs.
Separate historical producer checks, checks executed now, and external facts not checked.
Preserve partial dataset status: successful packaging or completed derived analysis does not prove the whole planned dataset or simulation complete.

## Sender Sealing

After validation, create a single-root `tar.gz` and an independent archive SHA-256 outside it.
Extract into a fresh temporary area using the safe archive checks in [receive-and-integrate.md](receive-and-integrate.md#inspect-and-record-receipt), then rerun the required checks on the actual artifact.
If any check changes payload files, regenerate the inventory as needed, reseal, and report the final archive hash.
Preserve failed candidates and prior successful packages; a failed candidate is not an accepted delivery.
