#!/usr/bin/env bash
# process-inbox.sh — Called by cron every 15 minutes
# 1. Checks if inbox has new files
# 2. Calls the configured agent to classify and archive them
# 3. Re-index ChromaDB
#
# Git is opt-in — the vault may live in Google Drive, OneDrive, or any other
# backup system. Set env vars to enable:
#   KB_PROCESS_AGENT=opencode  use OpenCode for inbox processing (default)
#   KB_PROCESS_AGENT=claude    use Claude Code for inbox processing
#   KB_PROCESS_MODEL=provider/model  model for the inbox processor cron
#   KB_PROCESS_VARIANT=minimal|low|high|max  OpenCode model variant (optional)
#   KB_PROCESS_EFFORT=low|medium|high|xhigh|max  Claude Code effort (optional)
#   KB_PROCESS_MAX_BUDGET_USD=0.25  Claude Code print-mode budget cap (optional)
#   KB_AUTO_COMMIT=true   commit changes locally after processing
#   KB_AUTO_PUSH=true     also push to remote (requires KB_AUTO_COMMIT=true)

set -euo pipefail

VAULT="${KB_VAULT:-$HOME/Knowledge}"
VENV="${KB_VENV:-$VAULT/.venv}"
LOG="$VAULT/logs/process.log"
KB_PROCESS_AGENT="${KB_PROCESS_AGENT:-opencode}"
OPENCODE_BIN="${OPENCODE_BIN:-$(command -v opencode 2>/dev/null || echo "$HOME/.opencode/bin/opencode")}"
CLAUDE_BIN="${CLAUDE_BIN:-$(command -v claude 2>/dev/null || echo "$HOME/.local/bin/claude")}"
KB_PROCESS_MODEL="${KB_PROCESS_MODEL:-}"
KB_PROCESS_VARIANT="${KB_PROCESS_VARIANT:-}"
KB_PROCESS_EFFORT="${KB_PROCESS_EFFORT:-}"
KB_PROCESS_MAX_BUDGET_USD="${KB_PROCESS_MAX_BUDGET_USD:-}"
KB_AUTO_COMMIT="${KB_AUTO_COMMIT:-false}"
KB_AUTO_PUSH="${KB_AUTO_PUSH:-false}"
PROCESS_PROMPT="Process the files in inbox/ following exactly the instructions in CLAUDE.md. For each file: classify it, create the destination file with correct frontmatter and full content, update wiki/_index.md, and delete the file from inbox/ (leave .gitkeep intact). When done, report what you processed and where each file was placed."

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
log "Processing $FILE_COUNT file(s) in inbox with $KB_PROCESS_AGENT..."
[ -n "$KB_PROCESS_MODEL" ] && log "Model: $KB_PROCESS_MODEL"
[ -n "$KB_PROCESS_VARIANT" ] && log "OpenCode variant: $KB_PROCESS_VARIANT"
[ -n "$KB_PROCESS_EFFORT" ] && log "Claude effort: $KB_PROCESS_EFFORT"
[ -n "$KB_PROCESS_MAX_BUDGET_USD" ] && log "Claude max budget: \$$KB_PROCESS_MAX_BUDGET_USD"

EXIT_CODE=0

case "$KB_PROCESS_AGENT" in
  opencode)
    OPENCODE_ARGS=(
      run
      --dir "$VAULT" \
      --dangerously-skip-permissions \
      --title "KeyBrain inbox processing"
    )
    [ -n "$KB_PROCESS_MODEL" ] && OPENCODE_ARGS+=(--model "$KB_PROCESS_MODEL")
    [ -n "$KB_PROCESS_VARIANT" ] && OPENCODE_ARGS+=(--variant "$KB_PROCESS_VARIANT")
    set +e
    "$OPENCODE_BIN" "${OPENCODE_ARGS[@]}" "$PROCESS_PROMPT" >> "$LOG" 2>&1
    EXIT_CODE=$?
    set -e
    ;;
  claude)
    CLAUDE_ARGS=(
      --print
      --cwd "$VAULT" \
      --allowedTools "Read,Write,Edit,Bash,Glob,Grep,WebFetch"
    )
    [ -n "$KB_PROCESS_MODEL" ] && CLAUDE_ARGS+=(--model "$KB_PROCESS_MODEL")
    [ -n "$KB_PROCESS_EFFORT" ] && CLAUDE_ARGS+=(--effort "$KB_PROCESS_EFFORT")
    [ -n "$KB_PROCESS_MAX_BUDGET_USD" ] && CLAUDE_ARGS+=(--max-budget-usd "$KB_PROCESS_MAX_BUDGET_USD")
    set +e
    "$CLAUDE_BIN" "${CLAUDE_ARGS[@]}" "$PROCESS_PROMPT" >> "$LOG" 2>&1
    EXIT_CODE=$?
    set -e
    ;;
  *)
    log "ERROR: unsupported KB_PROCESS_AGENT: $KB_PROCESS_AGENT"
    exit 1
    ;;
esac

if [ $EXIT_CODE -ne 0 ]; then
  log "ERROR: $KB_PROCESS_AGENT exited with code $EXIT_CODE"
  log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  exit $EXIT_CODE
fi

log "$KB_PROCESS_AGENT processing complete."

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
PYTHON_VENV="$VENV/bin/python3"
[ ! -f "$PYTHON_VENV" ] && PYTHON_VENV="$VENV/Scripts/python.exe"
if [ -f "$PYTHON_VENV" ]; then
  log "Re-indexing ChromaDB..."
  "$PYTHON_VENV" "$VAULT/bin/kb-index.py" >> "$LOG" 2>&1
  log "ChromaDB updated."
fi

log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
