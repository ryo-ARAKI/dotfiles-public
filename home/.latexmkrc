#!/usr/bin/perl

$latex = 'lualatex -synctex=1 %O %S -halt-on-error';
$bibtex = 'biblatex';
$biber = 'biber --bblencoding=utf8 -u -U --output_safechars';
$dvipdf = 'dvipdfmx -f takao.map %O %S';
$max_repeat = 5;
$pdf_mode = 3;
$pvc_view_file_via_temporary = 0;
$pdf_previewer = 'evince 2>/dev/null';
