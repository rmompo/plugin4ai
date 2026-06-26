---
name: export
description: Exports a CV draft to a final format (PDF, DOCX, HTML, MD) using Pandoc with graceful degradation.
---

# Export CV

Converts a CV draft (markdown META file) to a final output format using Pandoc. Each export creates a new sequenced file; previous exports are preserved.

> **Degraded port note**: PDF export requires `pdflatex`. If missing, it is automatically downgraded to HTML with a warning. `md` format never requires Pandoc.

```
STORAGE_ROOT = ~/.p4/p4-ccvv
```

```bash
PLUGIN_CACHE=$(ls -d ~/.codex/plugins/cache/plugin4ai-codex/p4-ccvv/*/ 2>/dev/null | sort -V | tail -1)
```

---

## Step 0 — Verify Pandoc availability

```bash
which pandoc 2>/dev/null
```

- If **pandoc is missing** and format ≠ `md` → stop with error:
  ```
  ❌ Pandoc not found. Install it to use this skill:
     Linux:  sudo apt install pandoc
     macOS:  brew install pandoc
     Windows: winget install JohnMacFarlane.Pandoc
  ```
- If format = `md` → Pandoc is not needed; continue regardless.

---

## Step 1 — Select user

Read `profiles.json`. Ask the user (via plain text) to select the profile.

---

## Step 2 — Select CV and export options

Read `cvs.json`. Ask the user (via plain text) to select the CV metadata entry.

Show existing exports for the selected CV, then ask:
1. Output format: `pdf` / `docx` / `html` / `md`
2. Language: `es` / `en` / `fr` / `de` / `it` / `pt`

---

## Step 2b — Handle PDF fallback

If format = `pdf`:
```bash
which pdflatex 2>/dev/null
```

If `pdflatex` is **missing**:
- Warn the user: "⚠️ pdflatex not found — downgrading export format from PDF to HTML."
- Change format to `html`.

---

## Step 3 — Prepare export

Calculate next `export_id` = `max(existing export ids for this metadata) + 1` (start at 1).

Output filename: `CV-[id_padded]-[export_id_padded]-[slug]-CV.[format]`

Output path: `$STORAGE_ROOT/profiles/[user]/output/CV-[id_padded]-[slug]/`

---

## Step 4 — Apply language translation to draft

If the target language differs from the draft language (`language` field in YAML):
- Translate all descriptive content following GUIDELINES §4
- **Never translate**: technology names, frameworks, tools, brands, acronyms, proper names
- Translate: section titles, descriptions, responsibilities, achievements, education status, language levels, interests, closing phrase

Update YAML `language` field to target language code.

---

## Step 5 — Run Pandoc (or copy for MD)

### PDF (after pdflatex check)
```bash
pandoc input.md -o output.pdf \
  --pdf-engine=pdflatex \
  --variable=geometry:margin=2cm \
  --variable=fontsize:11pt
```

### DOCX
```bash
pandoc input.md -o output.docx
```

### HTML
```bash
pandoc input.md -o output.html --standalone --embed-resources
```

### MD (clean copy — no Pandoc needed)
```bash
cp input.md output.md
```

If Pandoc fails: show full error and suggest running the p4-ccvv setup skill to verify dependencies.

---

## Step 6 — Update cvs.json

Append export entry to `metadata[n].exports[]` and update `info.total_exports`, `info.last_exported`.

---

## Step 7 — Copy exported file (optional)

Ask the user (via plain text) what to do with the exported file:
1. Copy to current directory (`$PWD`)
2. Copy to a specified path
3. Do not copy

Run `cp` accordingly and confirm the destination if copied.

---

## Step 8 — Confirm

```
✅ Exported: CV-[id_padded]-[export_id_padded]-[slug]-CV.[format]
   Format: [format] | Language: [lang] | Path: [full path]
   Copied to: [destination path]   ← only if copied
```
