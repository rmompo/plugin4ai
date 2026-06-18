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
| [`p4-core`](./plugins/p4-core/README.md) | stable | `git-commit`, `model-behaviour`, `sanitize`, `setup` ¹ |
| [`p4-plugin`](./plugins/p4-plugin/README.md) | beta | `create`, `update`, `remove`, `skill-add`, `skill-update`, `skill-remove`, `skill-doctor`, `doc-doctor` |
| [`p4-buddy`](./plugins/p4-buddy/README.md) | beta | `gcomp` |

> ¹ `skill-list` and `model-route` are Claude Code CLI/TUI-exclusive and are not ported to this CLI.

## Update the marketplace index

```bash
gh copilot plugins marketplace update plugin4ai-ghcopilot
```

## Remove the marketplace

```bash
gh copilot plugins marketplace remove plugin4ai-ghcopilot
```
