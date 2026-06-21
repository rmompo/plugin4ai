---
name: p4-coding
description: Coding standards auto-loader. Silently applies universal coding directives (SOLID, DRY, naming, error handling, security) at session start, then detects the project stack and suggests activating the relevant stack-specific skill if not already active.
model: inherit
---

## Session Initialization

### Step 1 — Load universal coding standards (silent)

```bash
find ~/.claude/plugins -path "*/p4-coding/skills/code-standards/SKILL.md" 2>/dev/null | head -1
```

Read that file in full and treat every directive (P4C-001 to P4C-016) as active and binding for all coding tasks during the entire session. Produce **no output** — this step is completely silent.

---

### Step 2 — Detect project stack and suggest stack-specific skill

Detect the stack by checking for indicator files in the project root:

```bash
root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
ls "$root/package.json" "$root/tsconfig.json" "$root/tsconfig.base.json" 2>/dev/null
ls "$root/pyproject.toml" "$root/requirements.txt" "$root/setup.py" "$root/setup.cfg" "$root/Pipfile" 2>/dev/null
ls "$root/go.mod" 2>/dev/null
ls "$root/pom.xml" "$root/build.gradle" "$root/build.gradle.kts" 2>/dev/null
```

**Detection rules** (evaluate in order — a project may match more than one):

| Indicator files | Detected stack | Skill to suggest |
|-----------------|---------------|-----------------|
| `package.json`, `tsconfig.json`, or `tsconfig.*.json` | TypeScript / JavaScript | `/p4-coding:typescript-standards` |
| `pyproject.toml`, `requirements.txt`, `setup.py`, `setup.cfg`, or `Pipfile` | Python | `/p4-coding:python-standards` |
| `go.mod` | Go | `/p4-coding:go-standards` *(proposal)* |
| `pom.xml`, `build.gradle`, or `build.gradle.kts` | Java / Kotlin | `/p4-coding:java-standards` *(proposal)* |

**Output rules:**

- If **no stack is detected**: produce no output.
- If **one or more stacks are detected**:
  - For each detected stack whose skill is **implemented** (`typescript-standards`, `python-standards`): output a suggestion line.
  - For each detected stack whose skill is **proposal** (`go-standards`, `java-standards`): output an informational note only.
  - Keep the output brief — one line per detected stack, prefixed with `💡 p4-coding:`.

**Suggestion format:**

```
💡 p4-coding: <Stack> project detected — activate stack-specific standards with /p4-coding:<skill>
```

**Proposal note format:**

```
💡 p4-coding: <Stack> project detected — /p4-coding:<skill> is planned but not yet implemented
```

**Example output for a TypeScript + Python monorepo:**

```
💡 p4-coding: TypeScript project detected — activate stack-specific standards with /p4-coding:typescript-standards
💡 p4-coding: Python project detected — activate stack-specific standards with /p4-coding:python-standards
```

This suggestion is shown **once per session**, at startup. It does not repeat during the session even if the user switches directories.
