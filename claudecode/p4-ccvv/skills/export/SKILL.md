---
name: export
description: Exports a CV draft to a final format (PDF, DOCX, HTML, MD) in the selected language using Pandoc. Also invoked explicitly as /p4-ccvv:export.
version: 7
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# Export CV

Converts a CV draft (markdown META file) to a final output format using Pandoc. Each export creates a new sequenced file; previous exports are preserved.

```
STORAGE_ROOT = ~/.p4/p4-ccvv
GUIDELINES   = <plugin-cache>/resources/CV-GENERATION-GUIDELINES.md
```

---

## Step 1 — Select user

Read `profiles.json`. Use **AskUserQuestion** to select the profile.

---

## Step 2 — Select CV and export options

Read `cvs.json`. Use **AskUserQuestion** to select the CV metadata entry.

Show existing exports for the selected CV, then collect:

1. Output format: `pdf` / `docx` / `html` / `md`
2. Language: `es` / `en` / `fr` / `de` / `it` / `pt`

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

## Step 5 — Run Pandoc

### PDF
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

### MD (clean copy)
```bash
cp input.md output.md
```

If Pandoc fails: show full error and suggest running `/p4-ccvv:setup` to verify dependencies.

---

## Step 6 — Update cvs.json

Append export entry to `metadata[n].exports[]` and update `info.total_exports`, `info.last_exported`.

---

## Step 7 — Copy exported file (optional)

Use **AskUserQuestion** to ask:

> "¿Qué deseas hacer con el fichero exportado?"

Options:
1. **Copiar al directorio actual** — copies the file to `$PWD` (use `pwd` to resolve it)
2. **Copiar a otro path** — ask for destination path, then copy
3. **No copiar** — skip

Run `cp` accordingly and confirm the destination if copied.

---

## Step 8 — Confirm

```
✅ Exported: CV-[id_padded]-[export_id_padded]-[slug]-CV.[format]
   Format: [format] | Language: [lang] | Path: [full path]
   Copied to: [destination path]   ← only if copied
```
