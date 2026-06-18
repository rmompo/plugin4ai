# Plugin Installation Guide

Plugin and skill lifecycle operations for each supported CLI. Processes vary significantly between CLIs — some are fully command-driven, others are TUI-based or require manual file management.

---

## Claude Code

### Install

From the marketplace:
```bash
claude plugin install <plugin>@<marketplace>

# Examples
claude plugin install p4-core@plugin4ai
claude plugin install p4-core@plugin4ai --scope project   # shared with the team (project-scoped)
claude plugin install p4-core@plugin4ai --scope local     # user-only (default)
```

From a local path (no marketplace):
```bash
claude plugin init <name>   # scaffolds under ~/.claude/skills/<name>/
                            # auto-discovered on next session as <name>@skills-dir
```

Add this marketplace first if not registered:
```bash
claude plugin marketplace add rmompo/plugin4ai
```

### Update

```bash
claude plugin update <plugin>@<marketplace>

# Example
claude plugin update p4-core@plugin4ai
```

### Uninstall

```bash
claude plugin uninstall <plugin>

# Uninstall and immediately clean up orphaned dependencies
claude plugin uninstall <plugin> --prune
```

Orphaned files are removed automatically after ~7 days even without `--prune`.

### Enable / Disable

```bash
claude plugin enable <plugin>
claude plugin disable <plugin>
```

Or use the interactive TUI — run `/plugin` inside a Claude Code session.

### List

```bash
claude plugin list              # shell
/plugin list                    # inside session
/plugin list --enabled          # only active plugins
/plugin list --disabled         # only inactive plugins
```

### Marketplace management

```bash
claude plugin marketplace add rmompo/plugin4ai    # register
claude plugin marketplace list                     # show registered
claude plugin marketplace update <n>               # refresh index
claude plugin marketplace remove <n>               # unregister
```

### Prune orphaned versions

```bash
claude plugin prune    # lists orphans and asks for confirmation
```

---

## GitHub Copilot CLI

### Install

From a marketplace:
```bash
copilot plugin install <plugin>@<marketplace>

# Example
copilot plugin install p4-core@plugin4ai
```

From a GitHub repo or local path:
```bash
copilot plugin install OWNER/REPO
copilot plugin install OWNER/REPO:path/to/plugin
copilot plugin install ./local/path/to/plugin
copilot plugin install https://github.com/o/r.git
```

Add this marketplace first if not registered:
```bash
copilot plugin marketplace add rmompo/plugin4ai
```

### Update

```bash
copilot plugin update <plugin>        # single plugin
copilot plugin update --all           # all plugins at once
```

### Uninstall

```bash
copilot plugin uninstall <plugin>
```

### Enable / Disable

```bash
copilot plugin enable <plugin>
copilot plugin disable <plugin>    # keeps plugin installed but inactive
```

### List

```bash
copilot plugin list
```

### Marketplace management

```bash
copilot plugin marketplace add rmompo/plugin4ai    # register
copilot plugin marketplace list                     # show registered
copilot plugin marketplace browse <marketplace>     # browse available plugins
copilot plugin marketplace remove <marketplace>     # unregister
```

---

## Antigravity CLI

### Install

```bash
agy plugin install <path-or-url>

# From local repo clone
agy plugin install ~/path/to/plugin4ai/antigravity/p4-core
agy plugin install ~/path/to/plugin4ai/antigravity/p4-plugin
agy plugin install ~/path/to/plugin4ai/antigravity/p4-antigravity
```

> **Note:** `agy plugin install` copies only `skills/`, `agents/`, `commands/`, `mcpServers/`, and `hooks/` directories. The `scripts/` directory and other custom files must be copied manually if required.

### Update

There is no `agy plugin update` command. Re-run the install command to update:

```bash
agy plugin install ~/path/to/plugin4ai/antigravity/<plugin>
```

### Uninstall

```bash
agy plugin uninstall <name>

# Or manually remove the plugin directory
rm -rf ~/.gemini/config/plugins/<plugin>/
```

### Enable / Disable

```bash
agy plugin enable <name>
agy plugin disable <name>
```

### List

```bash
agy plugin list
```

### Validate

```bash
agy plugin validate ~/path/to/plugin4ai/antigravity/<plugin>
```

### Import from Gemini CLI (migration)

```bash
agy plugin import gemini
```

### Plugin storage location

```
~/.gemini/config/plugins/<plugin>/
```

---

## Codex CLI

Plugin management in Codex is primarily **TUI-driven**. Open the plugin browser with:

```bash
codex
/plugins
```

### Install

```
codex → /plugins → browse → select plugin → Install plugin
```

### Update

```
codex → /plugins → select installed plugin → Update
```

### Uninstall

```
codex → /plugins → select installed plugin → Uninstall plugin
```

### Enable / Disable

**Via TUI:**
```
codex → /plugins → select plugin → Space   (toggles enabled/disabled)
```

**Via config file** (`~/.codex/config.toml`):
```toml
[plugins."p4-core@plugin4ai"]
enabled = false
```

Restart Codex after editing the config file.

### List

```
codex → /plugins   (shows installed and available plugins grouped by marketplace)
```

### Plugin storage location

```
~/.codex/plugins/<plugin>/
```

---

## Skills

Skills are bundled inside plugins. There is no separate install/remove command for individual skills — they are managed as part of the plugin lifecycle above.

To invoke a skill once a plugin is installed:

| CLI | Invocation |
|-----|-----------|
| Claude Code | `/<plugin>:<skill>` |
| GitHub Copilot | `/<plugin>:<skill>` |
| Antigravity CLI | `/<plugin>:<skill>` |
| Codex CLI | `/<plugin>:<skill>` |

---

## Quick reference

| Operation | Claude Code | GitHub Copilot | Antigravity CLI | Codex CLI |
|-----------|------------|----------------|-----------------|-----------|
| Install | `claude plugin install <p>@<mp>` | `copilot plugin install <p>@<mp>` | `agy plugin install <path>` | TUI: `/plugins` |
| Update | `claude plugin update <p>@<mp>` | `copilot plugin update <p>` | reinstall via `agy plugin install` | TUI: `/plugins` |
| Uninstall | `claude plugin uninstall <p>` | `copilot plugin uninstall <p>` | `agy plugin uninstall <p>` | TUI: `/plugins` |
| Enable | `claude plugin enable <p>` | `copilot plugin enable <p>` | `agy plugin enable <p>` | TUI: Space / `config.toml` |
| Disable | `claude plugin disable <p>` | `copilot plugin disable <p>` | `agy plugin disable <p>` | TUI: Space / `config.toml` |
| List | `claude plugin list` | `copilot plugin list` | `agy plugin list` | TUI: `/plugins` |
