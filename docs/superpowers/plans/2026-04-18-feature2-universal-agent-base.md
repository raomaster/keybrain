# Feature 2: Universal Agent Base (OpenClaw) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install KeyBrain skills and global instructions to OpenClaw (`~/.openclaw/workspace/`) when detected, in addition to Claude Code (already handled in step 10/11).

**Architecture:** Two new bash functions (`install_openclaw_skills`, `configure_openclaw_agents_md`) added to install.sh after the BASH_SOURCE guard (from Feature 1 plan). Steps 10c and 11b call them inside the main execution block. Detection uses `~/.openclaw/` directory OR `openclaw` binary in PATH.

**Prerequisite:** Feature 1 plan must be implemented first — this plan requires the BASH_SOURCE guard already in install.sh.

**Tech Stack:** Bash, pytest, subprocess

---

## File Map

| File | Action |
|------|--------|
| `setup/install.sh` | Add functions `install_openclaw_skills` + `configure_openclaw_agents_md` before guard; add steps 10c + 11b in main execution |
| `tests/unit/test_install_openclaw.py` | Create — 7 test cases |

---

### Task 1: Add OpenClaw functions to install.sh

**Files:**
- Modify: `setup/install.sh` (before the BASH_SOURCE guard line)

- [ ] **Step 1: Insert two functions before the guard**

In `setup/install.sh`, between `create_user_md_template` (from Feature 1) and the BASH_SOURCE guard line, insert:

```bash
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
```

- [ ] **Step 2: Verify bash syntax**

```bash
bash -n setup/install.sh && echo "syntax OK"
```

Expected: `syntax OK`

---

### Task 2: Write tests — must PASS immediately (functions already added in Task 1)

**Files:**
- Create: `tests/unit/test_install_openclaw.py`

- [ ] **Step 1: Write the tests**

```python
# tests/unit/test_install_openclaw.py
import subprocess
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def source_fn(fn_name, *args, extra_path=None):
    """Source install.sh (guard stops main execution) then call function."""
    env = os.environ.copy()
    if extra_path:
        env["PATH"] = extra_path + ":" + env.get("PATH", "")
    arg_str = " ".join(f'"{a}"' for a in args)
    cmd = f'source {REPO_ROOT}/setup/install.sh && {fn_name} {arg_str}'
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, env=env)


def make_skills_src(tmp_path):
    """Create a mock skills source with a skill.md file."""
    src = tmp_path / "skills"
    skill_dir = src / "kb-search"
    skill_dir.mkdir(parents=True)
    (skill_dir / "skill.md").write_text("---\ndescription: test\n---\ntest skill")
    return src


# ── install_openclaw_skills ────────────────────────────

def test_installs_skills_when_openclaw_dir_exists(tmp_path):
    src = make_skills_src(tmp_path)
    openclaw_dir = tmp_path / ".openclaw"
    openclaw_dir.mkdir()
    result = source_fn("install_openclaw_skills", str(src), str(openclaw_dir))
    assert result.returncode == 0
    skills_dest = openclaw_dir / "workspace" / "skills"
    assert skills_dest.exists()
    assert (skills_dest / "kb-search").exists()


def test_renames_skill_md_to_uppercase(tmp_path):
    src = make_skills_src(tmp_path)
    openclaw_dir = tmp_path / ".openclaw"
    openclaw_dir.mkdir()
    source_fn("install_openclaw_skills", str(src), str(openclaw_dir))
    skill_dir = openclaw_dir / "workspace" / "skills" / "kb-search"
    assert (skill_dir / "SKILL.md").exists()
    assert not (skill_dir / "skill.md").exists()


def test_skips_nothing_created_when_no_skills_src(tmp_path):
    src = tmp_path / "missing-skills"  # does not exist
    openclaw_dir = tmp_path / ".openclaw"
    openclaw_dir.mkdir()
    result = source_fn("install_openclaw_skills", str(src), str(openclaw_dir))
    # cp fails → function returns 1 with warn, does not crash script
    assert result.returncode == 1


# ── configure_openclaw_agents_md ──────────────────────

def test_creates_agents_md_when_absent(tmp_path):
    openclaw_dir = tmp_path / ".openclaw"
    workspace = openclaw_dir / "workspace"
    workspace.mkdir(parents=True)
    result = source_fn("configure_openclaw_agents_md", str(openclaw_dir))
    assert result.returncode == 0
    agents_md = workspace / "AGENTS.md"
    assert agents_md.exists()
    assert "KeyBrain" in agents_md.read_text()


def test_appends_when_exists_without_keybrain(tmp_path):
    openclaw_dir = tmp_path / ".openclaw"
    workspace = openclaw_dir / "workspace"
    workspace.mkdir(parents=True)
    agents_md = workspace / "AGENTS.md"
    agents_md.write_text("# Existing content\n")
    source_fn("configure_openclaw_agents_md", str(openclaw_dir))
    content = agents_md.read_text()
    assert "Existing content" in content
    assert "KeyBrain" in content


def test_skips_when_keybrain_already_present(tmp_path):
    openclaw_dir = tmp_path / ".openclaw"
    workspace = openclaw_dir / "workspace"
    workspace.mkdir(parents=True)
    agents_md = workspace / "AGENTS.md"
    agents_md.write_text("## KeyBrain\nalready here\n")
    source_fn("configure_openclaw_agents_md", str(openclaw_dir))
    # Content should not be duplicated
    content = agents_md.read_text()
    assert content.count("KeyBrain") == 1


def test_workspace_dir_created_if_absent(tmp_path):
    openclaw_dir = tmp_path / ".openclaw"
    openclaw_dir.mkdir()
    # workspace does not exist yet
    source_fn("configure_openclaw_agents_md", str(openclaw_dir))
    agents_md = openclaw_dir / "workspace" / "AGENTS.md"
    assert agents_md.exists()
```

- [ ] **Step 2: Run tests**

```bash
python -m pytest tests/unit/test_install_openclaw.py -v
```

Expected: all 7 tests PASS (functions were already added in Task 1).

---

### Task 4: Add steps 10c and 11b in main execution

**Files:**
- Modify: `setup/install.sh` (main execution block)

- [ ] **Step 1: Add step 10c after step 10 block**

In `setup/install.sh`, after the `create_user_md_template "$CLAUDE_DIR"` call (step 10b), add:

```bash
# ── 10c. OpenClaw skills ──────────────────────────────
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
```

- [ ] **Step 2: Add step 11b after step 11 block**

In `setup/install.sh`, after the step 11 block (after the `fi` that closes the `if ! grep -q "KeyBrain"` block), add:

```bash
# ── 11b. OpenClaw AGENTS.md ───────────────────────────
step "Configuring global OpenClaw instructions"
if [ "$OPENCLAW_DETECTED" = true ]; then
  configure_openclaw_agents_md "$HOME/.openclaw"
fi
```

- [ ] **Step 3: Verify bash syntax**

```bash
bash -n setup/install.sh && echo "syntax OK"
```

Expected: `syntax OK`

---

### Task 5: Run full test suite + commit

- [ ] **Step 1: Run all tests**

```bash
python -m pytest tests/unit/ -v
```

Expected: all tests PASS.

- [ ] **Step 2: Commit**

```bash
git add setup/install.sh tests/unit/test_install_openclaw.py
git commit -m "feat: install KeyBrain skills and AGENTS.md to OpenClaw on detection"
```
