# KeyBrain Install Prompt

Copy-paste the following to your AI agent (Claude Code, Copilot, Cursor, Gemini CLI):

---

```
I want to install KeyBrain, an AI-powered personal knowledge base.

Please do the following:

1. Clone the KeyBrain repository:
   git clone https://github.com/your-org/keybrain.git /tmp/keybrain-install

2. Run the installer:
   bash /tmp/keybrain-install/setup/install.sh

3. The installer will:
   - Ask where to install (default: ~/Knowledge, or any path like ~/Google Drive/Knowledge)
   - Install dependencies (Git, Node.js, Python 3.12, Obsidian, markitdown)
   - Create a Python virtual environment with ChromaDB
   - Set up CLI commands (kb, kb-search-semantic, kb-index)
   - Install Claude Code skills
   - Configure permissions

4. After installation, please also:
   - Configure a cron job to run $KB_VAULT/bin/process-inbox.sh every 15 minutes
   - Index the vault: kb-index

5. Verify everything works:
   - kb status (should show "Inbox: 0 pending file(s)")
   - kb-index (should index the initial content)

That's it! My vault should be ready.
```

---

**For Windows users:** Replace step 2 with:
```
Set-ExecutionPolicy RemoteSigned; .\tmp\keybrain-install\setup\install.ps1
```

**Custom path:** If you want the vault somewhere other than `~/Knowledge`, the installer will ask. Or set before running:
```bash
export KB_VAULT="/path/to/your/vault"
```
