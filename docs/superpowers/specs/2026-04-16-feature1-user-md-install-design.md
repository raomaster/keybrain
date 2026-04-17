# Feature 1: README + USER.md Install Design

## Goal

Add a "Personalizing your agent" section to the README and auto-generate a `~/.claude/USER.md` template during installation (Claude Code only).

## Architecture

Two changes: (1) README gets a new section explaining the USER.md pattern with a YAML template; (2) `install.sh` adds step 10b that creates `~/.claude/USER.md` from that template if Claude Code is detected and the file doesn't already exist.

## Components

### README — "Personalizing your agent" section

**Location:** Between "Configuration" and "Architecture" sections.

**Content:**
- What USER.md is: on-demand identity file the agent reads only when it needs user context, not on every prompt
- Why YAML: ~30% fewer tokens than prose (structured format, no quotes, no braces)
- The template (same as what install.sh generates)
- Note for non–Claude Code agents: concept applies but auto-install doesn't run

**Template shown in README:**
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

### install.sh — Step 10b

**Trigger condition:** `~/.claude/` directory exists AND `~/.claude/USER.md` does not exist.

**Action:** Write the USER.md template to `~/.claude/USER.md`.

**Position:** After step 10 (Claude Code skills install), before step 11 (CLAUDE.md append).

```bash
# ── 10b. USER.md template ─────────────────────────────
step "Creating USER.md template"
USER_MD="$CLAUDE_DIR/USER.md"
if [ -d "$CLAUDE_DIR" ] && [ ! -f "$USER_MD" ]; then
  cat > "$USER_MD" << 'USEREOF'
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
  log "USER.md template created at $USER_MD — edit it with your info."
else
  log "USER.md already exists or Claude Code not detected, skipping."
fi
```

### install.sh — Step 11 CLAUDE.md append

The existing CLAUDE.md append (step 11) already adds KeyBrain instructions. Append this line to the heredoc:

```
Read `~/.claude/USER.md` only when needing project/user context orientation.
```

## Data Flow

```
install.sh runs
  └─ step 10: skills → ~/.claude/commands/
  └─ step 10b: USER.md template → ~/.claude/USER.md  (if CC detected, file absent)
  └─ step 11: CLAUDE.md append → includes "Read USER.md on-demand" instruction

User edits ~/.claude/USER.md with real info

Agent session starts
  └─ CLAUDE.md loaded (every session)
  └─ USER.md read only when agent needs user context orientation
```

## Out of Scope

- Other agents (Copilot, Cursor, OpenClaw): README documents the concept, no auto-install
- Updating an existing USER.md: never overwritten, user owns it
- Validating USER.md content: not checked by install or by the agent

## Files Changed

- `README.md`: add "Personalizing your agent" section
- `setup/install.sh`: add step 10b + append USER.md instruction to step 11 heredoc
