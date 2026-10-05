# plugin4ai

A personal [Claude Code](https://claude.ai/code) plugin marketplace: productivity skills, agents and tooling for everyday development.

---

## Installation

```bash
claude plugin marketplace add rmompo/plugin4ai
claude plugin install <plugin>@plugin4ai
```

Full install, update, uninstall, enable and disable instructions → **[INSTALL.md](./INSTALL.md)**

---

## Plugins

| Plugin | Description | Status | Spec |
|--------|-------------|--------|------|
| `p4-agent` | Agent definition auditor: validates markdown agent files for structural completeness, naming conventions, and cross-reference integrity. | `beta` | [spec](./specs/p4-agent.md) |
| `p4-buddy` | Skills for \<company> employees: \<hr-platform> mission report generation from workspace context. | `beta` | [spec](./specs/p4-buddy.md) |
| `p4-ccvv` | AI-powered CV generation and management — multi-user profiles, job offer adaptation, and multi-format export. | `beta` | [spec](./specs/p4-ccvv.md) |
| `p4-claudecode` | Claude Code-exclusive enhancements: custom statusline with project path, git branch, active model and color-coded usage metrics. | `stable` | [spec](./specs/p4-claudecode.md) |
| `p4-coding` | Coding standards and best practices plugin: universal directives (SOLID, DRY, naming, error handling, security) auto-loaded at session start, with stack-specific skills for TypeScript, Python, Go, and Java. | `beta` | [spec](./specs/p4-coding.md) |
| `p4-converter` | Converts documents to Markdown (PDF, DOC, DOCX, PPT, PPTX) using a multi-step local tool pipeline. | `beta` | [spec](./specs/p4-converter.md) |
| `p4-core` | Core productivity plugin: behavioral directives (P4D), intelligent model routing via subagents, and Conventional Commits enforcement. | `stable` | [spec](./specs/p4-core.md) |
| `p4-crawler` | Web crawler and documentation extractor: crawls sites (static or SPA/Storybook), filters by topic, downloads attachments, and generates structured Markdown output. | `beta` | [spec](./specs/p4-crawler.md) |
| `p4-plugin` | Marketplace lifecycle tooling: create and manage plugins and skills with automatic version tracking. | `beta` | [spec](./specs/p4-plugin.md) |

Skills per plugin are indexed in [`plugins/README.md`](./plugins/README.md).

---

## Repository layout

| Path | Content |
|------|---------|
| `.claude-plugin/marketplace.json` | Marketplace index consumed by Claude Code |
| `plugins/<plugin>/` | One directory per plugin (`.claude-plugin/plugin.json`, `skills/`, optional `agents/`, `settings.json`) |
| `specs/<plugin>.md` | Canonical spec for each plugin |
| `specs/catalog.json` | Source of truth for plugins, skills, versions and changelogs (validated by `catalog.schema.json`) |

---

## Adding a New Plugin

Use the `p4-plugin` skill — it scaffolds everything in one step:

```
/p4-plugin:create <plugin-name> [skill1 skill2 ...]
```

See [`specs/p4-plugin.md`](./specs/p4-plugin.md) for full details.
