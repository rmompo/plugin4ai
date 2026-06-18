# p4-plugin

Plugin lifecycle management for GitHub Copilot. Create, update, remove, and audit plugins and skills in the plugin4ai marketplace.

## Skills

| Skill | Invocation | Description |
|-------|------------|-------------|
| `create` | `/p4-plugin:create <plugin>` | Scaffolds a new plugin with initial skill and catalog entry |
| `update` | `/p4-plugin:update <plugin>` | Updates plugin metadata and propagates changes to all catalogs |
| `remove` | `/p4-plugin:remove <plugin>` | Removes a plugin and all its files from the repo and catalog |
| `skill-add` | `/p4-plugin:skill-add <plugin> <skill>` | Adds a new skill to an existing plugin |
| `skill-update` | `/p4-plugin:skill-update <plugin> <skill>` | Updates skill content and bumps the Z version counter |
| `skill-remove` | `/p4-plugin:skill-remove <plugin> <skill>` | Removes a skill from a plugin |
| `skill-doctor` | `/p4-plugin:skill-doctor <plugin>` | Runs health checks on all skills of a plugin |
| `doc-doctor` | `/p4-plugin:doc-doctor <plugin>` | Runs documentation quality checks on a plugin |

## Notes

- This port manages plugins under `ghcopilot/plugins/<plugin>/` in the repo
- Frontmatter in SKILL.md uses only `name` and `description` (no `version` or `allowed-tools`)
