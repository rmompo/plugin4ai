# plugin4ai

> Code once, port where you need it.

A single repository for AI CLI/TUI plugins. Each plugin is a self-contained concept that gets ported to supported CLIs/TUIs as native extensions — only where it makes sense.

---

## Supported CLIs/TUIs

| CLI/TUI | Vendor | Folder | Install |
|-----|--------|--------|---------|
| [Claude Code CLI/TUI](https://claude.ai/code) | Anthropic | [`claudecode/`](./claudecode/) | `claude plugins marketplace add rmompo/plugin4ai` |
| [GitHub Copilot CLI/TUI](https://cli.github.com) | Microsoft / GitHub | [`ghcopilot/`](./ghcopilot/) | *(see folder README)* |
| [Antigravity CLI/TUI](https://github.com/google/antigravity-cli) ¹ | Google | [`antigravity/`](./antigravity/) | *(see folder README)* |
| [Codex CLI/TUI](https://github.com/openai/codex) | OpenAI | `codex/` *(planned)* | `npm install -g @openai/codex` |

> ¹ Antigravity CLI/TUI es el sucesor de Gemini CLI, anunciado en Google I/O 2026.

---

## Plugins

### General plugins

| Plugin | Description | Status | Spec |
|--------|-------------|--------|------|
| `p4-buddy` | Skills for <company> employees — <hr-platform> mission report generation | `beta` | [spec](./specs/p4-buddy.md) |
| `p4-coding` | Coding standards and best practices — universal directives (SOLID, DRY, naming, error handling) auto-loaded at session start, with stack-specific skills for TypeScript, Python, Go, and Java | `beta` | [spec](./specs/p4-coding.md) |
| `p4-core` | Behavioral directives (P4D), model routing, and Conventional Commits enforcement | `stable` | [spec](./specs/p4-core.md) |
| `p4-plugin` | Lifecycle tooling for this marketplace — create and manage plugins and skills | `beta` | [spec](./specs/p4-plugin.md) |

### CLI/TUI-specific plugins

| Plugin | CLI/TUI | Description | Status | Spec |
|--------|---------|-------------|--------|------|
| `p4-antigravity` | Antigravity | Powerline-style status bar with session, branch, model and usage metrics | `beta` | [spec](./specs/p4-antigravity.md) |
| `p4-claudecode` | Claude Code | Custom status bar with project, branch, model and usage metrics | `stable` | [spec](./specs/p4-claudecode.md) |

---

## Installation & Lifecycle

For detailed install, update, uninstall, enable, and disable instructions per CLI/TUI → **[INSTALL.md](./INSTALL.md)**

---

## Adding a New Plugin

Use the `p4-plugin` skill — it scaffolds everything in one step:

```
/p4-plugin:manage create <plugin-name> [skill1 skill2 ...]
```

See [`specs/p4-plugin.md`](./specs/p4-plugin.md) for full details.
