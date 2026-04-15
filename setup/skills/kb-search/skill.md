---
description: "Search the Knowledge Base semantically and respond with relevant context"
---

Search the Knowledge Base about: **$ARGUMENTS**

**Process:**

1. Run semantic search in ChromaDB:
   ```bash
   kb-search-semantic "$ARGUMENTS" --results 8
   ```

2. Read the full source files of the most relevant chunks returned (max 4 files)

3. If ChromaDB is empty or fails, search directly:
   - Read `${KB_VAULT:-$HOME/Knowledge}/wiki/_index.md`
   - Use Grep over `${KB_VAULT:-$HOME/Knowledge}/` to find the term

4. Synthesize the answer based on found content — don't list files, **answer the question**

5. Cite sources with paths relative to the vault

6. If the topic isn't in the vault, say so and suggest adding it with `kb "URL or text"`

If no query is provided ($ARGUMENTS empty), show statistics:
```bash
kb-search-semantic --results 0  # just shows count
```
And list the 5 most recent items by category from `wiki/_index.md`.

## Connections

- [[knowledge-base-system]]
- [[chromadb]]
