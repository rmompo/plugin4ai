# p4-plugin

Plugin lifecycle management for the plugin4ai Claude Code marketplace. Tools to scaffold, update and maintain plugins.

## Skills

| Skill | Invocation | What it does |
|-------|-----------|--------------|
| `create` | `/p4-plugin:create <name> [skills...]` | Scaffolds a complete new plugin with all required files and registry entries |
| `update` | `/p4-plugin:update <plugin>` | Updates plugin metadata (description, status, ports) and propagates changes to all catalogs and the CLI cache |
| `remove` | `/p4-plugin:remove <plugin>` | Removes a plugin and all its files from the repo, every catalog, and the CLI cache — requires explicit confirmation |
| `skill-add` | `/p4-plugin:skill-add <plugin> <skill>` | Adds a new skill to an existing plugin, bumps Z versioning, creates the SKILL.md, and syncs the CLI cache |
| `skill-update` | `/p4-plugin:skill-update <plugin> <skill>` | Bumps the version of an existing skill, records the changelog entry in catalog.json, and syncs the CLI cache |
| `skill-remove` | `/p4-plugin:skill-remove <plugin> <skill>` | Removes a skill from a plugin — deletes SKILL.md and updates catalog.json (Z does not decrease) |
| `skill-doctor` | `/p4-plugin:skill-doctor [plugin] [skill]` | Audits plugin skills for version mismatches, frontmatter issues, allowed-tools gaps, and structural defects — offers to auto-fix eligible findings |
| `doc-doctor` | `/p4-plugin:doc-doctor [plugin]` | Audits documentation completeness and language across specs, MARKETPLACE.md, and README.md — reports findings and offers to auto-generate missing content |
| `sanitize` | `/p4-plugin:sanitize [plugin] [skill]` | Scans plugin and skill files for sensitive information and offers to anonymize it |

## Installation

```bash
claude plugins marketplace add rmompo/plugin4ai
claude plugins install p4-plugin
```

## Notes

- Encodes the full plugin creation checklist to avoid common mistakes.
- Automatically updates both registry files (`marketplace.json` and `MARKETPLACE.md`).
