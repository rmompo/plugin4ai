---
name: setup
description: Verifies that all external dependencies (tools and plugins) required by p4-ccvv are installed and meet version constraints. Reports status with install instructions for each missing dependency. Also invoked explicitly as /p4-ccvv:setup.
version: 16
allowed-tools: [Bash]
---

# p4-ccvv Setup

Verifies that all required tools are available and prints a status report. Safe to re-run at any time.

---

## Step 1 — Check dependencies

Read the full `dependencies` array from `catalog.json` for p4-ccvv. Collect all entries, preserving their `type`.

Currently required:

| Type | Name | Required |
|------|------|----------|
| `tool` | `pandoc` | `>=2.0.0` |
| `tool` | `pdflatex` | `*` |
| `tool` | `python3` | `>=3.8.0` |

For each dependency, check by type:

| Type | How to check |
|------|-------------|
| `tool` | `which <name> 2>/dev/null && <name> --version 2>&1 \| head -1` — then verify version constraint |
| `plugin` | `ls ~/.claude/plugins/cache/plugin4ai-claudecode/<name>/ 2>/dev/null` — installed if directory has at least one entry |

```bash
which pandoc   && pandoc --version   2>&1 | head -1
which pdflatex && pdflatex --version 2>&1 | head -1
which python3  && python3 --version  2>&1
```

Parse the version string from each tool output.

---

## Step 2 — Evaluate constraints

For `type: "tool"` entries, compare found version against the `version` constraint from catalog. For `type: "plugin"` entries, only presence is checked — no version comparison.

---

## Step 3 — Print Markdown status table

```markdown
| Type | Dependency | Required | Found   | Status |
|------|------------|----------|---------|--------|
| tool | pandoc     | >=2.0.0  | 3.1.3   | ✅     |
| tool | pdflatex   | *        | —       | ❌     |
| tool | python3    | >=3.8.0  | 3.11.2  | ✅     |
```

---

## Step 4 — Install instructions for each ❌

### pdflatex

**Bash (Linux/WSL):**
```bash
sudo apt install texlive-latex-base texlive-latex-recommended texlive-fonts-recommended
```

**PowerShell (Windows):**
```powershell
winget install MiKTeX.MiKTeX
```

### pandoc (if missing)

**Bash (Linux/WSL):**
```bash
sudo apt install pandoc
```

**PowerShell (Windows):**
```powershell
winget install JohnMacFarlane.Pandoc
```

### python3 (if missing)

**Bash (Linux/WSL):**
```bash
sudo apt install python3
```

**PowerShell (Windows):**
```powershell
winget install Python.Python.3
```

---

## Step 5 — Final status

If all ✅ → print: `✅ p4-ccvv is ready. Storage root: ~/.p4/p4-ccvv/`

If any ❌ → print: `⚠️ Install missing dependencies before using p4-ccvv.`
