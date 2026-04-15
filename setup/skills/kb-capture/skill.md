---
description: "Capture an intelligent session summary to the Knowledge Base"
---

Generate a summary of this work session and save it to `${KB_VAULT:-$HOME/Knowledge}/inbox/`.

**Process:**

1. Review what was done this session: files modified, decisions made, problems solved, technologies used

2. If in a git project, get context:
   ```bash
   git log --oneline -10
   git diff HEAD~3 --stat 2>/dev/null
   ```

3. Generate a file in inbox with this format:
   ```markdown
   ---
   title: "Session: [project] — [date]"
   date: [date]
   tags: [session, [project], [mentioned technologies]]
   ---

   # Session: [project] — [date]

   ## What was done
   [3-5 concrete points]

   ## Decisions made
   - [decision 1 with context]
   - [decision 2 with context]

   ## Problems solved
   - [problem and solution]

   ## Next steps
   - [what remains]
   ```

4. Save the file:
   ```bash
   cat > ${KB_VAULT:-$HOME/Knowledge}/inbox/$(date +%Y%m%d-%H%M%S)-session-[project].md << 'EOF'
   [content]
   EOF
   ```

5. Confirm what you saved with a 2-line summary.

Be concrete and direct — capture only what's worth remembering in 6 months.

## Connections

- [[knowledge-base-system]]
