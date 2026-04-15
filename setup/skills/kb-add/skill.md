---
description: "Add content to the KeyBrain Knowledge Base inbox"
---

Add the following to the Knowledge Base inbox at `${KB_VAULT:-$HOME/Knowledge}/inbox/`:

**Input:** $ARGUMENTS

**Process:**

1. Determine the input type:

   - **YouTube URL** (contains `youtube.com` or `youtu.be`):
     1. Run markitdown to extract metadata and transcript:
        ```bash
        python3 -c "
        from markitdown import MarkItDown
        md = MarkItDown()
        result = md.convert('$ARGUMENTS')
        print(result.text_content)
        " > "$KB_VAULT/inbox/$(date +%Y%m%d-%H%M%S)-youtube.md"
        ```
     2. Confirm the file was saved and tell the user it will be processed shortly.
     3. Launch background processing:
        ```bash
        cd "$KB_VAULT" && nohup bash bin/process-inbox.sh &>/dev/null &
        ```
     4. When background processing completes, tell the user the content has been archived with connections.

   - **Other URL**: save as `YYYYMMDD-HHMMSS.md` with the URL and a note to process later. Try to fetch the content to save it fully in the file.

   - **Text/idea**: save as `YYYYMMDD-HHMMSS.md` with the text.

   - **File path**: copy the file to inbox/ with its original name.

   - **No input**: ask the user what they want to add.

2. File format for non-YouTube URLs and text:
   ```markdown
   # [User input or extracted title]

   Date: YYYY-MM-DD HH:MM

   [Full content or URL]
   ```

3. Confirm what you saved and which file.

## Connections

- [[knowledge-base-sistema]]
