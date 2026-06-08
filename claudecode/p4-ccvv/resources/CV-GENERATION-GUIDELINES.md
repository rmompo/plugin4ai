# Directrices de Generación de CVs

Este documento contiene las directrices maestras para la generación de CVs en el proyecto CCVV.

**IMPORTANTE**: TODOS los agentes que generen o modifiquen CVs (cv-assistant, cv-regen, cv-exporter) DEBEN seguir estas directrices.

---

## Plantilla de Referencia

**Ubicación**: `resources/templates/cv-template.md`

Esta plantilla contiene la estructura base que TODOS los CVs generados deben seguir.

---

## 1. Estructura Obligatoria de Secciones

Las secciones DEBEN aparecer en este orden EXACTO:

1. **PERFIL PROFESIONAL**
2. **STACK TECNOLÓGICO**
3. **PROYECTOS DESTACADOS**
4. **EXPERIENCIA PROFESIONAL**
5. **EDUCACIÓN**
6. **FORMACIÓN Y CERTIFICACIONES**
7. **IDIOMAS E INTERESES**

❌ **Este orden NO puede alterarse bajo ninguna circunstancia.**

---

## 2. Numeración de Secciones

### Regla

TODAS las secciones y subsecciones deben estar numeradas.

### Formato

- **Secciones principales** (nivel 2, `##`): `1.`, `2.`, `3.`, etc.
- **Subsecciones** (nivel 3, `###`): `1.1.`, `1.2.`, `2.1.`, `2.2.`, etc.
- **Títulos de secciones principales**: MAYÚSCULAS

### ⚠️ CRÍTICO: Secciones Vacías

**Regla**: Si una sección NO tiene contenido, NO debe incluirse en el CV.

**Numeración**: La numeración debe mantenerse coherente saltando el número de la sección omitida.

**Ejemplo**:
```markdown
## 1. PERFIL PROFESIONAL
...contenido...

## 2. STACK TECNOLÓGICO
...contenido...

<!-- SECCIÓN 3. PROYECTOS DESTACADOS omitida porque no hay proyectos -->

## 3. EXPERIENCIA PROFESIONAL
...contenido...

## 4. EDUCACIÓN
...contenido...
```

❌ **INCORRECTO**:
```markdown
## 3. PROYECTOS DESTACADOS

No aplica
```

✅ **CORRECTO**:
```markdown
<!-- La sección PROYECTOS DESTACADOS se omite completamente -->
<!-- La numeración continúa: 1. PERFIL, 2. STACK, 3. EXPERIENCIA (sin incluir PROYECTOS) -->
```

### Ejemplo de Numeración Correcta

```markdown
## 1. PERFIL PROFESIONAL
## 2. STACK TECNOLÓGICO
### 2.1. Backend Development
### 2.2. Frontend Development
### 2.3. Databases
## 3. PROYECTOS DESTACADOS
### 3.1. Proyecto A
### 3.2. Proyecto B
```

---

## 3. Ordenamiento de Contenido

### 3.1. Experiencias Laborales

**Orden**: Descendente por fecha de fin

**Criterios**:
1. **Primer orden**: Fecha de fin (descendente)
   - `"Actualidad"`, `"onGoing"`, `"Present"` = más recientes (van primero)
   - Luego por año de fin numérico: 2026, 2025, 2024, etc.

2. **Segundo orden**: Fecha de inicio (si hay empate en fecha de fin)
   - También descendente

### 3.2. Proyectos Destacados

**Orden**: Tipo → Alfabético

**Criterios**:
1. **Primer orden**: Tipo de proyecto
   - Primero: `type: "professional"`
   - Después: `type: "personal"`

2. **Segundo orden**: Alfabético por título
   - Dentro de cada grupo (professional/personal)
   - Case-insensitive
   - Ignorar artículos ("El", "La", "Un", etc.)

**Formato**:
- NO incluir campo "Estado"
- Campos permitidos: Descripción, Tecnologías, URL (opcional)

---

## 4. Idioma del Contenido

### Regla Principal

TODO el contenido del CV debe estar en el idioma especificado en el campo `language` de metadata YAML.

### ⚠️ CRÍTICO: Qué NO Traducir

**ESTAS REGLAS SON CRÍTICAS Y OBLIGATORIAS**

De forma general, **NO SE DEBE TRADUCIR**:

❌ **NO traducir NUNCA**:
- **Nombres de tecnologías**: Java, Python, TypeScript, JavaScript, C++, Ruby, etc.
- **Nombres de frameworks**: Spring, SpringBoot, Angular, React, Django, Express, Hibernate, etc.
- **Nombres de herramientas**: Docker, Jenkins, Maven, Gradle, Git, npm, Kubernetes, etc.
- **Marcas o productos**: Oracle, MySQL, PostgreSQL, MongoDB, AWS, Azure, Google Cloud, etc.
- **Nombres propios**: Personas, empresas, instituciones, organizaciones
- **Nombres de lugares**: Ciudades, países, regiones
- **URLs y enlaces**: Mantener exactamente como están
- **Códigos y siglas técnicas**: API, REST, HTML, CSS, JSON, XML, HTTP, CI/CD, etc.
- **Acrónimos**: PAC, UE, SIGPAC, CRM, UI, IoT, OL, etc.
- **Palabras en inglés de uso común**: front, back, frontend, backend, webservices, deploy, workflow, debug, etc.
- **Nombres de certificaciones oficiales**: Mantener nombre oficial
- **Nombres de proyectos**: Cuando son marcas registradas o productos específicos

### Ejemplos de NO Traducción

```markdown
❌ INCORRECTO (traducido):
- Desarrollo de aplicaciones usando Primavera y Java
- Despliegue con Estibador y Kubertetes
- Base de datos Oráculo

✅ CORRECTO (sin traducir nombres técnicos):
- Desarrollo de aplicaciones usando Spring y Java
- Despliegue con Docker y Kubernetes
- Base de datos Oracle
```

### Traducciones de Campos Comunes

#### Español (es)
- **EDUCACIÓN**:
  - Estado: "Completado", "No finalizado", "En curso"
  - Período: "1998 - 2006", "2010 - No finalizado"
- **IDIOMAS**:
  - "Español: Nativo"
  - "Inglés: Fluido"
- **INTERESES**:
  - "Electrónica", "Robótica", "Física", "Programación de videojuegos"

#### Inglés (en)
- **EDUCATION**:
  - Status: "Completed", "Not finished", "In progress"
  - Period: "1998 - 2006", "2010 - Not finished"
- **LANGUAGES**:
  - "Spanish: Native"
  - "English: Fluent"
- **INTERESTS**:
  - "Electronics", "Robotics", "Physics", "Game programming"

---

## 5. Formato de Foto de Perfil

### Ubicación

Inmediatamente después del YAML front-matter, antes de la primera sección.

### Formato LaTeX Obligatorio

```latex
\begin{table}[h]
\centering
\begin{tabular}{>{\centering\arraybackslash}m{4cm}>{\raggedright\arraybackslash}m{11cm}}
\includegraphics[width=3cm]{../../input/photo.jpg} &
\textbf{\LARGE Nombre Completo} \newline
\textit{Título 1 | Título 2 | Título 3} \newline
\newline
email@ejemplo.com | +34 XXX XXX XXX \newline
\href{https://linkedin.com/in/perfil}{linkedin.com/in/perfil}
\end{tabular}
\end{table}

\vspace{0.5cm}
```

### Especificaciones

- Foto a la izquierda (columna de 4cm)
- Información a la derecha (columna de 11cm)
- Ruta de foto: `../../input/photo.jpg` (relativa desde output/)
- Tamaño de foto: 3cm de ancho
- Nombre en negrita y tamaño grande
- Títulos en itálica
- Contacto e información en la misma columna

---

## 6. Cierre del Documento

### Formato Obligatorio

```markdown
---


\begin{center}
[FRASE DE CIERRE EN IDIOMA DEL CV]
\end{center}
```

### Especificaciones

- Línea horizontal (`---`)
- **Exactamente 2 líneas vacías** entre la línea horizontal y el bloque center
- Frase centrada usando `\begin{center}...\end{center}`
- Frase en el idioma del CV

### Frases de Cierre por Idioma

- **Español (es)**: Referencias y detalles adicionales disponibles bajo solicitud
- **Inglés (en)**: References and additional details available upon request
- **Francés (fr)**: Références ou détails disponibles sur demande
- **Alemán (de)**: Referenzen oder Details auf Anfrage verfügbar
- **Italiano (it)**: Riferimenti o dettagli disponibili su richiesta
- **Portugués (pt)**: Referências ou detalhes disponíveis mediante solicitação

---

## 7. Metadatos YAML

### Formato Obligatorio

```yaml
---
tipo: curriculum-vitae
puesto: [Puesto del CV]
metadata_id: [ID numérico]
slug: [slug_del_puesto]
language: [código de idioma: es, en, fr, etc.]
generado: [Timestamp ISO 8601]
actualizado: [Timestamp ISO 8601 - opcional, añadido por cv-regen]
profile_version: [Versión del profile.json]
offer_analyzed: [true/false]
keywords: [array de keywords]
header-includes: |
  \usepackage{graphicx}
  \usepackage{array}
---
```

### Campos Obligatorios

- `tipo`: Siempre "curriculum-vitae"
- `puesto`: Puesto al que se aplica
- `metadata_id`: ID del metadata en cvs.json
- `slug`: Versión slug del puesto (lowercase, guiones bajos)
- `language`: Código ISO 639-1 (2 letras: es, en, fr, de, etc.)
- `generado`: Timestamp de generación inicial
- `profile_version`: Versión del profile.json usado
- `offer_analyzed`: true si se analizó oferta, false si es genérico
- `keywords`: Array de keywords (puede estar vacío si offer_analyzed=false)

### Campos Opcionales

- `actualizado`: Timestamp de última regeneración (añadido por cv-regen)

---

## 8. Comentarios HTML

### Propósito

Los comentarios HTML sirven para:
- Delimitar secciones
- Añadir notas internas
- Proporcionar contexto para IA

### Formato

```markdown
<!-- SECCIÓN: Perfil Profesional -->
## 1. PERFIL PROFESIONAL
...

<!-- SECCIÓN: Stack Tecnológico -->
## 2. STACK TECNOLÓGICO
...

<!-- Proyectos Profesionales (ordenados alfabéticamente) -->
### 3.1. Proyecto A
...

<!-- Proyectos Personales (ordenados alfabéticamente) -->
### 3.5. Proyecto Personal
...

<!-- NOTAS PARA GENERACIÓN FINAL -->
<!--
Este CV está optimizado para...
-->

<!-- FIN DE DOCUMENTO -->
```

---

## 9. Formato de Proyectos Destacados

### Campos Permitidos

✅ **Incluir**:
- Descripción (obligatorio)
- Tecnologías (obligatorio)
- URL (opcional - solo si el proyecto es público)

❌ **NO incluir**:
- Estado (Completed, In Development, etc.)

### Formato

```markdown
### 3.1. Nombre del Proyecto

**Descripción**: Descripción del proyecto

**Tecnologías**:

- **Categoría 1**: Tecnología A, Tecnología B
- **Categoría 2**: Tecnología C, Tecnología D

**URL**: https://ejemplo.com (solo si aplica)

---
```

### Nota para Proyectos Personales

Añadir `(personal)` al final del título del proyecto:

```markdown
### 3.5. Nombre del Proyecto Personal (personal)
```

---

## 10. Espaciado y Formato

### ⚠️ CRÍTICO: Líneas Horizontales

**Regla**: Las líneas horizontales (`---`) SOLO se usan para separar secciones principales (##), NUNCA para separar subsecciones (###).

**Aplicación**:
- ✅ USAR línea horizontal (`---`) DESPUÉS de cada sección principal (##)
- ❌ NO USAR línea horizontal entre subsecciones (###)
- ❌ NO USAR línea horizontal entre experiencias laborales
- ❌ NO USAR línea horizontal entre proyectos
- ❌ NO USAR línea horizontal entre formaciones o certificaciones

**Ejemplo CORRECTO**:
```markdown
## 1. PERFIL PROFESIONAL
...contenido...

---

## 2. STACK TECNOLÓGICO

### 2.1. Backend Development
...contenido...

### 2.2. Frontend Development
...contenido...

---

## 3. EXPERIENCIA PROFESIONAL

### 3.1. Título del Puesto - Empresa
...contenido...

### 3.2. Otro Título - Otra Empresa
...contenido...

---

## 4. EDUCACIÓN
...contenido...

---
```

**Ejemplo INCORRECTO**:
```markdown
## 2. STACK TECNOLÓGICO

### 2.1. Backend Development
...contenido...

---  ← ❌ NO usar línea horizontal entre subsecciones

### 2.2. Frontend Development
...contenido...

---  ← ❌ NO usar línea horizontal entre subsecciones
```

### Secciones Técnicas

```markdown
### 2.1. Backend Development

**Lenguajes**: Java, Python, TypeScript

**Frameworks**: Spring, Django, Express
```

- Línea en blanco después del título de subsección
- Separar categorías técnicas con espacio
- NO usar línea horizontal entre subsecciones técnicas

### Experiencias Laborales

```markdown
### 4.1. Título del Puesto - Empresa

**Período**: 2020 - Actualidad | **Ubicación**: Madrid, España | **Equipo**: 5-10 personas

[Descripción]

**Responsabilidades**:
- Responsabilidad 1
- Responsabilidad 2

**Logros**:
- Logro 1
- Logro 2

**Stack Tecnológico**: Java, Spring, Docker, PostgreSQL

### 4.2. Otro Título - Otra Empresa

**Período**: 2018 - 2020 | **Ubicación**: Barcelona, España

[Descripción]

**Responsabilidades**:
- Responsabilidad 1
- Responsabilidad 2

**Stack Tecnológico**: Python, Django, PostgreSQL
```

- NO usar separador horizontal (`---`) entre experiencias
- Período, Ubicación y Equipo en una línea
- Stack Tecnológico inline (separado por comas)
- Espacio entre subsecciones mediante una línea en blanco

---

## 11. Validación

### Checklist de Validación

Antes de generar/exportar un CV, verificar:

- [ ] Orden de secciones correcto (1. PERFIL, 2. STACK, 3. PROYECTOS, 4. EXPERIENCIA, 5. EDUCACIÓN, 6. FORMACIÓN, 7. IDIOMAS E INTERESES)
- [ ] TODAS las secciones y subsecciones numeradas
- [ ] **Secciones vacías NO incluidas** (si no hay contenido, omitir la sección completa)
- [ ] **Numeración coherente** (saltar números de secciones omitidas)
- [ ] **Líneas horizontales SOLO entre secciones principales** (##), NUNCA entre subsecciones (###)
- [ ] **NO hay líneas horizontales** entre experiencias laborales, proyectos, formaciones, o cualquier subsección
- [ ] Experiencias ordenadas por fecha de fin (descendente)
- [ ] Proyectos ordenados por tipo (professional → personal) y alfabéticamente
- [ ] TODO el contenido en el idioma correcto
- [ ] Campos de EDUCACIÓN traducidos
- [ ] Idiomas y niveles traducidos
- [ ] Intereses traducidos
- [ ] NO hay campo "Estado" en proyectos
- [ ] Foto de perfil con formato LaTeX correcto
- [ ] Cierre de documento con 2 líneas vacías y centrado
- [ ] Frase de cierre en el idioma correcto
- [ ] Metadatos YAML completos y correctos
- [ ] Comentarios HTML en sus ubicaciones

---

## 12. Responsabilidades por Agente

### cv-assistant
- Generar archivo META inicial desde profile.json
- Aplicar TODAS las directrices de este documento
- Crear metadata en cvs.json
- Registrar exports en cvs.json

### cv-regen
- Regenerar archivo META existente con datos actualizados
- Aplicar TODAS las directrices de este documento
- Mantener ID de metadata original
- Actualizar timestamp "updated" en metadata
- NO modificar parámetros originales (puesto, oferta, keywords)

### cv-exporter
- Leer archivo META
- Convertir a formato final (PDF, DOCX, HTML, MD)
- Aplicar directrices de formato y traducción
- NO modificar archivo META original
- NO modificar cvs.json

---

## 13. Plantilla de Referencia

**Ubicación**: `resources/templates/cv-template.md`

Esta plantilla contiene:
- Estructura completa con todas las secciones en orden correcto
- Formato de metadatos YAML
- Formato de foto de perfil
- Ejemplos de todas las secciones
- Formato de cierre correcto
- Comentarios HTML en ubicaciones correctas

**Uso**:
- Consultar la plantilla al generar un nuevo CV
- Verificar estructura y formato contra la plantilla
- Copiar bloques de código LaTeX exactamente como aparecen

---

## 14. Actualización de Directrices

Cuando se actualicen estas directrices:

1. Actualizar este documento (`resources/CV-GENERATION-GUIDELINES.md`)
2. Actualizar la plantilla (`resources/templates/cv-template.md`)
3. Actualizar directrices específicas en agentes:
   - `agents/cv-assistant/AGENT.md` (DA-007 y otras)
   - `agents/cv-regen/AGENT.md` (referencia a DA-007 de cv-assistant)
   - `agents/cv-exporter/AGENT.md` (DA-002, DA-007 y otras)
4. Actualizar README.md si aplica
5. Crear commit explicando los cambios

---

## Notas Importantes

1. Estas directrices son **obligatorias** y **no opcionales**
2. NO se pueden ignorar o modificar sin actualizar este documento
3. En caso de conflicto entre directrices, este documento prevalece
4. Cualquier agente nuevo que genere CVs DEBE seguir estas directrices
5. Las directrices son versionadas mediante git

---

**Última actualización**: 2026-02-06
**Versión**: 1.1

**Cambios en v1.1**:
- Añadida regla crítica: Secciones vacías no deben incluirse
- Añadida regla crítica: Líneas horizontales solo entre secciones principales (##)
- Actualizada checklist de validación
