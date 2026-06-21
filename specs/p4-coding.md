# Plugin Spec: p4-coding

> **Status:** `beta` | **Version:** `1.0.6` | **Ports:** Claude Code (full), GitHub Copilot (Phase 1)

## Overview

`p4-coding` is a coding standards plugin for the plugin4ai ecosystem. It provides universal coding directives (SOLID, DRY, KISS, naming, error handling, security, testability, complexity control) that load automatically at session start, plus stack-specific directives for TypeScript/JavaScript and Python that can be activated on demand.

The universal directives are identified by the `P4C-NNN` scheme (Plugin4 Coding), and stack-specific ones use a sub-namespace (`P4C-TS-NNN`, `P4C-PY-NNN`, etc.).

---

## Skill: `code-standards`

### Purpose
Loads and activates 16 universal coding directives (P4C-001 to P4C-016) applicable to any programming language or stack. Fires automatically at session start via the `p4-coding` agent.

### Invocation
```
/p4-coding:code-standards
```
Also fires silently at session start — no invocation needed.

### Directives covered

| ID | Category | Summary |
|----|----------|---------|
| P4C-001 | SOLID: SRP | One class/module/function = one reason to change |
| P4C-002 | SOLID: OCP | Extend without modifying existing code |
| P4C-003 | SOLID: LSP | Subtypes must not break the supertype contract |
| P4C-004 | SOLID: ISP | Small, specific interfaces — no "Swiss Army knife" |
| P4C-005 | SOLID: DIP | Depend on abstractions, inject dependencies |
| P4C-006 | DRY/KISS/YAGNI | No duplication, no speculation, simplest solution wins |
| P4C-007 | Naming | Descriptive, consistent, semantic prefixes |
| P4C-008 | Functions | One thing, max 4 params, early return, no bool flags |
| P4C-009 | Immutability | Immutable by default, minimize global state |
| P4C-010 | Error Handling | Fail fast, descriptive messages, never silence |
| P4C-011 | Documentation | Comment the why, not the what; sync comments with code |
| P4C-012 | Testability | Designed to test, DI, AAA, one behavior per test |
| P4C-013 | Modularity | High cohesion, low coupling, domain-based structure |
| P4C-014 | Complexity | Low cyclomatic, no deep nesting, Boy Scout Rule |
| P4C-015 | Security | Sanitize inputs, no secrets in code, least privilege |
| P4C-016 | Style | One linter/formatter, code review before merge, atomic commits |

### Non-Goals
- Does not replace linters or static analysis tools
- Does not apply to a specific language (use stack-specific skills for that)

---

## Skill: `typescript-standards`

### Purpose
Activates 10 TypeScript/JavaScript-specific coding directives (P4C-TS-001 to P4C-TS-010) to complement the universal standards.

### Invocation
```
/p4-coding:typescript-standards
```

### Directives covered

| ID | Summary |
|----|---------|
| P4C-TS-001 | `"strict": true` mandatory, no `any` |
| P4C-TS-002 | Explicit types at public/exported boundaries |
| P4C-TS-003 | `async/await` over raw Promises |
| P4C-TS-004 | No non-null assertion (`!`) without comment justification |
| P4C-TS-005 | `const` > `let`, never `var`, `readonly` on non-mutating props |
| P4C-TS-006 | ESM over CommonJS, one primary export per file |
| P4C-TS-007 | Custom error classes extending `Error` |
| P4C-TS-008 | No `==`, no `eval()`, no parameter mutation, no `delete` |
| P4C-TS-009 | Jest/Vitest: test files co-located, mock at boundary |
| P4C-TS-010 | ESLint + Prettier mandatory, CI enforces lint |

### Non-Goals
- Does not cover framework-specific rules (React, Next.js, Vue, etc.)
- Does not replace `tsc` type checking

---

## Skill: `python-standards`

### Purpose
Activates 10 Python-specific coding directives (P4C-PY-001 to P4C-PY-010) to complement the universal standards.

### Invocation
```
/p4-coding:python-standards
```

### Directives covered

| ID | Summary |
|----|---------|
| P4C-PY-001 | PEP 8 via `ruff`/`black`, 88-char lines |
| P4C-PY-002 | Type hints mandatory, `mypy --strict` |
| P4C-PY-003 | `with` for all resources, never manual `.close()` |
| P4C-PY-004 | No bare `except:`, custom exception hierarchy, `raise ... from err` |
| P4C-PY-005 | `@dataclass`, `Protocol`, `TypedDict` over raw classes/dicts |
| P4C-PY-006 | `tuple` over `list` for immutable, no mutable defaults |
| P4C-PY-007 | Generators over lists for single-pass iteration |
| P4C-PY-008 | `isort` import order, no `import *`, explicit relative imports |
| P4C-PY-009 | `pytest` + fixtures + `@pytest.mark.parametrize`, 80% coverage |
| P4C-PY-010 | `pyproject.toml`, separate dev deps, pin versions in production |

### Non-Goals
- Does not cover framework-specific rules (Django, FastAPI, etc.)
- Does not replace `mypy` or `ruff` type/lint checking

---

## Skill: `go-standards` *(proposal)*

### Purpose
Will activate Go-specific coding directives covering goroutines, channels, error returns, interface patterns, `defer`, context propagation, and `go test`.

### Invocation
```
/p4-coding:go-standards
```

> **Status: proposal — not yet implemented.**

---

## Skill: `java-standards` *(proposal)*

### Purpose
Will activate Java/Kotlin-specific coding directives covering Java 17+ features, Spring Boot patterns, exception hierarchy, Stream API, Optional, and JUnit 5 testing.

### Invocation
```
/p4-coding:java-standards
```

> **Status: proposal — not yet implemented.**

---

## Skill: `code-review` *(proposal)*

### Purpose
Will analyze the current `git diff` or a specified file against all active p4-coding standards (universal + any loaded stack-specific skill) and return a structured violation report with severity levels (ERROR / WARNING / INFO).

### Invocation
```
/p4-coding:code-review [file-or-diff-target]
```

> **Status: proposal — not yet implemented.**

---

## Port Status

| CLI | Location | Status | Notes |
|-----|----------|--------|-------|
| Claude Code | `claudecode/p4-coding/` | ✅ Beta | Full — all 6 skills (3 implemented, 3 proposal) |
| GitHub Copilot | `ghcopilot/plugins/p4-coding/` | ✅ Beta | Phase 1 only: `code-standards`, `typescript-standards`, `python-standards` |
| Antigravity | — | 🔲 Proposal | — |
| Codex | — | 🔲 Proposal | — |

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.0.6 | Add `code-review` skill (proposal) |
| 1.0.5 | Add `java-standards` skill (proposal) |
| 1.0.4 | Add `go-standards` skill (proposal) |
| 1.0.3 | Add `python-standards` skill |
| 1.0.2 | Add `typescript-standards` skill |
| 1.0.1 | Add `code-standards` skill |
| 1.0.0 | Initial release |
