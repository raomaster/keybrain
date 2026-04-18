# Feature 3: Episodic Memory + Dreaming Design

## Goal

Implement a three-layer memory system: raw episodic notes written during sessions (`memory/YYYY-MM-DD.md`), consolidated behavioral context for session start (`MEMORY.md`), and provisional KB knowledge promoted by a deterministic dreaming script (`raw/memory-derived/`). No LLM tokens consumed by dreaming.

## Architecture

```
Session (agent writes incrementally)
  └─ memory/YYYY-MM-DD.md   ← episodic raw claims

kb-dream (nightly cron, Python, zero LLM tokens)
  ├─ user-rule/preference + high → MEMORY.md (rebuilt) + raw/memory-derived/
  ├─ decision + high             → raw/memory-derived/
  ├─ technical-finding + med/hi  → raw/memory-derived/
  └─ temporary-context / low     → stays in memory/ only

Session start
  └─ agent reads MEMORY.md explicitly (not via ChromaDB)

User curates raw/memory-derived/
  └─ status: verified → manually promote to raw/ or wiki/
```

**ChromaDB exclusions** (both explicit — not just directory-level):
- `memory/**` — episodic data, not knowledge
- `MEMORY.md` — session context, not semantic recall

---

## Layer 1: memory/YYYY-MM-DD.md

### Format

```yaml
---
type: memory
date: 2026-04-18
tags: [memory, session]
---

- claim: "Search order: kb-search → own knowledge → WebSearch, no exceptions"
  memory_type: user-rule
  confidence: high
  context: "user rule enforced multiple times"

- claim: "install.sh step 10c: skills to ~/.openclaw/workspace/skills/"
  memory_type: technical-finding
  confidence: medium
  context: "designed today, not tested yet"
```

### `memory_type` values

| Value | Description |
|-------|-------------|
| `user-rule` | behavioral rule the agent must follow |
| `user-preference` | style/communication preference |
| `decision` | architectural or technical decision |
| `technical-finding` | discovered fact about a tool/system |
| `temporary-context` | context only valid this session |

### When the agent writes

- Incrementally during session — not only at end (process may die mid-session)
- One append per new claim worth recording
- Claims are cheap to write; dreaming decides what survives

---

## Layer 2: MEMORY.md — session behavioral context

Only `user-rule + high` and `user-preference + high` entries. Rebuilt from scratch by kb-dream each run.

### Format (lean, one line per entry)

```markdown
# Memory
_Updated: 2026-04-18 by kb-dream_

- [user-rule] Search order: kb-search → own knowledge → WebSearch (no exceptions)
- [user-preference] Responses in Spanish, direct, no filler, no trailing summaries
```

**Size target:** under 30 lines. If a `memory_type` accumulates more than 10 entries, kb-dream keeps the 10 most recent by date when rebuilding.

**Not in ChromaDB.** Read explicitly at session start via CLAUDE.md instruction.

---

## Layer 3: raw/memory-derived/ — provisional KB knowledge

### Promotion matrix (deterministic — no LLM)

| `memory_type` | `low` | `medium` | `high` |
|---------------|-------|----------|--------|
| `user-rule` | memory/ only | memory/ only | **MEMORY.md** + raw/memory-derived/ |
| `user-preference` | memory/ only | memory/ only | **MEMORY.md** + raw/memory-derived/ |
| `decision` | memory/ only | memory/ only | raw/memory-derived/ |
| `technical-finding` | memory/ only | raw/memory-derived/ | raw/memory-derived/ |
| `temporary-context` | memory/ only | memory/ only | memory/ only |

### Frontmatter

```yaml
---
title: "OpenClaw loads skills from ~/.openclaw/workspace/skills/"
date: 2026-04-18
source: "memory/2026-04-18.md"
tags: [memory-derived, technical-finding, openclaw]
status: unverified
confidence: medium
promoted_by: dream
---
```

### `status` values

| Value | Meaning |
|-------|---------|
| `unverified` | promoted automatically, not yet confirmed |
| `verified` | user confirmed as accurate |
| `rejected` | user marked as wrong/outdated — kept for audit, excluded from search |
| `superseded` | replaced by a newer entry or KB article |

`rejected` and `superseded` entries stay on disk for audit but are excluded from ChromaDB via status filter in `kb-index.py`.

### Deduplication

Dedupe key: `f"{memory_type}:{slugify(claim)}"` where `slugify` lowercases, strips punctuation, collapses spaces to hyphens, truncates to 60 chars.

If a file with the same dedupe key already exists in `raw/memory-derived/`, kb-dream skips creation. If the existing entry has `status: rejected` or `status: superseded`, kb-dream also skips (don't resurrect dismissed claims).

**No promotion to `wiki/` or `decisions/` from kb-dream.** Those paths require deliberate curation. ADR format in `decisions/` has context/options/rationale that dreaming cannot generate.

---

## bin/kb-dream + bin/kb-dream.py

Follows the existing KeyBrain CLI pattern: `bin/kb-dream` is a short shell wrapper, `bin/kb-dream.py` holds all real logic. Same pattern as `kb-search-semantic` / `kb-search-semantic.py` and `kb-index` / `kb-index.py`.

### Responsibilities (kb-dream.py)

1. Parse all `memory/YYYY-MM-DD.md` files in the last 30 days (configurable via `--days`)
2. Apply promotion matrix
3. Rebuild `MEMORY.md` from all qualifying user-rule/preference + high entries (most recent wins for duplicates)
4. For each entry qualifying for raw/memory-derived/: compute dedupe key, skip if exists (unless creating is appropriate per dedup rules above), write new file
5. Print a minimal summary: N claims read, N promoted to MEMORY.md, N new files in raw/memory-derived/, N skipped (dedupe)

### Invocation

```bash
# bin/kb-dream (shell wrapper — same pattern as kb-search-semantic)
#!/bin/bash
exec "$(dirname "$0")/../.venv/bin/python3" "$(dirname "$0")/kb-dream.py" "$@"

# Manual
kb dream

# Cron (nightly at 2am)
0 2 * * * $KB_VAULT/bin/kb-dream >> $KB_VAULT/memory/dream.log 2>&1
```

### Title generation for raw/memory-derived/

Truncate claim to 80 chars, capitalize first letter. Not an LLM call — just string formatting. Example:
- claim: `"install.sh step 10c: skills to ~/.openclaw/workspace/skills/"` → title: `"Install.sh step 10c: skills to ~/.openclaw/workspace/skills/"`

### Filename convention

`YYYY-MM-DD-<memory_type>-<claim_slug_30chars>.md`

Example: `2026-04-18-technical-finding-install-sh-step-10c-skills-to.md`

---

## Changes to existing files

### bin/kb-index.py

**Add exclusions** (two explicit checks alongside any existing directory exclusions):
```python
EXCLUDED_PATHS = {"memory", "MEMORY.md"}  # relative to vault root

def should_index(path: Path, vault_root: Path) -> bool:
    rel = path.relative_to(vault_root)
    # parts[0] catches both memory/ directory and MEMORY.md root file
    if rel.parts[0] in EXCLUDED_PATHS:
        return False
    return True
```

**Extend `get_doc_type()`** to recognize `raw/memory-derived/`:
```python
if "memory-derived" in parts:
    return "memory-derived"
```

**Filter `status: rejected/superseded`** from indexing:
```python
if frontmatter.get("status") in ("rejected", "superseded"):
    return  # skip
```

### setup/install.sh

**New directories and files (step 7, vault setup):**
```bash
mkdir -p "$VAULT_DIR/memory"
touch "$VAULT_DIR/memory/.gitkeep"
if [ ! -f "$VAULT_DIR/MEMORY.md" ]; then
  printf "# Memory\n_Updated: never — run kb dream to populate_\n" > "$VAULT_DIR/MEMORY.md"
fi
mkdir -p "$VAULT_DIR/raw/memory-derived"
touch "$VAULT_DIR/raw/memory-derived/.gitkeep"
```

**Install kb-dream (step 8, permissions):**
```bash
chmod +x "$VAULT_DIR/bin/kb-dream"
# kb-dream.py is not executed directly — only via wrapper, no chmod needed
```

**Add to CLAUDE.md heredoc (step 11):**
```
memory:
  write: "During session, append claims to memory/YYYY-MM-DD.md (incremental, not only at end)"
  format: "- claim: \"...\"\n  memory_type: user-rule|user-preference|decision|technical-finding|temporary-context\n  confidence: low|medium|high\n  context: \"...\""
  load: "Read MEMORY.md at session start for behavioral context"
```

**Add to summary box:**
```
│  Set up dream (nightly memory consolidation):                   │
│    "Configure a cron job: 0 2 * * * $KB_VAULT/bin/kb-dream"    │
```

### CLAUDE.md (vault, keybrain repo)

Add to "General Rules" section:
```
- **memory/ is not inbox**: never process `memory/` files with kb-process. They are episodic logs, not classifiable content.
- **MEMORY.md is not wiki**: never edit or include MEMORY.md in wiki compilation.
```

---

## Graph isolation in Obsidian

- `memory/YYYY-MM-DD.md`: tagged `[memory, session]` → filterable from graph
- `raw/memory-derived/`: tagged `[memory-derived]` → filterable from graph
- Both directories can be excluded from Obsidian graph via Settings → Graph → Filters → `-tag:#memory-derived -tag:#memory`

---

## Testing

`tests/unit/test_kb_dream.py`:

1. `test_user_rule_high_promotes_to_memory_md` — claim with `user-rule + high` → appears in MEMORY.md
2. `test_user_rule_low_stays_in_memory_dir` — `user-rule + low` → not in MEMORY.md, not in raw/memory-derived/
3. `test_technical_finding_medium_promotes_to_raw` — `technical-finding + medium` → file created in raw/memory-derived/
4. `test_temporary_context_never_promotes` — any confidence → stays in memory/ only
5. `test_decision_high_to_raw_not_memory_md` — `decision + high` → raw/memory-derived/, NOT in MEMORY.md
6. `test_dedupe_skips_existing_claim` — same memory_type + claim slug → no new file created
7. `test_dedupe_skips_rejected_claim` — existing file with `status: rejected` → not recreated
8. `test_memory_md_rebuilt_from_scratch` — MEMORY.md reflects only current qualifying entries, not accumulates
9. `test_memory_md_excluded_from_index` — MEMORY.md path returns False from `should_index()`
10. `test_memory_dir_excluded_from_index` — any path under `memory/` returns False from `should_index()`
11. `test_memory_derived_doc_type` — path under `raw/memory-derived/` returns `"memory-derived"` from `get_doc_type()`
12. `test_rejected_status_excluded_from_index` — file with `status: rejected` skipped by indexer

---

## Files created/modified

| File | Action | Install step |
|------|--------|-------------|
| `bin/kb-dream` | Create: shell wrapper | step 8 (chmod +x) |
| `bin/kb-dream.py` | Create: Python implementation | step 8 (no chmod) |
| `bin/kb-index.py` | Modify: exclusions + memory-derived type + status filter | — |
| `setup/install.sh` | Modify: memory/ dirs + MEMORY.md init (step 7/8), CLAUDE.md heredoc (step 11), summary box | — |
| `CLAUDE.md` (vault) | Modify: add memory/ rules to General Rules | — |
| `setup/skills/kb-dream/skill.md` | Create: slash command to trigger dreaming manually | step 10 (copied to commands/) |
| `memory/.gitkeep` | Create via install | step 7 |
| `raw/memory-derived/.gitkeep` | Create via install | step 7 |
| `MEMORY.md` | Create via install (empty template) | step 7 |
