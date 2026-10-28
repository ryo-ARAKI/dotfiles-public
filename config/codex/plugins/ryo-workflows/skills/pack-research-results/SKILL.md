---
name: pack-research-results
description: Use when preparing saved research calculation results for transfer and local reporting, or drafting instructions for a remote agent to assemble such a data package; excludes running new calculations, report writing, and editable figure packaging.
---

# Package Saved Research Results

Prepare saved numerical results that a recipient can verify, regroup, and plot without rerunning the simulation or estimator.
Preserve individual estimates, scientific conditions, and provenance rather than delivering only figures or averages.

## Select the Operation

- **Instructions only:** inspect available local data and report loaders, then produce a remote-agent request specifying the target analysis, required outputs, verification, and completion evidence below. Distinguish observed local facts from remote facts still to discover. Do not connect to the remote or package data merely to draft instructions.
- **Package results:** inspect the authoritative analysis and recipient requirements, then assemble and verify a new distribution directory. Preserve existing packages and source inputs. Creating the package does not authorize transfer, deletion, Git operations, deployment, or new scientific calculations.

Reuse recipient schemas, selectors, and provenance formats when they already express the needed contract.
Keep host names, personal paths, and numerical analysis conditions task-specific.
Determine the intended local scope: plotting saved estimates, arithmetic regrouping, or full scientific recomputation.
The default is plotting and arithmetic regrouping; full recomputation needs a separately agreed input and environment scope.

## Required Package Contents

| Deliverable | Required information |
| --- | --- |
| Saved results | Original numerical tables, including individual IC, matching, replicate, sample-size, and directional estimates wherever available. Keep summaries as comparison inputs. Include spectra, energies, or other diagnostics needed for the requested report. |
| Conditions and provenance | Original input manifests and sidecar metadata; scientific definitions, input identities, generating code identity and environment, and new/reused result lineage. |
| File inventory | Relative path, role, bytes, SHA-256, CSV data-row count where applicable, source host/path, analysis ID, and assembly time. Reuse an existing manifest or snapshot; otherwise use `manifest.json`. |
| Reproduction boundary | Included dependencies and externally required files with exact identities; remote locations and identifiers of omitted large raw inputs or selection indices. State which local operations are possible and which require those omitted inputs. |
| Verification | Existing producer validation plus a package verifier and a separate record of checks actually run during assembly. |
| README | Purpose, file/column meanings, units, condition selectors, verification command and dependencies, principal saved results, limitations, and unresolved items. |

Copy original CSV and metadata bytes unchanged, preserving precision, row order, headers, and line endings.
If extraction or schema adaptation is needed, keep the originals and write a separate derived table with its transformation script and source-row mapping.
Retain original TOML/JSON sidecars rather than replacing them with a lossy metadata summary during transfer preparation.
Preserve existing identifiers when combining reused and newly computed results; each row or unambiguous partition must retain its actual producer and input identity.
An input-manifest byte hash, an analysis signature, and a converted JSON hash identify different things.

## Scientific Conditions to Resolve

Record the applicable items below from authoritative metadata; label unknown and not-applicable values separately.

- Parameters, IC/member IDs and counts, actual pair/sample counts, physical times and saved indices, requested and realized lag/time pairs.
- Bands or shell sets, pairing method, difference sign, selection method, seed, and saved selection-index location/identity. A seed alone is not a substitute for saved indices when exact selection matters.
- Estimator name and version, neighborhood count, distance metric, normalization, pooling/transformation order, directional column meanings, units, and normalization coefficients with their sources.
- Shared ICs or members, paired versus unpaired replicates, nested versus separate sample-size selections, and weighting rules. Do not pool dependent rows as independent observations.
- Producer commit and dirty state, relevant code hashes, runtime/dependency versions, and source input identities. Do not infer a clean revision from a commit alone.

For example, inclusive v1 and strict v2 estimates remain distinct even at equal sample counts.
Preserve direction labels for negative rates and define the sum as a signed sum when that is the producer's definition.
Document SD, SE, or CI and the averaging/variance denominator; a single replicate has no estimable sample SD.

## Verify and Seal

Use an existing verifier if it covers the package contract; otherwise include a small `verify.py`, preferably using the Python standard library for CSV/JSON packages.
The verifier must locate inputs relative to its own package, work after relocation without source-host access, and exit nonzero on a violated contract.
Check:

1. File presence, sizes, SHA-256, and CSV data-row counts. Inventory payload files explicitly; avoid self-hashing the inventory or its generated verification record.
2. Key uniqueness and expected key sets derived from declared conditions, including missing conditions and unexpected extras. Distinguish planned coverage from accepted completed coverage.
3. Required values and nonfinite entries using the producer's explicit missing/censoring rules. Preserve and report invalid entries; do not silently drop or fill them.
4. Applicable identities such as directional signed sums and summary mean/SD reconstructed from saved individual values. Record tolerance and aggregation definitions. If individual values are unavailable, state that the summary cannot be independently reconstructed.
5. Condition and provenance consistency, including new/reused partitions and external dependencies. Flag unavailable external inputs separately from verified included files.

Package verification does not prove that the estimator, raw inputs, or simulation were scientifically correct.
Separate producer claims from fresh assembly checks, and analysis completion from whole-simulation completion.
For incomplete analyses, describe the delivered subset and missing conditions; do not label the planned analysis complete.

After verification, create a `tar.gz` with a single package root and a separate archive SHA-256.
Extract it into a fresh temporary directory and rerun the verifier there to check the actual transfer artifact and its relative dependencies.
If verification fails, report the candidate and failures without presenting it as an accepted delivery or overwriting a previous successful package.

## Completion and Handoff

For packaging, return the archive's absolute path, byte size, SHA-256, included analysis/coverage, verification command and results, and unresolved or externally dependent items.
For instructions-only work, return a copyable request covering the same deliverables and done-when; remote Codex must discover unavailable remote facts rather than assume them.
Report source preparation, actual transfer, and recipient verification as separate states.
Local figure production and report writing are subsequent tasks; this skill ends at a verified data package or the requested remote instructions.
