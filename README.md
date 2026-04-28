# KeyBrain

**Persistent memory and research base for AI coding agents. Local-first, open source, yours.**

[Install](#install) · [How it works](#how-it-works) · [Commands](#commands) · [Docs](docs/use-cases/) · [Contributing](CONTRIBUTING.md)

---

## What is KeyBrain?

KeyBrain gives AI coding agents (Claude Code, Copilot, Cursor) persistent memory and a research base they can actually use. Capture URLs, PDFs, papers, decisions, and notes — your agent classifies, organizes, and recalls them across sessions via semantic search.

No more re-explaining context every conversation. No cloud. No API keys. No vendor lock-in.

## Why KeyBrain?

Two weeks ago Andrej Karpathy [tweeted](https://x.com/karpathy/status/2039805659525644595) something that crystallized what I'd been building:

> *"Using LLMs to build personal knowledge bases for various topics of research interest..."*

The problem is concrete: AI coding agents start from zero every session. They forget your architectural decisions, your conventions, your accumulated research. Existing solutions (Notion AI, Mem, hosted plugins) ship your context to servers you don't control.

KeyBrain is the local-first answer: a knowledge base your agent maintains for you, that lives on your disk, and works across every AI tool you use.

## Install

Copy-paste this prompt to any AI agent (Claude Code, Copilot, Cursor, Gemini CLI):

```
I want to install KeyBrain — persistent memory and research base for my AI coding agents.

1. Clone the repo: git clone https://github.com/raomaster/keybrain.git ~/keybrain
2. Run the installer: bash ~/keybrain/setup/install.sh
3. The script will ask where to install (default: ~/Knowledge)
4. After installation, configure auto-processing:
   "Configure a cron job to run $KB_VAULT/bin/process-inbox.sh every 15 minutes."
```

During installation, KeyBrain detects OpenCode and Claude Code and asks which agent should power `kb process`. OpenCode is the recommended default for corporate environments where Claude is not approved.

**Requirements:** macOS, Linux, or Windows 10/11. Python 3.12+ installed automatically.

### Setting up Obsidian

After the installer runs, open your vault in Obsidian:

1. Install [Obsidian](https://obsidian.md) if not already installed
   - macOS: the installer does this automatically via Homebrew
   - Windows/Linux: download from obsidian.md
2. Open Obsidian
3. Click **Open folder as vault**
4. Navigate to your vault path (default: `~/Knowledge`)
5. Click **Open**

Your knowledge base will appear with all folders and notes organized automatically.

> **Corporate Windows users (Git Bash):** Run `bash setup/install.sh` directly from Git Bash — no PowerShell required. Python 3.12+ must be installed first from [python.org](https://python.org).

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
| `KB_VENV` | `$KB_VAULT/.venv` | Python virtual environment location |
| `KB_CHROMADB` | `$KB_VAULT/.chromadb` | ChromaDB index location |
| `KB_PROCESS_AGENT` | `opencode` | Agent backend for `kb process` (`opencode` or `claude`) |

```bash
# In your shell profile (.zshrc / .bashrc / PowerShell $PROFILE)
export KB_VAULT="$HOME/Google Drive/My Drive/Knowledge"  # cloud sync
export KB_VENV="$HOME/.local/share/keybrain/venv"        # optional runtime outside sync
export KB_CHROMADB="$HOME/.local/share/keybrain/chromadb" # optional index outside sync
export KB_PROCESS_AGENT="opencode"                       # or "claude"
export PATH="$KB_VAULT/bin:$PATH"
```

## Personalizing your agent

KeyBrain installs a `USER.md` template to `~/.claude/USER.md` during setup (Claude Code only). Edit it with your name, role, and preferences — the agent reads it on demand to tailor responses to you.

**Why YAML?** Structured key-value format uses ~30% fewer tokens than prose ([reference](https://dev.to/inozem/structured-prompts-how-yaml-cut-my-llm-costs-by-30-3a56)), keeping your identity file fast to load.

```yaml
---
# USER.md — [Your Name]
# Read on-demand, not every prompt.
---

identity:
  name: [Your Name]
  role: [e.g. "Senior Software Engineer", "Data Scientist"]

expertise: [python, typescript, react]

projects:
  main: [~/Code/myproject]

style:
  expects: [peer-level technical, options with tradeoffs]
  dislikes: [over-explanation, unsolicited refactors]
```

For other agents (Copilot, Cursor, Codex): create the file manually and add an instruction to read it in your agent's config (e.g., `.github/copilot-instructions.md`, `AGENTS.md`).

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
