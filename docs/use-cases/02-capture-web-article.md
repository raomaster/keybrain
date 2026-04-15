# Use Case 2: Capture a Web Article

**Goal:** Save an article from the web to your knowledge base.

## Steps

1. Copy the article URL
2. In your terminal:
   ```bash
   kb "https://example.com/interesting-article"
   ```
3. Or use the slash command in Claude Code:
   ```
   /kb-add https://example.com/interesting-article
   ```
4. The article is saved to `inbox/` as a timestamped `.md` file
5. When processed (cron or `kb process`):
   - The agent fetches the full content via WebFetch
   - Creates a file in `raw/articles/` with frontmatter, summary, and full content
   - Adds relevant `[[wikilinks]]` in the Connections section
   - Updates `wiki/_index.md`

## Tips
- You can also use Obsidian Web Clipper to save directly to `inbox/`
- The agent writes a 3-5 paragraph summary highlighting key points
- If the URL is a YouTube video, the agent uses `yt-dlp` to get the transcript
