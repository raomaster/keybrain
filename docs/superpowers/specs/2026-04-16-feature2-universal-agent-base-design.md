# Feature 2: kb as Universal Agent Base Design

## Goal

`install.sh` detects which AI agents are present on the machine and installs KeyBrain skills and global instructions to each one's standard directory — without the user having to do it manually.

## Architecture

Two new steps in `install.sh` (10c and 11b) handle OpenClaw. Claude Code and Cowork already share `~/.claude/` so steps 10 and 11 cover both. OpenClaw detection is computed once into `OPENCLAW_DETECTED` and reused across both new steps.

## Agent Coverage

| Agent | Detection | Skills dir | Config file |
|-------|-----------|------------|-------------|
| Claude Code | `~/.claude/` exists | `~/.claude/commands/` | `~/.claude/CLAUDE.md` |
| Cowork | same as Claude Code | same | same |
| OpenClaw | `~/.openclaw/` exists OR `openclaw` in PATH | `~/.openclaw/workspace/skills/` | `~/.openclaw/workspace/AGENTS.md` |

## Components

### Step 10c — OpenClaw skills

Positioned after step 10 (Claude Code skills), before step 11 (CLAUDE.md).

Detection: set `OPENCLAW_DETECTED=true` if `~/.openclaw/` exists OR `openclaw` binary is in PATH.

If detected:
- `mkdir -p ~/.openclaw/workspace/skills/`
- Copy all skill directories from `$VAULT_DIR/setup/skills/` to `~/.openclaw/workspace/skills/`
- Rename `skill.md` → `SKILL.md` (OpenClaw requires uppercase; KeyBrain uses lowercase)

```bash
# ── 10c. OpenClaw skills ──────────────────────────────
step "Installing KeyBrain skills in OpenClaw"
OPENCLAW_DETECTED=false
if [ -d "$HOME/.openclaw" ] || command -v openclaw &>/dev/null; then
  OPENCLAW_DETECTED=true
fi

if [ "$OPENCLAW_DETECTED" = true ]; then
  OPENCLAW_SKILLS_DIR="$HOME/.openclaw/workspace/skills"
  mkdir -p "$OPENCLAW_SKILLS_DIR"
  if cp -r "$SKILLS_SRC/"* "$OPENCLAW_SKILLS_DIR/"; then
    find "$OPENCLAW_SKILLS_DIR" -name "skill.md" -type f -execdir mv {} SKILL.md \;
    log "OpenClaw skills installed to $OPENCLAW_SKILLS_DIR"
  else
    warn "Could not copy skills to OpenClaw. Check permissions on $OPENCLAW_SKILLS_DIR"
  fi
else
  log "OpenClaw not detected, skipping."
fi
```

### Step 11b — OpenClaw AGENTS.md

Positioned after step 11 (CLAUDE.md append).

If `OPENCLAW_DETECTED=true`: append KeyBrain rules to `~/.openclaw/workspace/AGENTS.md` using `>>` (creates the file if absent, same pattern as step 11). Guards with `grep -q "KeyBrain"` to avoid duplicate appends on re-runs.

```bash
# ── 11b. OpenClaw AGENTS.md ───────────────────────────
step "Configuring global OpenClaw instructions"
if [ "$OPENCLAW_DETECTED" = true ]; then
  OPENCLAW_AGENTS_MD="$HOME/.openclaw/workspace/AGENTS.md"
  if ! grep -q "KeyBrain" "$OPENCLAW_AGENTS_MD" 2>/dev/null; then
    cat >> "$OPENCLAW_AGENTS_MD" << 'AGENTSEOF'

## KeyBrain
When making an important technical decision, save it without asking: `kb "Decision: [what] — Why: [reason] — Rejected: [alternatives]"`
After executing a Superpowers plan, export the file: `kb add docs/superpowers/plans/[plan].md`
KeyBrain KB at `$KB_VAULT` with ChromaDB — use `kb-search-semantic "query"` before answering technical questions that might be in the vault.
AGENTSEOF
    log "Global OpenClaw AGENTS.md configured."
  else
    log "OpenClaw AGENTS.md already has KeyBrain instructions."
  fi
fi
```

Note: the AGENTS.md content mirrors CLAUDE.md but in OpenClaw's preferred prose format (not YAML-dense, since OpenClaw agents don't benefit from the same token optimization that Claude Code does with CLAUDE.md loading).

## Data Flow

```
install.sh runs
  └─ step 10:  Claude Code skills → ~/.claude/commands/
  └─ step 10c: detect OpenClaw → ~/.openclaw/workspace/skills/ + rename SKILL.md
  └─ step 11:  Claude Code CLAUDE.md append
  └─ step 11b: OpenClaw AGENTS.md append (>> creates if absent)
```

## Idempotency

- Skills copy: `cp -r` overwrites existing files on re-run (same as step 10)
- `find -execdir mv`: rename is safe on re-run (SKILL.md already uppercase → no match)
- AGENTS.md: `grep -q "KeyBrain"` guard prevents duplicate append

## Out of Scope

- USER.md template for OpenClaw: not auto-generated (Feature 1 is Claude Code only)
- Other agents (Cursor, Copilot, Codex): documented in README, no auto-install
- Updating skills after install: handled by `kb update` (existing command)

## Testing

`tests/unit/test_install_openclaw.py`:

1. `test_installs_skills_when_openclaw_dir_exists` — `~/.openclaw/` present → skills copied, `SKILL.md` uppercase
2. `test_installs_skills_when_openclaw_binary_in_path` — no dir but binary in PATH → same
3. `test_skips_when_openclaw_not_detected` — no dir, no binary → nothing created
4. `test_agents_md_created_when_absent` — AGENTS.md doesn't exist → created with KeyBrain section
5. `test_agents_md_appended_when_exists_without_keybrain` — exists but no "KeyBrain" → appended
6. `test_agents_md_not_duplicated_on_rerun` — "KeyBrain" already present → not duplicated
7. `test_skill_md_rename` — verifies `skill.md` → `SKILL.md` rename happens correctly

## Files Changed

- `setup/install.sh`: add steps 10c and 11b
- `tests/unit/test_install_openclaw.py`: 7 test cases
