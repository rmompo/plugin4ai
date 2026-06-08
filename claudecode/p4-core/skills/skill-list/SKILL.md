---
name: skill-list
description: Lists all p4-* plugin skills installed in the current CLI, in a table with columns plugin|skill|v|enabled|ready|description. Also invoked explicitly as /p4-core:skill-list.
version: 15
allowed-tools: [Bash, Read]
---

# Skill List

Lists all p4-* plugin skills installed in the current CLI, in a Markdown table with columns `plugin | skill | v | enabled | ready | description`.

Only plugins compatible with the current CLI (e.g. claudecode) are included.

---

## Step 0 — Detectar CLI y cache base

```bash
# Claude Code
CACHE_BASE=~/.claude/plugins/cache/plugin4ai-claudecode
CATALOG=~/.p4/catalog.json
# Fallback: marketplace install path (used before ~/.p4/catalog.json is created)
[ ! -f "$CATALOG" ] && CATALOG=~/.claude/plugins/marketplaces/plugin4ai-claudecode/specs/catalog.json
```

---

## Step 1 — Enumerar plugins p4-*

```bash
ls "$CACHE_BASE" | grep "^p4-"
# Para cada plugin, tomar la versión más alta instalada
```

---

## Step 2 — Leer skills de cada plugin

Para cada plugin encontrado:

```bash
# Leer plugin.json para obtener la versión activa
cat "$CACHE_BASE/<plugin>/<version>/.claude-plugin/plugin.json"

# Leer cada SKILL.md para obtener name, version y description
cat "$CACHE_BASE/<plugin>/<version>/skills/<skill>/SKILL.md"
```

Extraer del frontmatter YAML de cada SKILL.md:
- `name` → nombre del skill (fuente primaria para identificación)
- `description` → columna **description** (primera oración antes de ". Also invoked")

**La versión del skill se lee siempre desde `catalog.json`**, no desde el frontmatter SKILL.md. El catalog es la fuente de verdad — el frontmatter puede estar desincronizado si el skill fue actualizado directamente sin pasar por `skill-update`.

```python
skill_version = catalog["plugins"][plugin]["skills"][skill_name]["version"]
```

---

## Step 3 — Determinar estado enabled

Un skill está **enabled** si su SKILL.md existe en la versión activa del plugin en cache.

Mostrar `yes` / `no`.

---

## Step 3b — Determine ready status

`ready` indicates whether the skill is **usable as-is** — either it has no external dependencies, or all of its dependencies are present.

For each skill, resolve its dependency list with the following priority:

1. **Skill-level `dependencies`** — if the skill has `dependencies` in `catalog.json` → use that list
2. **Plugin-level `dependencies`** — if the plugin has `dependencies` in `catalog.json` and the skill has none → use the plugin-level list
3. **No dependencies** — if neither has `dependencies` → skill is unconditionally ready

**Unconditional exception:** the `setup` skill always shows an empty `ready` column. It is the skill that performs the check — showing ✅/❌ there would be circular.

For each dependency in the resolved list, check by type:

| Type | How to check |
|------|-------------|
| `tool` | `which <name> 2>/dev/null` — present if exit code 0 |
| `plugin` | `ls ~/.claude/plugins/cache/plugin4ai-claudecode/<name>/ 2>/dev/null` — installed if directory has at least one entry |

- **No dependencies** → `ready` = `✅`
- **All dependencies satisfied** → `ready` = `✅`
- **Any dependency missing** → `ready` = `❌`

Version checking is not done here — only presence. Detailed version verification is the responsibility of each plugin's `setup` skill.

---

## Step 4 — Imprimir tabla

Formato de salida: **tabla Markdown** con columnas alineadas.

### Reglas de formato

- **Columna `plugin`**: mostrar `<plugin> (v<plugin-version>)` únicamente en la **primera fila** de cada plugin. En las filas siguientes del mismo plugin dejar la celda **vacía**.
- **Columna `skill`**: solo el nombre del skill, sin versión.
- **Columna `v`**: versión del skill como número entero (`9`, `2`, `10`…). Siempre presente.
- **Columna `enabled`**: `yes` / `no`.
- **Columna `ready`**: ✅ si el skill está listo para usar (sin dependencias o todas satisfechas); ❌ si alguna dependencia falta; vacío solo para el skill `setup` (excepción circular).
- **Columna `description`**: primera oración hasta ". Also invoked".

Orden de columnas: `plugin | skill | v | enabled | ready | description`

```markdown
| plugin               | skill           | v  | enabled | ready | description                                   |
|----------------------|-----------------|----|---------|-------|-----------------------------------------------|
| p4-ccvv (v1.0.15)   | export          | 7  | yes     | ✅    | Exports a CV draft to a final format          |
|                      | generate        | 14 | yes     | ✅    | Generates an adapted CV draft                 |
|                      | setup           | 15 | yes     |       | Verifies external dependencies for p4-ccvv   |
| p4-converter (v1.0.6)| any-to-md      | 4  | yes     | ❌    | Converts documents to structured Markdown     |
|                      | setup           | 6  | yes     |       | Verifies external tools for p4-converter      |
| p4-core (v1.2.15)   | git-commit      | 1  | yes     | ✅    | Enforces Conventional Commits format          |
|                      | model-behaviour | 2  | yes     | ✅    | Loads and activates P4D behavioral directives |
|                      | setup           | 14 | yes     |       | Verifies external dependencies for p4-core    |
|                      | skill-list      | 15 | yes     | ✅    | Lists all p4-* plugin skills in the current CLI |
| ...                  | ...             | .. | ...     | ...   | ...                                           |
```

Ordenar por `plugin` ASC, luego `skill` ASC.

Terminar con un pie de página:

```
**N plugins · M skills · M enabled**
```
