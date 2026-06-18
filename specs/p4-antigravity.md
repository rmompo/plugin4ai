# p4-antigravity

**Status:** beta  
**Version:** 1.0.0  
**CLI:** Antigravity CLI/TUI (exclusive)

---

## Purpose

Provides a powerline-style status bar for Antigravity CLI/TUI (`agy`) that renders real-time session information: working directory, git branch, active model name, and color-coded usage metrics.

---

## Ports

| CLI/TUI | Status |
|-----|--------|
| Antigravity CLI/TUI | `beta` |
| Claude Code CLI/TUI | `not-applicable` |
| GitHub Copilot CLI/TUI | `not-applicable` |
| Codex CLI/TUI | `not-applicable` |

---

## Statusline format

```
 ⌂ ~/project   ⎇ main   ✦ Antigravity 2.0 Flash   CX12% SN5% WK88%
```

| Segment | Symbol | Background | Text |
|---------|--------|------------|------|
| Directory | `⌂` | Bright yellow | Black |
| Git branch | `⎇` | Bright cyan | Black |
| Model | `✦` | Bright magenta | Black |
| Usage (if available) | `CX` `SN` `WK` | Normal | Green / Yellow / Red |

### Usage thresholds

- 🟢 Green: `<= 40%`
- 🟡 Yellow: `40% < x <= 75%`
- 🔴 Red: `> 75%`

---

## Skills

| Skill | Invocation | Description |
|-------|------------|-------------|
| `statusline` | automatic (registered as `statusLine` command) | Renders the powerline-style status bar. Reads JSON from stdin, emits ANSI-colored output to stdout. |

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/rmompo/plugin4ai.git

# 2. Install the plugin
agy plugin install ./plugin4ai/antigravity/p4-antigravity

# 3. Register as statusLine in ~/.gemini/config/settings.json
```

```json
"statusLine": {
  "type": "command",
  "command": "~/.gemini/config/plugins/p4-antigravity/scripts/statusline.sh"
}
```

---

## Dependencies

| Type | Name | Version |
|------|------|---------|
| tool | `bash` | >= 4.0 |
| tool | `python3` | >= 3.0.0 |
| tool | `git` | * |
| runtime | Terminal with ANSI + Nerd Fonts support | — |

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.0.0 | Initial release — statusline skill |
