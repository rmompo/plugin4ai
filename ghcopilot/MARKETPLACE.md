# GitHub Copilot CLI/TUI Marketplace

This directory is a self-contained GitHub Copilot CLI/TUI plugin marketplace.  
Register it once and all plugins become available via `gh copilot plugins install`.

## Register the marketplace

```bash
gh copilot plugins marketplace add https://github.com/rmompo/plugin4ai/tree/main/ghcopilot
```

## Install a plugin

```bash
gh copilot plugins install p4-core
```

## Available plugins

| Plugin | Status | Skills |
|--------|--------|--------|
| [`p4-core`](./plugins/p4-core/) | stable | `git-commit`, `model-behaviour`, `model-route`, `sanitize`, `setup`, `skill-list` |
| [`p4-plugin`](./plugins/p4-plugin/) | beta | `create`, `update`, `remove`, `skill-add`, `skill-update`, `skill-remove`, `skill-doctor`, `doc-doctor` |
| [`p4-buddy`](./plugins/p4-buddy/) | beta | `gcomp` |
| [`p4-coding`](./plugins/p4-coding/) | beta | `code-standards`, `typescript-standards`, `python-standards`, `go-standards`, `java-standards`, `code-review` |
| [`p4-agent`](./plugins/p4-agent/) | beta | `md-check`, `md-checkrefs` |
| [`p4-ccvv`](./plugins/p4-ccvv/) | beta | `profile-gather`, `profile-update`, `generate`, `regen`, `export` |
| [`p4-converter`](./plugins/p4-converter/) | beta | `any-to-md` ¹ |
| [`p4-crawler`](./plugins/p4-crawler/) | beta | `extract` ² |

> ¹ `any-to-md`: best-effort mode — missing `libreoffice`/`qpdf`/`python3` trigger graceful degradation instead of hard stops.
> ² `extract`: static (curl-only) mode — Playwright/SPA rendering is not supported.

## Update the marketplace index

```bash
gh copilot plugins marketplace update plugin4ai-ghcopilot
```

## Remove the marketplace

```bash
gh copilot plugins marketplace remove plugin4ai-ghcopilot
```
