---
name: statusline
description: One-time setup skill for p4-claudecode. Installs the statusline script and activates it in ~/.claude/settings.json. Invoke once after installing the plugin. Also invoked explicitly as /p4-claudecode:statusline.
version: 2
argument-hint: []
allowed-tools: [Bash, Read, Edit]
---

# p4-claudecode Setup

Installs the custom statusline for Claude Code. Run once after installing the plugin.

## What it does

1. Copies `statusline-command.sh` from the plugin to `~/.claude/`
2. Makes it executable
3. Patches `~/.claude/settings.json` to activate it

---

## Step 1 — Locate the script

The script is bundled at `<plugin-root>/statusline/statusline-command.sh`.

Find it with:

```bash
find ~/.claude/plugins -name "statusline-command.sh" 2>/dev/null | grep p4-claudecode | head -1
```

---

## Step 2 — Install the script

```bash
cp "<plugin-root>/statusline/statusline-command.sh" "$HOME/.claude/statusline-command.sh"
chmod +x "$HOME/.claude/statusline-command.sh"
```

Skip if the file already exists and is identical.

---

## Step 3 — Patch settings.json

Read `~/.claude/settings.json` and add or update the `statusLine` block:

```json
"statusLine": {
  "type": "command",
  "command": "bash ~/.claude/statusline-command.sh"
}
```

- Already configured with this exact command → skip.
- Different value already set → ask the user before overwriting.
- Key absent → add it.

Use the Edit tool for a minimal patch, not a full rewrite.

---

## Step 4 — Confirm

| Step | Result |
|------|--------|
| Script | ✅ `~/.claude/statusline-command.sh` |
| settings.json | ✅ `statusLine` activated |

> 💡 Restart Claude Code if the statusline does not appear immediately.

---

## Idempotent

Safe to run multiple times — skips steps that are already done.

---

## Expected result

```
[~/your/project] · [⎇ main] · Sonnet 4.6 · cx:16% sn:88% wk:8%
```

| Segment | Color | Description |
|---------|-------|-------------|
| `[~/path]` | 🟡 Yellow | Project directory, `~`-collapsed |
| `[⎇ branch]` | 🔵 Cyan | Current git branch |
| `Model` | 🟠 Orange | Active model name |
| `cx:%` | 🟢/🟡/🔴 | Context window usage |
| `sn:%` | 🟢/🟡/🔴 | 5-hour session rate limit |
| `wk:%` | 🟢/🟡/🔴 | 7-day weekly rate limit |
