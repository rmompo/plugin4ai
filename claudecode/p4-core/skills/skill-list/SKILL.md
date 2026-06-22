---
name: skill-list
description: Lists all p4-* plugin skills installed in the current CLI, in a table with columns plugin|skill|v|ready|description. Also invoked explicitly as /p4-core:skill-list.
version: 22
allowed-tools: [Bash, Read]
---

# Skill List

Lists all p4-* plugin skills installed in the current CLI, in a Markdown table with columns `plugin | skill | v | ready | description`.

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

## Step 3 — Determinar estado enabled (indicador visual)

El estado enabled se indica con un emoji prefijado en las celdas `plugin` y `skill`, **no** como columna separada:

- **Plugin enabled** → su directorio existe en cache con al menos una versión instalada → prefijo 🟢 en la celda `plugin`.
- **Plugin disabled** → no existe en cache → prefijo 🔴 en la celda `plugin`.
- **Skill enabled** → su SKILL.md existe en la versión activa del plugin en cache → prefijo 🟢 en la celda `skill`.
- **Skill disabled** → SKILL.md no existe → prefijo 🔴 en la celda `skill`.

No hay columna `enabled` en la tabla.

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

Formato de salida: **tabla con caracteres de caja Unicode**, envuelta en un bloque de código ` ```text ` para preservar el alineado monoespaciado.

---

### 4.1 — Anchos de columna

- Columnas `plugin`, `skill`, `v`, `ready`: ancho dinámico = `max(ancho_header, contenido_más_largo) + 2` (1 espacio de padding a cada lado).
- Columna `description`: ancho **fijo de 62** (60 chars de contenido + 2 de padding).
- **Emojis** 🟢 🔴 ✅ ❌ ocupan **2 columnas de terminal**. Al calcular el relleno de espacios, compensar restando 1 por cada emoji presente en la celda.

---

### 4.2 — Tipos de línea separadora

Hay **dos tipos** de separador, nunca uno solo:

| Tipo | Cuándo | Estructura |
|------|--------|-----------|
| **Completo** | Entre plugins / tras cabecera / borde superior e inferior | `├─────┼─────┼─────┼─────┼─────┤` (cruza todas las columnas) |
| **Parcial** | Entre skills del mismo plugin | `│ {plugin_cell} ├─────┼─────┼─────┼─────┤` (la columna `plugin` continúa con `│`, los demás con `├─┼─┤`) |

En el separador parcial, la celda `plugin` muestra el contenido que le corresponde en esa línea física (ver §4.4).

---

### 4.3 — Alineación

- **Cabeceras**: **centradas** dentro de cada columna.
- **Datos**: **alineados a la izquierda** en todas las columnas.

---

### 4.4 — Columna `plugin` — siempre 2 líneas físicas de contenido

La columna `plugin` tiene **exactamente 2 líneas de contenido** por grupo de plugin, contando en líneas físicas (incluyendo separadores parciales y líneas de wrap de description):

| Línea física global dentro del grupo | Contenido en columna `plugin` |
|--------------------------------------|-------------------------------|
| 0                                    | `🟢 {plugin_name}` o `🔴 {plugin_name}` |
| 1                                    | `(v{plugin_version})` (ej. `(v1.2.18)`) |
| ≥ 2                                  | vacío |

Las líneas de separadores parciales y las líneas de wrap **cuentan** como líneas físicas para este índice. La columna `plugin` nunca se repite para el mismo plugin.

---

### 4.5 — Reglas por columna

- **`plugin`**: ver §4.4. No se repite entre skills del mismo grupo.
- **`skill`**: `🟢 {skill_name}` o `🔴 {skill_name}`. Solo en la primera línea física del skill.
- **`v`**: versión entera del skill (`7`, `14`…). Solo en la primera línea física del skill.
- **`ready`**: `✅` / `❌` según dependencias; **vacío** para el skill `setup` (excepción circular). Solo en la primera línea física del skill.
- **`description`**: primera oración completa hasta ". Also invoked", sin truncar, sin ellipsis. Si supera 60 chars se hace **wrap** en líneas adicionales; las demás columnas quedan vacías en esas líneas extra.

Orden de columnas: `plugin │ skill │ v │ ready │ description`

---

### 4.6 — Ejemplo de salida

```text
┌────────────────────────┬──────────────────────┬────┬───────┬──────────────────────────────────────────────────────────────┐
│        plugin          │        skill         │ v  │ ready │                         description                          │
├────────────────────────┼──────────────────────┼────┼───────┼──────────────────────────────────────────────────────────────┤
│ 🟢 p4-ccvv            │ 🟢 export            │ 7  │ ✅    │ Exports a CV draft to a final format                         │
│ (v1.0.15)             ├──────────────────────┼────┼───────┼──────────────────────────────────────────────────────────────┤
│                        │ 🟢 generate          │ 14 │ ✅    │ Generates an adapted CV draft                                │
│                        ├──────────────────────┼────┼───────┼──────────────────────────────────────────────────────────────┤
│                        │ 🟢 setup             │ 15 │       │ Verifies external dependencies for p4-ccvv                   │
├────────────────────────┼──────────────────────┼────┼───────┼──────────────────────────────────────────────────────────────┤
│ 🟢 p4-core            │ 🟢 git-commit         │ 1  │ ✅    │ Enforces Conventional Commits format, translates to English, │
│ (v1.2.18)             │                      │    │       │ and strips co-authorship lines                               │
│                        ├──────────────────────┼────┼───────┼──────────────────────────────────────────────────────────────┤
│                        │ 🟢 model-behaviour   │ 2  │ ✅    │ Loads and activates P4D behavioral directives for the        │
│                        │                      │    │       │ session                                                      │
│                        ├──────────────────────┼────┼───────┼──────────────────────────────────────────────────────────────┤
│                        │ 🟢 setup             │ 14 │       │ Verifies external dependencies required by p4-core skills    │
│                        ├──────────────────────┼────┼───────┼──────────────────────────────────────────────────────────────┤
│                        │ 🟢 skill-list        │ 21 │ ✅    │ Lists all p4-* plugin skills installed in the current CLI    │
└────────────────────────┴──────────────────────┴────┴───────┴──────────────────────────────────────────────────────────────┘
```

Ordenar por `plugin` ASC, luego `skill` ASC dentro de cada grupo.

---

### 4.7 — Pie de página

Imprimir inmediatamente después de la tabla (fuera del bloque de código):

```
**N plugins · M skills · M enabled**
```
