# Writing and Tables

## Questions, Answers, and Evidence

For a follow-up, read the preceding report's questions, established findings, unresolved issues, quantities and notation, and level of explanation, then identify the answer added here.
Inherit that context subject to the latest user instructions and authoritative definitions.
Map each research question to the relevant established finding, additional result, conditional answer, and supporting figure or table.
A short list of question/answer pairs can expose this correspondence when several questions motivate the report; choose the structure that serves the argument.
For each comparison, connect the saved statistic definition, reference value, comparison objects and direction, condition range, and supporting evidence before phrasing the answer.
State the conditions under which the answer holds and distinguish observed trends from interpretation.
Compare like quantities and identify changes in method, reference, sampling, or conditions that limit a comparison.
Keep endpoint and zero-boundary decisions consistent with the supplied scientific contract rather than importing a rule from another experiment.

### Statistics and Counterexamples

Read the definitions and condition-level saved values behind a claim, rather than inferring another statistic from a visually similar plot.
Keep RMSE, SD, and the mean's deviation from its specified reference distinct; use the corresponding saved results, reference definitions, and uncertainty definitions for claims about each.
A smaller SD or RMSE alone does not establish reduced bias or error cancellation as a mechanism.
An interval for one quantity is not evidence for a differently named quantity.
Check claims such as “all conditions,” “always,” or “larger/smaller” against the relevant directions, observation lengths, and other condition keys, including values that reverse the ordering.
Retain condition-level counterexamples in the verification evidence while focusing the body on overall trends, scientific meaning, and essential conditions and representative values.
During review, distinguish small local ranking reversals from exceptions that change the answer to the research question.
Do not reject a supported overall trend solely because of a minor reversal; use “generally” or “tend to” when that accurately scopes the claim.
Judge the difference's magnitude and relevance to the conclusion from the saved results rather than applying a universal numerical threshold.
State conclusion-changing exceptions briefly or narrow the claim to the supported range instead of extending one direction or length to the whole experiment.
Select qualifications by their relevance to the research question and effect on the claim, keeping necessary limitations close to that claim rather than listing generic unverified properties.
Omitting detail from the body does not remove saved values or verification evidence.
Replace “it depends on conditions” with the conditions and trends actually established by the saved results.
If evidence or a definition is missing, hold or narrow only the dependent claim and continue independently supported work.

### Meaning and Size of a Comparison

Distinguish finite-lag reference quantities from their derivative limits; use the intended reference for each reported error.
Keep a theoretical quantity's invariance under rescaling or standardization separate from finite-sample estimator error and its observed changes.
Separate differences between methods at a given condition from changes within each method when a condition varies.
When the question asks how much a choice matters, give the magnitude and range supported by the saved values as well as the ordering, using representative values and essential conditions in the body.
State the denominator for a relative change and distinguish it from a difference between methods.
Exhaustive lists of condition-specific change rates and ranking reversals are not a default reporting format.
Keep parameter values such as τ and k when they explain the conditions or their scientific meaning.
List method-specific RMSE values only when the numerical comparison is needed for the argument; otherwise refer to the figure, using representative values or a range when useful.
A small observed change alone proves neither equivalence nor absence of a statistically significant difference.
Use the existing inferential evidence for such claims; verifying arithmetic on saved values does not authorize recomputing estimators or confidence intervals.
Choose precision and wording that answer the research question without turning this report's change rates into universal thresholds.

Connect physical or statistical interpretations to the relevant saved results, verified analytical relations, or established model properties, comparing related figures where they clarify the finding.
Distinguish the observed trend, its interpretation, and a proposed mechanism, and limit any estimator guarantee to what the supporting evidence establishes.
For an error scan that decreases, levels off, and then increases, explain the balance of variability and mean deviation when the saved components and error definition support that interpretation.
Distinguish a low-error region or minimum among measured discrete settings from a generally optimal parameter or validated selection rule.

### Current User Edits and Material Selection

Use the latest user-edited text and request as the baseline for argument and tone.
Identify what each section, table, or figure contributes to a question and retain evidence needed for the comparison, rather than restoring material from an old plan.
Honor decisions to remove details, qualifications, analyses, or appendices; an older plan alone is no reason to restore them.
Distinguish omission from the manuscript, removal from Git tracking, and deletion of files; each has a different effect and authority requirement.
A request to untrack data leaves the actual files in place; physical deletion needs authorization for those targets.

## Prose and Notation

At a figure's first body reference, first identify the displayed quantities and comparison axes.
State the main feature or trend in a subsequent sentence, then give the interpretation needed for the research question when supported by evidence.
For example, introduce the comparison with “Figure … compares RMSE across methods as τ varies.”
Follow with a supported observation, such as “The results show that RMSE generally decreases over the scanned range.”
Cite the supporting figure or table explicitly from the body and adapt the opening and paragraph structure to the argument.
Distinguish prior knowledge from what the new results establish.
Use equations and algorithms for definitions and procedures, tables and captions for shared conditions, and the body for comparisons and interpretations.
Refer explicitly to the existing equation, algorithm, table, or caption instead of repeating its definitions, steps, or common conditions.
Restate a condition or explain a formula in the body when it changes the comparison's meaning or supplies a non-obvious interpretive link.
Remove repeated explanations, unnecessary negative statements, and internal processing detail that do not help assess the finding, keeping decisive values, definitions, and scientific qualifications explicit.
Leave work history such as “we performed additional analysis” or “we reused existing results” out of the body when it does not change the meaning of the results.
Treat TODOs and outline notes as working material, separate from this rule for report prose.
For Japanese section headings, prefer noun phrases that describe the section's content.

Use one sentence per source line for natural language that you touch, including body text, captions, and explanatory lists.
Leave code, raw data, and multiline equations in their appropriate syntax and layout.
Use mathematical notation for quantities and powers of ten where it improves reading.
Keep quantity definitions, symbols, and units consistent across prose, equations, axes, legends, and captions.
When observation duration is the question's axis, use time after confirming the saved-sample interval and count/index/endpoint convention; retain sample count when count itself is the question.
For coefficients in theoretical formulas, use suitable general symbols after checking the assumptions and statistical denominators; state the current sample size separately as an experimental condition.
Notation-only changes preserve numerical values and scientific meaning.
Check that prose names for methods explain the relevant distinction rather than exposing opaque internal identifiers or implying unwarranted exactness.

Keep reader-facing conditions and method distinctions visible.
Move commit hashes, run IDs, internal paths, and implementation identifiers that do not help the argument into comments or existing tracking records while preserving working lookups, assertions, and provenance links.
Use the existing recording mechanism rather than adding a visible reproducibility appendix by default.

## Conditions and Tables

Present fixed and scanned conditions and reference values where they best support interpretation: body, caption, or table.
Use a concise table when exact values, conditions, or definitions are needed for a decision or comparison, or when explicitly requested.
Do not automatically add a condition table or a detailed numerical companion to a figure.
Distinguish quantities with different roles, such as integration step and saved-sample interval, even when their numeric values coincide.
Choose row/column orientation, headings, and widths for the reader's comparison; transpose only when it improves reading at the inherited page and text size.
Shorten a crowded heading before shrinking the entire table.
Put symbols, meanings, and units where they can be found easily, using the caption for shared definitions when that avoids repeated cells.
Keep condition keys traceable to their saved values even when the visible labels are simplified.

For a true scan range, a “Range” heading with minimum–maximum and an emphasized reference value can be concise.
Identify discrete scans as discrete and show actual values or selections when needed to avoid implying nonexistent measured conditions or obscuring the comparison.
An exhaustive scan listing is not required by default.
Distinguish a selected baseline from the extrema and avoid implying that it was measured when it was only a reference.
Use readable numbers or short terms in cells, mathematical powers instead of raw `1e+05` notation, and existing document conventions for emphasis.
Explain empty cells when their meaning is ambiguous; do not invent a correspondence for an unmatched method.

Consolidate shared caption definitions and use an explicit cross-reference for details supplied elsewhere, keeping each table's identity and necessary interpretation clear.
