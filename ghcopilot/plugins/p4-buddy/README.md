# p4-buddy — GitHub Copilot

Company-specific skills for GitHub Copilot.

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `gcomp` | `/p4-buddy:gcomp [hint]` | Generates a ready-to-paste `<hr-platform>` mission report from the active project or a user hint |

---

## Usage

```
/p4-buddy:gcomp
```
Auto-infers all fields from the active workspace (git log, README, file structure).

```
/p4-buddy:gcomp <project-hint>
```
Uses the hint as the primary source, complemented with workspace context.

---

## Notes

- Designed for `<company>` employees using the `<hr-platform>` competency management platform.
- Technical competencies are validated against the official `<hr-platform>` catalog.
- Output is a ready-to-paste mission report — no automatic submission.
