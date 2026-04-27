#!/usr/bin/env bash
# process-inbox.sh — Called by cron every 15 minutes
# 1. Checks if inbox has new files
# 2. Calls Claude to classify and archive them
# 3. Re-index ChromaDB
#
# Git is opt-in — the vault may live in Google Drive, OneDrive, or any other
# backup system. Set env vars to enable:
#   KB_AUTO_COMMIT=true   commit changes locally after processing
#   KB_AUTO_PUSH=true     also push to remote (requires KB_AUTO_COMMIT=true)

set -euo pipefail

VAULT="${KB_VAULT:-$HOME/Knowledge}"
LOG="$VAULT/logs/process.log"
CLAUDE_BIN="${CLAUDE_BIN:-$(command -v claude 2>/dev/null || echo "$HOME/.local/bin/claude")}"
KB_AUTO_COMMIT="${KB_AUTO_COMMIT:-false}"
KB_AUTO_PUSH="${KB_AUTO_PUSH:-false}"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG" 2>/dev/null || echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Ensure log dir exists
mkdir -p "$VAULT/logs"

# Check if inbox has real files (not just .gitkeep)
FILE_COUNT=$(find "$VAULT/inbox" -type f ! -name '.gitkeep' 2>/dev/null | wc -l | tr -d ' ')

if [ "$FILE_COUNT" -eq 0 ]; then
  exit 0
fi

log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Processing $FILE_COUNT file(s) in inbox..."

# Call Claude non-interactive to process inbox
"$CLAUDE_BIN" \
  --print "Process the files in inbox/ following exactly the instructions in CLAUDE.md. For each file: classify it, create the destination file with correct frontmatter and full content, update wiki/_index.md, and delete the file from inbox/ (leave .gitkeep intact). When done, report what you processed and where each file was placed." \
  --cwd "$VAULT" \
  --allowedTools "Read,Write,Edit,Bash,Glob,Grep,WebFetch" \
  >> "$LOG" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  log "ERROR: Claude exited with code $EXIT_CODE"
fi

log "Claude processing complete."

# Git sync (opt-in)
if [ "$KB_AUTO_COMMIT" = "true" ]; then
  cd "$VAULT"
  git add -A
  if ! git diff --cached --quiet; then
    COMMIT_MSG="kb: auto-processed $(date '+%Y-%m-%d %H:%M')"
    git commit -m "$COMMIT_MSG"
    log "Committed locally: $COMMIT_MSG"
    if [ "$KB_AUTO_PUSH" = "true" ]; then
      if git push 2>> "$LOG"; then
        log "Pushed to remote."
      else
        log "WARNING: Push failed. Commit saved locally."
      fi
    fi
  else
    log "No changes to commit."
  fi
fi

# Re-index ChromaDB
PYTHON_VENV="$VAULT/.venv/bin/python3"
if [ -f "$PYTHON_VENV" ]; then
  log "Re-indexing ChromaDB..."
  "$PYTHON_VENV" "$VAULT/bin/kb-index.py" >> "$LOG" 2>&1
  log "ChromaDB updated."
fi

log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
