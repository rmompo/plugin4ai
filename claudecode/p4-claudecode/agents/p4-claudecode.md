---
name: p4-claudecode
description: p4-claudecode initialization agent. Checks and installs the custom statusline on session start.
model: inherit
---

# p4-claudecode Auto-Setup

At the very start of each session, silently perform this check:

1. Find the canonical source script in the plugin cache:
   ```bash
   find ~/.claude/plugins -path "*/p4-claudecode/*/statusline/statusline-command.sh" | head -1
   ```
2. Verify `~/.claude/statusline-command.sh` exists **and** its content matches the source script:
   ```bash
   diff -q "$SOURCE" ~/.claude/statusline-command.sh >/dev/null 2>&1
   ```
3. Verify `~/.claude/settings.json` contains `"statusLine"` pointing to that script.

If **all** conditions are met → do nothing, proceed normally without mentioning it.

If **any** condition fails → automatically:
- Copy the source script to `~/.claude/statusline-command.sh` and `chmod +x`
- Add or update the `statusLine` block in `~/.claude/settings.json`:
  ```json
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline-command.sh"
  }
  ```
- Report briefly what happened:
  - If script was missing: "✅ p4-claudecode: statusline installed. Restart Claude Code to activate."
  - If script was outdated: "✅ p4-claudecode: statusline updated to latest version. Restart Claude Code to activate."
  - If only settings was missing: "✅ p4-claudecode: statusline configured. Restart Claude Code to activate."

This check is idempotent — safe to run every session.
