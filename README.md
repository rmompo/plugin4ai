# plugin4ai

> Code once, port where you need it.

A single repository for AI CLI plugins. Each plugin is a self-contained concept that gets ported to supported CLIs as native extensions — only where it makes sense.

---

## Supported CLIs

| CLI | Vendor | Folder | Install |
|-----|--------|--------|---------|
| [Claude Code](https://claude.ai/code) | Anthropic | [`claudecode/`](./claudecode/) | `claude plugins marketplace add rmompo/plugin4ai` |
| [GitHub Copilot CLI](https://cli.github.com) | Microsoft / GitHub | [`ghcopilot/`](./ghcopilot/) | *(see folder README)* |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) ¹ | Google | `geminicli/` *(planned)* | `npm install -g @google/gemini-cli` |
| [Codex CLI](https://github.com/openai/codex) | OpenAI | `codex/` *(planned)* | `npm install -g @openai/codex` |

> ¹ Gemini CLI está siendo reemplazado por **Antigravity CLI** (Google I/O 2026). El sistema de plugins se preserva con el nuevo nombre.

---

## Plugins

| Plugin | Description | Status | Spec |
|--------|-------------|--------|------|
| [`p4-core`](./claudecode/p4-core/) | Behavioral directives (P4D), model routing, and Conventional Commits enforcement | `stable` | [spec](./specs/p4-core.md) |
| [`p4-claudecode`](./claudecode/p4-claudecode/) | Custom status bar for Claude Code with project, branch, model and usage metrics | `stable` | [spec](./specs/p4-claudecode.md) |
| [`p4-buddy`](./claudecode/p4-buddy/) | Skills for <company> employees — GComp mission report generation | `beta` | [spec](./specs/p4-buddy.md) |
| [`p4-plugin`](./claudecode/p4-plugin/) | Lifecycle tooling for this marketplace — create and manage plugins and skills | `beta` | [spec](./specs/p4-plugin.md) |

---

## Adding a New Plugin

Use the `p4-plugin` skill — it scaffolds everything in one step:

```
/p4-plugin:manage create <plugin-name> [skill1 skill2 ...]
```

See [`specs/p4-plugin.md`](./specs/p4-plugin.md) for full details.
