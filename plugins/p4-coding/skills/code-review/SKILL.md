---
name: code-review
description: Analyzes the current git diff or a specified file against active p4-coding standards (universal + any loaded stack-specific) and returns a structured violation report. Also invoked explicitly as /p4-coding:code-review with an optional file path or diff target.
version: 6
argument-hint: "[file-or-diff-target]"
allowed-tools: [Bash, Read]
status: proposal
---

# P4C-Review — Code Review Against Active Standards

> **Status: PROPOSAL — Content pending implementation.**
>
> This skill is scaffolded but not yet implemented. Planned behavior:
>
> 1. Detect active standards: always includes P4C-001 to P4C-016 (universal).
>    If a stack-specific skill was loaded this session, include those too.
> 2. Read the diff: `git diff` (unstaged), `git diff --cached` (staged), or a
>    specific file path if provided as argument.
> 3. Evaluate each changed hunk against active directives.
> 4. Output a structured report:
>    - Violations: directive ID, file, line range, description, suggestion
>    - Compliance: directives that were visibly followed (positive reinforcement)
> 5. Severity levels: ERROR (must fix), WARNING (should fix), INFO (consider).
>
> **Non-goals:**
> - Does not replace CI linters (ESLint, mypy, etc.)
> - Does not check build or compile errors
> - Does not post comments to GitHub PRs (use the built-in `/code-review` for that)

---

## TODO: define skill steps here
