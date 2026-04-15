---
title: "Decision: Obsidian + ChromaDB for Knowledge Management"
date: 2026-04-14
status: decided
tags: [decision, tools]
area: "tools"
---

# Decision: Obsidian + ChromaDB for Knowledge Management

## Context

Need a personal knowledge base system that supports: semantic search, visual graph exploration, local-first storage, and AI agent integration. The system must work without cloud services or API keys for basic functionality.

## Options considered

### Visualization / Note-taking
- **Obsidian**: Local markdown files, graph view, extensible, huge plugin ecosystem. Free.
- **Notion**: Cloud-first, great UI but no local-first option. API requires paid plan.
- **Roam Research**: Graph-native but proprietary, expensive ($15/mo), no local-first.
- **Logseq**: Open source, local-first, but smaller ecosystem than Obsidian.

### Semantic Search
- **ChromaDB**: Python, embedded (no server), persistent, supports incremental indexing. MIT license.
- **FAISS**: C++ library, very fast but requires manual index management, no built-in persistence.
- **Pinecone**: Cloud-only, requires API key and paid plan.
- **Weaviate**: Requires running a server, overkill for personal use.

## Decision

**Obsidian + ChromaDB.**

Reasons:
1. **Local-first**: Both store data locally. No cloud dependency for core features.
2. **Zero-config**: ChromaDB runs as a Python library, no server to manage.
3. **Graph view**: Obsidian's graph view makes connections visible from day one.
4. **Incremental indexing**: ChromaDB supports upsert, so we only re-index changed files.
5. **Free**: Both are free and open source.
6. **Agent-friendly**: Markdown files are the natural format for AI agents to read and write.

## Consequences

**Positive:**
- Users can see their knowledge graph grow in real-time
- Semantic search works offline
- No API keys needed for basic functionality
- Obsidian's plugin ecosystem provides extensibility

**Negative:**
- Obsidian requires a desktop app (no mobile-only setup)
- ChromaDB adds a Python dependency
- Graph view requires Obsidian — not visible in plain text editors

## Connections

- [[knowledge-base-system]]
- [[chromadb]]
