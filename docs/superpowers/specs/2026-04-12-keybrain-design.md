# KeyBrain — Diseño v0.1.0

**Fecha:** 2026-04-12
**Autor:** Raomaster
**Estado:** Aprobado — listo para plan de implementación

---

## Problema

No existe un estándar simple y accesible para que cualquier persona (developer, escritor, científico) tenga una base de conocimiento personal administrada por agentes AI — con búsqueda semántica local, grafo visual en Obsidian, y skills que funcionan en cualquier agente.

## Solución

Un repositorio público, instalable con un copy-paste a tu agente AI, que provee:
- Vault local con ChromaDB para búsqueda semántica en milisegundos
- Organización automática por el agente (clasifica, vincula, archiva)
- Skills multi-agente via agentskills.io
- Grafo visual en Obsidian desde el primer arranque
- Update model versionado con notificación via agente

---

## Repositorio

- **Nombre:** KeyBrain (`kb` — de **K**ey**B**rain, la llave a tu cerebro de conocimiento)
- **Pronunciación:** "kíbren" /kiː-breɪn/
- **Tipo:** nuevo repo público — separado del vault privado de Raomaster
- **Versión inicial:** v0.1.0
- **Relación con vault privado de Raomaster:** agrega el repo público como `upstream`, usa `kb update` para sincronizar mejoras al framework

---

## Arquitectura general

```
Usuario
  │
  ├─ copia INSTALL-PROMPT.md → pega a su agente AI
  │     └─ agente detecta OS y corre install.sh o install.ps1
  │           ├─ instala dependencias (Node.js, Python 3.12, Claude Code, Obsidian)
  │           ├─ pip install chromadb + markitdown[pdf,docx,xlsx,pptx]
  │           ├─ pregunta ruta de instalación (default $HOME/Knowledge)
  │           ├─ instala skills via npx skills@latest
  │           ├─ configura CLAUDE.md global + settings.json
  │           └─ corre smoke tests automáticos
  │
  ├─ agrega contenido
  │     ├─ kb "texto o URL"       → inbox/
  │     ├─ kb add archivo.pdf     → inbox/ → markitdown convierte → Markdown
  │     └─ Obsidian Web Clipper   → inbox/
  │           └─ agente clasifica, vincula wikilinks, archiva, actualiza wiki/
  │
  └─ consulta
        └─ /kb-search "query" → ChromaDB local (ms) → respuesta con contexto
```

---

## Stack

| Componente | Tecnología | Justificación |
|-----------|-----------|--------------|
| CLI | zsh/bash + PowerShell | nativo en cada OS |
| Búsqueda semántica | ChromaDB (Python) | local-first, sin API key |
| Conversión de archivos | markitdown (Python) | PDF/Word/Excel/PPT/imágenes/audio/YouTube |
| Visualización | Obsidian | grafo de conocimiento, vault nativo |
| Skills | agentskills.io | multi-agente sin infraestructura |
| Package manager macOS | Homebrew | estándar |
| Package manager Windows | winget | nativo Windows 10/11 |

---

## Estructura del repositorio

```
/
├── bin/
│   ├── kb                    # CLI principal (macOS/Linux/WSL2)
│   ├── kb-update             # descarga framework actualizado desde GitHub
│   ├── kb-index              # shell wrapper para kb-index.py
│   ├── kb-index.py           # indexa vault en ChromaDB
│   ├── kb-search-semantic    # shell wrapper para búsqueda semántica
│   ├── kb-search-semantic.py # búsqueda ChromaDB
│   ├── kb-install-hooks      # instala git hooks en proyecto externo
│   └── process-inbox.sh      # procesamiento del inbox (llamado por cron)
├── setup/
│   ├── install.sh            # macOS + Linux + WSL2
│   ├── install.ps1           # Windows nativo
│   ├── test-install.sh       # smoke tests post-instalación (corre en CI)
│   ├── test-install.ps1      # smoke tests Windows (corre manualmente por Raomaster)
│   └── git-hooks/
│       └── post-commit       # captura commits al inbox
├── tests/
│   ├── unit/
│   │   ├── test_kb.py        # pytest: bin/kb via subprocess
│   │   ├── test_process.py   # pytest: process-inbox.sh + markitdown
│   │   └── test_index.py     # pytest: ChromaDB indexación y búsqueda
│   ├── integration/
│   │   └── test_install.py   # pytest: smoke test completo post-install
│   └── fixtures/
│       ├── sample.pdf
│       ├── sample.docx
│       ├── sample.xlsx
│       └── sample-article.md
├── templates/
│   ├── article.md
│   ├── decision.md
│   └── course.md
├── inbox/                    # zona de entrada — .gitkeep
├── raw/
│   ├── articles/             # artículos y posts
│   ├── courses/              # notas de cursos
│   ├── research/             # papers, repos
│   ├── projects/             # READMEs de proyectos propios
│   └── ideas/                # ideas sueltas
├── wiki/
│   ├── _index.md             # índice auto-mantenido (pre-poblado)
│   ├── concepts/
│   ├── technologies/
│   └── projects/
├── decisions/
├── conversations/
├── output/
├── docs/
│   ├── use-cases/            # casos de uso paso a paso
│   └── superpowers/specs/    # specs de diseño
├── .agents/skills/           # skills universales (agentskills.io)
├── .github/
│   └── workflows/
│       └── ci.yml
├── CLAUDE.md                 # instrucciones para el agente
├── CONTRIBUTING.md           # guía para la comunidad
├── CHANGELOG.md              # historial Keep a Changelog
├── VERSION                   # "0.1.0"
├── README.md
└── INSTALL-PROMPT.md
```

---

## Instalación

### Entry point

`INSTALL-PROMPT.md` contiene un prompt listo para copiar y pegar al agente AI. El agente detecta el OS y ejecuta el script correspondiente sin intervención del usuario.

### Detección de plataforma

```bash
# install.sh
OS="$(uname -s)"
if grep -qi microsoft /proc/version 2>/dev/null; then PLATFORM="wsl2"
elif [ "$OS" = "Darwin" ]; then PLATFORM="macos"
elif [ "$OS" = "Linux" ]; then PLATFORM="linux"
fi
```

### Selección de ruta (interactiva)

```bash
echo "¿Dónde instalar tu Knowledge Vault?"
echo "  (ej: $HOME/Knowledge, $HOME/Google Drive/My Drive/Knowledge)"
read -r -p "Ruta [Enter para $HOME/Knowledge]: " VAULT_PATH
VAULT_PATH="${VAULT_PATH:-$HOME/Knowledge}"
```

El usuario que usa Google Drive, OneDrive o Dropbox como carpeta de sync escribe esa ruta. No hay configuración extra — el vault vive dentro del cloud folder y el sync es automático.

### Dependencias instaladas

**macOS (Homebrew):**
- git, node, python@3.12, obsidian, yt-dlp
- `pip install chromadb markitdown[pdf,docx,xlsx,pptx]`
- `npm install -g @anthropic-ai/claude-code`

**Windows nativo (winget):**
- Git.Git, OpenJS.NodeJS.LTS, Python.Python.3.12, Obsidian.Obsidian, yt-dlp.yt-dlp
- PATH refresh con `[System.Environment]::GetEnvironmentVariable("PATH","Machine")` después de cada winget install
- `pip install chromadb markitdown[pdf,docx,xlsx,pptx]`

**WSL2 (Ubuntu 24.04 LTS):**
- apt: git, nodejs, python3.12, yt-dlp
- Obsidian: avisa al usuario que debe instalarlo en el lado Windows
- Cloud sync: el usuario provee la ruta `/mnt/...` correspondiente

### Flags para CI / uso no interactivo

```bash
bash setup/install.sh --skip-obsidian --skip-drive
```

### Cron / automatización

**Fuera del install.sh.** Documentado en README como prompt copy-paste al agente:

> "Configura un cron job que ejecute ~/Knowledge/bin/process-inbox.sh cada 15 minutos."

---

## Procesamiento del inbox

`process-inbox.sh` ejecuta en este orden para cada archivo en `inbox/`:

1. Si el archivo no es `.md` → convierte con markitdown:
   ```bash
   [[ "$file" != *.md ]] && markitdown "$file" > "${file%.*}.md" && rm "$file"
   ```
2. Llama al agente para clasificar, archivar, actualizar `wiki/_index.md`
3. Git commit automático
4. (Si cloud folder detectado) sync es automático por el desktop app

**Formatos soportados vía markitdown:**
PDF, Word (.docx), Excel (.xlsx/.xls), PowerPoint (.pptx), imágenes (OCR), audio (transcripción), HTML, CSV, JSON, YouTube URLs, EPubs.

> **Nota:** transcripción de audio e imágenes OCR avanzado requieren API key de OpenAI. Conversión de archivos de oficina funciona 100% local.

---

## Update model

```
kb update
  ├── lee VERSION local (ej: "0.1.0")
  ├── consulta GitHub API: última tag del repo público
  ├── si hay versión nueva → agente notifica al usuario y pregunta "¿actualizo?"
  ├── si usuario dice sí → descarga archivos de framework:
  │     bin/, setup/, templates/, CLAUDE.md, README.md, INSTALL-PROMPT.md
  └── nunca toca: raw/, wiki/, decisions/, inbox/, conversations/, VERSION
```

`VERSION` solo se actualiza cuando el usuario confirma la actualización.

---

## Multi-agente

| Superficie | Método | Scope |
|-----------|--------|-------|
| Claude Code | agentskills.io (`npx skills@latest`) | v0.1.0 |
| GitHub Copilot (VS Code) | agentskills.io | v0.1.0 |
| Cursor / Gemini CLI / Codex / Roo Code | agentskills.io | v0.1.0 |
| Claude.ai Projects | copy-paste SKILL.md → instrucciones del Project | v0.1.0 |
| M365 Copilot (Word/Excel/PowerPoint) | plugin declarativo separado | v0.2.0+ |

---

## Contenido inicial (self-documenting)

El vault viene pre-poblado con contenido sobre el proyecto mismo. Al abrir Obsidian por primera vez el grafo ya tiene nodos y conexiones reales.

| Archivo | Tipo | Contenido |
|---------|------|-----------|
| `raw/articles/YYYY-MM-DD-que-es-knowledge-vault.md` | Artículo | Filosofía, qué es, para qué sirve |
| `raw/articles/YYYY-MM-DD-tutorial-primeros-pasos.md` | Tutorial | Paso a paso con ejemplo tweet Karpathy |
| `decisions/YYYY-MM-DD-obsidian-chromadb.md` | ADR | Por qué Obsidian + ChromaDB vs alternativas |
| `wiki/_index.md` | Índice | Pre-poblado con los 3 archivos anteriores |

---

## Casos de uso (docs/use-cases/)

Documentación paso a paso para cualquier perfil de usuario:

1. **Instalación desde cero** — copy-paste del INSTALL-PROMPT.md al agente
2. **Capturar un artículo web** — web clipper o `kb "https://..."`
3. **Capturar un PDF o Word doc** — `kb add archivo.pdf`
4. **Capturar un tweet** — ejemplo con tweet de Karpathy
5. **Consultar el vault** — `/kb-search "query"`
6. **Registrar una decisión técnica** — `kb "Decidí usar X porque..."`
7. **Actualizar el vault** — `kb update` (o el agente avisa)

---

## Testing

### Estructura

```
tests/
├── unit/
│   ├── test_kb.py       # bin/kb via subprocess: add, status, text
│   ├── test_process.py  # process-inbox.sh + conversión markitdown
│   └── test_index.py    # ChromaDB: indexar y buscar
├── integration/
│   └── test_install.py  # smoke test completo post-install
└── fixtures/
    ├── sample.pdf
    ├── sample.docx
    ├── sample.xlsx
    └── sample-article.md
```

### Herramientas

- **pytest** — runner único en todas las plataformas (Python ya en el stack)
- **subprocess.run()** — para testear scripts de shell y PowerShell desde Python
- Sin bats, sin Pester — una sola herramienta

### Cobertura

| Plataforma | Tests | CI automatizado |
|-----------|-------|----------------|
| macOS | pytest completo | ✅ `macos-latest` |
| Linux (Ubuntu 24.04) | pytest completo | ✅ `ubuntu-24.04` |
| Windows nativo | instalación manual | Raomaster (manual) |
| WSL2 (Ubuntu 24.04) | instalación manual | Raomaster (manual) |

### CI — GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-24.04, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install vault
        run: bash setup/install.sh --skip-obsidian --skip-drive
      - name: Run tests
        run: python -m pytest tests/ -v
```

---

## Versionamiento

- **Formato:** Semantic Versioning — `MAJOR.MINOR.PATCH`
- **v0.1.0** — primera release pública (MVP)
- **Tags de git:** `v0.1.0`, `v0.2.0`, etc.
- **Archivo `VERSION`** en raíz del repo — `kb update` lo lee para comparar

### CHANGELOG.md (Keep a Changelog)

```markdown
# Changelog

## [Unreleased]

## [0.1.0] - 2026-04-XX
### Added
- Estructura del vault (inbox, raw, wiki, decisions, conversations)
- install.sh (macOS, Linux, WSL2) + install.ps1 (Windows)
- Detección de plataforma y selección interactiva de ruta
- markitdown para inbox multi-formato (PDF, Word, Excel, PPT, YouTube)
- ChromaDB para búsqueda semántica local
- Skills multi-agente via agentskills.io
- kb update con notificación via agente
- Contenido self-documenting (4 archivos iniciales)
- Casos de uso paso a paso (7 escenarios)
- CI con GitHub Actions (macOS + Ubuntu 24.04)
- CONTRIBUTING.md + CODE_OF_CONDUCT.md
```

---

## Comunidad — CONTRIBUTING.md

Incluye:
- **Cómo reportar bugs** — issue template con OS, versión, pasos para reproducir
- **Cómo proponer features** — issue template con problema, solución propuesta, alternativas
- **Cómo contribuir skills** — SKILL.md debe tener `name`, `description` (entre comillas si contiene `: `), y sección de test manual
- **PR guidelines** — una rama por feature, tests pasan en CI, entrada obligatoria en CHANGELOG
- **Code of conduct** — Contributor Covenant

---

## GitHub Pages (post v0.1.0)

Landing page del proyecto — milestone v0.2.0.

Contenido:
- Hero: qué es + install prompt
- Demo: gif/video del flujo completo
- Casos de uso visuales
- Agentes soportados
- Quick start

---

## Fuera de scope v0.1.0

- Cron/Task Scheduler automático (documentado en README como prompt)
- M365 Copilot plugin (Word/Excel/PowerPoint)
- GitHub Pages landing
- rclone (reemplazado por cloud folder detection)

## Conexiones

- [[knowledge-base-sistema]]
- [[chromadb]]
