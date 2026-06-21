# p4-coding

Coding standards and best practices for Claude Code. Universal directives (SOLID, DRY, naming, error handling, security) load automatically at session start. Stack-specific standards for TypeScript, Python, Go, and Java can be activated on demand.

## Skills

| Skill | Invocation | Auto | Description |
|-------|-----------|:----:|-------------|
| `code-standards` | `/p4-coding:code-standards` | ✅ | Universal coding directives: SOLID, DRY/KISS/YAGNI, naming, functions, immutability, error handling, documentation, testability, modularity, complexity, security, style |
| `typescript-standards` | `/p4-coding:typescript-standards` | — | TypeScript/JavaScript-specific standards: strict mode, type safety, async/await, null safety, ESLint/Prettier |
| `python-standards` | `/p4-coding:python-standards` | — | Python-specific standards: PEP 8, type hints, context managers, exceptions, dataclasses, pytest |
| `go-standards` | `/p4-coding:go-standards` | — | Go-specific standards *(proposal)* |
| `java-standards` | `/p4-coding:java-standards` | — | Java/Kotlin-specific standards *(proposal)* |
| `code-review` | `/p4-coding:code-review` | — | Review current diff against active standards *(proposal)* |

## How loading works

```
Session start
    └── p4-coding agent fires automatically
            └── code-standards loaded silently (P4C-001 to P4C-016 active)

On demand
    └── /p4-coding:typescript-standards  →  P4C-TS-001 to P4C-TS-010 active
    └── /p4-coding:python-standards      →  P4C-PY-001 to P4C-PY-010 active
```

## Installation

```bash
claude plugins marketplace add rmompo/plugin4ai
claude plugins install p4-coding
```
