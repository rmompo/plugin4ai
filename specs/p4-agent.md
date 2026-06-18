# Plugin Spec: p4-agent

> **Status:** `beta` | **Version:** `1.0.5` | **Ports:** Claude Code CLI/TUI

---

## Overview

p4-agent is a structural auditor for agent definition files written in Markdown. It validates that agent files conform to expected structural conventions, naming rules, and internal consistency. It also verifies that all cross-referenced files exist and are themselves structurally sound.

Designed to be used as a quality gate before committing agent definitions to a repository.

---

## Port Status

| CLI/TUI | Location | Status |
|-----|----------|--------|
| Claude Code CLI/TUI | `claudecode/p4-agent/` | ⏳ Proposal |
| GitHub Copilot CLI/TUI | — | ⏳ Proposal |
| Antigravity CLI/TUI | — | ⏳ Proposal |
| Codex CLI/TUI | — | ⏳ Proposal |

---

## Skill: `md-check`

### Purpose
Audits a single agent markdown file against a fixed battery of checks. Produces a findings report with severity and mitigation guidance. Does not modify the audited file.

### Check battery

#### A1 — Semantics, syntax and spelling  `MAJOR`
Verify that the file is free of:
- Markdown syntax errors (unclosed fences, broken table formatting, invalid heading levels)
- Spelling errors in prose sections
- Semantic inconsistencies (terms used with different meanings in different sections)

#### A2 — Instructions: synthetic, clear, unambiguous  `MAJOR`
Every instruction block must be:
- **Synthetic** — no redundant or verbose phrasing; each instruction expresses exactly one directive
- **Clear** — no implicit assumptions; the reader does not need external context to understand the instruction
- **Unambiguous** — no instruction can be interpreted in more than one way

Flag any instruction that is verbose, implicit, or admits multiple interpretations.

#### A3 — No collisions (contradictions)  `CRITICAL`
Scan all instruction blocks across the file for contradictions:
- Two instructions that cannot both be true simultaneously
- An instruction that negates or overrides another without explicit supersession

Flag each contradictory pair with both locations.

#### A4 — Frontmatter completeness  `CRITICAL`
The file must have a YAML frontmatter block (`---`) containing all of the following fields:

| Field | Description |
|-------|-------------|
| `name` | Unique identifier for the agent or skill |
| `description` | One-line description of the file's purpose |
| `version` | Semantic or monotonic version number |
| `changelog` | At least one entry matching the current version |

Flag each missing field individually.

### Invocation
```
/p4-agent:md-check <path/to/agent.md>
```

### Non-Goals
- Does not follow or validate referenced files (see `md-checkrefs`)
- Does not modify the audited file
- Does not enforce a specific frontmatter schema beyond the required fields

---

## Skill: `md-checkrefs`

### Purpose
Audits an agent markdown file and all files it references, expanding the scope across the full reference graph. Runs checks A1–A4 (identical to `md-check`) on every file in the graph, plus an additional check for reference integrity.

### Check battery

Runs **A1–A4** (same as `md-check`) on every file in the reference graph, plus:

#### B1 — Reference integrity  `CRITICAL`
Resolve every local file reference found in the entry file and in all transitively referenced files:
- `[label](./path/to/file.md)` style links
- Embedded includes or `@import`-style directives if present

For each reference:
- Verify the target file exists at the given path
- Verify the target file itself passes A4 (has required frontmatter)

Flag each broken reference with its location and the missing target path.

### Invocation
```
/p4-agent:md-checkrefs <path/to/agent.md>
```

### Non-Goals
- Does not modify any of the audited files
- Does not follow external URLs — only local file references
- Does not recursively follow references beyond the explicitly linked files (no deep graph traversal unless the linked file itself contains further references)

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.0.5 | Promote to beta — version scheme 0.1.x → 1.0.x |
| 0.1.5 | Implement `md-checkrefs`: reference graph traversal, B1 + A1–A4 on all files |
| 0.1.4 | Implement `md-check`: A1 syntax/spelling, A2 clarity, A3 contradictions, A4 frontmatter |
| 0.1.3 | Define check battery: A1–A4 for `md-check`, B1 for `md-checkrefs` |
| 0.1.2 | Add `md-checkrefs` skill definition |
| 0.1.1 | Initial proposal — `md-check` skill definition |
