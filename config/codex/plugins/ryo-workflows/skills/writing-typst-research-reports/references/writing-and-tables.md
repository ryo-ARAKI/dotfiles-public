# Writing and Tables

## Questions, Answers, and Evidence

Map each research question to the relevant established finding, additional result, conditional answer, and supporting figure or table.
A short list of question/answer pairs can expose this correspondence when several questions motivate the report; choose the structure that serves the argument.
For each comparison, connect the saved statistic definition, reference value, comparison objects and direction, condition range, and supporting evidence before phrasing the answer.
State the conditions under which the answer holds and distinguish observed trends from interpretation.
Compare like quantities and identify changes in method, reference, sampling, or conditions that limit a comparison.
Keep endpoint and zero-boundary decisions consistent with the supplied scientific contract rather than importing a rule from another experiment.

### Statistics and Counterexamples

Read the definitions and condition-level saved values behind a claim, rather than inferring another statistic from a visually similar plot.
RMSE alone does not establish bias or SD: locate the corresponding bias/SD results and their reference and uncertainty definitions before describing them.
An interval for one quantity is not evidence for a differently named quantity.
Check claims such as “all conditions,” “always,” or “larger/smaller” against the relevant directions, observation lengths, and other condition keys, including values that reverse the ordering.
Retain counterexamples and narrow the claim to the supported range instead of extending one direction or length to the whole experiment.
Replace “it depends on conditions” with the conditions and trends actually established by the saved results.
If evidence or a definition is missing, hold or narrow only the dependent claim and continue independently supported work.

### Meaning and Size of a Comparison

Distinguish finite-lag reference quantities from their derivative limits; use the intended reference for each reported error.
Keep a theoretical quantity's invariance under rescaling or standardization separate from finite-sample estimator error and its observed changes.
Separate differences between methods at a given condition from changes within each method when a condition varies.
When the question asks how much a choice matters, give the magnitude and range supported by the saved values as well as the ordering.
For example, compare a method's saved values before and after a boundary-rule change with a stated denominator; that relative change is distinct from its difference from another method.
A small observed change alone proves neither equivalence nor absence of a statistically significant difference.
Use the existing inferential evidence for such claims; verifying arithmetic on saved values does not authorize recomputing estimators or confidence intervals.
Choose precision and wording that answer the research question without turning this report's change rates into universal thresholds.

### Current User Edits and Material Selection

Use the latest user-edited text and request as the baseline for argument and tone.
Identify what each section, table, or figure contributes to a question and retain evidence needed for the comparison, rather than restoring material from an old plan.
Previously removed analyses and past appendix requests are history, not requirements to rebuild them.
Distinguish omission from the manuscript, removal from Git tracking, and deletion of files; each has a different effect and authority requirement.
A request to untrack data leaves the actual files in place; physical deletion needs authorization for those targets.

## Prose and Notation

Lead result paragraphs with the trend and its research meaning, then cite the supporting figure or table from the body.
Distinguish prior knowledge from what the new results establish, and keep limitations close to the claims they qualify.
Replace lists of fine numerical values and internal processing steps with the level of detail needed to assess the finding; retain decisive values and definitions where they matter.
Remove repeated explanations and unnecessary negative statements, keeping necessary constraints and scientific qualifications explicit.
For Japanese section headings, prefer noun phrases that describe the section's content.

Use one sentence per source line for natural language that you touch, including body text, captions, and explanatory lists.
Leave code, raw data, and multiline equations in their appropriate syntax and layout.
Use mathematical notation for quantities and powers of ten where it improves reading, with consistent symbols and defined units.
Check that prose names for methods explain the relevant distinction rather than exposing opaque internal identifiers or implying unwarranted exactness.

Keep reader-facing conditions and method distinctions visible.
Move commit hashes, run IDs, internal paths, and implementation identifiers that do not help the argument into comments or existing tracking records while preserving working lookups, assertions, and provenance links.
Use the existing recording mechanism rather than adding a visible reproducibility appendix by default.

## Conditions and Tables

Introduce fixed conditions in the body and collect scanned conditions and reference values in a readable table.
Distinguish quantities with different roles, such as integration step and saved-sample interval, even when their numeric values coincide.
Choose row/column orientation, headings, and widths for the reader's comparison; transpose only when it improves reading at the inherited page and text size.
Shorten a crowded heading before shrinking the entire table.
Put symbols, meanings, and units where they can be found easily, using the caption for shared definitions when that avoids repeated cells.
Keep condition keys traceable to their saved values even when the visible labels are simplified.

For a true scan range, a “Range” heading with minimum–maximum and an emphasized reference value can be concise.
Retain discrete scan values or explicit selections when a range alone would imply nonexistent conditions or obscure the comparison.
Distinguish a selected baseline from the extrema and avoid implying that it was measured when it was only a reference.
Use readable numbers or short terms in cells, mathematical powers instead of raw `1e+05` notation, and existing document conventions for emphasis.
Explain empty cells when their meaning is ambiguous; do not invent a correspondence for an unmatched method.

Retain a detailed table only when its values support a decision or comparison that the text and figures do not already communicate.
Consolidate shared caption definitions and use an explicit cross-reference for details supplied elsewhere, keeping each table's identity and necessary interpretation clear.
