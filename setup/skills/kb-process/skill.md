---
description: "Process the inbox — classify, archive"
---

Process all new files in `${KB_VAULT:-$HOME/Knowledge}/inbox/` following exactly the instructions in `${KB_VAULT:-$HOME/Knowledge}/CLAUDE.md`.

**Steps:**

1. Read `${KB_VAULT:-$HOME/Knowledge}/CLAUDE.md` to review the classification rules
2. List all files in `${KB_VAULT:-$HOME/Knowledge}/inbox/` (ignore `.gitkeep`)
3. For each file:
   - Determine type (article, decision, course, research, project, conversation)
   - Create destination file with correct frontmatter and naming `YYYY-MM-DD-slug.md`
   - Include full content + summary
   - Delete the file from inbox when processed
4. Update `${KB_VAULT:-$HOME/Knowledge}/wiki/_index.md` with new items
5. If there are recurring concepts or technologies, create or update articles in `${KB_VAULT:-$HOME/Knowledge}/wiki/`
6. Show a summary: what you processed and where each item was placed

Do NOT commit or push automatically. The vault may not have a remote configured, and the user may not want to commit all files. If the user wants to publish, they can run:
```bash
cd ${KB_VAULT:-$HOME/Knowledge} && git add -A && git commit -m "kb: processed inbox" && git push
```

If the inbox is empty, say so and suggest how to add content (`kb "text"` or `kb add file`).

## Connections

- [[knowledge-base-system]]
