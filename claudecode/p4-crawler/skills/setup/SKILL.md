---
name: setup
description: Verifies that all external dependencies required by p4-crawler are installed — system tools (python3, curl) and pip packages (beautifulsoup4, html2text). Reports status with install instructions for each missing dependency. Also invoked explicitly as /p4-crawler:setup.
version: 1
allowed-tools: [Bash]
---

# p4-crawler Setup

Verifies that all required tools and Python packages are available. Safe to re-run at any time.

---

## Step 1 — Read system dependencies from catalog

```bash
CATALOG=~/.p4/catalog.json
# Fallback: marketplace install path (used before ~/.p4/catalog.json is created)
[ ! -f "$CATALOG" ] && CATALOG=~/.claude/plugins/marketplaces/plugin4ai-claudecode/specs/catalog.json
```

Read the full `dependencies` array for p4-crawler from `catalog.json`. Currently required:

| Type | Name | Required |
|------|------|----------|
| `tool` | `python3` | `>=3.8.0` |
| `tool` | `curl` | `*` |

For each dependency, check by type:

| Type | How to check |
|------|-------------|
| `tool` | `which <name> 2>/dev/null && <name> --version 2>&1 \| head -1` — then verify version constraint |
| `plugin` | `ls ~/.claude/plugins/cache/plugin4ai-claudecode/<name>/ 2>/dev/null` — installed if directory has at least one entry |

```bash
which python3 && python3 --version 2>&1
which curl    && curl --version 2>&1 | head -1
```

---

## Step 2 — Check pip packages

These packages are required at runtime but are not system binaries — checked separately:

```bash
python3 -c "import bs4; print(bs4.__version__)"     2>/dev/null
python3 -c "import html2text; print(html2text.__version__)" 2>/dev/null
```

| Package | Required | How to check |
|---------|----------|-------------|
| `beautifulsoup4` | required | `import bs4` |
| `html2text` | required | `import html2text` |

---

## Step 3 — Check optional: playwright (SPA mode)

```bash
python3 -m playwright --version 2>/dev/null
```

Playwright is **optional** — only needed for SPA sites (Angular, React, Storybook). Static sites use `curl` only.

---

## Step 4 — Print unified status table

```
══════════════════════════════════════════
  p4-crawler SETUP CHECK
══════════════════════════════════════════
```

System tools (from catalog):

| Type | Dependency | Required | Found | Status |
|------|------------|----------|-------|--------|
| tool | python3 | >=3.8.0 | 3.11.2 | ✅ |
| tool | curl | * | 7.88.1 | ✅ |

Pip packages:

| Package | Found | Status |
|---------|-------|--------|
| beautifulsoup4 | 4.12.2 | ✅ |
| html2text | 2020.1.16 | ✅ |

Optional:

| Component | Found | Status |
|-----------|-------|--------|
| playwright | 1.42.0 | ✅ (SPA mode available) |

---

## Step 5 — Install instructions for each ❌

### python3 (if missing)

**Bash (Linux/WSL):**
```bash
sudo apt install python3
```

**PowerShell (Windows):**
```powershell
winget install Python.Python.3
```

### curl (if missing)

**Bash (Linux/WSL):**
```bash
sudo apt install curl
```

**PowerShell (Windows):**
```powershell
winget install cURL.cURL
```

### beautifulsoup4 (if missing)

```bash
pip install beautifulsoup4
```

### html2text (if missing)

```bash
pip install html2text
```

### playwright (if missing — optional)

```bash
pip install playwright && playwright install chromium
```

---

## Step 6 — Final verdict

If all required dependencies ✅:
```
✅ p4-crawler is ready. Run /p4-crawler:extract to start a crawl session.
   Note: playwright not found — SPA mode unavailable (static sites work fine).
```

If any required dependency ❌:
```
⚠️  Install missing dependencies before using p4-crawler.
```
