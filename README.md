# KeyBrain

**Your AI-powered personal knowledge base. Local-first, agent-managed, visually explorable.**

[Install](#install) · [How it works](#how-it-works) · [Commands](#commands) · [Docs](docs/use-cases/) · [Contributing](CONTRIBUTING.md)

---

## What is KeyBrain?

KeyBrain is an open-source framework that turns any folder into a personal knowledge base managed by AI agents. It captures articles, PDFs, decisions, course notes, and ideas — then automatically classifies, organizes, and makes them searchable.

**No cloud. No API keys. No vendor lock-in.**

## Install

Copy-paste this prompt to any AI agent (Claude Code, Copilot, Cursor, Gemini CLI):

```
I want to install KeyBrain — my personal knowledge base.

1. Clone the repo: git clone https://github.com/your-org/keybrain.git ~/keybrain
2. Run the installer: bash ~/keybrain/setup/install.sh
3. The script will ask where to install (default: ~/Knowledge)
4. After installation, configure auto-processing:
   "Configure a cron job to run $KB_VAULT/bin/process-inbox.sh every 15 minutes."
```

**Requirements:** macOS, Linux, or Windows 10/11. Python 3.12+ installed automatically.

## How it works

```
You                          AI Agent
 │                             │
 │  kb "article URL"           │
 │  kb add document.pdf        │
 │  Obsidian Web Clipper       │
 │         ↓                   │
 │    inbox/                   │
 │         ↓                   │
 │                      process-inbox.sh
 │                             │
 │                      ┌──────┴──────┐
 │                      │ Classifies   │
 │                      │ Archives     │
 │                      │ Links wikis  │
 │                      │ Updates index│
 │                      └──────┬──────┘
 │                             │
 │         ↓                   │
 │  wiki/ + raw/ + decisions/  │
 │         ↓                   │
 │  /kb-search "query"         │
 │  → ChromaDB (milliseconds)  │
```

## Commands

| Command | What it does |
|---------|-------------|
| `kb "text or URL"` | Save text or URL to inbox |
| `kb add <file>` | Copy file (PDF, Word, Excel, etc.) to inbox |
| `kb process` | Force inbox processing now |
| `kb status` | Show pending inbox count + last commit |
| `kb update` | Update KeyBrain framework from GitHub |
| `kb open` | Open vault in file manager |

### Semantic search (slash commands)

| Command | What it does |
|---------|-------------|
| `/kb-search "query"` | Search the vault semantically |
| `/kb-add` | Add content to inbox |
| `/kb-process` | Process the inbox |
| `/kb-health` | Audit the vault for issues |
| `/kb-compile` | Compile/update the wiki |

## Supported formats

Via [markitdown](https://github.com/microsoft/markitdown):

| Format | Extension |
|--------|-----------|
| PDF | `.pdf` |
| Word | `.docx` |
| Excel | `.xlsx`, `.xls` |
| PowerPoint | `.pptx` |
| Images (OCR) | `.jpg`, `.png` |
| Audio (transcription) | `.mp3`, `.wav` |
| HTML | `.html` |
| CSV/JSON | `.csv`, `.json` |
| YouTube | URLs (extracts title, description, and transcript) |
| EPub | `.epub` |

## Supported agents

KeyBrain works with any AI agent via [agentskills.io](https://agentskills.io):

| Agent | Method |
|-------|--------|
| Claude Code | Skills via `npx skills@latest` |
| GitHub Copilot (VS Code) | Skills via agentskills.io |
| Cursor / Gemini CLI / Codex / Roo Code | Skills via agentskills.io |
| Claude.ai Projects | Copy-paste SKILL.md to Project instructions |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `KB_VAULT` | `$HOME/Knowledge` | Vault location |

```bash
# In your shell profile (.zshrc / .bashrc / PowerShell $PROFILE)
export KB_VAULT="$HOME/Google Drive/My Drive/Knowledge"  # cloud sync
export PATH="$KB_VAULT/bin:$PATH"
```

## Architecture

```
vault/
├── inbox/           ← Entry zone (you add files here)
├── raw/articles/    ← Processed articles
├── raw/courses/     ← Course notes
├── raw/research/    ← Papers and research
├── wiki/            ← Compiled knowledge (agent-maintained)
├── decisions/       ← Architecture Decision Records
├── conversations/   ← Chat exports
├── bin/             ← CLI tools + Python scripts
├── CLAUDE.md        ← Agent instructions (the "magic")
└── .chromadb/       ← Local vector database
```

The "magic" is `CLAUDE.md` — 250+ lines of instructions that tell your AI agent exactly how to classify, organize, and maintain your knowledge. The scripts are thin wrappers.

## Cloud sync

KeyBrain works with any cloud sync provider. If you store your vault inside a synced folder, exclude `.venv/` and `.chromadb/` — they are regenerable and can be hundreds of MB.

| Provider | How to exclude a folder |
|----------|------------------------|
| **Google Drive** | Create an empty `.gdignore` file inside the folder |
| **iCloud** | Rename the folder with a `.nosync` extension (e.g. `.venv.nosync`) |
| **OneDrive** | Rename the folder with a `.nosync` extension |
| **Dropbox** | Use Selective Sync in the Dropbox desktop app |

```bash
# Google Drive example
touch ~/Knowledge/.venv/.gdignore
touch ~/Knowledge/.chromadb/.gdignore
```

## License

MIT

## Links

- [Use Cases](docs/use-cases/) — step-by-step scenarios
- [Contributing](CONTRIBUTING.md) — how to contribute
- [Changelog](CHANGELOG.md) — version history
