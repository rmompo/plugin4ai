---
name: any-to-md
description: Converts PDF, DOC, DOCX, PPT, and PPTX documents to structured Markdown using a 9-step pipeline with best-effort tool degradation.
---

# Any to Markdown

Converts documents (PDF, DOC, DOCX, PPT, PPTX) to structured, LLM-optimized Markdown using a 9-step pipeline: inventory → to-pdf → split → extract → consolidate → review.

> **Degraded port note**: Tool availability is checked at runtime. Missing tools trigger best-effort fallbacks instead of hard stops. See Step 2 for details.

```
CONSOLIDATE_SCRIPT = <plugin-cache>/resources/scripts/all-to-md-consolidate.py
```

```bash
PLUGIN_CACHE=$(ls -d ~/.codex/plugins/cache/plugin4ai-codex/p4-converter/*/ 2>/dev/null | sort -V | tail -1)
CONSOLIDATE_SCRIPT="$PLUGIN_CACHE/resources/scripts/all-to-md-consolidate.py"
```

**Processing model:** for each document in the inventory, run Steps 4 through 9 in full before moving to the next.

**Key variables:**

| Variable | Value |
|----------|-------|
| `SOURCE_FOLDER` | Absolute path to the folder containing the source document |
| `OUTPUT_PATH` | Destination folder for `.md` files; `null` means co-located with source |
| `reprocess` | Boolean — whether to reprocess already-converted files |
| `HAS_LIBREOFFICE` | Boolean — set in Step 2 |
| `HAS_QPDF` | Boolean — set in Step 2 |
| `HAS_PYTHON3` | Boolean — set in Step 2 |

---

## Step 1 — Resolve plugin cache and collect parameters

Ask the user (via plain text) to provide the three conversion parameters (or resolve from environment / skill argument).

### 1.1 — Input path
Resolve in order of precedence:
1. Environment variable `AGENT_ALL_TO_MD_PATTERN`
2. Argument passed to the skill invocation
3. Ask the user for: a folder, a single file, or a glob pattern.

Expand `~` to the actual home directory before any file operation.
Supported formats: `.pdf` `.doc` `.docx` `.ppt` `.pptx`

### 1.2 — Selection within the input path
If the input path is a **folder**, ask how to select files:
- All supported files (recursive if needed)
- Glob pattern relative to the input path
- Explicit file(s)

If already a single file or full glob → skip this sub-question.

### 1.3 — Output path
Resolve in order of precedence:
1. `AGENT_ALL_TO_MD_OUTPUT` env var → if unset/empty/`"source"` → `OUTPUT_PATH = null` (co-located)
2. Ask the user: same folder as source *(Recommended)* or custom absolute path

### 1.4 — Reprocess flag
- `AGENT_ALL_TO_MD_REPROCESS=true` → `reprocess = true`
- Otherwise → `reprocess = false`

---

## Step 2 — Verify tools (best-effort mode)

Check availability and set flags:

```bash
which qpdf       2>/dev/null && HAS_QPDF=true       || HAS_QPDF=false
which python3    2>/dev/null && HAS_PYTHON3=true     || HAS_PYTHON3=false
which libreoffice 2>/dev/null && HAS_LIBREOFFICE=true || HAS_LIBREOFFICE=false
```

Print a tool status summary:
```
Tool availability:
  qpdf:         [✅ found / ⚠️ missing — PDF splitting disabled; single-chunk mode]
  python3:      [✅ found / ⚠️ missing — consolidation script unavailable; LLM-only mode]
  libreoffice:  [✅ found / ⚠️ missing — DOC/DOCX/PPT/PPTX conversion disabled]
```

**Degradation rules:**
- `HAS_LIBREOFFICE=false` AND inventory contains Office files → **skip** those files (warn per file)
- `HAS_QPDF=false` → process each PDF as a **single chunk** (no page split)
- `HAS_PYTHON3=false` → **skip consolidation script** (Step 7); use LLM-only merging instead

Do NOT stop — continue with whatever tools are available.

---

## Step 3 — Build inventory

Resolve the glob pattern and collect files: `.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx`.

For each file:
- If Office file AND `HAS_LIBREOFFICE=false` → mark as **skipped (no libreoffice)**, warn user
- Otherwise: determine route (pdf direct / office→pdf→md)

| Extension | Conversion route |
|-----------|-----------------|
| `.pdf` | Direct → Step 5 (split or single-chunk) |
| `.doc`, `.docx`, `.ppt`, `.pptx` | Step 4 (to PDF) → Step 5 |

Compute target `.md` path. If target already exists AND `reprocess = false` → mark skipped.

Ask the user (via plain text) whether to reprocess already-converted files.

Print inventory summary and Ask the user (via plain text) to confirm the inventory before proceeding.:
```
══════════════════════════════════════════
  DOCUMENT INVENTORY
══════════════════════════════════════════
  Files to convert:  N
  Files skipped:     N
  ...
══════════════════════════════════════════
```

---

## Step 4 — Convert non-PDF files to PDF (LibreOffice)

Only runs if `HAS_LIBREOFFICE=true` AND there are Office files in inventory.

For each Office file:
- If `{name}.pdf` already exists → reuse it, notify
- Otherwise:

```bash
libreoffice --headless --convert-to pdf --outdir {SOURCE_FOLDER} {SOURCE_FOLDER}/{name}.{ext}
```

Verify generated PDF exists and size > 0. If verification fails → skip this file and warn.

---

## Step 5 — Split PDF into chunks (qpdf or single-chunk fallback)

**If `HAS_QPDF=true`** — normal split (chunk size = 5 pages):
```bash
qpdf --show-npages {SOURCE_FOLDER}/{pdf-input}
# Generate chunks:
qpdf {SOURCE_FOLDER}/{pdf-input} --pages . {page_start}-{page_end} -- {SOURCE_FOLDER}/{name}_{start_fmt}-{end_fmt}.tmp.pdf
```

**If `HAS_QPDF=false`** — single-chunk mode:
```bash
cp {SOURCE_FOLDER}/{pdf-input} {SOURCE_FOLDER}/{name}_001-999.tmp.pdf
```
Warn: "⚠️ qpdf not found — processing as single chunk. Large PDFs may produce lower quality output."

---

## Step 6 — Extract content (LLM reads each chunk)

Process chunks sequentially. For each chunk `.tmp.pdf`:

Use the **Read tool** to open the chunk — the model interprets text and images directly.

Apply omission rules (page headers/footers, page numbers, TOC, document control sheets) and conversion rules (headings, lists, tables, code blocks, Mermaid diagrams, image descriptions).

Save extracted content to: `{SOURCE_FOLDER}/{name}_{page_start}-{page_end}.tmp.md`

---

## Step 7 — Consolidate chunks

**If `HAS_PYTHON3=true` AND consolidation script exists:**
```bash
python3 "$CONSOLIDATE_SCRIPT" \
  --source {source-path}/{source-name}.{ext} \
  --pdf    {source-path}/{name}.pdf \
  --output {output-path}/{name}.md
```

**If `HAS_PYTHON3=false` OR script missing — LLM-only consolidation:**
- Read all `.tmp.md` files in ascending order
- Merge content: remove chunk boundary duplicates, unify heading hierarchy
- Write manually to `{output-path}/{name}.md` using the Write tool
- Add frontmatter manually:
```yaml
---
source: {source-name}.{ext}
converted: {ISO_TIMESTAMP}
note: consolidated via LLM (python3 unavailable)
---
```

---

## Step 8 — Review and cleanup

Read `{name}.md`. Correct spelling/grammar errors, remove redundancies, verify code block syntax, ensure heading hierarchy is consistent.

Remove temp files:
```bash
rm {SOURCE_FOLDER}/{name}_*.tmp.pdf
rm {SOURCE_FOLDER}/{name}_*.tmp.md
```

---

## Step 9 — Final summary (per document)

```
══════════════════════════════════════════
  DOCUMENT CONVERTED SUCCESSFULLY
══════════════════════════════════════════
  Source:      {SOURCE_FOLDER}/{name}.{ext}
  Output:      {output-path}/{name}.md
  Temp files:  deleted
  Mode:        [normal / qpdf-missing-single-chunk / python3-missing-llm-only]
══════════════════════════════════════════
```
