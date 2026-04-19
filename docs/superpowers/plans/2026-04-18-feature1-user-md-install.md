# Feature 1: README + USER.md Install — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `create_user_md_template` to install.sh (step 10b) and add a "Personalizing your agent" section to the README.

**Architecture:** Extract the USER.md creation into a testable bash function in install.sh, guarded by a BASH_SOURCE check so tests can source the file without running the full installer. Feature 2 and Feature 3 build on top of this same guard pattern — implement this plan first.

**Tech Stack:** Bash, pytest, subprocess

---

## File Map

| File | Action |
|------|--------|
| `setup/install.sh` | Add function `create_user_md_template` + BASH_SOURCE guard + step 10b call + step 11 heredoc line |
| `tests/unit/test_install_user_md.py` | Create — 3 test cases |
| `README.md` | Add "Personalizing your agent" section between Configuration and Architecture |

---

### Task 1: Add BASH_SOURCE guard + `create_user_md_template` to install.sh

**Files:**
- Modify: `setup/install.sh:26-28`

- [ ] **Step 1: Insert function block and guard**

In `setup/install.sh`, between line 26 (end of `step()` definition) and line 28 (`# Parse arguments`), insert:

```bash
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

# Guard: stop execution when sourced (e.g., by tests)
[[ "${BASH_SOURCE[0]}" != "${0}" ]] && return 0
```

- [ ] **Step 2: Verify install.sh still runs**

```bash
bash setup/install.sh --help 2>&1 || bash setup/install.sh --non-interactive --vault-path /tmp/kb-test-verify 2>&1 | head -5
```

Expected: script starts (shows `[KB] Detected platform:`) or exits with unknown option — either confirms the script is still valid bash.

---

### Task 2: Write tests — must PASS immediately (function already added in Task 1)

**Files:**
- Create: `tests/unit/test_install_user_md.py`

- [ ] **Step 1: Write the tests**

```python
# tests/unit/test_install_user_md.py
import subprocess
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def source_fn(fn_name, *args):
    """Source install.sh (guard stops main execution) then call function."""
    arg_str = " ".join(f'"{a}"' for a in args)
    cmd = f'source {REPO_ROOT}/setup/install.sh && {fn_name} {arg_str}'
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)


def test_creates_user_md_when_claude_dir_exists(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    result = source_fn("create_user_md_template", str(claude_dir))
    assert result.returncode == 0
    user_md = claude_dir / "USER.md"
    assert user_md.exists()
    content = user_md.read_text()
    assert "identity:" in content
    assert "expertise:" in content
    assert "style:" in content


def test_skips_when_user_md_already_exists(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    user_md = claude_dir / "USER.md"
    user_md.write_text("existing content")
    source_fn("create_user_md_template", str(claude_dir))
    assert user_md.read_text() == "existing content"


def test_skips_when_claude_dir_does_not_exist(tmp_path):
    claude_dir = tmp_path / ".claude"  # intentionally not created
    source_fn("create_user_md_template", str(claude_dir))
    assert not (claude_dir / "USER.md").exists()
```

- [ ] **Step 2: Run tests**

```bash
python -m pytest tests/unit/test_install_user_md.py -v
```

Expected: all 3 PASS (function was already added in Task 1).

---

### Task 4: Add step 10b call in main execution

**Files:**
- Modify: `setup/install.sh` (after step 10 block, before step 11)

- [ ] **Step 1: Add step 10b**

In `setup/install.sh`, after the step 10 block (the `if [ -d "$SKILLS_SRC" ]` closing `fi` around line 183), add:

```bash
# ── 10b. USER.md template ─────────────────────────────
step "Creating USER.md template"
create_user_md_template "$CLAUDE_DIR"
```

- [ ] **Step 2: Verify install.sh is valid bash**

```bash
bash -n setup/install.sh && echo "syntax OK"
```

Expected: `syntax OK`

---

### Task 5: Add USER.md instruction to step 11 CLAUDE.md heredoc

**Files:**
- Modify: `setup/install.sh` (step 11 heredoc)

- [ ] **Step 1: Add the line to the heredoc**

In `setup/install.sh`, inside the heredoc of step 11 (`cat >> "$CLAUDE_MD" << 'CLAUDEEOF'`), append before `CLAUDEEOF`:

```bash
Read \`~/.claude/USER.md\` only when needing project/user context orientation.
```

The full heredoc after the change:

```bash
cat >> "$CLAUDE_MD" << 'CLAUDEEOF'

# Global

When making an important technical decision, save it without asking: `kb "Decision: [what] — Why: [reason] — Rejected: [alternatives]"`
After executing a Superpowers plan, export the file: `kb add docs/superpowers/plans/[plan].md`
KeyBrain KB at `$KB_VAULT` with ChromaDB — use `kb-search-semantic "query"` before answering technical questions that might be in the vault.
Read `~/.claude/USER.md` only when needing project/user context orientation.
CLAUDEEOF
```

- [ ] **Step 2: Verify bash syntax**

```bash
bash -n setup/install.sh && echo "syntax OK"
```

Expected: `syntax OK`

---

### Task 6: Add README "Personalizing your agent" section

**Files:**
- Modify: `README.md:118` (between Configuration and Architecture sections)

- [ ] **Step 1: Insert section**

In `README.md`, after line 117 (closing ``` of the Configuration code block) and before line 119 (`## Architecture`), insert:

```markdown

## Personalizing your agent

KeyBrain installs a `USER.md` template to `~/.claude/USER.md` during setup (Claude Code only). Edit it with your name, role, and preferences — the agent reads it on demand to tailor responses to you.

**Why YAML?** Structured key-value format uses ~30% fewer tokens than prose ([reference](https://dev.to/inozem/structured-prompts-how-yaml-cut-my-llm-costs-by-30-3a56)), keeping your identity file fast to load.

```yaml
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
```

For other agents (Copilot, Cursor, Codex): create the file manually and add an instruction to read it in your agent's config (e.g., `.github/copilot-instructions.md`, `AGENTS.md`).
```

- [ ] **Step 2: Verify README renders — check section exists**

```bash
grep -n "Personalizing your agent" README.md
```

Expected: 1 match at the correct line.

---

### Task 7: Run full test suite + commit

- [ ] **Step 1: Run all tests**

```bash
python -m pytest tests/unit/ -v
```

Expected: all tests PASS (existing tests untouched).

- [ ] **Step 2: Commit**

```bash
git add setup/install.sh tests/unit/test_install_user_md.py README.md
git commit -m "feat: add USER.md template install + README personalizing section"
```
