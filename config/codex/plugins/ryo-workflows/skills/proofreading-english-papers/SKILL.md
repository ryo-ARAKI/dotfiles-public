---
name: proofreading-english-papers
description: Use when proofreading or polishing existing English scientific manuscripts, including requests for Japanese explanations or original/revised comparisons. Excludes translation from Japanese alone, writing from scratch, section planning, and page layout alone.
---

# Proofread English Papers

Improve existing English while preserving the author's scientific meaning and evidential scope.
Prioritize **claims and argument → evidence and scope → readability → grammar and notation**.
Retain correct prose and clear direct observations; do not manufacture improvements or hedge every statement.

## Establish scope

The required inputs are the existing English and the proofreading request.
Use surrounding text, definitions, Japanese intent notes, and journal or spelling preferences when supplied; do not require a questionnaire.
The full revised text means the sentences, paragraphs, or section requested this time.
Read other sections as context without expanding the editing scope.
Return chat proposals for pasted text; reading a file alone does not authorize editing it.
Edit files only when requested, within the authorized scope.

This skill owns language revision across document formats.
It does not supply missing research, calculations, literature searches, independent verification of citations or journal rules, or persistent records of the author's habits.
Japanese-only translation, new writing, and document or section design are separate tasks.
For a full Typst report task, `writing-typst-research-reports` owns document structure, page composition, and artifact validation; this skill supplies English revision criteria.
English-only proofreading of Typst does not require that report workflow, PDF generation, or layout inspection.
This skill can be used without any other skill or source notes.

## Revise with seven lenses

Use these as judgment criteria, not seven mandatory report sections.

| Lens | Decision |
| --- | --- |
| Sentence role | Distinguish definitions, assumptions, aims, methods, derivations, observations, interpretations, and predictions. Choose verbs accordingly; an aim expressed with “to demonstrate” is not a reported result. |
| Evidence and claim | Match the claim to supplied evidence. “Is consistent with” does not establish causation. Finite measurements alone do not establish a limit or mechanism. Preserve supported assertions without adding may/suggest merely for caution. |
| Comparisons and conditions | Compare like quantities: a coefficient with a coefficient, not a case. Clarify omitted targets or evaluation criteria only when context identifies them uniquely. Retain parameter ranges, assumptions, methods, and comparison conditions. |
| Subject, verb, modifiers | Make the subject and verb express the intended relation. Place modifiers near their targets, resolve pronoun antecedents when unambiguous, and align parallel elements. Do not guess what an ambiguous modifier refers to. |
| Technical terms | Keep one term for one concept. Distinguish quantities such as energy and energy per unit mass, or wavenumber and wavevector. Preserve definitions and inherited terminology; stylistic variety does not justify changing concepts. |
| Sentence and paragraph logic | Clarify local information order, repetition, and links such as condition, contrast, and consequence within the requested scope. Introduce existing definitions before use where helpful. Do not invent missing definitions, impose a paragraph formula, or redesign sections. |
| Grammar and notation | Check agreement, countability, articles, prepositions, parallelism, equation punctuation, and role-appropriate tense. Inherit manuscript spelling and explicit journal conventions rather than imposing one tense or English variant throughout. |

## Preserve meaning and handle uncertainty

Compare the candidate with the original before returning it.
Preserve numbers, units, symbols, equations, conditions, comparison scope, assumptions, citation meaning and keys, labels, cross-references, and document syntax.
Keep the strength of claims as well as their content.
Separate proposals affecting scientific meaning or claim strength from ordinary grammar corrections, with their rationale and any needed author decision.
Do not silently strengthen or weaken a claim, add a causal explanation, or fill a gap with plausible research content.

When meaning is not unique or supporting evidence is missing, retain the affected original wording in the revised text, identify it as unresolved, and ask the single question needed for the next decision.
Continue other determinate revisions; do not present the whole passage as settled.
If manuscript text conflicts with intent notes or definitions, identify the specific conflict and ask rather than choosing the scientific interpretation.
If a revision requires a new scientific fact, separate it as an author decision instead of supplying the fact.
If surrounding sections or evidence cannot be read, state the inspected scope and do not claim external consistency or scientific correctness has been verified.
If source syntax cannot be preserved confidently, provide a safe English proposal and its intended location instead of applying a speculative source edit.

## Return usable text and reasons

By default, return the full revised text for the requested scope first, followed by the important change reasons in Japanese.
Connect each reason to the changed expression and its purpose in this manuscript.
Group minor grammar corrections when useful; fix neither a change count nor an explanation count.
If no changes are needed, return the requested text and say so without inventing reasons.
Explain actual revisions, not generic advice or judgments about the author's ability or habits inferred from repeated advice.

Honor explicit alternatives for format or explanation language.
Keep unresolved wording visible in either format, with its reason and the one outstanding question.

When comparison format is requested, choose the form for each sentence or paragraph by how easily the correspondence can be followed, not a fixed character count or change percentage.
Mix the following forms within a request as needed, preserving every change:

- **Local edits:** For word or phrase replacements, additions, or deletions that retain the sentence structure, show one combined sentence with deletions as `~~old~~` and additions as `**new**`, followed by the Japanese reason. Multiple local edits can share one sentence when easy to follow.
- **Larger rewrites:** For reordered phrases or clauses, split or merged sentences, or a combined diff that is hard to follow, show **original → revised → Japanese reason** separately. Strike through changed spans on the original side and bold changed spans on the revised side. Treat moved wording as a deletion at its old position and an addition at its new position.

Leave unchanged text unmarked; do not invent edits or emphasis for passages needing no change.
Use the smallest readable changed unit: a whole word for an inflection or attached-punctuation change, or a phrase or clause for a structural rewrite, rather than emphasizing an unchanged sentence or paragraph.
Connect Japanese reasons to the actual changed expressions and their purposes.
Do not routinely repeat the full clean revised text in addition to a requested comparison.

Apply display markup only after the original and revision are settled; do not revise the English to fit the display.
For a combined diff, check that reading the deletion side or addition side reconstructs the original or revision, including punctuation and conditions.
For separate versions, remove the display markup and check each against its corresponding text.
Keep comparison markup out of manuscript files.

If markup would interfere with Markdown, LaTeX, Typst, code, or existing emphasis, leave protected syntax intact.
When safe word-level markup is not possible, show faithful original and revised text in code blocks or another syntax-preserving form, with explicit deletion/addition labels and the corresponding wording outside the protected text.
If the display cannot render the distinction, use those labels without retrying color effects or claiming successful rendering.
Retain unresolved original wording, explain why it remains unresolved, and ask only the next needed question while continuing determinate revisions elsewhere.

## Comparison examples

### Local edits

Context uniquely identifies the reference as the coefficient measured in case B under the same conditions.

At 300 K, the coefficient in case A ~~agree~~ **agrees** with **that in** case B within 2%.

理由：`agree` を単数主語に合わせて `agrees` に修正しました。
`case B` を `that in case B` とし、文脈で特定できる係数同士の比較を明示しました。
300 K、2%、比較条件と一致の強さは維持しています。
比較対象が文脈から特定できなければ、その箇所は原文のまま残して確認します。

### Larger rewrite

Original: ~~We used the measurements at 300 K to calculate~~ the ~~coefficient,~~ ~~and we did this separately for each sample~~.

Revised: **For each sample, we calculated** the **coefficient** **from the measurements at 300 K**.

理由：`we did this separately for each sample` を文頭の `For each sample` にまとめ、各試料について計算したことを明示しました。
`used the measurements ... to calculate` を `calculated ... from the measurements` に組み替え、算出対象を主語・動詞の近くに置きました。
後続節の統合に伴い、`coefficient,` のコンマを削除しました。
測定温度300 Kと各試料を別々に扱う条件は維持しています。
