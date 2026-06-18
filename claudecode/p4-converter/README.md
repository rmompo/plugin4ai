# p4-converter

Document-to-Markdown converter plugin for Claude Code. Converts PDF, DOC, DOCX, PPT, and PPTX files to structured, LLM-optimized Markdown using a 6-step local pipeline.

## Pipeline

```
Input (PDF/DOC/DOCX/PPT/PPTX)
    ↓ LibreOffice (non-PDF only)
    PDF
    ↓ qpdf (5-page chunks)
    .tmp.pdf chunks
    ↓ LLM extraction (sequential)
    .tmp.md chunks
    ↓ Python consolidation script
    .md (with frontmatter)
    ↓ LLM review + cleanup
    Final .md (LLM-optimized)
```

## Skills

| Skill | Invocation | What it does |
|-------|-----------|--------------|
| `setup` | `/p4-converter:setup` | Verifies that qpdf, python3, and libreoffice are installed |
| `any-to-md` | `/p4-converter:any-to-md [path]` | Converts documents to structured Markdown |

## Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| `qpdf` | ≥11.0.0 | Split PDF into chunks |
| `python3` | ≥3.8.0 | Consolidation script |
| `libreoffice` | ≥7.0.0 | Convert DOC/DOCX/PPT/PPTX to PDF |

## Quick start

```bash
# 1. Verify dependencies
/p4-converter:setup

# 2. Convert a document
/p4-converter:any-to-md input/docs/manual.docx

# 3. Convert a whole folder
/p4-converter:any-to-md input/docs/
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_ALL_TO_MD_PATTERN` | — | Input path/glob (overrides interactive prompt) |
| `AGENT_ALL_TO_MD_REPROCESS` | `false` | Set to `true` to reprocess already-converted files |

## Output

Each converted document produces a `.md` file in the same folder as the source, with YAML frontmatter:

```yaml
---
source: manual.docx
source_format: docx
converted_via_pdf: true
converted: 2026-06-05T10:30:00
pages: 12
chunks: 3
chunk_size: 5
split_tool: qpdf
---
```

## Installation

```bash
claude plugins marketplace add rmompo/plugin4ai
claude plugins install p4-converter
```
