---
name: git-sanitize
description: Ensures the current git repo has correct line-ending hygiene. At session start, silently checks for .gitattributes with eol=lf and CRLF-contaminated tracked files. Reports and fixes issues. Also invoked explicitly as /p4-core:git-sanitize.
---

# git-sanitize

Ensures every git repo has `.gitattributes` enforcing LF line endings and that no tracked file carries CRLF contamination.

**When triggered at session start**: silent if everything is clean; acts only when issues are found.  
**When invoked explicitly** (`/p4-core:git-sanitize`): always prints a full status report.

---

## Step 1 — Detect git repo

```bash
git rev-parse --show-toplevel 2>/dev/null
```

If the command fails (not a git repo): **exit silently**. No output.

Store the result as `REPO_ROOT`.

---

## Step 2 — Check .gitattributes

```bash
cat "$REPO_ROOT/.gitattributes" 2>/dev/null
```

The file is considered **compliant** if it contains a line matching:
```
* text=auto eol=lf
```

### If missing or non-compliant

Create or update `$REPO_ROOT/.gitattributes`. If the file exists, prepend the rule at the top; if it does not exist, create it with this content:

```
# Force LF line endings for all text files, regardless of OS or core.autocrlf
* text=auto eol=lf

# Binary files — never touch line endings
*.png   binary
*.jpg   binary
*.jpeg  binary
*.gif   binary
*.ico   binary
*.woff  binary
*.woff2 binary
*.ttf   binary
*.eot   binary
*.vsix  binary
*.zip   binary
*.tar   binary
*.gz    binary
*.7z    binary
*.pdf   binary
```

After writing, print:
```
✅ git-sanitize: .gitattributes created/updated — eol=lf enforced
```

---

## Step 3 — Detect CRLF-contaminated tracked files

```bash
git -C "$REPO_ROOT" ls-files \
  | xargs -I{} sh -c 'file "$REPO_ROOT/{}" 2>/dev/null | grep -q CRLF && echo "{}"'
```

Collect all matching paths as `CRLF_FILES`.

### If no files found

**Exit silently** (session-start mode) or print `✅ git-sanitize: no CRLF files found` (explicit invocation).

### If files found

Print a report:

```
⚠️  git-sanitize: N tracked file(s) with CRLF line endings found:

  client/tools/sidecar/main.py
  client/vscode/esbuild.config.js
  ...
```

Ask the user: `"N tracked file(s) have CRLF line endings. Normalize all to LF now? [yes/no]"`

---

## Step 4 — Normalize (if confirmed)

For each file in `CRLF_FILES`:

```bash
sed -i 's/\r$//' "$REPO_ROOT/$file"
```

Then stage only those files:

```bash
git -C "$REPO_ROOT" add -- $CRLF_FILES
```

Print:
```
✅ git-sanitize: N file(s) normalized and staged.

Next step: commit the normalization
  git commit -m "chore(git): normalize CRLF to LF across tracked files"
```

---

## Step 5 — Summary (explicit invocation only)

When invoked explicitly, always print a closing summary:

```
══════════════════════════════════════════
  git-sanitize COMPLETE
══════════════════════════════════════════
  Repo:              <REPO_ROOT>
  .gitattributes:    ✅ compliant  |  ⚠️ created
  CRLF files found:  N
  CRLF files fixed:  N
══════════════════════════════════════════
```
