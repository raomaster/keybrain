---
description: "Compile and update the wiki from all raw content"
---

Compile and update the wiki at `${KB_VAULT:-$HOME/Knowledge}/wiki/`.

**The wiki is distilled knowledge — not raw notes. You maintain it, the user doesn't touch it.**

**Process:**

1. Read current wiki state:
   - `${KB_VAULT:-$HOME/Knowledge}/wiki/_index.md`
   - All files in `${KB_VAULT:-$HOME/Knowledge}/wiki/concepts/` and `${KB_VAULT:-$HOME/Knowledge}/wiki/technologies/`

2. Read all source content:
   - `${KB_VAULT:-$HOME/Knowledge}/raw/articles/`
   - `${KB_VAULT:-$HOME/Knowledge}/raw/research/`
   - `${KB_VAULT:-$HOME/Knowledge}/raw/courses/`
   - `${KB_VAULT:-$HOME/Knowledge}/decisions/`

3. For each topic appearing in 2+ sources:
   - If no wiki article exists: create one in `wiki/concepts/` or `wiki/technologies/`
   - If it exists: update with new information, keep what's already good

4. Structure of each wiki article:
   ```markdown
   ---
   title: "Concept/Technology Name"
   updated: YYYY-MM-DD
   tags: [wiki, concept/technology]
   sources: X
   ---

   # Name

   ## What it is
   [clear, concise explanation]

   ## Why it matters (for this vault)
   [personal relevance, connection to projects or decisions]

   ## Resources in vault
   - [Article](../../raw/articles/...)
   - [Related decision](../../decisions/...)

   ## Connections
   - [[Related concept 1]]
   - [[Related concept 2]]
   ```

5. Update `wiki/_index.md` with all new/updated articles

6. Commit:
   ```bash
   cd ${KB_VAULT:-$HOME/Knowledge} && git add wiki/ && git commit -m "wiki: compiled from $(date '+%Y-%m-%d')" && git push
   ```

Report what articles you created, which you updated, and which are on your radar for future compilations.

## Connections

- [[knowledge-base-system]]
