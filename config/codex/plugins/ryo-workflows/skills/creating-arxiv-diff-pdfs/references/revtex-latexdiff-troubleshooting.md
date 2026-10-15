# REVTeX and latexdiff Troubleshooting

Use this reference only after the immutable raw latexdiff source fails or hangs. Make repairs in a separately named compatible copy, record them, and keep the raw file and its checksum unchanged.

## Diagnose Before Repairing

**Trigger:** TeX consumes CPU without progress, exits fatally, or leaves a short PDF. **Check:** inspect the latest `.log`, process state, last completed page, and a bounded minimal reproduction. Bisect by document boundary or macro family only when it narrows the first failing expansion. **Repair:** change the smallest demonstrated compatibility boundary. **Keep unchanged:** official source trees, raw latexdiff output, diff semantics, and full-document completion requirement.

## CFONT in Moving Arguments

**Trigger:** a REVTeX section/title or PDF-bookmark moving argument containing CFONT `\DIFadd`/`\DIFdel` repeatedly expands or hangs; the same content works outside the moving argument. **Check:** reduce to the affected heading and confirm the hang disappears when only that moving-argument expansion is neutralized. **Repair:** in the compatible copy only, make the visible commands robust and give hyperref explicit PDF-string behavior, adapting the existing generated macro names:

```tex
\let\DIFadd\relax
\let\DIFdel\relax
\let\DIFaddFL\relax
\let\DIFdelFL\relax
\DeclareRobustCommand{\DIFadd}[1]{\DIFaddtex{#1}}
\DeclareRobustCommand{\DIFdel}[1]{\DIFdeltex{#1}}
\DeclareRobustCommand{\DIFaddFL}[1]{\DIFadd{#1}}
\DeclareRobustCommand{\DIFdelFL}[1]{\DIFdel{#1}}
\pdfstringdefDisableCommands{%
  \def\DIFdel#1{}%
  \def\DIFadd#1{#1}%
  \def\DIFdelFL#1{}%
  \def\DIFaddFL#1{#1}%
  \def\DIFaddbegin{}\def\DIFaddend{}%
  \def\DIFdelbegin{}\def\DIFdelend{}%
  \def\DIFaddbeginFL{}\def\DIFaddendFL{}%
  \def\DIFdelbeginFL{}\def\DIFdelendFL{}%
}
```

Do not apply this pattern merely because the document uses REVTeX; require the moving-argument evidence. Keep visible red/blue CFONT content and raw source unchanged.

## Labels in Deleted Unnumbered Math

**Trigger:** a deleted `\label` inside `equation*`, `align*`, or another unnumbered construct causes a fatal counter/reference expansion. **Check:** isolate the deleted unnumbered block and confirm the label alone triggers failure. **Repair:** neutralize only that label in the compatible copy; if surviving new text still references the old key, add a documented compatibility alias or tag derived from the official sources. **Keep unchanged:** the displayed deleted mathematics, surrounding diff markers, and raw output.

## Bibliography Boilerplate

**Trigger:** natbib/REVTeX fails because latexdiff interleaves two generated `.bbl` structures or omits the old bibliography environment boilerplate. **Check:** compare the diff tail with both official-version `.bbl` files and identify missing environment/open-close commands separately from entries. **Repair:** restore old-version boilerplate and deleted old entries verbatim from the official old `.bbl`, while retaining the new version's current bibliography structure and entries. Never reconstruct old bibliography text from memory or an unrelated database. **Keep unchanged:** citation content, entry provenance, raw diff, and complete document scope.

## Warning Triage

Treat `LaTeX Error`, package errors, emergency stops, fatal errors, undefined-reference summaries, and undefined-citation summaries as failures. Treat multiply-defined citation/label warnings as reviewable warnings only when every key comes from intentionally retained old/new bibliography material and the final report records the count and reason. Re-run enough passes for references to settle; do not hide warnings by deleting log lines or globally suppressing diagnostics.

## Failed Completion Patterns

A short PDF produced before a hang, a few successful chunks, a page-limited build, omitted sections, rasterized pages, or concatenated partial PDFs is diagnostic evidence—not the final artifact. Disabling all diff markup, editing the immutable raw file, importing bibliography text without official provenance, or inspecting only one page also fails the contract. Completion requires one full PDF, structural and log gates, and actual visual inspection of first, middle, and last pages.
