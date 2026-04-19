# Feature 4: Git Bash + Copilot/JetBrains + Obsidian README — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Support corporate Windows users (Git Bash + Python, no PowerShell/WSL2) by adding Git Bash platform detection to install.sh, auto-configure GitHub Copilot and JetBrains AI instructions, and add clear Obsidian vault setup steps to README.

**Architecture:** Two new bash functions (`configure_copilot_instructions`, `configure_jetbrains_ai`) added to install.sh before the BASH_SOURCE guard, following the same pattern as `configure_openclaw_agents_md`. Platform detection adds `gitbash` as a valid PLATFORM value. Git Bash-specific paths skip Homebrew, apt, Obsidian install, and Node install — warn instead of error when Claude Code is absent. README gets a "Setting up Obsidian" section after the install block.

**Tech Stack:** Bash, pytest, subprocess

---

## File Map

| File | Action |
|------|--------|
| `setup/install.sh` | Modify: add `configure_copilot_instructions()` + `configure_jetbrains_ai()` before guard; add `gitbash` to platform detection; adjust steps 3, 6, 9, 11c, 11d |
| `README.md` | Modify: add "Setting up Obsidian" section after ## Install |
| `tests/unit/test_install_copilot.py` | Create: 6 test cases for the two new functions |

---

### Task 1: Write failing tests for configure_copilot_instructions and configure_jetbrains_ai

**Files:**
- Create: `tests/unit/test_install_copilot.py`

- [ ] **Step 1: Write the tests**

```python
# tests/unit/test_install_copilot.py
import subprocess
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def source_fn(fn_name, *args):
    arg_str = " ".join(f'"{a}"' for a in args)
    cmd = f'source {REPO_ROOT}/setup/install.sh && {fn_name} {arg_str}'
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)


# ── configure_copilot_instructions ────────────────────────

def test_creates_copilot_file_when_absent(tmp_path):
    copilot_file = tmp_path / ".github" / "copilot-instructions.md"
    result = source_fn("configure_copilot_instructions", str(copilot_file))
    assert result.returncode == 0
    assert copilot_file.exists()
    assert "KeyBrain" in copilot_file.read_text()


def test_copilot_appends_when_exists_without_keybrain(tmp_path):
    copilot_file = tmp_path / "copilot-instructions.md"
    copilot_file.write_text("# Existing instructions\n")
    source_fn("configure_copilot_instructions", str(copilot_file))
    content = copilot_file.read_text()
    assert "Existing instructions" in content
    assert "KeyBrain" in content


def test_copilot_skips_when_keybrain_present(tmp_path):
    copilot_file = tmp_path / "copilot-instructions.md"
    copilot_file.write_text("## KeyBrain\nalready here\n")
    source_fn("configure_copilot_instructions", str(copilot_file))
    assert copilot_file.read_text().count("KeyBrain") == 1


# ── configure_jetbrains_ai ────────────────────────────────

def test_creates_jetbrains_rules_file(tmp_path):
    rules_dir = tmp_path / ".aiassistant" / "rules"
    result = source_fn("configure_jetbrains_ai", str(rules_dir))
    assert result.returncode == 0
    rules_file = rules_dir / "keybrain.md"
    assert rules_file.exists()
    assert "KeyBrain" in rules_file.read_text()


def test_jetbrains_skips_when_file_exists(tmp_path):
    rules_dir = tmp_path / ".aiassistant" / "rules"
    rules_dir.mkdir(parents=True)
    rules_file = rules_dir / "keybrain.md"
    rules_file.write_text("## KeyBrain\nexisting\n")
    source_fn("configure_jetbrains_ai", str(rules_dir))
    assert rules_file.read_text().count("KeyBrain") == 1


def test_jetbrains_creates_parent_dirs(tmp_path):
    rules_dir = tmp_path / ".aiassistant" / "rules"
    result = source_fn("configure_jetbrains_ai", str(rules_dir))
    assert result.returncode == 0
    assert (rules_dir / "keybrain.md").exists()
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
python3 -m pytest tests/unit/test_install_copilot.py -v
```

Expected: FAIL — functions don't exist yet.

---

### Task 2: Add configure_copilot_instructions and configure_jetbrains_ai to install.sh

**Files:**
- Modify: `setup/install.sh` (before BASH_SOURCE guard at line ~93)

- [ ] **Step 1: Add configure_copilot_instructions function**

In `setup/install.sh`, after `configure_openclaw_agents_md()` and before the BASH_SOURCE guard, add:

```bash
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
```

- [ ] **Step 2: Run tests — expect green**

```bash
python3 -m pytest tests/unit/test_install_copilot.py -v
```

Expected: all 6 PASS.

- [ ] **Step 3: Run existing tests — verify no regression**

```bash
python3 -m pytest tests/unit/ -v
```

Expected: all tests PASS.

- [ ] **Step 4: Commit**

```bash
git add setup/install.sh tests/unit/test_install_copilot.py
git commit -m "feat: add configure_copilot_instructions and configure_jetbrains_ai"
```

---

### Task 3: Add Git Bash platform detection to install.sh

**Files:**
- Modify: `setup/install.sh`

Context: In Git Bash on Windows, `uname -s` returns strings like `MINGW64_NT-10.0-19041` or `MSYS_NT-10.0`. The existing detection fails with "Unsupported OS".

- [ ] **Step 1: Add gitbash to platform detection**

In `setup/install.sh`, replace the platform detection block (around line 106):

```bash
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
```

- [ ] **Step 2: Adjust step 3 — Node/Claude Code (skip install on gitbash)**

Replace the `if ! command -v claude` block in step 3:

```bash
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
```

- [ ] **Step 3: Adjust step 6 — Python (require existing install on gitbash)**

Replace the `PYTHON_BIN` line in step 6:

```bash
if [ "$PLATFORM" = "gitbash" ]; then
  PYTHON_BIN="$(command -v python3 2>/dev/null || command -v python 2>/dev/null)"
  if [ -z "$PYTHON_BIN" ]; then
    error "Python not found. Install Python 3.12+ from python.org and re-run."
  fi
else
  PYTHON_BIN="$(command -v python3.12 || command -v python3)"
fi
```

- [ ] **Step 4: Adjust step 9 — PATH (use .bashrc on gitbash)**

Replace the SHELL_RC block in step 9:

```bash
SHELL_RC="$HOME/.zshrc"
if [ "$SHELL" = "/bin/bash" ] || [ "$PLATFORM" = "gitbash" ]; then
  SHELL_RC="$HOME/.bashrc"
fi
```

- [ ] **Step 5: Verify bash syntax**

```bash
bash -n setup/install.sh && echo "syntax OK"
```

Expected: `syntax OK`

- [ ] **Step 6: Commit**

```bash
git add setup/install.sh
git commit -m "feat: add Git Bash (MINGW/MSYS) platform support for corporate Windows"
```

---

### Task 4: Call new functions from main execution (steps 11c and 11d)

**Files:**
- Modify: `setup/install.sh` (after step 11b OpenClaw AGENTS.md block)

- [ ] **Step 1: Add steps 11c and 11d**

In `setup/install.sh`, after the `# ── 11b. OpenClaw AGENTS.md` block, add:

```bash
# ── 11c. GitHub Copilot instructions ──────────────────────
step "Configuring GitHub Copilot instructions"
configure_copilot_instructions "$HOME/.github/copilot-instructions.md"

# ── 11d. JetBrains AI rules ───────────────────────────────
step "Configuring JetBrains AI rules"
configure_jetbrains_ai "$HOME/.aiassistant/rules"
```

- [ ] **Step 2: Add to summary box**

In the summary `echo` block at the bottom, before the closing line, add:

```bash
echo "│                                                          │"
echo "│  AI agent instructions configured:                      │"
echo "│    ~/.github/copilot-instructions.md  (Copilot)        │"
echo "│    ~/.aiassistant/rules/keybrain.md   (JetBrains AI)   │"
```

- [ ] **Step 3: Verify bash syntax**

```bash
bash -n setup/install.sh && echo "syntax OK"
```

Expected: `syntax OK`

- [ ] **Step 4: Run full test suite**

```bash
python3 -m pytest tests/unit/ -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add setup/install.sh
git commit -m "feat: call copilot + jetbrains config in install steps 11c/11d"
```

---

### Task 5: Update README with Obsidian setup section

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add Obsidian setup section**

In `README.md`, after the `## Install` section (after the code block that ends the install prompt, before `## How it works`), add:

```markdown
### Setting up Obsidian

After the installer runs, open your vault in Obsidian:

1. Install [Obsidian](https://obsidian.md) if not already installed
   - macOS: the installer does this automatically via Homebrew
   - Windows/Linux: download from obsidian.md
2. Open Obsidian
3. Click **Open folder as vault**
4. Navigate to your vault path (default: `~/Knowledge`)
5. Click **Open**

Your knowledge base will appear with all folders and notes organized automatically.

> **Corporate Windows users (Git Bash):** Run `bash setup/install.sh` directly from Git Bash — no PowerShell required. Python 3.12+ must be installed first from [python.org](https://python.org).
```

- [ ] **Step 2: Verify README renders correctly**

```bash
cat README.md | grep -A 20 "Setting up Obsidian"
```

Expected: the section appears cleanly after the install block.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add Obsidian vault setup steps + Git Bash install note to README"
```

---

### Task 6: Full test suite + release

- [ ] **Step 1: Run all tests**

```bash
python3 -m pytest tests/unit/ -v
```

Expected: all tests PASS.

- [ ] **Step 2: Export plan to KB**

```bash
kb add docs/superpowers/plans/2026-04-19-feature4-gitbash-copilot-obsidian.md
```
