---
description: "Add content to the KeyBrain Knowledge Base inbox"
---

Add the following to the Knowledge Base inbox at `${KB_VAULT:-$HOME/Knowledge}/inbox/`:

**Input:** $ARGUMENTS

**Process:**

1. Determine the input type:
   - **URL**: save as `YYYYMMDD-HHMMSS.md` with the URL and a note to process later
   - **Text/idea**: save as `YYYYMMDD-HHMMSS.md` with the text
   - **File path**: copy the file to inbox/ with its original name
   - **No input**: ask the user what they want to add

2. File format:
   ```markdown
   # [User input or extracted title]

   Date: YYYY-MM-DD HH:MM

   [Full content or URL]
   ```

3. Confirm what you saved and which file

4. Remind the user that the cron processes the inbox automatically every 15 minutes, or they can force it with `/kb-process`

If the input is a URL, try to fetch the content to save it fully in the file (easier to process later).

## Connections

- [[knowledge-base-system]]
