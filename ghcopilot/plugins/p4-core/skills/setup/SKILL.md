---
name: setup
description: Verifies that all external dependencies (tools and plugins) required by p4-core skills are installed and available. Reports status with install instructions for each missing dependency. Also invoked explicitly as /p4-core:setup.
version: 14
allowed-tools: [Bash]
---

# p4-core Setup

Checks that all external tools required by p4-core skills are present and reachable. Safe to re-run at any time.

---

## Step 0 — Install / update ~/.p4/catalog.json

Copy the latest `catalog.json` from the marketplace to the global user path. This is idempotent — safe to re-run.

```bash
_src=$(find ~/.ghcopilot/plugins/marketplaces -path "*/plugin4ai*/specs/catalog.json" 2>/dev/null | head -1)
if [ -n "$_src" ]; then
  mkdir -p ~/.p4
  cp "$_src" ~/.p4/catalog.json
  echo "✅ ~/.p4/catalog.json installed from: $_src"
else
  echo "⚠️  Marketplace catalog not found — add the marketplace first:"
  echo "   gh copilot extension add rmompo/plugin4ai"
fi
```

---

## Step 1 — Read requirements from catalog

```bash
CATALOG=~/.p4/catalog.json
# Fallback: marketplace install path (used before ~/.p4/catalog.json is created)
[ ! -f "$CATALOG" ] && CATALOG=~/.ghcopilot/plugins/marketplaces/plugin4ai-claudecode/specs/catalog.json
```

Read `catalog["plugins"]["p4-core"]["dependencies"]` and the `dependencies` of each skill entry for p4-core. Collect the full deduplicated list, preserving the `type` field for each entry.

Currently required:

| Type | Name | Required by | Version constraint |
|------|------|------------|-------------------|
| `tool` | `git` | `git-commit` skill | `*` (any) |

---

## Step 2 — Check each dependency

For each dependency, run the appropriate check based on `type`:

| Type | How to check |
|------|-------------|
| `tool` | `which <name> 2>/dev/null && <name> --version 2>&1 \| head -1` |
| `plugin` | `ls ~/.ghcopilot/plugins/cache/<name>/ 2>/dev/null` — installed if directory has at least one entry |

For `type: "tool"`, also verify the version constraint against the `version` field.

---

## Step 3 — Print status table

```
══════════════════════════════════════════
  p4-core SETUP CHECK
══════════════════════════════════════════
```

| Type | Dependency | Required by | Required | Found | Status |
|------|------------|------------|----------|-------|--------|
| tool | `git` | `git-commit` | `*` | `git version 2.39.2` | ✅ |

- ✅ = dependency found and version constraint satisfied
- ❌ = missing or version below minimum

---

## Step 4 — Install instructions for missing tools

For each ❌ dependency, print install commands:

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
✅ ~/.p4/catalog.json installed.
✅ All p4-core dependencies satisfied. No action required.
```

If any tool is missing:
```
✅ ~/.p4/catalog.json installed.
❌ N dependency/dependencies missing. Install the tools above and re-run /p4-core:setup.
```
