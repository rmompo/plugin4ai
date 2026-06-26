# Antigravity CLI/TUI Marketplace

This directory contains plugin ports for Antigravity (`agy`) CLI/TUI.

## Available plugins

| Plugin | Status | Skills |
|--------|--------|--------|
| `p4-core` | stable | `git-commit`, `git-sanitize`, `model-behaviour`, `model-route`, `sanitize`, `setup`, `skill-list` |
| `p4-plugin` | beta | `create`, `update`, `remove`, `skill-add`, `skill-update`, `skill-remove`, `skill-doctor`, `doc-doctor` |
| `p4-buddy` | beta | `gcomp` |
| `p4-coding` | beta | `code-standards`, `typescript-standards`, `python-standards`, `go-standards`, `java-standards`, `code-review` |
| `p4-agent` | beta | `md-check`, `md-checkrefs` |
| `p4-antigravity` | beta | `statusline` |
| `p4-ccvv` | beta | `profile-gather`, `profile-update`, `generate`, `regen`, `export` ¹ |
| `p4-converter` | beta | `any-to-md` ² |
| `p4-crawler` | beta | `extract` ³ |

> ¹ `export`: PDF requires `pdflatex`; if missing, automatically downgrades to HTML.
> ² `any-to-md`: best-effort mode — missing `libreoffice`/`qpdf`/`python3` trigger graceful degradation.
> ³ `extract`: static (curl-only) mode — Playwright/SPA rendering is not supported.

## Notes on this port

- **Frontmatter**: minimal — only `name` and `description` fields are present in SKILL.md files.
- **Interactive input**: no `AskUserQuestion` or `ask_user` tool — all interactive steps use plain text prompts.
- **Storage paths**: `~/.p4/` (universal, shared across CLIs), `~/.gemini/config/plugins/` (agy plugin cache).
