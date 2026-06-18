# Plugin Spec: p4-ccvv

> **Status:** `beta` | **Version:** `1.0.16` | **Ports:** Claude Code CLI/TUI only

---

## Overview

AI-powered CV generation and management system. Extracts structured profile data from existing CVs, adapts content to specific job offers, and exports to multiple formats. Supports multiple users with isolated profile storage.

All data is stored globally at `~/.p4/p4-ccvv/` following the p4-* scope convention.

---

## Port Status

| CLI | Location | Status |
|-----|----------|--------|
| Claude Code CLI/TUI | `claudecode/p4-ccvv/` | ✅ Beta |
| GitHub Copilot CLI/TUI | — | Proposal |
| Antigravity CLI/TUI | — | Proposal |
| Codex CLI/TUI | — | Proposal |

---

## Skill: `setup`

### Purpose
Verifies that all required external tools (pandoc, pdflatex, python3) are available and correctly versioned.

### Invocation
```
/p4-ccvv:setup
```

### Output
Markdown table with dependency status and install instructions (Bash + PowerShell) for any missing tool.

---

## Skill: `profile-gather`

### Purpose
Reads a source CV file (PDF/DOCX) from the user's `input/` folder and extracts structured data into `profile.json` following the profile schema.

### Invocation
```
/p4-ccvv:profile-gather
```

### Non-Goals
- Does not modify existing profile data (use `profile-update` instead)
- Does not generate CVs

---

## Skill: `profile-update`

### Purpose
Updates an existing `profile.json` with new or corrected data. Supports document-based and interactive modes. Always creates a timestamped backup.

### Invocation
```
/p4-ccvv:profile-update
```

---

## Skill: `generate`

### Purpose
Generates a new CV draft adapted to a specific job position. Optionally analyzes a job offer to extract keywords and tailor content. Produces an editable markdown draft.

### Invocation
```
/p4-ccvv:generate
```

### Output
- `CV-[id]-META-[slug]-CV.md` — editable CV draft
- `CV-[id]-META-[slug]-LETTER.md` — cover letter (optional)

---

## Skill: `regen`

### Purpose
Regenerates an existing CV draft using updated profile data. Preserves original job parameters (position, offer analysis, keywords).

### Invocation
```
/p4-ccvv:regen
```

---

## Skill: `export`

### Purpose
Converts a CV draft to a final output format (PDF, DOCX, HTML, MD) in the selected language using Pandoc.

### Invocation
```
/p4-ccvv:export
```

### Output
`CV-[id]-[export_id]-[slug]-CV.[format]`

### Supported formats
`pdf`, `docx`, `html`, `md`

### Supported languages
`es` (Español), `en` (English), `fr` (Français), `de` (Deutsch), `it` (Italiano), `pt` (Português)

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.0.6 | Initial release with 6 skills |
