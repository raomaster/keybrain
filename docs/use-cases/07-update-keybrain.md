# Use Case 7: Update KeyBrain

**Goal:** Get the latest framework improvements without losing your content.

## Steps

1. In your terminal:
   ```bash
   kb update
   ```
2. The update checks GitHub for the latest release
3. If an update is available, it shows what will change
4. Confirm to update
5. The update only touches framework files:
   - `bin/`, `setup/`, `templates/`
   - `CLAUDE.md`, `README.md`, `INSTALL-PROMPT.md`
   - `CONTRIBUTING.md`, `CHANGELOG.md`, `requirements.txt`
6. Your content is never touched:
   - `raw/`, `wiki/`, `decisions/`, `inbox/`, `conversations/`
   - `VERSION` (updated only on confirmation)

## What gets updated

| Updated | Not touched |
|---------|-------------|
| CLI scripts | Your articles |
| Install scripts | Your decisions |
| Templates | Your wiki |
| CLAUDE.md | Your inbox |
| Skills | Your conversations |

## Tips
- The agent notifies you when an update is available
- You can always check your version: `cat $KB_VAULT/VERSION`
- If something breaks after updating, check the CHANGELOG
