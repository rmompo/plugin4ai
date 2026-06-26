---
name: sanitize
description: Scans all files that may contain sensitive information across the repo and offers to anonymize findings. Also invoked explicitly as /p4-core:sanitize with optional args.
version: 29
argument-hint: "[path]"
allowed-tools: [Bash, Read, Edit, ask_user]
---

# Sanitize

Scans **all files that may contain sensitive information** across the repo (documents, configs, scripts, structured data) for PII, credentials, company names, and infrastructure data — and offers to replace findings with safe placeholders, interactively, one at a time.

---

## Invocation modes

| Invocation | Scope |
|-----------|-------|
| `/p4-core:sanitize` | All plugins **and all sensitive-capable files** in the repo |
| `/p4-plugin:sanitize p4-buddy` | All files in a specific plugin |
| `/p4-plugin:sanitize p4-buddy gcomp` | A single skill only |

---

## Step 1 — Resolve scope

Locate repo root:
```bash
find ~ -name "marketplace.json" -path "*plugin4ai*" ! -path "*cache*" ! -path "*marketplaces*" 2>/dev/null | head -1
# REPO_ROOT = two levels up
```

Determine target files based on arguments:

- **No args**: ALL sensitive-capable files in the repo (recursive from repo root)
- **Plugin only**: `claudecode/<plugin>/`, `specs/<plugin>.md`
- **Plugin + skill**: `claudecode/<plugin>/skills/<skill>/SKILL.md` only

### Sensitive-capable file types

Scan any file matching the following extensions (binary files are always skipped):

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
  \( -name "*.md" -o -name "*.txt" -o -name "*.rst" -o -name "*.adoc" \
     -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.toml" \
     -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" -o -name "*.env" \
     -o -name "*.properties" -o -name "*.sh" -o -name "*.bash" -o -name "*.py" \
     -o -name "*.js" -o -name "*.ts" -o -name "*.rb" -o -name "*.ps1" \
     -o -name "*.xml" -o -name "*.csv" -o -name "*.tsv" -o -name "*.log" \
     -o -name "*.sql" \) \
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
- Patterns: API keys, tokens, passwords, secrets, AWS keys, connection strings
- Regex hints: `[A-Za-z0-9+/]{32,}`, `sk-[a-zA-Z0-9]{32,}`, `Bearer `, `password\s*=`, `token\s*=`
- Also: certificate fragments, hashes used as credentials

### 🌐 Infrastructure (auto-flag — high confidence)
- Private IPs: `10.x.x.x`, `192.168.x.x`, `172.16-31.x.x`
- Localhost variants with non-standard ports
- Internal/staging URLs (non-public domains, `.internal`, `.local`, `.corp`)
- System paths with username: `/home/<username>/`, `/Users/<username>/`, `C:\Users\<username>\`

### 👤 Personal identity — PII (flag with context check)
- Email addresses
- Phone numbers
- Real person names (inferred from context — flag if clearly a real person, not a role/example)
- National IDs, passport numbers, SSN-like patterns
- Date of birth patterns

### 🏢 Company & business (flag with context check)
- Employer or client company names (real organizations, not generic terms)
- Internal project names or product names
- Vendor or partner names

### 💳 Financial data (auto-flag — high confidence)
- Credit/debit card numbers (Luhn-detectable patterns)
- IBAN, SWIFT/BIC codes
- Bank account numbers

### 🏥 Special category data — GDPR (auto-flag if present)
- Health/medical information
- Ethnic or racial origin
- Political opinions, religious beliefs
- Biometric data references
- Sexual orientation

### 📋 Metadata
- File paths or comments revealing personal or internal infrastructure info
- Timestamps or commit references tied to personal accounts

---

## Step 3 — Build findings report

Group findings by file and category. For each finding record:
- File path (relative to repo root)
- Line number
- Category
- Matched text (excerpt, truncated if long)
- Confidence: `high` (auto-flag) or `review` (needs human judgment)
- Suggested placeholder (see table below)

### Placeholder conventions

| Category | Placeholder |
|----------|------------|
| Company name | `<company>` |
| Client name | `<client>` |
| Project name | `<project>` |
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
| Health data | `<health-data>` |

---

## Step 4 — Present findings and confirm

If **no findings**: report clean and exit.

If findings exist:

1. Show a summary table: file → N findings per category
2. Call `ask_user`:
   - question: `"X sensitive findings detected across Y files. How do you want to proceed?"`
   - header: `"Action"`
   - options:
     - `"Review and fix one by one"` — walk through each finding interactively
     - `"Fix all high-confidence findings automatically"` — apply all `high` confidence replacements without prompting; still confirm `review` items
     - `"Show report only, no changes"` — print full report and exit

---

## Step 5 — Apply fixes

### One-by-one mode
For each finding:
- Show: file, line, matched text, suggested placeholder
- Call `ask_user`:
  - question: `"Replace this finding?"`
  - header: `"Finding N/M"`
  - options: `["Yes, use suggested placeholder", "Yes, let me type a custom replacement", "Skip this finding", "Stop here"]`
- Apply using `Edit` tool with exact string match

### Auto mode (high-confidence only)
Apply all `high` confidence findings directly via `Edit`, then present `review` items one by one as above.

---

## Step 6 — Summary

After all fixes are applied, output:

```
═══════════════════════════════════════════════════
  SANITIZE COMPLETE
═══════════════════════════════════════════════════

Files scanned:   N
Findings total:  N  (N high / N review)
Fixed:           N
Skipped:         N

Files modified:
  docs/architecture.md
  claudecode/<plugin>/skills/<skill>/SKILL.md
  config/settings.yml
  ...

Next steps:
  1. Review changes with: git diff
  2. git add + commit
  3. claude plugins update <plugin>  (if skill content changed)
═══════════════════════════════════════════════════
```
