# GitHub Copilot CLI — CLI Bootstrap

This file defines the concrete tools to use for each abstract operation declared in skill files.
All skills in this marketplace read this file to resolve CLI-specific implementations.

---

## Operation Map

| Operation | Tool | Notes |
|-----------|------|-------|
| `collect_user_input` | `ask_user` | Use for any interactive input, confirmations, or choices from the user |

---

## Usage in skills

When a skill declares `collect_user_input`, use the `ask_user` tool to collect structured input from the user.
