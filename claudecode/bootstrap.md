# Claude Code — CLI Bootstrap

This file defines the concrete tools to use for each abstract operation declared in skill files.
All skills in this marketplace read this file to resolve CLI-specific implementations.

---

## Operation Map

| Operation | Tool | Notes |
|-----------|------|-------|
| `collect_user_input` | `AskUserQuestion` | Use for any interactive input, confirmations, or choices from the user |

---

## Usage in skills

When a skill declares `collect_user_input`, use the `AskUserQuestion` tool with clearly defined options. Do not use free-text prompts for collecting structured user input.
