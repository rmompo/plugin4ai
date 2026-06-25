# Claude Code CLI/TUI Marketplace

This directory is a self-contained Claude Code CLI/TUI plugin marketplace.  
Register it once and all plugins become available via `claude plugins install`.

## Register the marketplace

```bash
claude plugins marketplace add rmompo/plugin4ai
```

## Install a plugin

```bash
claude plugins install p4-core
```

## Available plugins

| Plugin | Status | Skills | Auto-setup |
|--------|--------|--------|------------|
| [`p4-core`](./p4-core/README.md) | stable | `model-behaviour`, `model-route`, `git-commit`, `git-sanitize`, `sanitize`, `skill-list`, `setup` | ✅ via agent |
| [`p4-claudecode`](./p4-claudecode/README.md) | stable | `statusline` | ✅ via agent |
| [`p4-buddy`](./p4-buddy/README.md) | beta | `gcomp` | — |
| [`p4-plugin`](./p4-plugin/README.md) | beta | `create`, `update`, `remove`, `skill-add`, `skill-update`, `skill-remove`, `skill-doctor`, `doc-doctor` | — |
| [`p4-ccvv`](./p4-ccvv/README.md) | beta | `setup`, `profile-gather`, `profile-update`, `generate`, `regen`, `export` | — |
| [`p4-converter`](./p4-converter/README.md) | beta | `setup`, `any-to-md` | — |
| [`p4-crawler`](./p4-crawler/README.md) | beta | `setup`, `extract` | — |
| [`p4-agent`](./p4-agent/README.md) | beta | `md-check`, `md-checkrefs` | — |
| [`p4-coding`](./p4-coding/README.md) | beta | `code-standards`, `typescript-standards`, `python-standards`, `go-standards`, `java-standards`, `code-review` | ✅ via agent |

## Update the marketplace index

```bash
claude plugins marketplace update plugin4ai-claudecode
```

## Remove the marketplace

```bash
claude plugins marketplace remove plugin4ai-claudecode
```
