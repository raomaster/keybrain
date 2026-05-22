---
name: keybrain
description: Use when the user asks to search, consult, save, remember, process, audit, or update their KeyBrain knowledge base. Trigger on phrases like "busca en mi kb", "search my KB", "que se sobre", "guarda esto en KeyBrain", "revisa mi vault", or "check my knowledge base".
---

# KeyBrain

Use KeyBrain as the user's local-first persistent memory and research base.

KeyBrain lives at `${KB_VAULT:-$HOME/Knowledge}` and provides:

- Durable capture with `kb`
- Semantic search with `kb-search-semantic`
- Inbox processing with `kb process`
- Indexing with `kb-index`
- Memory consolidation with `kb-dream`

## Search First

When the user asks to search or consult their KB:

1. Extract the actual search query from the user's request.
2. Run:
   ```bash
   kb-search-semantic "<query>" --results 8
   ```
   If `kb-search-semantic` is not on `PATH`, run:
   ```bash
   ${KB_VAULT:-$HOME/Knowledge}/bin/kb-search-semantic "<query>" --results 8
   ```
3. If semantic search fails with a ChromaDB readonly database error, explain that the agent needs filesystem permission to the KeyBrain vault and retry only if the current environment has that access.
4. Read the most relevant source files when needed.
5. Answer the user's question directly. Cite vault-relative paths when useful.

## Save Durable Knowledge

Save important durable knowledge without asking when:

- The user makes an important technical decision
- You discover a reusable project fact
- You capture a durable user preference
- You finish an investigation whose result should persist across sessions

Use:

```bash
kb "Decision: [what was decided] - Why: [constraints/rationale] - Discarded: [alternatives rejected]"
```

If `kb` is not on `PATH`, run:

```bash
${KB_VAULT:-$HOME/Knowledge}/bin/kb "Decision: [what was decided] - Why: [constraints/rationale] - Discarded: [alternatives rejected]"
```

## Add Content

When the user gives a URL, note, document, transcript, or file that should be remembered:

```bash
kb "text or URL"
kb add /path/to/file
```

Then tell the user what was added and that it will be processed by the configured inbox processor.

## Process And Maintain

Use these only when the user asks:

```bash
kb process
kb status
kb-index --force
kb-dream --days 30
kb update
```

Do not process, rewrite, re-index, or update the whole vault unless the user asks.

## Boundaries

- Prefer KeyBrain search before web search for technical questions that may already be in the vault.
- Do not change scheduled inbox processing flows unless explicitly requested.
- Do not commit or push vault changes unless the user asks.
- If a command fails because the vault is outside the current sandbox, ask for or use the agent's normal filesystem access mechanism rather than inventing a workaround.
