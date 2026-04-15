# Use Case 5: Search Your Knowledge Base

**Goal:** Find information stored in your vault.

## Steps

### Semantic search (recommended)
In Claude Code:
```
/kb-search "what do I know about ChromaDB?"
```

Or in terminal:
```bash
kb-search-semantic "ChromaDB vector database" --results 5
```

This returns the most relevant chunks ranked by similarity.

### Filter by type
```bash
kb-search-semantic "machine learning" --type article
kb-search-semantic "architecture decision" --type decision
kb-search-semantic "Python course" --type course
```

### Browse manually
```bash
cat ~/Knowledge/wiki/_index.md
```

The index lists everything by category with links to the full files.

## How it works

1. `kb-index` scans all `.md` files in the vault
2. Splits content into chunks (1200 chars, 150 char overlap)
3. Stores chunks in ChromaDB with metadata (title, date, type, tags)
4. When you search, ChromaDB finds the closest matching chunks
5. The agent reads the full source files and synthesizes an answer

## Tips
- Run `kb-index` after adding content manually (cron does this automatically)
- Use `kb-index --force` to re-index everything
- ChromaDB stores data locally in `$VAULT/.chromadb/`
