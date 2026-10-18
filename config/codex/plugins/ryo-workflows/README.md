# Ryo Workflows

Reusable Codex workflows with no personal repository paths or host names.

## Skills

- `dotfiles-deploy`: managed-source generation, layered planning, and authorized deployment.
- `creating-arxiv-diff-pdfs`: complete PDFs from official arXiv source versions, preserving raw latexdiff output and checking first/middle/last pages.
- `export-editable-typst-figures`: portable, editable Typst figure bundles with data provenance and scoped rendering checks.
- `writing-typst-research-reports`: new reports, revisions, and read-only reviews connecting research questions, scientific evidence, prose, tables, and report composition while inheriting document formatting.
- `extrip-to-ics`: Google Calendar importable ICS files from Japanese train and hotel reservation Markdown, with departure-station and hotel Google Maps links.

## Source and deployment

The public manifest deploys this plugin to `~/plugins/ryo-workflows` in local context.
Its metadata points to `./skills/`; every referenced resource is deployed with the entrypoint.
Registration and enablement remain explicit local setup, separate from copying these files.

An optional private layer can add repository-specific skills and replace this plugin's
metadata without changing the plugin directory or duplicating the shared skill sources.
Existing private marketplace registration and enablement continue to select that combined plugin.
Use matching public/private source revisions and start a fresh Codex session after deployment.
