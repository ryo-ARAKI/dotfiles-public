# Receive and Integrate Saved Results

Read [data-contract.md](data-contract.md) for values, identities, inventories, and verification scope.
This procedure accepts a full historical package or a selected data bundle; it does not initiate sender packaging.

## Inspect and Record Receipt

Use the received archive/directory, any independently supplied sender hash, existing accepted inputs, and the recipient's placement policy.
Leave the received original unchanged and use a new candidate area for validation and integration; follow the user’s storage instructions rather than automatically creating another archival copy.
Before extraction, inspect all archive member names and types: require a single root and reject absolute paths, parent traversal/root escapes, duplicate normalized destinations, dangerous symbolic/hard links, and special files.
For directory receipts, likewise check resolved paths and links before using them; do not follow references outside the declared receipt except explicitly inventoried reusable inputs.
Keep extraction inside the new area and do not overwrite existing files.

Record receipt time, source, original location and retention status, archive size/SHA-256 (or directory inventory), sender-hash comparison, commands actually run and their results, and external checks not performed. Integrate these records into existing documentation or inventory when adequate; add a separate receipt record only when needed.
If the sender hash is absent, record **not supplied**; the receiver's computed hash is an identity, not proof of agreement with the sender.
An absent sender hash permits internal validation with that limit disclosed; a supplied but mismatched hash rejects the candidate.

For a full historical delivery, retain its structure, original manifest bytes, and producer verification records in the candidate during receipt validation, and run applicable original checks there.
Record the adopted subset in the existing current inventory or an equivalent distinct record and validate it under its own contract; do not modify the original manifest to describe it.
Do not require every historical file in a current subset or alter the historical verifier/manifest to manufacture success.
Identify failures belonging only to retained old versions separately; a failure affecting the version proposed for adoption blocks that adoption.

## Build and Check the Integration Candidate

Select the minimum inputs needed to regenerate the report and perform its required checks, explaining each input's role. For example, summaries and individual values may both be needed to verify a mean and SD; the number of tables depends on the task. Do not automatically add batch tables, snapshots, duplicate subsets, logs, or history to Git.
Reuse existing data placement, naming, schemas, loaders, selectors, inventory, and explanations. Do not create an analysis-ID or receipt-date directory, separate README or receipt JSON, custom loader or verifier, or code-level hash dictionary when existing mechanisms suffice. Retain necessary sidecars when existing records cannot express their content.
Keep adopted source tables' values and bytes intact; map columns at read time when needed. Avoid unnecessary transformation, merging, and duplication. Consolidate conditions, averaging and SD definitions, analysis ID, hashes, provenance, and verification limits into the existing explanation or inventory.
Follow the user’s original-storage policy; do not automatically retain old inputs or another copy of the delivery. Check dependencies of shared inputs before replacing references, including other conditions; a Git-ignored area inside a worktree still needs a handoff before that worktree is removed and is not automatically permanent storage.
Integration alone does not authorize deleting files, untracking duplicates, changing history, or relocating originals outside the approved scope.

Compare incoming and accepted inputs by identity, scientific conditions, keys, values, and lineage:

| Situation | Integration decision |
| --- | --- |
| Same payload bytes | A shared reference to one canonical file is allowed; retain every source identity and role. Existing duplicates remain unless their deletion is separately authorized. |
| Same key and consistent value/conditions | Verify shared rows and retain all relevant lineage; do not relabel reused rows with the new producer's identity. |
| Same key but conflicting value or adoption condition | Stop adoption and report both sources. Do not overwrite, average, or select by latest timestamp alone. |
| Different scientific conditions or estimator versions | Keep separate partitions/selectors and their definitions; do not silently harmonize them. |
| Required existing reuse input absent or hash differs | Stop as an unmet differential-delivery prerequisite. Identify the missing/wrong dependency; do not substitute nearby conditions. |

Prefer source lists/selectors over a combined CSV when they satisfy the loader.
If a combined table is necessary, treat it as derived and retain per-row/partition producer/input identity and source-row mappings under the data contract.
Do not copy the same CSV for each figure or analysis when shared references suffice.

Separately from full-delivery receipt checks, verify the adopted subset with only candidate inputs and explicitly verified reusable dependencies available. Run the existing loader or a small input-read check, required selections and arithmetic regrouping, and agreement checks on the existing shared portion. Check promised hashes, row counts, keys, conditions, means and SD where applicable; identify recalculations requiring omitted originals as limits.
Verify the current inventory, required metadata, keys, and scientific conditions under the common contract.
Adoption requires all checks necessary for the promised scope to pass; historical producer success does not replace fresh candidate checks.

## Adopt Without Losing Prior State

Before updating accepted references, record their previous content/hash and the intended replacements.
Prefer an atomic selector/reference switch where appropriate. Do not automatically create archives of the received original or previous accepted version; follow the user’s retention instructions and preserve existing files unless separately authorized to remove them.
For unavoidable multiple-file updates, keep a journal of only this operation's writes and a restoration path for each.
Recheck expected prior content before each replacement to detect concurrent user edits.
On failure, restore only writes still matching this operation's replacement; leave intervening user edits intact and report unresolved restoration conflicts.
Never reset a whole working tree or copy an old directory wholesale over user work.
Validate the resulting adopted references/read contract; if that fails, restore the previous references under the same preservation rules and report incomplete adoption.

## Failure and Completion Evidence

Reject adoption for payload hash mismatch, required missing files, invalid keys/conditions, conflicting values, unsafe paths, or failed required checks.
Leave the received original and existing accepted inputs and user edits unchanged; record rejected candidate evidence in the existing records where suitable.
Distinguish a runner failure before command start or unavailable dependency environment from a data failure; report unexecuted checks and do not install an environment without authorization.
An upstream original needed only for omitted reruns may remain externally unverified if all promised local operations pass; an external dependency needed for those operations leaves them incomplete.
Old historical failures, repaired accepted versions, and current candidate failures must have separate identities and outcomes.

Before staging, inspect the final diff and each new file’s role, and stage only necessary files when staging is authorized.

Return the receipt evidence, original location or retention status, adopted inputs and reusable source identities, current inventory, executed checks/results, conflicts/missing inputs, and external limits.
Report prepared, actually transferred, receipt-verified, and integrated as separate states, with planned/delivered/adopted coverage and partial dataset status.
For replacements, inspect dependencies through readers, generated data, relevant figure PDFs, and report text and captions. State the requested scope and any downstream updates still needed. Figure production and manuscript editing require explicit task scope; complete only the portions authorized.
