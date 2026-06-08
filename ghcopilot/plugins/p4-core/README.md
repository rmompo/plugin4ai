# p4-core

Essential productivity skills for GitHub Copilot CLI that improve day-to-day development workflow.

## Skills

### 🔀 `model-routing`
Automatically guides model selection based on task complexity:

| Tier | Best for |
|------|----------|
| **Lightweight** | Quick lookups, file search, simple formatting |
| **Standard** | General development, refactoring, PR reviews |
| **Advanced** | Architecture design, complex debugging, critical decisions |

This skill activates automatically when Copilot detects task complexity signals, and explains its routing decision when relevant.

---

### 📝 `commit`
Enforces [Conventional Commits](https://www.conventionalcommits.org/) format on every commit.

Activates automatically whenever Copilot is about to propose or execute a `git commit`. Ensures:
- Correct type (`feat`, `fix`, `docs`, `refactor`, etc.)
- Proper scope notation
- Subject line ≤72 chars in imperative mood
- Breaking changes properly flagged with `!` and `BREAKING CHANGE:` footer
- Issue references in footer

**Example output:**
```
feat(auth): add OAuth2 login with Google provider

Implements social login flow using the Google OAuth2 provider.
Token refresh is handled automatically via the existing session middleware.

Closes #87
```

## Installation

```bash
# Add the marketplace to GitHub Copilot CLI
gh copilot plugins marketplace add https://github.com/rmompo/plugin4ai/tree/main/ghcopilot

# Then install the plugin
gh copilot plugins install p4-core
```

## Port

This is the **GitHub Copilot CLI** port of the `p4-core` plugin.  
See `../../claudecode/p4-core/` for the Claude Code adaptation.
