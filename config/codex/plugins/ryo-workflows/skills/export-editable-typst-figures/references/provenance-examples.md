# Provenance Examples

These TOML excerpts illustrate [Provenance Records](data-and-provenance.md#provenance-records); they do not require TOML, new schema fields, or loader changes.
Keep the existing normalization block and generation records in place, replace placeholders with observed identities, and include only checks actually performed.
Omit unknown identities and record the gaps; hashes do not establish upstream calculation correctness.

## Minimal Extraction

This example copies one CSV unchanged. Repeat input/snapshot entries for multiple inputs; storage transformations also need their mappings and reconstruction evidence.
The normalization hash identifies the original input before provenance was appended, not the final TOML containing that hash.

```toml
# Existing normalization settings and generation records remain unchanged.
[bundle_provenance.extraction]
repository = "SOURCE_REPOSITORY_URL"
commit = "FULL_SOURCE_COMMIT"
figure_path = "figures/original.typ"
normalization_path = "data/original_normalization.toml"
normalization_sha256 = "ORIGINAL_NORMALIZATION_SHA256"

[[bundle_provenance.extraction.inputs]]
path = "data/original.csv"
sha256 = "ORIGINAL_CSV_SHA256"
row_count = 2

[[bundle_provenance.extraction.snapshot]]
path = "data/values.csv"
sha256 = "ORIGINAL_CSV_SHA256"
row_count = 2
encoding = "UTF-8"
line_endings = "LF"

[[bundle_provenance.current.data]]
path = "data/values.csv"
sha256 = "ORIGINAL_CSV_SHA256"
row_count = 2

[[bundle_provenance.verifications]]
id = "extraction-001"
operation = "new-extraction"
baseline = "Observed source inputs at the recorded revision"
checked = ["CSV bytes and normalization settings retained", "Compilation and relocation"]
unverified = ["Upstream calculations"]
```

Keep extraction immutable during later edits; current data describes the files now used, and verifications append scoped observations.
Record the environment of rendering checks using the bundle's existing representation.
The following updates each start independently from this snapshot, not from one another.

## Data Update

For an authorized added measurement, replace the existing current-data entry for that path and append the verification; do not append duplicate current entries or overwrite extraction history.
This is an update excerpt, not text to append wholesale to the extraction example.

```toml
# Replace the existing current-data entry for this path.
[[bundle_provenance.current.data]]
path = "data/values.csv"
sha256 = "REPLACEMENT_CSV_SHA256"
row_count = 3

# Append only after the corresponding checks pass.
[[bundle_provenance.verifications]]
id = "data-002"
operation = "data-change"
baseline = "Local pre-edit inputs: ORIGINAL_CSV_SHA256"
data_sha256 = "REPLACEMENT_CSV_SHA256"
change = "Added the requested measurement; existing cells retained"
checked = ["Requested delta", "Normalization retained", "Affected outputs regenerated and inspected"]
unverified = ["Upstream calculations"]
```

Record the replacement data's source and available generation identity in the existing format.
An authorized scientific delta does not require lossless reconstruction; that check applies to storage transformations.
If normalization changes too, preserve the old settings as history and record new settings and their generation identity separately.

## Presentation Update

For a font edit to the minimal snapshot, retain extraction, current data, and normalization definitions/values; append only the performed rendering verification.
The original CSV hash below is unchanged and does not depend on the data-update example.
If this append shares a loaded normalization file, its bytes/hash change; check the final loaded settings and affected rendering as required by [Stage, Verify, and Update](data-and-provenance.md#stage-verify-and-update).

```toml
[[bundle_provenance.verifications]]
id = "presentation-002"
operation = "presentation-change"
baseline = "Fresh compilation of the identified local pre-edit source"
data_sha256 = "ORIGINAL_CSV_SHA256"
change = "Changed the requested font; data selection and aggregation retained"
source_sha256 = "EDITED_SOURCE_SHA256"
output_path = "figure.pdf"
output_sha256 = "VALIDATED_OUTPUT_SHA256"
typst_version = "OBSERVED_TYPST_VERSION"
packages = ["OBSERVED_PACKAGE_SPECIFICATION"]
fonts = ["OBSERVED_FONT_NAME"]
checked = ["CSV bytes and normalization settings unchanged", "Affected outputs compiled and inspected"]
unverified = ["Unavailable upstream comparison", "Upstream calculations"]
```

For a display conversion, also describe the observed formula, units, scope, and numerical checks using existing descriptive fields.
For additional affected helpers, panels, or formats, record their validated identities and checks in the existing representation; full-PDF success does not prove them.
Separate saved-output/source mismatches and environment substitutions from the intended change, and report unavailable upstream materials specifically.
Candidates from failed/partial attempts must not replace successful output hashes; follow [Stage, Verify, and Update](data-and-provenance.md#stage-verify-and-update).
