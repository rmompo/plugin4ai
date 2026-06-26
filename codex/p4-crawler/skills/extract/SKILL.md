---
name: extract
description: Crawls a website (static/curl mode only), filters content by topic, downloads pages and attachments, and generates a structured Markdown index.
---

# p4-crawler Extract

Orchestrates the full documentation extraction pipeline: configure → login (optional) → crawl → dedup → filter → download → generate.

> **Degraded port note**: This port runs in **static (curl-only) mode**. Playwright / SPA rendering is not supported. If the target site requires JavaScript rendering, the extracted content may be incomplete.

```bash
SCRIPTS=$(ls -d ~/.codex/plugins/cache/plugin4ai-codex/p4-crawler/*/ 2>/dev/null | sort -V | tail -1)scripts
```

---

## Phase 1 — Configure

Ask the user (via plain text) to provide the following configuration.

**Batch 1:**
1. Start URL (e.g. `https://docs.example.com/`)
2. Output folder (default: `./generated/scrapp/<YYYYMMDD-HHMMSS>/`)
3. Max crawl depth (default: `3`)
4. Render mode input by user: any value is accepted BUT this port always uses **`static`** internally
   - If user requests `playwright` or `auto` → warn: "⚠️ Playwright not supported in this port — using static (curl) mode instead."

**Batch 2 (if needed):**
1. Login required? (`yes` / `no`)
   - If yes: login URL, login type (`joomla` / `form` / `basic`)
2. Topic for filtering (one line, e.g. "API endpoints")
3. Keywords for filtering (comma-separated)
4. Additional filters: language, attachment types, date range (optional)

**Credential handling (if login required):**
- Ask the user (via plain text) for username and password.
- Store in memory as `session_credentials` — **never write to disk**
- Use only for login phase; discard after phase 2

Generate `scrapper-config.json` at the output folder (always with `"mode": "static"`, no credentials):

```json
{
  "metadata": {"version": "2.1", "created": "<timestamp>"},
  "crawl": {
    "start_url": "<url>",
    "base_domain": "<domain>",
    "max_depth": "<depth>",
    "pause_ms": 500,
    "save_interval": 50
  },
  "spa": {"mode": "static"},
  "auth": {"login_required": "<true|false>", "login_url": "<url>", "login_type": "<type>"},
  "filter": {"topic": "<topic>", "keywords": ["<kw1>", "<kw2>"]},
  "output": {"folder": "<output_path>", "main_file": "INDEX.md", "mode": "multi"},
  "session": {"status": "configured", "crawl": null, "filter": null, "generate": null}
}
```

Print: `✅ Configuration saved → <output_path>/scrapper-config.json`

---

## Phase 2 — Login (skip if auth.login_required = false)

Extract CSRF token from login page and POST credentials via curl:

```bash
# Fetch login page and extract CSRF token
curl -s -c <output>/scrapper-cookies.txt "<login_url>" | grep -oP 'name="[a-f0-9]{32}" value="1"' | head -1

# POST credentials
curl -s -c <output>/scrapper-cookies.txt -b <output>/scrapper-cookies.txt \
  -d "username=<u>&passwd=<p>&<csrf_field>=1&option=com_users&task=user.login&return=aW5kZXgucGhw" \
  "<login_url>"

# Verify session
curl -s -b <output>/scrapper-cookies.txt -o /dev/null -w "%{http_code}" "<start_url>"
```

- `scrapper-cookies.txt` is scoped to `local-gitignore`
- Credentials stay in-session memory only — clear after this phase
- If verification fails → print error and stop

Print: `✅ Session authenticated — cookies saved`

---

## Phase 3 — Crawl

```bash
python3 "$SCRIPTS/crawl.py" "<output>/scrapper-config.json"
```

Produces:
- `<output>/web-map.json` — JSONL with all discovered nodes
- `<output>/web-map-excluded.json` — filtered-out nodes
- `<output>/web-map-meta.json` — crawl statistics

Print progress. On completion: `✅ Crawl complete — <N> nodes discovered`

---

## Phase 4 — Deduplication

```bash
python3 "$SCRIPTS/dedup.py" "<output>/scrapper-config.json"
```

Removes duplicate nodes. Print: `✅ Dedup complete — <N> duplicates removed`

---

## Phase 5 — Filter

```bash
python3 "$SCRIPTS/filter.py" "<output>/scrapper-config.json"
```

Produces `<output>/web-map-filtered.json`. Print: `✅ Filter complete — <N> nodes kept / <M> excluded`

---

## Phase 6 — Download

```bash
python3 "$SCRIPTS/download.py" "<output>/scrapper-config.json"
```

Downloads all filtered pages and attachments. Converts HTML to Markdown. Saves to:
- `<output>/downloads/pages/*.md`
- `<output>/downloads/files/*.md`

Print: `✅ Download complete — <N> pages, <M> files`

---

## Phase 7 — Generate

```bash
python3 "$SCRIPTS/generate.py" "<output>/scrapper-config.json"
```

Produces `<output>/INDEX.md`. Print: `✅ INDEX.md generated`

---

## Phase 8 — Summary

```
══════════════════════════════════════════
  p4-crawler EXTRACT COMPLETE
══════════════════════════════════════════

  Output:  <output_path>/
  Index:   <output_path>/INDEX.md
  Pages:   <N>
  Files:   <M>
  Mode:    static (curl-only)
  Nodes:   <K> crawled · <F> filtered · <D> downloaded
══════════════════════════════════════════
```

---

## Error Handling

- If any phase script fails → print the error and ask the user whether to retry or abort
- If `python3` not found → stop with: "❌ python3 is required to run crawl scripts. Install it and retry."
- If login verification fails (HTTP ≠ 200/302) → print error with response code and stop before crawl
- Sessions are resumable: re-running extract with an existing output folder resumes from the last completed phase (detected from `session.status` in `scrapper-config.json`)
