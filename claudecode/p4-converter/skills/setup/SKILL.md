---
name: setup
description: Verifies that all external dependencies (tools and plugins) required by p4-converter are installed and meet minimum version constraints. Also invoked explicitly as /p4-converter:setup.
version: 6
allowed-tools: [Bash]
---

# Setup — Dependency Check

Verifies that all tools required by `p4-converter` are installed and meet the minimum version constraints defined in `catalog.json`.

```
PLUGIN_NAME = p4-converter
```

---

## Step 1 — Locate plugin cache and read dependencies

```bash
PLUGIN_CACHE=$(ls -d ~/.claude/plugins/cache/plugin4ai-claudecode/p4-converter/*/ 2>/dev/null | sort -V | tail -1)
```

Read the full `dependencies` array from the plugin entry in `catalog.json`. Collect all entries, preserving their `type`.

Currently required:

| Type | Name | Required version | Use |
|------|------|-----------------|-----|
| `tool` | `qpdf` | `>=10.0.0` | Split PDF into 5-page chunks |
| `tool` | `python3` | `>=3.8.0` | Run the consolidation script |
| `tool` | `libreoffice` | `>=7.0.0` | Convert DOC/DOCX/PPT/PPTX to PDF (required only for non-PDF inputs) |

For each dependency, check by type:

| Type | How to check |
|------|-------------|
| `tool` | `which <name> 2>/dev/null && <name> --version 2>&1 \| head -1` — then verify version constraint |
| `plugin` | `ls ~/.claude/plugins/cache/plugin4ai-claudecode/<name>/ 2>/dev/null` — installed if directory has at least one entry |

---

## Step 2 — Check each dependency

```bash
# qpdf
which qpdf && qpdf --version 2>&1 | head -1

# python3
which python3 && python3 --version 2>&1 | head -1

# libreoffice
which libreoffice && libreoffice --version 2>&1 | head -1
```

Parse the version output and compare against the constraint. For `type: "plugin"` entries, only presence is checked — no version comparison.

---

## Step 3 — Print results table

Print a Markdown table with the check results:

```
| Type | Dependency  | Required  | Found      | Status |
|------|-------------|-----------|------------|--------|
| tool | qpdf        | >=10.0.0  | 11.9.1     | ✅     |
| tool | python3     | >=3.8.0   | 3.10.12    | ✅     |
| tool | libreoffice | >=7.0.0   | 7.6.4.1    | ✅     |
```

Status values:
- ✅ — installed and version constraint satisfied (or plugin present)
- ❌ — missing or version below the minimum

---

## Step 4 — Install instructions for missing tools

For each ❌ tool, show install commands for both environments:

**qpdf**

```bash
# Bash (Linux/WSL — Debian/Ubuntu)
sudo apt install qpdf

# Bash (Linux/WSL — RHEL/Fedora)
sudo dnf install qpdf

# PowerShell (Windows)
winget install qpdf
```

**python3**

```bash
# Bash (Linux/WSL — Debian/Ubuntu)
sudo apt install python3

# Bash (Linux/WSL — RHEL/Fedora)
sudo dnf install python3

# PowerShell (Windows)
winget install Python.Python.3
```

**libreoffice**

```bash
# Bash (Linux/WSL — Debian/Ubuntu)
sudo apt install libreoffice

# Bash (Linux/WSL — RHEL/Fedora)
sudo dnf install libreoffice

# PowerShell (Windows)
winget install TheDocumentFoundation.LibreOffice
```

---

## Step 5 — Final verdict

If all tools are ✅:
```
✅ All dependencies satisfied. p4-converter is ready to use.
   Run /p4-converter:any-to-md to start converting documents.
```

If any tool is ❌:
```
❌ Missing dependencies detected. Install the tools above and run /p4-converter:setup again.
```

This skill is idempotent — safe to re-run at any time.
