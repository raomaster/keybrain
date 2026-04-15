# Use Case 1: Install KeyBrain from Scratch

**Goal:** Get KeyBrain running on a new machine.

## Steps

1. Copy the install prompt from `INSTALL-PROMPT.md`
2. Paste it to your AI agent (Claude Code, Copilot, Cursor)
3. The agent will:
   - Detect your OS (macOS/Linux/Windows)
   - Ask where to install (default: `~/Knowledge`)
   - Install dependencies (Git, Node.js, Python 3.12, Obsidian, yt-dlp)
   - Create the vault structure
   - Set up ChromaDB
   - Install skills
   - Configure permissions
4. After installation, configure auto-processing:
   ```
   "Configure a cron job to run $KB_VAULT/bin/process-inbox.sh every 15 minutes."
   ```
5. Verify: `kb status` should show "Inbox: 0 pending file(s)"

## Tips
- On macOS, install Homebrew first if you don't have it
- On Windows, ensure `winget` is available (install "App Installer" from Microsoft Store)
- To install in a cloud-synced folder, specify the path when prompted (e.g., `~/Google Drive/Knowledge`)
