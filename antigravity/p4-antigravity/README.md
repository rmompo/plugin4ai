# p4-antigravity

Plugin visual para Antigravity CLI (`agy`). Proporciona un statusline powerline-style con información de sesión en tiempo real.

## Estructura

```text
p4-antigravity/
├── plugin.json                  # Manifiesto del plugin
├── README.md
├── scripts/
│   └── statusline.sh            # Script de renderizado del statusbar
└── skills/
    └── statusline/
        └── SKILL.md             # Metadatos y documentación del skill
```

## Formato de la barra

```
 ⌂ ~/proyecto   ⎇ main   ✦ Gemini 3.5 Flash   CX12% SN5% WK88%
```

- **Segmento 1** `⌂ pwd` — fondo amarillo brillante, texto negro (reverse)
- **Segmento 2** `⎇ branch` — fondo cyan brillante, texto negro (reverse)
- **Segmento 3** `✦ model` — fondo magenta brillante, texto negro (reverse)
- **Segmento 4** `CX SN WK` — etiquetas en blanco, valores coloreados por umbral (solo si el CLI provee los datos)

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/rmompo/plugin4ai.git

# 2. Instalar el plugin
agy plugin install ./plugin4ai/antigravity/p4-antigravity

# 3. Configurar settings.json
```

Añadir a `~/.gemini/antigravity-cli/settings.json`:

```json
"statusLine": {
  "type": "command",
  "command": "~/.gemini/antigravity-cli/plugins/p4-antigravity/scripts/statusline.sh"
}
```

## Dependencias

- `bash` ≥ 4.0
- `python3` (para parsear JSON del payload)
- `git` (para leer la rama actual)
- Terminal con soporte ANSI y Nerd Fonts (para los símbolos `⌂ ⎇ ✦`)
