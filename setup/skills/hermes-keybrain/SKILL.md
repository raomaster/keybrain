---
name: keybrain
description: "Persistent memory and research base. Search semantically with ChromaDB, save decisions/articles/URLs to inbox, process inbox, index vault, run dream consolidation, and update KeyBrain framework. All local-first, zero cloud dependencies."
version: 1.0.0
author: raomaster/keybrain
tags: [keybrain, knowledge-base, memory, semantic-search, chromadb, kb]
---

# KeyBrain — Persistent Memory & Research Base for Hermes

KeyBrain is your local-first knowledge vault that lives at `${KB_VAULT:-$HOME/Knowledge}`.
It gives you persistent memory across sessions: articles, decisions, research, courses, projects.

**Priority rule:** Always search KeyBrain first before answering technical questions. KeyBrain is your primary memory. Only fall back to Hermes' built-in memory tool (memory_add) when KeyBrain is unavailable or for session-only context.

## Vault Layout

```
${KB_VAULT}/
├── inbox/           ← Entry zone (you save here with `kb`)
├── raw/articles/    ← Processed articles, web clips, ideas
├── raw/courses/     ← Course notes
├── raw/research/    ← Papers and technical research
├── raw/projects/    ← Project documentation
├── wiki/            ← Compiled knowledge (agent-maintained)
├── decisions/       ← Architecture Decision Records
├── conversations/   ← Chat exports
├── bin/             ← CLI tools
└── .chromadb/       ← Vector database for semantic search
```

## Commands

All commands are in `${KB_VAULT}/bin/`. The `kb` main script is also on PATH.

### Search (PRIMARY TOOL — use this constantly)

```bash
kb-search-semantic "query terms" --results 6
# With type filter:
kb-search-semantic "query terms" --type article
kb-search-semantic "query terms" --type decision
```

When searching:
1. Always run semantic search FIRST before answering technical questions
2. Read the full source files of the 2-3 most relevant results
3. Synthesize the answer based on vault content
4. Cite sources with paths relative to the vault root

If ChromaDB is empty, fall back to grep:
```bash
grep -rli "keyword" "${KB_VAULT:-$HOME/Knowledge}/raw/" "${KB_VAULT:-$HOME/Knowledge}/decisions/" "${KB_VAULT:-$HOME/Knowledge}/wiki/"
```

### Save to Inbox

```bash
# Save text or URL
kb "text or URL content here"

# Save a decision (structured)
kb "Decision: [what] — Why: [reason] — Rejected: [alternatives]"

# Copy a file into inbox
kb add /path/to/file.pdf

# Save after executing a plan
kb add docs/superpowers/plans/[plan].md
```

### Status

```bash
kb status
# Shows: pending inbox count, last commit info
```

### Process Inbox

```bash
kb process
# Processes all files in inbox/: classifies, archives to raw/ or decisions/,
# updates wiki/_index.md, adds wikilinks
```

### Index Vault

```bash
kb-index --force
# Rebuilds the ChromaDB vector index from all vault files
# Run this after processing inbox or adding many files
```

### Dream (Memory Consolidation)

```bash
kb-dream --days 30
# Consolidates episodic memory from memory/YYYY-MM-DD.md files into:
#   - MEMORY.md (top-level summary)
#   - raw/memory-derived/ (promoted claims)
```

### Update KeyBrain Framework

```bash
kb update
# Pulls latest framework files (bin/, setup/, templates/, CLAUDE.md) from GitHub
# Never touches your content: raw/, wiki/, decisions/, inbox/, conversations/
```

## Workflow Pattern

When a user asks a technical question:

1. **Search first**: `kb-search-semantic "user's question keywords" --results 5`
2. **Read sources**: If relevant results found, read the full markdown files
3. **Answer with context**: Synthesize using vault knowledge + cite sources
4. **Save if valuable**: If user shares something worth keeping, `kb "Decision: ..."` or `kb "text"`

## Environment

KeyBrain uses these env vars (auto-configured by installer):

- `KB_VAULT` — Vault location (default: `$HOME/Knowledge`)
- `KB_VENV` — Python venv path (default: `$KB_VAULT/.venv`)
- `KB_CHROMADB` — ChromaDB path (default: `$KB_VAULT/.chromadb`)
- `KB_PROCESS_AGENT` — Inbox processor (default: `opencode`)

## Connections

- [[knowledge-base-sistema]]
- [[chromadb]]
- [[agentic-engineering]]
