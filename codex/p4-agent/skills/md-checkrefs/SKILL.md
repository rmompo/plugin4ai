---
name: md-checkrefs
description: Audits an agent markdown file and all files it references — runs checks A1–A4 on every file in the reference graph, plus B1 reference integrity. Also invoked explicitly as /p4-agent:md-checkrefs.
---

# md-checkrefs

Expands the scope of `md-check` across the full reference graph of an agent markdown file. Runs checks A1–A4 (identical to `/p4-agent:md-check`) on every file in the graph, plus check B1 for reference integrity. Does not modify any file.

---

## Step 0 — Resolve entry file

```bash
realpath "$ARGUMENTS" 2>/dev/null || echo "FILE_NOT_FOUND"
```

If the file does not exist → print:
```
❌ File not found: <path>
```
and stop.

---

## Step 1 — Build the reference graph

Starting from the entry file, discover all local file references recursively:

```bash
# Extract local markdown links from a file
grep -oP '\[.*?\]\(\K[^)]+' <file> | grep -v '^https\?://' | grep -v '^#'
```

**Algorithm:**

1. Add entry file to the graph (visited set)
2. Parse the file for local references: `[label](./relative/path.md)` or `[label](../other.md)`
3. Resolve each reference relative to the containing file's directory
4. For each resolved path:
   - If file exists and not yet visited → add to graph, recurse
   - If file does not exist → record as B1 broken reference (do not recurse)
   - If already visited → skip (avoid cycles)
5. Repeat until no new files are found

**Scope:** only local file references (relative paths). Ignore:
- External URLs (`http://`, `https://`)
- Anchor-only links (`#section`)
- References inside fenced code blocks

Print the discovered graph before running checks:

```
📂 Reference graph (entry: agent.md)
  ├── agent.md
  ├── commands/COMMAND-SETUP.md
  ├── commands/COMMAND-CRAWL.md
  └── templates/TEMPLATE-CONFIG.md
  ✖ commands/COMMAND-MISSING.md  ← broken reference
```

---

## Step 2 — Check B1: Reference integrity  `CRITICAL`

For each reference found during graph traversal:

- If target file **does not exist** → B1 finding
- If target file exists but has **no frontmatter** (`name`, `description`, `version`, `changelog`) → A4 finding (handled in Step 3 per-file)

```
Defect:    broken reference in <source_file> line N → <target_path> does not exist
Mitigate:  create the missing file or fix the reference path
```

Collect all B1 findings. These are reported first (highest priority).

---

## Step 3 — Run A1–A4 on every file in the graph

For each file in the graph (excluding broken references), run the full `md-check` battery:

- **A1** — Semantics, syntax and spelling
- **A2** — Instructions: synthetic, clear, unambiguous
- **A3** — No collisions (contradictions)
- **A4** — Frontmatter completeness (name, description, version, changelog)

Each finding is tagged with its source file for traceability.

---

## Step 4 — Emit findings report

If **no findings** → print:
```
✅ <entry_file> + N referenced files — no issues found (B1, A1–A4)
```
and stop.

If findings exist, print:

```
══════════════════════════════════════════
  MD-CHECKREFS REPORT
  Entry: <path>
  Files audited: N
══════════════════════════════════════════
```

Then the findings table, grouped by file:

```
── agent.md ──────────────────────────────
| # | check | severity | location | defect | mitigation |
|---|-------|----------|----------|--------|-----------|
| 1 | A4 | CRITICAL | frontmatter | missing field: changelog | add changelog: to frontmatter |

── commands/COMMAND-SETUP.md ─────────────
| # | check | severity | location | defect | mitigation |
|---|-------|----------|----------|--------|-----------|
| 2 | B1 | CRITICAL | agent.md line 12 | broken ref → COMMAND-MISSING.md | create file or fix path |
| 3 | A2 | MAJOR | line 8 | ambiguous instruction | replace with concrete directive |
```

Sort within each file: `CRITICAL` first, then `MAJOR`; by line number ASC within same severity.

Print summary footer:
```
Files audited: N · Findings: T total · C critical · M major
```

---

## Step 5 — Summary line

```
<entry_file>: N files · T findings (C critical · M major)
```
