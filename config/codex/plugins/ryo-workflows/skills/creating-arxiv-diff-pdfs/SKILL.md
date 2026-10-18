---
name: creating-arxiv-diff-pdfs
description: Use when producing a complete latexdiff PDF from two official arXiv source versions, especially when TeX compilation hangs, REVTeX or natbib output breaks, or a partial PDF could be mistaken for completion.
---

# Creating arXiv Diff PDFs

## Outcome Contract

Deliver one complete diff PDF based on the two official source versions. Keep the exact raw latexdiff output immutable. Apply compatibility edits only to a separately named copy and report every edit.

## Workflow

1. Inspect existing archives, extracted trees, logs, outputs, and processes. Do not repeat failed attempts without reading their evidence.
2. Confirm official-source provenance and the two main TeX files. Compile each original version or reuse fresh recorded baseline evidence.
3. Run and record the exact user-selected latexdiff command. Save its raw output, checksum it, and never edit it.
4. Compile in an isolated output area using the source project's engine and bibliography workflow.
5. If compilation hangs or fails, copy the raw source to a compatible source, read the troubleshooting reference, find the smallest failing boundary, and make only evidence-backed repairs.

When the raw build hangs or fails, read [REVTeX and latexdiff troubleshooting](references/revtex-latexdiff-troubleshooting.md).

6. Rebuild the full document and check expected sections, bibliography, and appendices against the source versions. Do not substitute chunks, early pages, a page-limited build, or a concatenation of partial builds.
7. From this skill's directory, run `python3 scripts/verify_diff_pdf.py --pdf ABSOLUTE_PDF --log ABSOLUTE_LOG --output-dir ABSOLUTE_OUTPUT_DIR` with the final TeX `.log` from that build and a fresh verification directory.
   The script checks TeX errors, a completed-build summary, matching log/PDF page counts, PDF structure, and sample rendering; it cannot establish source coverage or visual correctness.
   Open and inspect every rendered first/middle/last image; a generated image is not visual evidence until inspected.

## Completion

Report absolute artifact paths, exact latexdiff command, compile passes, raw-source checksum and reproduction evidence, compatibility repairs, structural checks, log status, page count, and visual findings for first/middle/last pages. State any unverified item; do not claim completion while one remains.
