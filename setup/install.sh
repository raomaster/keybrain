#!/bin/bash
# ============================================================
# KeyBrain — Setup Script (macOS / Linux / WSL2)
# ============================================================
# Usage: bash setup/install.sh
#   --vault-path PATH   Set vault location (default: $HOME/Knowledge)
#   --skip-obsidian     Skip Obsidian installation
#   --non-interactive   No prompts (for CI)
# ============================================================

set -e

VAULT_DIR="$HOME/Knowledge"
NON_INTERACTIVE=false
SKIP_OBSIDIAN=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_REPO_DIR="$(dirname "$SCRIPT_DIR")"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()    { echo -e "${GREEN}[KB]${NC} $*"; }
warn()   { echo -e "${YELLOW}[KB WARN]${NC} $*"; }
error()  { echo -e "${RED}[KB ERROR]${NC} $*"; exit 1; }
step()   { echo -e "\n${GREEN}━━━ $* ━━━${NC}"; }

# ── Feature functions (testable via source) ─────────────

create_user_md_template() {
  local claude_dir="$1"
  local user_md="$claude_dir/USER.md"
  if [ -d "$claude_dir" ] && [ ! -f "$user_md" ]; then
    cat > "$user_md" << 'USEREOF'
---
# USER.md — [Your Name]
# Read on-demand, not every prompt.
---

identity:
  name: [Your Name]
  role: [e.g. "Senior Software Engineer", "Data Scientist"]

expertise: [python, typescript, react]

projects:
  main: [~/Code/myproject]

style:
  expects: [peer-level technical, options with tradeoffs]
  dislikes: [over-explanation, unsolicited refactors]
USEREOF
    log "USER.md template created at $user_md — edit it with your info."
  else
    log "USER.md already exists or Claude Code not detected, skipping."
  fi
}

install_openclaw_skills() {
  local skills_src="$1"
  local openclaw_dir="$2"
  local openclaw_skills_dir="$openclaw_dir/workspace/skills"
  mkdir -p "$openclaw_skills_dir"
  if cp -r "$skills_src/"* "$openclaw_skills_dir/"; then
    find "$openclaw_skills_dir" -name "skill.md" -type f -execdir mv {} SKILL.md \;
    log "OpenClaw skills installed to $openclaw_skills_dir"
    return 0
  else
    warn "Could not copy skills to OpenClaw. Check permissions on $openclaw_skills_dir"
    return 1
  fi
}

configure_openclaw_agents_md() {
  local openclaw_dir="$1"
  local agents_md="$openclaw_dir/workspace/AGENTS.md"
  mkdir -p "$(dirname "$agents_md")"
  if ! grep -q "KeyBrain" "$agents_md" 2>/dev/null; then
    cat >> "$agents_md" << 'AGENTSEOF'

## KeyBrain
When making an important technical decision, save it without asking: `kb "Decision: [what] — Why: [reason] — Rejected: [alternatives]"`
After executing a Superpowers plan, export the file: `kb add docs/superpowers/plans/[plan].md`
KeyBrain KB at `$KB_VAULT` with ChromaDB — use `kb-search-semantic "query"` before answering technical questions that might be in the vault.
AGENTSEOF
    log "Global OpenClaw AGENTS.md configured."
  else
    log "OpenClaw AGENTS.md already has KeyBrain instructions."
  fi
}

configure_copilot_instructions() {
  local copilot_file="$1"
  mkdir -p "$(dirname "$copilot_file")"
  if ! grep -q "KeyBrain" "$copilot_file" 2>/dev/null; then
    cat >> "$copilot_file" << 'COPILOTEOF'

## KeyBrain
When making an important technical decision, save it without asking: `kb "Decision: [what] — Why: [reason] — Rejected: [alternatives]"`
KeyBrain KB at `$KB_VAULT` with ChromaDB — use `kb-search-semantic "query"` before answering technical questions that might be in the vault.
After executing a Superpowers plan, export the file: `kb add docs/superpowers/plans/[plan].md`
COPILOTEOF
    log "GitHub Copilot instructions configured at $copilot_file"
  else
    log "Copilot instructions already have KeyBrain."
  fi
}

configure_jetbrains_ai() {
  local rules_dir="$1"
  local rules_file="$rules_dir/keybrain.md"
  mkdir -p "$rules_dir"
  if [ ! -f "$rules_file" ]; then
    cat > "$rules_file" << 'JBEOF'
## KeyBrain
When making an important technical decision, save it without asking: `kb "Decision: [what] — Why: [reason] — Rejected: [alternatives]"`
KeyBrain KB at `$KB_VAULT` with ChromaDB — use `kb-search-semantic "query"` before answering technical questions that might be in the vault.
After executing a Superpowers plan, export the file: `kb add docs/superpowers/plans/[plan].md`
JBEOF
    log "JetBrains AI rules configured at $rules_file"
  else
    log "JetBrains AI rules already exist."
  fi
}

# Guard: stop execution when sourced (e.g., by tests)
[[ "${BASH_SOURCE[0]}" != "${0}" ]] && return 0

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --vault-path)    VAULT_DIR="$2"; shift 2 ;;
    --skip-obsidian) SKIP_OBSIDIAN=true; shift ;;
    --non-interactive) NON_INTERACTIVE=true; shift ;;
    *) error "Unknown option: $1" ;;
  esac
done

# ── Detect OS ──────────────────────────────────────────────
OS="$(uname -s)"
if grep -qi microsoft /proc/version 2>/dev/null; then
  PLATFORM="wsl2"
elif echo "$OS" | grep -qiE "mingw|msys|cygwin"; then
  PLATFORM="gitbash"
elif [ "$OS" = "Darwin" ]; then
  PLATFORM="macos"
elif [ "$OS" = "Linux" ]; then
  PLATFORM="linux"
else
  error "Unsupported OS: $OS. Use install.ps1 on Windows."
fi

log "Detected platform: $PLATFORM"

# ── Interactive vault path ─────────────────────────────────
if [ "$NON_INTERACTIVE" = false ]; then
  echo ""
  echo "Where should KeyBrain be installed?"
  echo "  (e.g. $HOME/Knowledge, $HOME/Google Drive/My Drive/Knowledge)"
  read -r -p "Path [Enter for $VAULT_DIR]: " USER_PATH
  VAULT_DIR="${USER_PATH:-$VAULT_DIR}"
fi

# ── 1. Homebrew (macOS) ────────────────────────────────────
if [ "$PLATFORM" = "macos" ]; then
  step "Homebrew"
  if ! command -v brew &>/dev/null; then
    log "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  else
    log "Homebrew already installed: $(brew --version | head -1)"
  fi
fi

# ── 2. Git ─────────────────────────────────────────────────
step "Git"
if ! command -v git &>/dev/null; then
  if [ "$PLATFORM" = "macos" ]; then
    brew install git
  else
    sudo apt-get install -y git || sudo yum install -y git
  fi
else
  log "Git already installed: $(git --version)"
fi

# ── 3. Node.js + Claude Code CLI ───────────────────────────
step "Claude Code CLI"
if ! command -v node &>/dev/null; then
  if [ "$PLATFORM" = "macos" ]; then
    brew install node
  elif [ "$PLATFORM" = "gitbash" ]; then
    warn "Node.js not found. Install manually from nodejs.org if you want Claude Code."
  else
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
  fi
fi

if ! command -v claude &>/dev/null; then
  if [ "$PLATFORM" = "gitbash" ]; then
    warn "Claude Code not found. Install it manually or use GitHub Copilot / JetBrains AI instead."
  else
    log "Installing Claude Code..."
    npm install -g @anthropic-ai/claude-code 2>/dev/null || {
      warn "npm not available. Install Claude Code manually from: https://claude.ai/code"
    }
  fi
else
  log "Claude Code already installed: $(claude --version 2>/dev/null || echo 'ok')"
fi

# ── 4. Obsidian ────────────────────────────────────────────
if [ "$SKIP_OBSIDIAN" = false ]; then
  step "Obsidian"
  if [ "$PLATFORM" = "macos" ]; then
    if ! [ -d "/Applications/Obsidian.app" ]; then
      log "Installing Obsidian..."
      brew install --cask obsidian
    else
      log "Obsidian already installed."
    fi
  elif [ "$PLATFORM" = "wsl2" ]; then
    warn "Install Obsidian on the Windows side, then open the vault from there."
  else
    warn "Install Obsidian manually from: https://obsidian.md"
  fi
fi

# ── 5. markitdown (YouTube + document processing) ──────────
# markitdown is installed via requirements.txt in the Python venv (see step 6)
log "markitdown: will be installed via pip install -r requirements.txt"

# ── 6. Python 3.12 + venv + deps ──────────────────────────
step "Python 3.12 + dependencies"
if [ "$PLATFORM" = "gitbash" ]; then
  PYTHON_BIN="$(command -v python3 2>/dev/null || command -v python 2>/dev/null)"
  if [ -z "$PYTHON_BIN" ]; then
    error "Python not found. Install Python 3.12+ from python.org and re-run."
  fi
else
  PYTHON_BIN="$(command -v python3.12 || command -v python3)"
fi
VENV_DIR="$VAULT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
  log "Creating venv in $VENV_DIR..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

log "Installing Python dependencies..."
"$VENV_DIR/bin/pip" install -r "$VAULT_REPO_DIR/requirements.txt" --quiet
log "ChromaDB: $($VENV_DIR/bin/python3 -c 'import chromadb; print(chromadb.__version__)' 2>/dev/null || echo 'installed')"

# ── 7. Copy vault to target path ───────────────────────────
step "Setting up vault at $VAULT_DIR"
if [ "$VAULT_REPO_DIR" != "$VAULT_DIR" ]; then
  if [ -d "$VAULT_DIR" ]; then
    warn "$VAULT_DIR already exists. Not overwriting."
  else
    log "Copying vault to $VAULT_DIR..."
    cp -r "$VAULT_REPO_DIR" "$VAULT_DIR"
  fi
else
  log "Already at vault: $VAULT_DIR"
fi

mkdir -p "$VAULT_DIR/memory"
touch "$VAULT_DIR/memory/.gitkeep"
mkdir -p "$VAULT_DIR/raw/memory-derived"
touch "$VAULT_DIR/raw/memory-derived/.gitkeep"
if [ ! -f "$VAULT_DIR/MEMORY.md" ]; then
  printf "# Memory\n_Updated: never — run kb-dream to populate_\n" > "$VAULT_DIR/MEMORY.md"
fi

# ── 8. Script permissions ──────────────────────────────────
step "Execution permissions"
chmod +x "$VAULT_DIR/bin/kb" "$VAULT_DIR/bin/process-inbox.sh"
chmod +x "$VAULT_DIR/bin/kb-index" "$VAULT_DIR/bin/kb-search-semantic"
chmod +x "$VAULT_DIR/bin/kb-import-chatgpt" "$VAULT_DIR/bin/kb-update"
chmod +x "$VAULT_DIR/bin/kb-dream"
log "Scripts are executable."

# ── 9. PATH + KB_VAULT in shell ────────────────────────────
step "Adding bin/ to PATH and setting KB_VAULT"
SHELL_RC="$HOME/.zshrc"
if [ "$SHELL" = "/bin/bash" ] || [ "$PLATFORM" = "gitbash" ]; then
  SHELL_RC="$HOME/.bashrc"
fi

if ! grep -q "KB_VAULT" "$SHELL_RC" 2>/dev/null; then
  echo '' >> "$SHELL_RC"
  echo '# KeyBrain' >> "$SHELL_RC"
  echo "export KB_VAULT=\"$VAULT_DIR\"" >> "$SHELL_RC"
  echo 'export PATH="$KB_VAULT/bin:$PATH"' >> "$SHELL_RC"
  log "KB_VAULT and PATH added to $SHELL_RC"
else
  log "KB_VAULT already configured."
fi

# ── 10. Claude Code skills ─────────────────────────────────
step "Installing Claude Code skills"
COMMANDS_DIR="$HOME/.claude/commands"
mkdir -p "$COMMANDS_DIR"

SKILLS_SRC="$VAULT_DIR/setup/skills"
if [ -d "$SKILLS_SRC" ]; then
  cp -r "$SKILLS_SRC/"* "$COMMANDS_DIR/"
  log "Skills installed to $COMMANDS_DIR"
fi

# ── 10b. USER.md template ─────────────────────────────────
step "Creating USER.md template"
create_user_md_template "$HOME/.claude"

# ── 10c. OpenClaw skills ───────────────────────────────────
step "Installing KeyBrain skills in OpenClaw"
OPENCLAW_DETECTED=false
if [ -d "$HOME/.openclaw" ] || command -v openclaw &>/dev/null; then
  OPENCLAW_DETECTED=true
fi
if [ "$OPENCLAW_DETECTED" = true ]; then
  install_openclaw_skills "$SKILLS_SRC" "$HOME/.openclaw"
else
  log "OpenClaw not detected, skipping."
fi

# ── 11. Claude Code global CLAUDE.md ───────────────────────
step "Configuring global Claude Code instructions"
CLAUDE_DIR="$HOME/.claude"
mkdir -p "$CLAUDE_DIR"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"

if ! grep -q "KeyBrain" "$CLAUDE_MD" 2>/dev/null; then
  cat >> "$CLAUDE_MD" << 'CLAUDEEOF'

# Global

When making an important technical decision, save it without asking: `kb "Decision: [what] — Why: [reason] — Rejected: [alternatives]"`
After executing a Superpowers plan, export the file: `kb add docs/superpowers/plans/[plan].md`
KeyBrain KB at `$KB_VAULT` with ChromaDB — use `kb-search-semantic "query"` before answering technical questions that might be in the vault.
Read `~/.claude/USER.md` only when needing project/user context orientation.
memory:
  write: "During session, append claims to memory/YYYY-MM-DD.md (incremental, not only at end)"
  format: "- claim: \"...\"\n  memory_type: user-rule|user-preference|decision|technical-finding|temporary-context\n  confidence: low|medium|high\n  context: \"...\""
  load: "Read MEMORY.md at session start for behavioral context"
CLAUDEEOF
  log "Global CLAUDE.md configured."
else
  log "Global CLAUDE.md already has KeyBrain instructions."
fi

# ── 11b. OpenClaw AGENTS.md ───────────────────────────────
step "Configuring global OpenClaw instructions"
if [ "$OPENCLAW_DETECTED" = true ]; then
  configure_openclaw_agents_md "$HOME/.openclaw"
else
  log "OpenClaw not detected, skipping."
fi

# ── 12. Claude Code settings.json ──────────────────────────
step "Configuring automatic permissions for the vault"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"

if [ ! -f "$SETTINGS_FILE" ]; then
  cat > "$SETTINGS_FILE" << SETTINGSEOF
{
  "permissions": {
    "allow": [
      "Edit($VAULT_DIR/**)",
      "Write($VAULT_DIR/**)",
      "Read($VAULT_DIR/**)",
      "Bash(cd $VAULT_DIR*)",
      "Bash(ls $VAULT_DIR*)",
      "Bash(find $VAULT_DIR*)",
      "Bash(git -C $VAULT_DIR*)",
      "Bash(grep $VAULT_DIR*)",
      "Bash(python3 $VAULT_DIR/bin*)",
      "Bash($VAULT_DIR/.venv/bin/python3*)"
    ]
  }
}
SETTINGSEOF
  log "settings.json created with vault permissions."
elif ! grep -q "permissions" "$SETTINGS_FILE" 2>/dev/null; then
  warn "settings.json exists but has no vault permissions. Add them manually."
else
  log "settings.json already has permissions configured."
fi

# ── 13. Git repo ───────────────────────────────────────────
step "Git repo"
cd "$VAULT_DIR"
if [ ! -d ".git" ]; then
  git init
  git add -A
  git commit -m "init: KeyBrain knowledge vault"
  log "Git initialized."
  echo ""
  warn "To connect with GitHub:"
  warn "  1. Install gh CLI: brew install gh"
  warn "  2. Authenticate: gh auth login"
  warn "  3. Create repo: gh repo create keybrain-vault --private --source=. --remote=origin --push"
else
  log "Git already initialized."
fi

# ── 14. SSH for GitHub ─────────────────────────────────────
step "Verifying SSH for GitHub"
if ! ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null; then
  warn "Could not add GitHub to known_hosts. Check your connection."
fi

# ── 15. Open Obsidian ──────────────────────────────────────
if [ "$SKIP_OBSIDIAN" = false ] && [ "$PLATFORM" = "macos" ] && [ -d "/Applications/Obsidian.app" ]; then
  step "Opening vault in Obsidian"
  log "Opening Obsidian with vault..."
  open -a Obsidian "$VAULT_DIR" 2>/dev/null || true
fi

# ── Summary ────────────────────────────────────────────────
echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│  KeyBrain installed and ready                           │"
echo "│                                                          │"
echo "│  Commands (open a new terminal):                        │"
echo "│    kb \"text or URL\"    → save to inbox                  │"
echo "│    kb add <file>      → copy file to inbox              │"
echo "│    kb process         → process inbox now               │"
echo "│    kb status          → vault status                    │"
echo "│    kb update          → update KeyBrain framework       │"
echo "│                                                          │"
echo "│  Slash commands in Claude Code:                         │"
echo "│    /kb-add             → add content                    │"
echo "│    /kb-process         → process inbox                  │"
echo "│    /kb-search <query>  → search the vault               │"
echo "│    /kb-health          → audit the vault                │"
echo "│    /kb-compile         → compile the wiki               │"
echo "│                                                          │"
echo "│  Set up auto-processing (copy-paste to your agent):     │"
echo "│    \"Configure a cron job to run \$KB_VAULT/bin/          │"
echo "│     process-inbox.sh every 15 minutes.\"                 │"
echo "│                                                          │"
echo "│  Set up nightly dream (memory consolidation):           │"
echo "│    \"Configure cron: 0 2 * * * \$KB_VAULT/bin/kb-dream\"  │"
echo "└─────────────────────────────────────────────────────────┘"
echo ""
