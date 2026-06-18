---
name: commit
description: This skill should be used whenever Copilot is about to propose, write, or execute a git commit. It activates automatically when the user asks to commit changes, when running `git commit`, when generating commit messages after staged changes, or when the user asks for help writing a commit message. Enforces Conventional Commits format.
---

# Commit Format — Conventional Commits Enforcer

This skill ensures all git commits follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for consistent, machine-readable history.

## Commit Message Structure

```
<type>(<scope>): <short description>

[optional body]

[optional footer(s)]
```

### Rules
- **Subject line**: max 72 characters, imperative mood, no period at end
- **Type**: lowercase, from the allowed list below
- **Scope**: optional, lowercase, describes the affected module/area
- **Body**: wrap at 72 chars, explain *what* and *why* (not *how*)
- **Footer**: reference issues, breaking changes

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

## Examples

```
feat(auth): add OAuth2 login with Google provider

fix(api): handle null response from payment gateway

docs(readme): update installation instructions for WSL2

refactor(parser): extract tokenizer into separate module

test(user-service): add unit tests for password reset flow

chore(deps): bump axios from 1.6.0 to 1.7.2

feat(ui)!: redesign navigation bar layout

BREAKING CHANGE: The sidebar component has been removed.
Users should migrate to the new TopNav component.

Closes #142
```

---

## Breaking Changes

Mark breaking changes with `!` after the type/scope and include a `BREAKING CHANGE:` footer:

```
feat(api)!: rename /users endpoint to /accounts

BREAKING CHANGE: All clients must update API calls from
/api/v1/users to /api/v1/accounts. The old endpoint is
removed as of this release.
```

---

## Before Starting

Inspect the staged changes before generating a commit message:
- Run `git diff --staged` to see what's included
- Identify the primary intent of the change

## Output Structure

A properly formatted commit message following Conventional Commits:
1. Subject line: `<type>(<scope>): <description>` — ≤72 chars
2. Body (if needed): explain the *why*, wrapped at 72 chars
3. Footer (if applicable): `BREAKING CHANGE:` or `Closes #N`

## Step-by-Step Instructions

1. **Inspect staged changes**: Determine the files and nature of changes
2. **Identify the primary type**: What is the dominant intent of this commit?
3. **Determine scope**: What module, component, or area is affected?
4. **Write a crisp subject**: Imperative mood, ≤72 chars, no trailing period
5. **Add body if needed**: For non-trivial changes, explain the *why*
6. **Add footer if needed**: Issue references (`Closes #N`) or breaking changes

## Validation Checklist

- [ ] Type is from the allowed list
- [ ] Subject is ≤72 characters
- [ ] Subject uses imperative mood ("add", not "added" or "adds")
- [ ] No trailing period on subject line
- [ ] Breaking changes are marked with `!` and `BREAKING CHANGE:` footer
- [ ] Issue references are in the footer, not the subject
