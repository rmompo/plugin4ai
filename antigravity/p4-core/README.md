# p4-core

Core productivity plugin for Antigravity CLI. Provides behavioral directives (P4D), Conventional Commits enforcement, sensitive data sanitization, and dependency verification.

## Skills

| Skill | Invocation | Description |
|-------|------------|-------------|
| `git-commit` | `/p4-core:git-commit [hint]` | Enforces Conventional Commits format, translates to English, strips co-authorship lines |
| `model-behaviour` | `/p4-core:model-behaviour` | Loads and activates P4D behavioral directives for the session |
| `sanitize` | `/p4-core:sanitize [path]` | Scans all files for sensitive information and offers interactive anonymization |
| `setup` | `/p4-core:setup` | Verifies that all external dependencies required by p4-core are installed |

## Not ported

| Skill | Reason |
|-------|--------|
| `skill-list` | Reads from Claude Code plugin cache — not applicable |
| `model-route` | Antigravity CLI handles model selection via `--model` flag |

## Installation

```bash
agy plugin install ~/path/to/plugin4ai/antigravity/p4-core
```

## Notes

- Pairs well with `p4-antigravity` for a complete Antigravity CLI setup
- `model-behaviour` should be loaded at the start of every session
