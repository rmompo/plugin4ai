# Plugin Spec: p4-core

> **Status:** `stable` | **Version:** `1.2.15` | **Ports:** Claude Code CLI/TUI, GitHub Copilot CLI/TUI

## Overview

`p4-core` bundles three skills that address the most common friction points in daily AI-assisted development: enforcing behavioral directives, choosing the right model, and writing consistent commit messages. All three skills activate automatically from context and can also be invoked explicitly.

---

## Port Status

| CLI | Location | Status |
|-----|----------|--------|
| Claude Code CLI/TUI | `claudecode/p4-core/` | ✅ Stable |
| GitHub Copilot CLI/TUI | `ghcopilot/plugins/p4-core/` | ✅ Stable |
| Antigravity CLI/TUI | `antigravity/p4-core/` | 🔶 Beta |
| Codex CLI/TUI | `codex/p4-core/` | 🔶 Beta |

## Skill 1: `model-behaviour`

### Purpose

Load and apply P4D behavioral directives for the session. Fires automatically at session start via the p4-core agent. Ensures the model always operates from the canonical, up-to-date directive set — never from training memory or stale context.

### Invocation

```bash
/p4-core:model-behaviour    # inspect or reload directives at any time
```

### Behavior

At session start, reads the directive file from the plugin cache:
```bash
find ~/.claude/plugins -path "*/p4-core/skills/model-behaviour/SKILL.md" 2>/dev/null | head -1
```

Applies directives P4D-000 through P4D-009 for the duration of the session.

### Key directives (summary)

| ID | Name | Effect |
|----|------|--------|
| P4D-000 | Load from source | Always read from plugin cache — never from memory |
| P4D-001 | Confirmation protocol | Any restricted action requires explicit user confirmation |
| P4D-002 | Destructive actions | Extra confirmation for irreversible operations |
| P4D-003 | Consultation mode | Default is propose/explain — not execute |
| P4D-004 | Commit gating | Never commit without explicit user instruction |
| P4D-005 | Ambiguity | Clarify before acting on ambiguous input |
| P4D-006 | Factual claims | State uncertainty explicitly — never hallucinate |
| P4D-007 | Independent evaluation | Evaluate before agreeing — no silent validation |
| P4D-008 | Language | Respond in the language of the user's last message |
| P4D-009 | Structured output | Lists and comparable items use numbered format |

### Non-Goals
- Does not apply to tasks where the user has explicitly overridden a directive
- Does not block execution indefinitely — one confirmation = one execution

---

## Skill 2: `model-route`

### Purpose

Guide the model into selecting the most appropriate model tier for a given task, balancing output quality, latency, and token cost.

### Invocation

```bash
/p4-core:model-route                  # route the current task
/p4-core:model-route <description>    # route a described task
```

### Routing tiers

| Tier | Characteristics | Representative Tasks |
|------|-----------------|----------------------|
| **Lightweight** | Fast, cheap, single-step | File search, grep, quick formatting, boilerplate, log parsing |
| **Standard** *(default)* | Balanced, multi-step | Feature impl, bug fixes, refactoring, PR review, test writing |
| **Advanced** | Deep reasoning, high stakes | System design, unknown-root debugging, security analysis, architecture decisions |

### Decision criteria
1. **Scope** — one step or a reasoning chain?
2. **Stakes** — cost of an error?
3. **Ambiguity** — is the problem well-defined?
4. **Frequency** — repeated in a loop?

### Non-Goals
- Does not override explicit model selections by the user
- Does not apply organizational or policy-level model restrictions

---

## Skill 3: `git-commit`

### Purpose

Ensure every `git commit` follows the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/) specification, producing a clean, machine-readable commit history.

### Invocation

```bash
/p4-core:git-commit              # auto-infer from staged changes
/p4-core:git-commit <hint>       # use hint to guide the message
```

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Allowed types

| Type | Use for |
|------|---------|
| `feat` | New user-facing feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, whitespace — no logic change |
| `refactor` | Code restructure without feature/fix |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `build` | Build system or dependency changes |
| `ci` | CI/CD pipeline changes |
| `chore` | Maintenance, tooling, non-production |
| `revert` | Reverts a previous commit |

### Rules
- Subject line: max 72 chars, imperative mood, no trailing period
- Always written in English regardless of user language
- Never includes `Co-Authored-By:` lines
- Breaking changes: `feat(api)!:` + `BREAKING CHANGE:` footer

### Non-Goals
- Does not block commits — suggests and corrects, never refuses
- Does not validate scope against real module names

---

## Skill: `skill-list`

### Purpose

Print a table of all installed p4-* plugin skills with their version, tool availability, enabled status, and description. Reads from the CLI cache and `catalog.json` to produce an always-current view.

### Invocation

```bash
/p4-core:skill-list
```

### Non-Goals
- Does not install or enable skills — read-only view
- Does not check skill logic or correctness — use `/p4-plugin:skill-doctor` for that

---

## Skill: `setup`

### Purpose

Verify that all external tools required by p4-core skills are installed and reachable in `PATH`. Currently checks `git` (required by `git-commit`). Prints a status table with install instructions for any missing dependency.

### Invocation

```bash
/p4-core:setup
```

### Non-Goals
- Does not install tools automatically
- Does not verify tool versions — only presence (`which`)

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.2.3 | Skill versions normalized to Z system (integers) |
| 1.2.0 | Skill renames: commit→git-commit, model-routing→model-route, behaviour→model-behaviour |
| 1.1.0 | Add model-behaviour skill (P4D directives) |
| 1.0.0 | Initial release — model-route and git-commit skills |
