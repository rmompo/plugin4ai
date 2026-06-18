---
name: git-commit
description: This skill should be used whenever Claude is about to propose, write, or execute a git commit. It activates automatically when the user asks to commit changes, when Claude runs `git commit`, when generating commit messages after staged changes, or when the user asks for help writing a commit message. Also invoked explicitly as /p4-core:git-commit with an optional hint. Enforces Conventional Commits format, translates to English, and strips co-authorship lines.
version: 1
argument-hint: [message or scope hint]
allowed-tools: [Bash]
---

# Commit Format — Conventional Commits Enforcer

This skill generates or adapts git commit messages to follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Absolute Rules

1. **Always write in English** — regardless of the language used by the user or in comments. Translate any input before formatting.
2. **Never include `Co-Authored-By:` lines** — strip them unconditionally.
3. **Never include `Co-authored-by:` lines** — same rule, any casing variant.
4. **Subject line**: max 72 characters, imperative mood, no trailing period.
5. **Type**: lowercase, from the allowed list only.

---

## Commit Message Structure

```
<type>(<scope>): <short description>

[optional body]

[optional footer(s)]
```

- **Body**: wrap at 72 chars, explain *what* and *why* (not *how*)
- **Footer**: issue references and breaking changes only — no co-authorship

---

## Allowed Types

| Type       | When to use                                                        |
|------------|--------------------------------------------------------------------|
| `feat`     | A new feature visible to the user or API consumer                 |
| `fix`      | A bug fix                                                          |
| `docs`     | Documentation changes only                                        |
| `style`    | Formatting, whitespace — no logic change                          |
| `refactor` | Code restructured without adding features or fixing bugs          |
| `perf`     | Performance improvements                                          |
| `test`     | Adding or fixing tests                                            |
| `build`    | Changes to build system or dependencies (webpack, npm, etc.)      |
| `ci`       | CI/CD pipeline configuration changes                              |
| `chore`    | Maintenance tasks, tooling, non-production code                   |
| `revert`   | Reverts a previous commit                                         |

---

## Input Interpretation

When the user provides a hint or comment (in any language), apply this process:

1. **Understand the intent** — what is the user trying to express?
2. **Translate to English** — render the meaning in clear, technical English
3. **Map to a type** — choose the most accurate Conventional Commits type
4. **Derive scope** — infer from staged files or the hint provided
5. **Write the subject** — imperative, concise, ≤72 chars

### Examples of input adaptation

| User input | Output |
|------------|--------|
| `"arreglé el login"` | `fix(auth): resolve login failure on invalid credentials` |
| `"nueva pantalla de perfil"` | `feat(profile): add user profile screen` |
| `"limpieza de código en el parser"` | `refactor(parser): clean up tokenizer logic` |
| `"actualicé dependencias"` | `chore(deps): update project dependencies` |

---

## Breaking Changes

Mark with `!` after type/scope and add `BREAKING CHANGE:` footer:

```
feat(api)!: rename /users endpoint to /accounts

BREAKING CHANGE: All clients must update from /api/v1/users
to /api/v1/accounts. The old endpoint is removed.
```

---

## How to Apply This Skill

1. **If invoked with a hint** (`/p4-core:git-commit <hint>`): interpret the hint, translate to English, format as Conventional Commit
2. **If invoked automatically** (Claude is about to commit): inspect staged changes with `git diff --staged`, infer type and scope, generate the message
3. **If the user wrote a draft message**: adapt it — correct type, translate to English, enforce format, strip co-authorship

---

## Validation Checklist

- [ ] Written entirely in English
- [ ] Type is from the allowed list
- [ ] Subject is ≤72 characters
- [ ] Subject uses imperative mood ("add", not "added" or "adds")
- [ ] No trailing period on subject line
- [ ] Breaking changes marked with `!` and `BREAKING CHANGE:` footer
- [ ] Issue references in footer (`Closes #N`), not in subject
- [ ] No `Co-Authored-By:` or `Co-authored-by:` lines anywhere
