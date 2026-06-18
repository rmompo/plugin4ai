---
name: setup
description: Verifies that all external dependencies required by p4-core skills are installed and available. Reports status with install instructions for each missing dependency. Also invoked explicitly as /p4-core:setup.
---

# p4-core Setup

Checks that all external tools required by p4-core skills are present and reachable. Safe to re-run at any time.

---

## Step 1 — Dependencies

Currently required by p4-core skills:

| Tool | Required by | Version |
|------|------------|---------|
| `git` | `git-commit` skill | any |

---

## Step 2 — Check each tool

```bash
which git 2>/dev/null && git --version 2>&1 | head -1
```

---

## Step 3 — Print status table

```
══════════════════════════════════════════
  p4-core SETUP CHECK
══════════════════════════════════════════
```

| Tool | Required by | Found | Status |
|------|------------|-------|--------|
| `git` | `git-commit` | `git version x.y.z` | ✅ / ❌ |

- ✅ = tool found
- ❌ = tool missing

---

## Step 4 — Install instructions for missing tools

### `git`

**Debian / Ubuntu / WSL:**
```bash
sudo apt install git
```

**RHEL / Fedora:**
```bash
sudo dnf install git
```

**macOS:**
```bash
brew install git
```

**Windows (PowerShell):**
```powershell
winget install Git.Git
```

---

## Step 5 — Summary

If all tools are present:
```
✅ All p4-core dependencies satisfied. No action required.
```

If any tool is missing:
```
❌ N dependency/dependencies missing. Install the tools above and re-run /p4-core:setup.
```
