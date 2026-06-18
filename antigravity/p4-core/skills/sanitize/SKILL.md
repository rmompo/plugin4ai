---
name: sanitize
description: Scans all files that may contain sensitive information across the repo and offers to anonymize findings. Also invoked explicitly as /p4-core:sanitize with an optional path argument.
---

# Sanitize

Scans **all files that may contain sensitive information** across the repo (documents, configs, scripts, structured data) for PII, credentials, company names, and infrastructure data — and offers to replace findings with safe placeholders, interactively, one at a time.

---

## Invocation modes

| Invocation | Scope |
|-----------|-------|
| `/p4-core:sanitize` | All sensitive-capable files in the repo |
| `/p4-core:sanitize <path>` | Specific file or directory only |

---

## Step 1 — Resolve scope

Locate repo root (look for `.git` directory):
```bash
git rev-parse --show-toplevel 2>/dev/null
```

Determine target files based on arguments:

- **No args**: ALL sensitive-capable files in the repo (recursive from repo root)
- **Path arg**: files under the specified path only

### Sensitive-capable file types

| Category | Extensions |
|----------|-----------|
| Documents | `.md`, `.txt`, `.rst`, `.adoc` |
| Config & data | `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.env`, `.properties` |
| Scripts | `.sh`, `.bash`, `.py`, `.js`, `.ts`, `.rb`, `.ps1` |
| Structured data | `.xml`, `.csv`, `.tsv` |
| Other text | `.log`, `.sql` |

Exclusions (always skip):
```bash
find "$REPO_ROOT" -type f \
  \( -name "*.md" -o -name "*.txt" -o -name "*.json" -o -name "*.yaml" \
     -o -name "*.yml" -o -name "*.toml" -o -name "*.sh" -o -name "*.py" \
     -o -name "*.js" -o -name "*.ts" \) \
  ! -path "*/.git/*" \
  ! -path "*/node_modules/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/.venv/*" \
  | sort
```

---

## Step 2 — Scan for sensitive information

Read each target file and look for the following categories:

### 🔐 Credentials & secrets (auto-flag — high confidence)
- API keys, tokens, passwords, secrets, connection strings
- Patterns: `sk-[a-zA-Z0-9]{32,}`, `Bearer `, `password\s*=`, `token\s*=`

### 🌐 Infrastructure (auto-flag — high confidence)
- Private IPs: `10.x.x.x`, `192.168.x.x`, `172.16-31.x.x`
- Internal URLs (`.internal`, `.local`, `.corp`)
- System paths with username: `/home/<username>/`, `/Users/<username>/`

### 👤 Personal identity — PII (flag with context check)
- Email addresses, phone numbers, real person names
- National IDs, date of birth patterns

### 🏢 Company & business (flag with context check)
- Employer or client company names (real organizations)
- Internal project or product names

### 💳 Financial data (auto-flag — high confidence)
- Credit card numbers, IBAN, SWIFT/BIC codes

---

## Step 3 — Build findings report

Group findings by file and category. For each finding record:
- File path (relative to repo root)
- Line number
- Category
- Matched text (excerpt, truncated if long)
- Confidence: `high` (auto-flag) or `review` (needs human judgment)
- Suggested placeholder

### Placeholder conventions

| Category | Placeholder |
|----------|------------|
| Company name | `<company>` |
| Person name | `<name>` |
| Email | `<email>` |
| Phone | `<phone>` |
| API key / token | `<api-key>` |
| Password | `<password>` |
| IP address | `<ip-address>` |
| Internal URL | `<internal-url>` |
| System path | `<system-path>` |
| IBAN / bank | `<financial-data>` |
| National ID | `<national-id>` |

---

## Step 4 — Present findings and confirm

If **no findings**: report clean and exit.

If findings exist:

1. Show a summary table: file → N findings per category
2. Ask the user how to proceed:
   - **"Review and fix one by one"** — walk through each finding interactively
   - **"Fix all high-confidence findings automatically"** — apply all `high` replacements without prompting; confirm `review` items one by one
   - **"Show report only, no changes"** — print full report and exit

---

## Step 5 — Apply fixes

### One-by-one mode
For each finding:
- Show: file, line, matched text, suggested placeholder
- Ask: replace with suggested placeholder / custom replacement / skip / stop
- Apply with exact string match

### Auto mode (high-confidence only)
Apply all `high` confidence findings directly, then present `review` items one by one.

---

## Step 6 — Summary

After all fixes:

```
═══════════════════════════════════════════════════
  SANITIZE COMPLETE
═══════════════════════════════════════════════════

Files scanned:   N
Findings total:  N  (N high / N review)
Fixed:           N
Skipped:         N

Files modified:
  path/to/file.md
  ...

Next steps:
  1. Review changes with: git diff
  2. git add + commit
═══════════════════════════════════════════════════
```
