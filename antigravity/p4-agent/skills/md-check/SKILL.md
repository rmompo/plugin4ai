---
name: md-check
description: Audits a single agent markdown file for frontmatter completeness, instruction clarity, internal contradictions, and Markdown syntax. Emits a prioritized findings report. Also invoked explicitly as /p4-agent:md-check.
---

# md-check

Audits a single agent markdown file against a fixed battery of checks (A1–A4). Produces a findings report sorted by severity. Does not modify the file.

---

## Step 0 — Resolve file path

```bash
# Expand the argument to an absolute path
realpath "$ARGUMENTS" 2>/dev/null || echo "FILE_NOT_FOUND"
```

If the file does not exist → print:
```
❌ File not found: <path>
```
and stop.

---

## Step 1 — Read the file

Use the Read tool to load the full content of the target file.

Parse two sections:
- **Frontmatter**: the YAML block between the opening and closing `---` delimiters (if present)
- **Body**: everything after the closing `---` delimiter

---

## Step 2 — Run checks

Run all checks in order. Collect every finding with:
- `check`: A1 / A2 / A3 / A4
- `severity`: `CRITICAL` / `MAJOR`
- `location`: line number or section name where the issue was found
- `defect`: description of what is wrong
- `mitigation`: how to fix it

### A1 — Semantics, syntax and spelling  `MAJOR`

Scan the full file for:

**Markdown syntax issues:**
- Unclosed fenced code blocks (` ``` ` opened but not closed)
- Broken table formatting (misaligned columns, missing separator row)
- Invalid heading level jumps (e.g. `##` followed immediately by `####` without `###`)
- Broken links or image references: `[text](` without closing `)`

**Spelling and semantic issues:**
- Obvious spelling errors in prose sections (not inside code blocks or code spans)
- Terms used with inconsistent meaning across sections (e.g. same word refers to two different concepts)

Flag each issue as a separate finding with its line number.

```
Defect:    unclosed fenced code block starting at line N
Mitigate:  add closing ``` at the appropriate position

Defect:    spelling error: "<word>" (suggestion: "<correction>")
Mitigate:  correct spelling in prose

Defect:    term "<word>" used inconsistently — two different meanings across sections
Mitigate:  standardize term usage or add a definitions section
```

### A2 — Instructions: synthetic, clear, unambiguous  `MAJOR`

Scan every instruction block in the body (numbered lists, bullet lists that describe agent behavior, directive sections).

Flag any instruction that fails one or more of these criteria:

| Criterion | What to flag |
|-----------|-------------|
| **Synthetic** | Instruction is verbose — repeats information stated elsewhere, or uses multiple sentences where one would suffice |
| **Clear** | Instruction relies on implicit context — the reader needs external knowledge to understand it |
| **Unambiguous** | Instruction admits more than one interpretation — e.g. "handle errors appropriately" |

```
Defect:    instruction at line N is verbose: "<excerpt>"
Mitigate:  condense to a single, direct directive

Defect:    instruction at line N is implicit: "<excerpt>"
Mitigate:  make assumption explicit; add the missing context inline

Defect:    instruction at line N is ambiguous: "<excerpt>"
Mitigate:  replace with a concrete, deterministic directive
```

### A3 — No collisions (contradictions)  `CRITICAL`

Scan all instruction blocks across the entire file. Identify pairs of instructions that:
- Cannot both be true simultaneously
- One negates or overrides another without explicit precedence marker (e.g. "supersedes", "overrides", "unless")

For each contradictory pair, flag both locations.

```
Defect:    contradiction between line N ("<excerpt A>") and line M ("<excerpt B>")
Mitigate:  remove one instruction, or add explicit precedence ("instruction at line M supersedes line N")
```

If no contradictions found → no finding for A3.

### A4 — Frontmatter completeness  `CRITICAL`

Check whether the file opens with a YAML frontmatter block (`---` ... `---`).

If no frontmatter block is present → one finding per required field.

If frontmatter is present, verify each required field exists and is non-empty:

| Field | Valid if |
|-------|---------|
| `name` | non-empty string |
| `description` | non-empty string, ideally one line |
| `version` | numeric or semver string (e.g. `1`, `2.3`, `1.0.4`) |
| `changelog` | present (list or inline — at least one entry) |

Flag each missing or empty field individually.

```
Defect:    missing frontmatter block
Mitigate:  add --- YAML block at top of file with name, description, version, changelog

Defect:    frontmatter missing required field: <field>
Mitigate:  add <field>: <value> to the frontmatter block

Defect:    frontmatter field <field> is empty
Mitigate:  provide a value for <field>
```

---

## Step 3 — Emit findings report

If **no findings** → print:
```
✅ <filename> — no issues found (A1–A4)
```
and stop.

If findings exist, print:

```
══════════════════════════════════════════
  MD-CHECK REPORT
  File: <path>
══════════════════════════════════════════
```

Then the findings table:

| # | check | severity | location | defect | mitigation |
|---|-------|----------|----------|--------|-----------|
| 1 | A4 | CRITICAL | frontmatter | missing field: name | add name: <value> to frontmatter |
| 2 | A3 | CRITICAL | line 14 ↔ line 38 | contradiction: "always ask" vs "never prompt" | add explicit precedence |
| 3 | A1 | MAJOR | line 22 | unclosed code fence | add closing ``` |
| 4 | A2 | MAJOR | line 31 | ambiguous: "handle errors appropriately" | replace with concrete directive |

Sort by: `CRITICAL` first, then `MAJOR`; within same severity by line number ASC.

Print summary footer:
```
Findings: N total · C critical · M major
```

---

## Step 4 — Summary line

```
<filename>: N findings (C critical · M major)
```
