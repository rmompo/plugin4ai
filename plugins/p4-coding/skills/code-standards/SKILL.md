---
name: code-standards
description: Loads and activates universal coding standards for the session (SOLID, DRY, naming, error handling, testing, security). Fires automatically at session start via the p4-coding agent. Also invoked explicitly as /p4-coding:code-standards to inspect or reload directives.
version: 1
trigger: session-start
allowed-tools: [Bash]
---

# P4C — Coding Standards (Universal)

These directives apply to any stack and are active for the entire session.

---

## P4C-001 — SOLID: Single Responsibility

A class/module/function has one reason to change. If you describe what it does using "and", it probably violates SRP. Split it.

---

## P4C-002 — SOLID: Open/Closed

Extend behavior without modifying existing code. Prefer composition, interfaces, and parameters over conditional logic that grows over time.

---

## P4C-003 — SOLID: Liskov Substitution

A subtype must be substitutable for its supertype without breaking the contract. Never throw new exceptions or restrict preconditions in subtypes.

---

## P4C-004 — SOLID: Interface Segregation

Interfaces must be small and specific. Never force a class to implement methods it does not need. Prefer multiple focused interfaces over one general-purpose one.

---

## P4C-005 — SOLID: Dependency Inversion

Depend on abstractions, not concrete implementations. Dependencies are injected — never instantiated internally without a deliberate reason.

---

## P4C-006 — DRY / KISS / YAGNI

- **DRY**: If you copy and paste code, something must be abstracted.
- **KISS**: The simplest solution that works correctly is the right one.
- **YAGNI**: Do not implement what you do not need right now. Speculative abstractions add complexity without benefit.

---

## P4C-007 — Naming

- Names must be descriptive and intentional. `getUserById()` not `getU()`.
- No ambiguous abbreviations: `tmp`, `data`, `info`, `mgr` are noise.
- Consistent convention within the project — do not mix `camelCase` with `snake_case`.
- Booleans use semantic prefixes: `isReady`, `hasPermission`, `canDelete`.
- Functions are named with a verb: `calculate`, `fetch`, `validate`.
- Classes and types are named with a noun: `OrderProcessor`, `UserRepository`.

---

## P4C-008 — Functions and Methods

- One function = one thing (correlates with P4C-001).
- Maximum 3–4 parameters. More → use an object/struct.
- No hidden side effects. If a function modifies external state, it must be obvious.
- Use early return to avoid excessive nesting.
- No boolean flags as parameters — they indicate the function does two things.

---

## P4C-009 — Immutability and State

- Prefer immutable data by default; mutate explicitly only when necessary.
- Minimize global state — the more local the state, the more predictable the code.
- Avoid unexpected side effects in pure functions.

---

## P4C-010 — Error Handling

- Never silence errors. An empty `catch` block is a time bomb.
- Fail fast: validate inputs at the entry point, not deep in the logic.
- Descriptive error messages — state what went wrong and where, not just `"Error"`.
- Distinguish recoverable errors (business exceptions) from fatal ones (programming bugs).

---

## P4C-011 — Comments and Documentation

- Code must be self-explanatory. If a comment is needed to understand *what* it does, rename instead.
- Comment the *why*, not the *what*. Example: `// Workaround for bug #1234 in lib X`.
- Keep comments synchronized — an outdated comment is worse than none.
- Always document public contracts (APIs, exposed interfaces).

---

## P4C-012 — Testability

- Code must be designed to be testable by default. If it is hard to test, the design has a problem.
- Prefer dependency injection — it enables mocking and isolation.
- Tests follow AAA: Arrange / Act / Assert.
- One test = one verified behavior. Avoid multiple independent assertions per test.

---

## P4C-013 — Modularity and Cohesion

- High cohesion: what belongs together, lives together.
- Low coupling: modules must be able to change without affecting others.
- Respect encapsulation — do not expose what does not need to be public.
- Folder structure must reflect the domain, not the technical type (`/orders/` not `/controllers/`).

---

## P4C-014 — Complexity Control

- Low cyclomatic complexity — few decision branches per function.
- Avoid nesting deeper than 3 levels. More → extract or simplify.
- Do not optimize prematurely: first correct, then clear, then fast (if needed).
- Boy Scout Rule: leave the code better than you found it. Refactor continuously.

---

## P4C-015 — Basic Security

- Never trust user input — always validate and sanitize.
- Secrets never in source code — use environment variables or vaults.
- Principle of least privilege: only the permissions strictly required.
- Never log sensitive data (passwords, tokens, PII).

---

## P4C-016 — Style and Consistency

- One linter/formatter per project, no exceptions.
- Code review is mandatory before merge.
- Atomic commits: one commit = one coherent logical change.
- Descriptive commit messages (Conventional Commits or equivalent).

---

## When asked about P4C directives

Reference directives by their `P4C-NNN` identifier. To reload this file:

```bash
find ~/.claude/plugins -path "*/p4-coding/skills/code-standards/SKILL.md" 2>/dev/null | head -1
```
