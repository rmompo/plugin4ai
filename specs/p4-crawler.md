# Plugin Spec: p4-crawler

> **Status:** `beta` | **Version:** `1.0.2` | **Ports:** Claude Code CLI/TUI only

---

## Overview

p4-crawler is a web crawler and documentation extractor. It systematically explores websites — both static (curl-based) and SPAs (Playwright-based: Angular, React, Storybook) — filters discovered content by topic and keywords, downloads pages and attachments (PDF, DOC, XLS), converts them to Markdown, and generates a structured index with metrics.

Designed for intranet documentation extraction. Supports authenticated sites (Joomla, form-based, HTTP Basic) with automatic session re-authentication.

---

## Port Status

| CLI | Location | Status |
|-----|----------|--------|
| Claude Code CLI/TUI | `claudecode/p4-crawler/` | ✅ Beta |

---

## Skill: `setup`

### Purpose
Verifies that all runtime dependencies are installed: system tools (python3, curl) from catalog, and pip packages (beautifulsoup4, html2text). Reports each dependency with its status and install instructions. Also checks for the optional playwright package (required only for SPA mode).

### Invocation
```
/p4-crawler:setup
```

### Non-Goals
- Does not install dependencies automatically — reports and guides only
- Does not validate crawl configuration

---

## Skill: `extract`

### Purpose
Orchestrates the full documentation extraction pipeline in 8 phases: configure (interactive), login (optional), crawl, deduplicate, filter, download, and generate. Produces a structured Markdown index (`INDEX.md`) with an extraction parameter table, page index, file directory tree, and process metrics.

### Invocation
```
/p4-crawler:extract
```

### Non-Goals
- Does not modify the crawled site
- Does not store credentials to disk — session memory only
- Does not support parallel crawling (sequential by design for rate-limiting compliance)

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.0.2 | Add `extract` skill — full pipeline: configure, crawl, dedup, filter, download, generate |
| 1.0.1 | Initial release — `setup` skill |
