---
description: "Consolidate episodic memory into MEMORY.md and raw/memory-derived/"
---

Run the dreaming process over the last $ARGUMENTS days (default: 30) of memory files.

**Process:**

1. Run kb-dream:
   ```bash
   ${KB_VAULT:-$HOME/Knowledge}/bin/kb-dream --days ${ARGUMENTS:-30}
   ```

2. Report what was promoted:
   - How many claims are now in `MEMORY.md`
   - How many new files in `raw/memory-derived/`
   - How many skipped (dedupe)

3. If there are new files in `raw/memory-derived/`, list them with their title and confidence.

## Connections

- [[knowledge-base-system]]
- [[memory-system]]
