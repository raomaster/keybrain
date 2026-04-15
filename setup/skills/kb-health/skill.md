---
description: "Audit the Knowledge Base for issues and improvements"
---

Run a complete health check of the Knowledge Base at `${KB_VAULT:-$HOME/Knowledge}/`.

**Audit (check each item):**

### 1. Structural integrity
- Files in `inbox/` that have been unprocessed for more than 1 hour (not `.gitkeep`)
- Files in `raw/` or `decisions/` without complete frontmatter (missing title, date, or tags)
- Broken links in wiki (references to nonexistent files)
- Files whose names don't follow the `YYYY-MM-DD-slug.md` convention

### 2. Index consistency
- Items in `raw/` or `decisions/` not listed in `wiki/_index.md`
- Items in `wiki/_index.md` whose files don't exist
- Update `wiki/_index.md` if there are discrepancies

### 3. Wiki opportunities
- Topics appearing in 3+ articles in `raw/` without a page in `wiki/concepts/` or `wiki/technologies/`
- Suggest the 3 most valuable wiki articles to create based on current content

### 4. Statistics
Show:
```
Vault status:
   Raw articles:    X
   Decisions:       X
   Courses:         X
   Compiled wiki:   X articles
   Pending inbox:   X
   Last commit:     YYYY-MM-DD HH:MM
```

### 5. Automatic actions
- If files have missing frontmatter, add it with available data
- If `wiki/_index.md` has missing items, add them

At the end, list actions taken and suggestions that need your review.

## Connections

- [[knowledge-base-system]]
