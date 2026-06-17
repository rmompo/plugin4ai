---
name: "statusline"
description: "Renders a powerline-style statusbar for Antigravity CLI with project directory, git branch, model name, and optional usage metrics."
version: "1.0.0"
---

# Statusline — Puerto Antigravity

Este skill gestiona la configuración y activación del script de statusline personalizado para Antigravity CLI.

## Qué hace

El script `scripts/statusline.sh` recibe un payload JSON de Antigravity CLI vía `stdin` cada vez que cambia el estado de la sesión, y emite por `stdout` una barra de estado con colores ANSI:

```
 ⌂ ~/proyecto   ⎇ main   ✦ Gemini 3.5 Flash   CX12% SN5% WK88%
```

## Segmentos

| Segmento | Símbolo | Fondo | Texto |
|---|---|---|---|
| Directorio | `⌂` | Amarillo | Terminal default |
| Rama Git | `⎇` | Cyan | Terminal default |
| Modelo | `✦` | Púrpura | Terminal default |
| Uso (si disponible) | `CX` `SN` `WK` | Normal | Verde / Amarillo / Rojo |

## Umbrales de color para uso

- 🟢 Verde: `<= 40%`
- 🟡 Amarillo: `40% < x <= 75%`
- 🔴 Rojo: `> 75%`

## Instalación

1. Instalar el plugin:
   ```bash
   agy plugin install ./antigravity/p4-antigravity
   ```

2. Añadir a `~/.gemini/antigravity-cli/settings.json`:
   ```json
   "statusLine": {
     "type": "command",
     "command": "~/.gemini/antigravity-cli/plugins/p4-antigravity/scripts/statusline.sh"
   }
   ```
