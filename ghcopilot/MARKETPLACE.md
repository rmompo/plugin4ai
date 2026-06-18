# GitHub Copilot CLI Marketplace

This directory is a self-contained GitHub Copilot CLI plugin marketplace.  
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
| [`p4-core`](./plugins/p4-core/README.md) | stable | `model-routing`, `commit` ¹ |

> ¹ The `setup` skill (statusline install) is Claude Code only and is not ported to this CLI.

## Update the marketplace index

```bash
gh copilot plugins marketplace update plugin4ai-ghcopilot
```

## Remove the marketplace

```bash
gh copilot plugins marketplace remove plugin4ai-ghcopilot
```
