# Plugin Installation Guide

Plugin and skill lifecycle operations for Claude Code.

---

## Plugins

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

## Skills

Skills are bundled inside plugins. There is no separate install/remove command for individual skills — they are managed as part of the plugin lifecycle above.

Once a plugin is installed, invoke a skill with:

```
/<plugin>:<skill>
```

---

## Quick reference

| Operation | Command |
|-----------|---------|
| Install | `claude plugin install <p>@<mp>` |
| Update | `claude plugin update <p>@<mp>` |
| Uninstall | `claude plugin uninstall <p>` |
| Enable | `claude plugin enable <p>` |
| Disable | `claude plugin disable <p>` |
| List | `claude plugin list` |
