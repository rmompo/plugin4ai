# Plugin Spec: p4-converter

> **Status:** `beta` | **Version:** `1.0.6` | **Ports:** Claude Code only

## Overview

`p4-converter` converts PDF, DOC, DOCX, PPT, and PPTX documents to structured, LLM-optimized Markdown. It uses a 6-step local pipeline driven by three external tools (`qpdf`, `python3`, `libreoffice`) and Claude's own vision/reading capabilities for content extraction.

The output is a clean `.md` file with YAML frontmatter, proper heading hierarchy, Mermaid diagrams where applicable, and no processing artifacts.

---

## Skill: `setup`

### Purpose

Verifies that all required external tools are installed and meet the minimum version constraints. Prints a status table and install instructions for any missing tool.

### Invocation

```
/p4-converter:setup
```

### Non-Goals

- Does not install tools automatically.
- Does not modify any system configuration.

---

## Skill: `any-to-md`

### Purpose

Converts one or more documents (PDF, DOC, DOCX, PPT, PPTX) to Markdown using a 6-step pipeline:

1. **Inventory** — resolve input glob, detect already-converted files, confirm with user
2. **To PDF** — convert non-PDF files via LibreOffice headless (permanent artifact)
3. **Split** — divide PDF into 5-page chunks via qpdf (`.tmp.pdf`)
4. **Extract** — LLM reads each chunk sequentially and produces `.tmp.md`
5. **Consolidate** — Python script merges chunks into final `.md` with frontmatter
6. **Review** — LLM quality pass + cleanup of all `.tmp.*` files

### Invocation

```
/p4-converter:any-to-md [path/to/file-or-folder-or-glob]
```

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_ALL_TO_MD_PATTERN` | — | Input path/glob (overrides interactive prompt) |
| `AGENT_ALL_TO_MD_OUTPUT` | — | Output folder for `.md` files; empty or `"source"` = co-located with source |
| `AGENT_ALL_TO_MD_REPROCESS` | `false` | Set to `true` to reprocess already-converted files without prompting |

### Output format

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

### Non-Goals

- Does not convert Markdown to other formats.
- Does not upload documents anywhere.
- Does not process images as standalone files (images embedded in documents are extracted/described inline).

---

## External dependencies

| Tool | Required version | Use | Optional? |
|------|-----------------|-----|-----------|
| `qpdf` | `>=10.0.0` | PDF splitting | No |
| `python3` | `>=3.8.0` | Consolidation script | No |
| `libreoffice` | `>=7.0.0` | DOC/DOCX/PPT/PPTX → PDF | Only if non-PDF inputs |

---

## Port Status

| CLI | Location | Status |
|-----|----------|--------|
| Claude Code | `claudecode/p4-converter/` | ✅ Beta |
| GitHub Copilot | `ghcopilot/p4-converter/` *(planned)* | 🔲 Not yet |

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.0.4 | Fix qpdf constraint to >=10.0.0; fix SOURCE_FOLDER / OUTPUT_PATH variable consistency; clarify inventory loop and Step 6.1 tool; document AGENT_ALL_TO_MD_OUTPUT env var |
| 1.0.3 | Add input-path, glob/file selection and output-path parameters to any-to-md |
| 1.0.2 | Add `any-to-md` skill — full 6-step conversion pipeline |
| 1.0.1 | Add `setup` skill — dependency verification |
| 1.0.0 | Initial plugin scaffold |
