# p4-coding — GitHub Copilot

Coding standards and best practices for GitHub Copilot.

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `code-standards` | `/p4-coding:code-standards` | Universal coding directives: SOLID, DRY/KISS/YAGNI, naming, error handling, testing, security |
| `typescript-standards` | `/p4-coding:typescript-standards` | TypeScript/JavaScript-specific standards: strict mode, type safety, async/await, ESLint/Prettier |
| `python-standards` | `/p4-coding:python-standards` | Python-specific standards: PEP 8, type hints, context managers, exceptions, pytest |

> `go-standards`, `java-standards`, and `code-review` are available in the Claude Code port and marked as proposal for this CLI.

## Usage

```
/p4-coding:code-standards
```
Load and display the universal coding standards (SOLID, DRY, naming, etc.).

```
/p4-coding:typescript-standards
```
Load TypeScript/JavaScript-specific directives to complement the universal ones.

```
/p4-coding:python-standards
```
Load Python-specific directives to complement the universal ones.

## Installation

```bash
gh copilot plugins marketplace add https://github.com/rmompo/plugin4ai/tree/main/ghcopilot
gh copilot plugins install p4-coding
```
