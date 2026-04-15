---
title: "Getting Started with KeyBrain — A Step-by-Step Tutorial"
date: 2026-04-14
source: "https://github.com/your-org/keybrain"
tags: [article, keybrain, tutorial]
status: raw
summary: "A hands-on tutorial walking through installing KeyBrain, capturing your first article, processing it, and searching for it."
---

# Getting Started with KeyBrain

This tutorial walks you through the complete KeyBrain workflow: install, capture, process, search.

## Step 1: Install

Copy the install prompt from `INSTALL-PROMPT.md` and paste it to your AI agent. The agent detects your OS and runs the installer automatically.

After installation, you'll have:
- `~/Knowledge/` — your vault
- `kb` command — the CLI
- 7 slash commands in Claude Code
- ChromaDB for semantic search

## Step 2: Capture your first article

Let's capture a real article. Open your terminal:

```bash
kb "https://arxiv.org/abs/2310.06775"
```

This saves a timestamped file in `inbox/` with the URL. The AI agent will fetch the actual content when processing.

You can also capture text directly:

```bash
kb "Decided to use ChromaDB over FAISS because it supports incremental indexing and doesn't require a separate server process."
```

## Step 3: Process the inbox

If you don't want to wait for the cron job:

```bash
kb process
```

Or use the slash command in Claude Code:

```
/kb-process
```

The agent will:
1. Read each file in inbox/
2. Classify it (article, decision, course, etc.)
3. Create a properly formatted file in the right folder
4. Update `wiki/_index.md`
5. Delete the file from inbox/
6. Git commit and push

## Step 4: Search your knowledge

```bash
kb-search-semantic "ChromaDB vs FAISS"
```

Or in Claude Code:

```
/kb-search "ChromaDB vs FAISS"
```

ChromaDB returns results in milliseconds, ranked by relevance.

## Step 5: Explore in Obsidian

Open `~/Knowledge/` in Obsidian. You'll see:
- A graph view showing connections between your notes
- The `wiki/_index.md` as a table of contents
- All your processed content organized by type

## What's next

- Add a cron job for automatic processing every 15 minutes
- Set up `KB_VAULT` to point to a cloud-synced folder (Google Drive, OneDrive)
- Install the post-commit git hook to capture commits from your projects
- Try `/kb-health` to audit your vault

## Connections

- [[knowledge-base-system]]
- [[chromadb]]
