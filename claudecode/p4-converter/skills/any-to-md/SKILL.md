---
name: any-to-md
description: Converts PDF, DOC, DOCX, PPT, and PPTX documents to structured Markdown using a 9-step pipeline (inventory → LibreOffice → qpdf split → LLM extraction → Python consolidation → LLM review). Also invoked explicitly as /p4-converter:any-to-md.
version: 4
argument-hint: "[path/to/file-or-folder-or-glob]"
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# Any to Markdown

Converts documents (PDF, DOC, DOCX, PPT, PPTX) to structured, LLM-optimized Markdown using a 9-step pipeline covering 6 conceptual phases: inventory → to-pdf → split → extract → consolidate → review.

```
CONSOLIDATE_SCRIPT = <plugin-cache>/resources/scripts/all-to-md-consolidate.py
```

Where `<plugin-cache>` = `~/.claude/plugins/cache/plugin4ai-claudecode/p4-converter/<version>/`

**Prerequisites:** run `/p4-converter:setup` first to verify tool availability.

**Processing model:** for each document in the inventory, run Steps 4 through 9 in full before moving to the next. Steps 4 and 5 reference "each file" within that per-document loop — not a batch over the whole inventory.

**Key variables** (established in Step 1, used throughout):

| Variable | Value |
|----------|-------|
| `SOURCE_FOLDER` | Absolute path to the folder containing the source document |
| `OUTPUT_PATH` | Destination folder for `.md` files; `null` means co-located with source |
| `reprocess` | Boolean — whether to reprocess already-converted files |

---

## Step 1 — Resolve plugin cache and collect parameters

```bash
PLUGIN_CACHE=$(ls -d ~/.claude/plugins/cache/plugin4ai-claudecode/p4-converter/*/ 2>/dev/null | sort -V | tail -1)
CONSOLIDATE_SCRIPT="$PLUGIN_CACHE/resources/scripts/all-to-md-consolidate.py"
```

Use **AskUserQuestion** to collect the three conversion parameters (or resolve from environment / skill argument):

### 1.1 — Input path

Resolve in order of precedence:
1. Environment variable `AGENT_ALL_TO_MD_PATTERN`
2. Argument passed to the skill invocation
3. Ask the user:

```
Input path — where are the source documents?
You can specify:
  - A folder:      /home/user/docs/
  - A single file: /home/user/docs/manual.docx
  - A glob:        /home/user/docs/reports/*.pdf

Supported formats: .pdf  .doc  .docx  .ppt  .pptx
```

Expand `~` to the actual home directory before any file operation.

### 1.2 — Selection within the input path

If the input path is a **folder**, ask the user how to select files within it:
- **All supported files** — process every `.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx` found (recursive if needed)
- **Glob pattern** — user provides a pattern relative to the input path (e.g. `reports_2026_*.pdf`)
- **Explicit file(s)** — user lists specific filenames

If the input path is already a **single file** or a **full glob** → skip this sub-question and use it directly.

### 1.3 — Output path

Resolve in order of precedence:
1. **Environment variable `AGENT_ALL_TO_MD_OUTPUT`**:
   - If unset, empty, or equal to `"source"` → `OUTPUT_PATH = null` (co-located mode)
   - Otherwise → `OUTPUT_PATH = <value>` (must be an absolute path; validate it exists or offer to create it)
2. **AskUserQuestion** (only if env var is unset or empty):
   - **Same folder as source** *(Recommended)* — each `.md` is saved next to its source file → `OUTPUT_PATH = null`
   - **Custom path** — user provides an absolute path to a different destination folder → validate it exists (or offer to create it); set `OUTPUT_PATH`

### 1.4 — Reprocess flag

- If `AGENT_ALL_TO_MD_REPROCESS=true` → `reprocess = true` (forced by env var; Step 3 will NOT ask again)
- Otherwise → `reprocess = false` (default; Step 3 may ask interactively if already-converted files are found)

---

## Step 2 — Verify tools

Before building the inventory, verify the three required tools are present:

```bash
which qpdf    && qpdf --version 2>&1 | head -1
which python3 && python3 --version 2>&1 | head -1
which libreoffice && libreoffice --version 2>&1 | head -1
```

- `libreoffice` is **mandatory** only if the inventory will contain DOC/DOCX/PPT/PPTX files.
- If any required tool is missing → stop and direct the user to run `/p4-converter:setup`.

---

## Step 3 — Build inventory

Resolve the glob pattern and collect files with extensions: `.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx`.

For each file, `SOURCE_FOLDER` = absolute path to the folder containing that file.

| Extension | Conversion route |
|-----------|-----------------|
| `.pdf` | Direct → Step 5 (split) |
| `.doc`, `.docx`, `.ppt`, `.pptx` | Step 4 (to PDF) → Step 5 (split) |

- Compute the target `.md` path:
  - If `OUTPUT_PATH` is set → `{OUTPUT_PATH}/{name}.md`
  - If `OUTPUT_PATH` is null → `{source-folder}/{name}.md` (co-located with source)
- If the target `.md` already exists AND `reprocess = false` → mark as **skipped**.
- If the target `.md` already exists AND `reprocess = true` → include in inventory.
- If the target `.md` does not exist → include in inventory.

Sort the inventory alphabetically by path.

**If there are skipped files AND `reprocess = false` (not forced by env var in Step 1.4)**, ask the user:
```
N file(s) already converted (their .md exists):
  - input/docs/manual.docx → output/manual.md (exists)

Do you want to reprocess them?
  1 - Yes, reprocess all
  2 - No, skip them (continue with pending only)
```

If `reprocess = true` (set by env var in Step 1.4) → include all files without asking.

**Print final inventory summary** and ask for confirmation before proceeding:
```
══════════════════════════════════════════
  DOCUMENT INVENTORY
══════════════════════════════════════════
  Files to convert:  N
  Files skipped:     N
  Input path:        [input path]
  Output path:       [output path or "co-located with source"]
  Reprocess:         yes/no
══════════════════════════════════════════

Files to process:
  1. input/docs/manual.docx       [docx → pdf → md]
  2. input/docs/guide.pdf         [pdf → md]
  3. input/docs/slides.pptx       [pptx → pdf → md]

Proceed with conversion? [y/N]
```

If the inventory is empty → stop with a clear message.

---

## Step 4 — Convert non-PDF files to PDF (LibreOffice)

Process only DOC/DOCX/PPT/PPTX files from the inventory.

For each file, check if `{name}.pdf` already exists in the same folder:
- **Exists** → skip conversion, reuse the existing PDF. Notify: `→ manual.docx: PDF already exists (manual.pdf), reusing`
- **Not exists** → convert:

```bash
libreoffice --headless --convert-to pdf --outdir {SOURCE_FOLDER} {SOURCE_FOLDER}/{name}.{ext}
```

The generated PDF keeps the same filename, only the extension changes. It is a **permanent artifact** — never deleted.

After each conversion, verify:
- `{name}.pdf` exists in the correct folder
- Size is greater than 0 bytes

If verification fails → stop and report which file failed.

**Summary:**
```
══════════════════════════════════════════
  PDF CONVERSION SUMMARY
══════════════════════════════════════════
  Converted:   2
    ✓ manual.docx   → manual.pdf  (new)
    → slides.pptx   → slides.pdf  (already existed, reused)
  Native PDF:  1
    → guide.pdf  (no conversion needed)
══════════════════════════════════════════
```

---

## Step 5 — Split PDF into chunks (qpdf)

For each document in the inventory, determine the PDF to split:

| Source file | PDF for qpdf |
|-------------|-------------|
| `guide.pdf` | `guide.pdf` |
| `manual.docx` | `manual.pdf` (generated in Step 4) |
| `slides.pptx` | `slides.pdf` (generated in Step 4) |

**Get page count:**
```bash
qpdf --show-npages {SOURCE_FOLDER}/{pdf-input}
```

**Calculate chunks** (chunk size = 5 pages):
```
chunk 1: pages 1  →  5   → {name}_001-005.tmp.pdf
chunk 2: pages 6  → 10   → {name}_006-010.tmp.pdf
...
chunk k: pages X  →  N   → {name}_0XX-0YY.tmp.pdf
```

Numeric format: 3 digits zero-padded (`001`, `006`, `011`…). **Note:** this naming supports documents up to 999 pages. Documents with ≥1000 pages would require 4-digit padding — flag this case to the user and stop.

**Generate each chunk:**
```bash
qpdf {SOURCE_FOLDER}/{pdf-input} --pages . {page_start}-{page_end} -- {SOURCE_FOLDER}/{name}_{start_fmt}-{end_fmt}.tmp.pdf
```

Verify all expected chunks were created and have size > 0.

**Summary:**
```
══════════════════════════════════════════
  SPLIT SUMMARY
══════════════════════════════════════════
  File:    manual.docx (via manual.pdf)
  Pages:   12
  Chunks:  3
    → manual_001-005.tmp.pdf  (pp. 1-5)
    → manual_006-010.tmp.pdf  (pp. 6-10)
    → manual_011-012.tmp.pdf  (pp. 11-12)
══════════════════════════════════════════
```

---

## Step 6 — Extract content (LLM reads each chunk)

Process chunks **strictly sequentially** — one at a time, in ascending page order. Do not start the next chunk until the previous one is complete.

For each chunk `.tmp.pdf`:

### 6.1 Read the chunk PDF

Use the **Read tool** to open the chunk `.tmp.pdf` — the model interprets text and images directly from the file. Do not use external text extractors (pdftotext, pdfimages, etc.) for this step.

### 6.2 Apply omission rules

**OMIT the following elements:**

| Element | Detection criterion |
|---------|---------------------|
| Page headers | Text repeated at the top of multiple pages |
| Page footers | Text repeated at the bottom of multiple pages |
| Page numbers | Isolated number in header or footer |
| TOC / Index | Always — regardless of position in the document |
| Document control sheet | Metadata table (title, version, date, authors) |
| Change history table | Document version history |

### 6.3 Text extraction rules

| Element | Markdown conversion |
|---------|---------------------|
| Main title | `# Title` |
| Sections | `## Section` / `### Subsection` |
| Paragraphs | Plain text |
| Numbered lists | `1. Item` |
| Bullet lists | `- Item` |
| Tables | Standard Markdown tables |
| Source code | ` ```language ` block with syntax highlighting |
| Shell / terminal commands | ` ```bash ` block |
| Notes / warnings / notices | `> **Note:** text` |
| Internal cross-references | `[text](#section-anchor)` |
| External URLs | `[text](url)` |
| Slides (PPT/PPTX origin) | Each slide as `##` section, slide title as heading |

### 6.4 Image interpretation rules (priority order)

| Priority | Image type | Conversion |
|----------|------------|------------|
| 1 | Flow / process diagram | Mermaid `flowchart` |
| 2 | Sequence diagram | Mermaid `sequenceDiagram` |
| 3 | Class / entity diagram | Mermaid `classDiagram` / `erDiagram` |
| 4 | State diagram | Mermaid `stateDiagram-v2` |
| 5 | System / infrastructure architecture | Mermaid `graph` |
| 6 | UI / mockup / screenshot | Textual description of layout (inputs, buttons, panels, labels, arrangement) |
| 7 | OCR image — code / shell / config | Code block with detected language |
| 8 | OCR image — general text | Plain extracted text |
| 9 | General image (photo, illustration) | Narrative description: subject, context, colors, action |
| 10 | Uninterpretable image | `[Image: {description or available alt text}]` |

### 6.5 Write the .tmp.md

The `.tmp.md` file has **NO frontmatter**. It starts directly with the extracted content.

Save to: `{SOURCE_FOLDER}/{name}_{page_start}-{page_end}.tmp.md`

**Summary after all chunks of a file:**
```
══════════════════════════════════════════
  EXTRACTION COMPLETE
══════════════════════════════════════════
  File:    manual.docx
  Chunks:  3
    ✓ manual_001-005.tmp.md
    ✓ manual_006-010.tmp.md
    ✓ manual_011-012.tmp.md
══════════════════════════════════════════
```

---

## Step 7 — Consolidate chunks (Python script)

Before consolidating, verify that all expected `.tmp.md` files exist (one per `.tmp.pdf` chunk from Step 5). If any is missing → stop and report.

Run the consolidation script:

```bash
python3 "$CONSOLIDATE_SCRIPT" \
  --source {source-path}/{source-name}.{ext} \
  --pdf    {source-path}/{name}.pdf \
  --output {output-path}/{name}.md
```

Where `{output-path}` is:
- `$OUTPUT_PATH` if set (Step 1.3)
- `{source-path}` if `OUTPUT_PATH` is null (co-located mode)

Parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--source` | Original file (for metadata) | `input/docs/manual.docx` |
| `--pdf` | Reference PDF (for page count) | `input/docs/manual.pdf` |
| `--output` | Final Markdown output path | `output/manual.md` |

The script automatically:
1. Locates all `.tmp.md` for the document (same prefix, same folder, ascending order)
2. Strips intermediate chunk frontmatter
3. Removes redundant chunk-boundary headers
4. Unifies section hierarchy
5. Generates consolidated frontmatter
6. Writes the final `{name}.md`

**Generated frontmatter:**
```yaml
---
source: manual.docx
source_format: docx
converted_via_pdf: true
converted: 2026-06-05T10:30:00
pages: 12
chunks: 3
chunk_size: 5
split_tool: qpdf
---
```

Verify that `{name}.md` has been created and is not empty.

---

## Step 8 — Review and cleanup

Read the complete `{name}.md` **before making any modifications** — full context is required.

### 8.1 Spelling and grammar

- Correct spelling and grammar errors.
- Keep technical terms in their original language (do not translate class names, methods, commands, paths).

### 8.2 Clarity and synthesis

| Aspect | Criterion |
|--------|-----------|
| Redundancies | Remove if the same information appears in multiple sections without adding context |
| Complex sentences | Simplify without losing technical precision |
| Empty sections | Remove or merge sections without relevant content |

### 8.3 LLM optimization

| Aspect | Criterion |
|--------|-----------|
| Code blocks | Verify all have a language specifier |
| Mermaid diagrams | Verify correct syntax |
| Tables | Verify correct column and header alignment |
| Heading hierarchy | `#` → `##` → `###` without skipping levels |
| Ambiguities | Add minimal context to sections that may be cryptic out of document context |
| Terminology | Consistent use of the same terms throughout |

### 8.4 Narrative continuity

| Aspect | Criterion |
|--------|-----------|
| Logical flow | Sections follow a logical progression |
| Artificial phrases | Remove phrases generated by fragmented processing ("As mentioned earlier…", "In the next section…") |
| Terminological coherence | Same concept named the same way throughout |
| Example continuity | Examples spanning multiple chunks must be seamlessly integrated |

### 8.5 Cleanup of temporary files

Once `{name}.md` is confirmed correct, remove all temporary files from **`SOURCE_FOLDER`** (the folder of the source document — NOT from `OUTPUT_PATH`, which only contains the final `.md`):

```bash
# Remove temporary PDF chunks — always in SOURCE_FOLDER
rm {SOURCE_FOLDER}/{name}_*.tmp.pdf

# Remove temporary Markdown chunks — always in SOURCE_FOLDER
rm {SOURCE_FOLDER}/{name}_*.tmp.md
```

**The `{SOURCE_FOLDER}/{name}.pdf` (PDF converted from DOC/DOCX/PPT/PPTX) is NOT deleted** — it is a permanent artifact reusable for future reprocessing.

Confirm deletion by listing the removed files.

---

## Step 9 — Final summary (per document)

```
══════════════════════════════════════════
  DOCUMENT CONVERTED SUCCESSFULLY
══════════════════════════════════════════
  Source:      {SOURCE_FOLDER}/manual.docx
  PDF:         {SOURCE_FOLDER}/manual.pdf  (preserved)
  Output:      {output-path}/manual.md
  Pages:       12
  Chunks:      3
  Temp files:  deleted (6 files)
══════════════════════════════════════════
```

For native PDF sources:
```
══════════════════════════════════════════
  DOCUMENT CONVERTED SUCCESSFULLY
══════════════════════════════════════════
  Source:      {SOURCE_FOLDER}/guide.pdf
  Output:      {output-path}/guide.md
  Pages:       7
  Chunks:      2
  Temp files:  deleted (4 files)
══════════════════════════════════════════
```

Where `{output-path}` = `OUTPUT_PATH` if set, or `SOURCE_FOLDER` if null (co-located).

**If the inventory has more files**, repeat Steps 4–9 for the next document in order.
