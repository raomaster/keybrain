# Feature 3: Episodic Memory + Dreaming — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a three-layer memory system: `memory/YYYY-MM-DD.md` (raw episodic log), `MEMORY.md` (lean session context), and `raw/memory-derived/` (provisional KB knowledge) consolidated nightly by `bin/kb-dream.py`.

**Architecture:** `bin/kb-dream` is a shell wrapper (same pattern as `kb-search-semantic`). `bin/kb-dream.py` holds all logic: parses memory files, applies a deterministic promotion matrix (memory_type × confidence), rebuilds MEMORY.md, and creates files in `raw/memory-derived/`. `bin/kb-index.py` gains exclusions for `memory/` and `MEMORY.md`, a new `memory-derived` doc type, and skips `status: rejected/superseded`. No LLM calls in dreaming.

**Prerequisite:** Feature 1 plan must be implemented first (for the BASH_SOURCE guard in install.sh).

**Tech Stack:** Python 3.12, pytest, chromadb, bash

---

## File Map

| File | Action |
|------|--------|
| `bin/kb-index.py` | Modify: add `should_index()`, extend `get_doc_type()`, skip rejected/superseded |
| `bin/kb-dream` | Create: shell wrapper |
| `bin/kb-dream.py` | Create: dreaming logic |
| `setup/install.sh` | Modify: create dirs (step 7), chmod (step 8), CLAUDE.md heredoc (step 11), summary box |
| `setup/skills/kb-dream/skill.md` | Create: slash command |
| `CLAUDE.md` (vault) | Modify: add memory/ rules to General Rules |
| `tests/unit/test_kb_index_memory.py` | Create: 4 test cases for indexer changes |
| `tests/unit/test_kb_dream.py` | Create: 8 test cases for dreaming logic |

---

### Task 1: Write failing tests for kb-index.py changes

**Files:**
- Create: `tests/unit/test_kb_index_memory.py`

- [ ] **Step 1: Write the tests**

```python
# tests/unit/test_kb_index_memory.py
import sys
from pathlib import Path
import importlib.util

REPO_ROOT = Path(__file__).parent.parent.parent
VAULT = Path("/tmp/kb-test-vault-index")


def load_kb_index():
    """Load kb-index.py as a module."""
    spec = importlib.util.spec_from_file_location("kb_index", REPO_ROOT / "bin/kb-index.py")
    mod = importlib.util.module_from_spec(spec)
    import os
    os.environ["KB_VAULT"] = str(VAULT)
    spec.loader.exec_module(mod)
    return mod


def test_memory_dir_excluded_from_index():
    mod = load_kb_index()
    vault = Path("/tmp/kb-test-vault")
    path = vault / "memory" / "2026-04-18.md"
    assert not mod.should_index(path, vault)


def test_memory_md_excluded_from_index():
    mod = load_kb_index()
    vault = Path("/tmp/kb-test-vault")
    path = vault / "MEMORY.md"
    assert not mod.should_index(path, vault)


def test_regular_article_included():
    mod = load_kb_index()
    vault = Path("/tmp/kb-test-vault")
    path = vault / "raw" / "articles" / "2026-04-18-test.md"
    assert mod.should_index(path, vault)


def test_memory_derived_doc_type():
    mod = load_kb_index()
    path = Path("/tmp/kb-test-vault/raw/memory-derived/2026-04-18-test.md")
    assert mod.get_doc_type(path) == "memory-derived"
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
python -m pytest tests/unit/test_kb_index_memory.py -v
```

Expected: FAIL — `should_index` and updated `get_doc_type` don't exist yet.

---

### Task 2: Implement kb-index.py changes

**Files:**
- Modify: `bin/kb-index.py`

- [ ] **Step 1: Add `EXCLUDED_PATHS` constant and `should_index()` function**

In `bin/kb-index.py`, after the `STATE_FILE` definition (line 18) and before `parse_frontmatter`, add:

```python
EXCLUDED_PATHS = {"memory", "MEMORY.md"}


def should_index(path: Path, vault_root: Path) -> bool:
    rel = path.relative_to(vault_root)
    # parts[0] catches both memory/ directory and MEMORY.md root file
    if rel.parts[0] in EXCLUDED_PATHS:
        return False
    return True
```

- [ ] **Step 2: Extend `get_doc_type()` with memory-derived**

Replace the `get_doc_type` function body:

```python
def get_doc_type(path: Path) -> str:
    parts = path.parts
    if "memory-derived" in parts: return "memory-derived"
    if "articles" in parts:       return "article"
    if "courses" in parts:        return "course"
    if "research" in parts:       return "research"
    if "projects" in parts:       return "project"
    if "decisions" in parts:      return "decision"
    if "conversations" in parts:  return "conversation"
    if "wiki" in parts:           return "wiki"
    return "note"
```

- [ ] **Step 3: Apply exclusions and status filter in `index_vault()`**

In `index_vault()`, replace the existing exclusion block inside the `for md_file` loop:

```python
    for md_file in sorted(VAULT.rglob("*.md")):
        if any(skip in md_file.parts for skip in SKIP_DIRS):
            continue
        if md_file.name in SKIP_FILES or md_file.name.startswith('.'):
            continue
        if not should_index(md_file, VAULT):
            continue

        rel_path = str(md_file.relative_to(VAULT))
        fhash = file_hash(md_file)

        if not force and state.get(rel_path) == fhash:
            skipped += 1
            continue

        text = md_file.read_text(encoding='utf-8', errors='ignore')
        if len(text.strip()) < 50:
            continue

        meta, content = parse_frontmatter(text)

        # Skip rejected or superseded provisional knowledge
        if meta.get("status") in ("rejected", "superseded"):
            continue

        doc_type = get_doc_type(md_file)
        # ... rest unchanged
```

- [ ] **Step 4: Run tests — expect green**

```bash
python -m pytest tests/unit/test_kb_index_memory.py -v
```

Expected: all 4 PASS.

- [ ] **Step 5: Run existing index tests**

```bash
python -m pytest tests/unit/test_index.py -v
```

Expected: all existing tests still PASS.

- [ ] **Step 6: Commit**

```bash
git add bin/kb-index.py tests/unit/test_kb_index_memory.py
git commit -m "feat: exclude memory/ and MEMORY.md from ChromaDB, add memory-derived type"
```

---

### Task 3: Write failing tests for kb-dream.py

**Files:**
- Create: `tests/unit/test_kb_dream.py`

- [ ] **Step 1: Write the tests**

```python
# tests/unit/test_kb_dream.py
import sys
import os
import importlib.util
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).parent.parent.parent


def make_vault(tmp_path):
    vault = tmp_path / "Knowledge"
    (vault / "memory").mkdir(parents=True)
    (vault / "raw" / "memory-derived").mkdir(parents=True)
    (vault / "MEMORY.md").write_text("# Memory\n")
    return vault


def write_memory_file(vault, claims):
    """Write a memory/YYYY-MM-DD.md file with given claim dicts."""
    today = date.today().isoformat()
    lines = ["---", "type: memory", f"date: {today}", "tags: [memory, session]", "---", ""]
    for c in claims:
        lines.append(f'- claim: "{c["claim"]}"')
        lines.append(f'  memory_type: {c["memory_type"]}')
        lines.append(f'  confidence: {c["confidence"]}')
        lines.append(f'  context: "{c.get("context", "test")}"')
        lines.append("")
    (vault / "memory" / f"{today}.md").write_text("\n".join(lines))


def load_dream(vault):
    os.environ["KB_VAULT"] = str(vault)
    spec = importlib.util.spec_from_file_location("kb_dream", REPO_ROOT / "bin/kb-dream.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_user_rule_high_appears_in_memory_md(tmp_path):
    vault = make_vault(tmp_path)
    write_memory_file(vault, [{"claim": "Search order: kb first", "memory_type": "user-rule", "confidence": "high"}])
    mod = load_dream(vault)
    mod.run_dream(vault, days=30)
    content = (vault / "MEMORY.md").read_text()
    assert "Search order: kb first" in content
    assert "[user-rule]" in content


def test_user_rule_low_not_in_memory_md(tmp_path):
    vault = make_vault(tmp_path)
    write_memory_file(vault, [{"claim": "Low confidence rule", "memory_type": "user-rule", "confidence": "low"}])
    mod = load_dream(vault)
    mod.run_dream(vault, days=30)
    content = (vault / "MEMORY.md").read_text()
    assert "Low confidence rule" not in content


def test_technical_finding_medium_creates_raw_file(tmp_path):
    vault = make_vault(tmp_path)
    write_memory_file(vault, [{"claim": "OpenClaw loads from workspace/skills", "memory_type": "technical-finding", "confidence": "medium"}])
    mod = load_dream(vault)
    mod.run_dream(vault, days=30)
    files = list((vault / "raw" / "memory-derived").glob("*.md"))
    assert len(files) == 1
    content = files[0].read_text()
    assert "OpenClaw loads from workspace/skills" in content
    assert "status: unverified" in content
    assert "promoted_by: dream" in content


def test_temporary_context_never_promotes(tmp_path):
    vault = make_vault(tmp_path)
    write_memory_file(vault, [{"claim": "This is temporary", "memory_type": "temporary-context", "confidence": "high"}])
    mod = load_dream(vault)
    mod.run_dream(vault, days=30)
    memory_md = (vault / "MEMORY.md").read_text()
    assert "This is temporary" not in memory_md
    files = list((vault / "raw" / "memory-derived").glob("*.md"))
    assert len(files) == 0


def test_decision_high_to_raw_not_memory_md(tmp_path):
    vault = make_vault(tmp_path)
    write_memory_file(vault, [{"claim": "Use markitdown over yt-dlp", "memory_type": "decision", "confidence": "high"}])
    mod = load_dream(vault)
    mod.run_dream(vault, days=30)
    memory_md = (vault / "MEMORY.md").read_text()
    assert "Use markitdown over yt-dlp" not in memory_md
    files = list((vault / "raw" / "memory-derived").glob("*.md"))
    assert len(files) == 1


def test_dedupe_skips_existing_claim(tmp_path):
    vault = make_vault(tmp_path)
    write_memory_file(vault, [{"claim": "Search order: kb first", "memory_type": "technical-finding", "confidence": "high"}])
    mod = load_dream(vault)
    mod.run_dream(vault, days=30)
    mod.run_dream(vault, days=30)  # second run
    files = list((vault / "raw" / "memory-derived").glob("*.md"))
    assert len(files) == 1  # no duplicate


def test_dedupe_skips_rejected_claim(tmp_path):
    vault = make_vault(tmp_path)
    write_memory_file(vault, [{"claim": "Wrong finding", "memory_type": "technical-finding", "confidence": "high"}])
    mod = load_dream(vault)
    mod.run_dream(vault, days=30)
    # Simulate user marking as rejected
    files = list((vault / "raw" / "memory-derived").glob("*.md"))
    content = files[0].read_text().replace("status: unverified", "status: rejected")
    files[0].write_text(content)
    # Run again — should not recreate
    mod.run_dream(vault, days=30)
    assert len(list((vault / "raw" / "memory-derived").glob("*.md"))) == 1


def test_memory_md_rebuilt_not_accumulated(tmp_path):
    vault = make_vault(tmp_path)
    write_memory_file(vault, [{"claim": "Rule A", "memory_type": "user-rule", "confidence": "high"}])
    mod = load_dream(vault)
    mod.run_dream(vault, days=30)
    mod.run_dream(vault, days=30)
    content = (vault / "MEMORY.md").read_text()
    assert content.count("Rule A") == 1  # not duplicated across runs
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
python -m pytest tests/unit/test_kb_dream.py -v
```

Expected: FAIL — `bin/kb-dream.py` doesn't exist yet.

---

### Task 4: Create bin/kb-dream (shell wrapper)

**Files:**
- Create: `bin/kb-dream`

- [ ] **Step 1: Write the wrapper**

```bash
#!/usr/bin/env bash
VAULT="${KB_VAULT:-$HOME/Knowledge}"
PYTHON="$VAULT/.venv/bin/python3"
[ ! -f "$PYTHON" ] && PYTHON="python3"
exec "$PYTHON" "$VAULT/bin/kb-dream.py" "$@"
```

- [ ] **Step 2: Make executable**

```bash
chmod +x bin/kb-dream
```

---

### Task 5: Create bin/kb-dream.py (dreaming logic)

**Files:**
- Create: `bin/kb-dream.py`

- [ ] **Step 1: Write the implementation**

```python
#!/usr/bin/env python3
"""
kb-dream — Consolidate episodic memory into MEMORY.md and raw/memory-derived/.
Usage: kb-dream [--days N]
  --days N  How many days of memory files to process (default: 30)
"""

import os
import re
import sys
import argparse
import hashlib
from pathlib import Path
from datetime import date, timedelta

VAULT = Path(os.environ.get("KB_VAULT", str(Path.home() / "Knowledge")))

PROMOTION_MATRIX = {
    # (memory_type, min_confidence) -> destinations
    # destinations: "memory_md" | "raw" | both
    ("user-rule",       "high"):   ["memory_md", "raw"],
    ("user-preference", "high"):   ["memory_md", "raw"],
    ("decision",        "high"):   ["raw"],
    ("technical-finding", "medium"): ["raw"],
    ("technical-finding", "high"):   ["raw"],
}

CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}
MEMORY_MD_MAX_PER_TYPE = 10


def slugify(text: str, max_len: int = 30) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text[:max_len]


def dedupe_key(memory_type: str, claim: str) -> str:
    return f"{memory_type}:{slugify(claim)}"


def parse_memory_file(path: Path) -> list:
    """Parse claims from a memory/YYYY-MM-DD.md file."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    # Strip frontmatter
    body = re.sub(r"^---.*?---\n?", "", text, flags=re.DOTALL).strip()
    claims = []
    current = {}
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("- claim:"):
            if current:
                claims.append(current)
            claim_val = line.split("claim:", 1)[1].strip().strip('"').strip("'")
            current = {"claim": claim_val, "date": path.stem}
        elif line.startswith("memory_type:") and current:
            current["memory_type"] = line.split(":", 1)[1].strip()
        elif line.startswith("confidence:") and current:
            current["confidence"] = line.split(":", 1)[1].strip()
        elif line.startswith("context:") and current:
            current["context"] = line.split("context:", 1)[1].strip().strip('"').strip("'")
    if current:
        claims.append(current)
    return claims


def get_destinations(memory_type: str, confidence: str) -> list:
    rank = CONFIDENCE_RANK.get(confidence, 0)
    for (mtype, min_conf), dests in PROMOTION_MATRIX.items():
        if mtype == memory_type and CONFIDENCE_RANK.get(min_conf, 0) <= rank:
            return dests
    return []


def existing_dedupe_keys(memory_derived_dir: Path) -> set:
    """Return set of dedupe keys for files already in raw/memory-derived/."""
    keys = set()
    for f in memory_derived_dir.glob("*.md"):
        text = f.read_text(encoding="utf-8", errors="ignore")
        status_match = re.search(r"^status:\s*(\w+)", text, re.MULTILINE)
        status = status_match.group(1) if status_match else "unverified"
        dk_match = re.search(r"^dedupe_key:\s*(.+)", text, re.MULTILINE)
        if dk_match:
            dk = dk_match.group(1).strip()
            if status in ("rejected", "superseded"):
                keys.add(f"__blocked__{dk}")
            else:
                keys.add(dk)
    return keys


def write_memory_derived(vault: Path, claim: dict, memory_derived_dir: Path, existing_keys: set) -> bool:
    """Write a raw/memory-derived/ file. Returns True if written."""
    dk = dedupe_key(claim["memory_type"], claim["claim"])
    if dk in existing_keys or f"__blocked__{dk}" in existing_keys:
        return False
    today = claim.get("date", date.today().isoformat())
    memory_type = claim.get("memory_type", "note")
    confidence = claim.get("confidence", "medium")
    title = claim["claim"][:80].capitalize()
    slug = f"{today}-{memory_type}-{slugify(claim['claim'])}"
    filename = memory_derived_dir / f"{slug}.md"
    content = f"""---
title: "{title}"
date: {today}
source: "memory/{today}.md"
tags: [memory-derived, {memory_type}]
status: unverified
confidence: {confidence}
promoted_by: dream
dedupe_key: {dk}
---

{claim['claim']}

> Context: {claim.get('context', '')}
"""
    filename.write_text(content, encoding="utf-8")
    existing_keys.add(dk)
    return True


def rebuild_memory_md(vault: Path, memory_md_claims: list):
    """Rebuild MEMORY.md from scratch with qualifying claims (max 10 per type)."""
    by_type: dict = {}
    for c in memory_md_claims:
        mt = c.get("memory_type", "unknown")
        by_type.setdefault(mt, []).append(c)
    lines = ["# Memory", f"_Updated: {date.today().isoformat()} by kb-dream_", ""]
    for mt, claims in sorted(by_type.items()):
        # Most recent first (claims ordered by file date already)
        for c in claims[:MEMORY_MD_MAX_PER_TYPE]:
            lines.append(f"- [{mt}] {c['claim']}")
    lines.append("")
    (vault / "MEMORY.md").write_text("\n".join(lines), encoding="utf-8")


def run_dream(vault: Path, days: int = 30):
    memory_dir = vault / "memory"
    memory_derived_dir = vault / "raw" / "memory-derived"
    memory_derived_dir.mkdir(parents=True, exist_ok=True)

    cutoff = date.today() - timedelta(days=days)
    memory_md_claims = []
    new_raw = 0
    skipped = 0
    existing_keys = existing_dedupe_keys(memory_derived_dir)

    for f in sorted(memory_dir.glob("*.md")):
        if f.name == ".gitkeep":
            continue
        try:
            file_date = date.fromisoformat(f.stem)
        except ValueError:
            continue
        if file_date < cutoff:
            continue
        for claim in parse_memory_file(f):
            dests = get_destinations(
                claim.get("memory_type", ""),
                claim.get("confidence", "low")
            )
            if "memory_md" in dests:
                memory_md_claims.append(claim)
            if "raw" in dests:
                written = write_memory_derived(vault, claim, memory_derived_dir, existing_keys)
                if written:
                    new_raw += 1
                else:
                    skipped += 1

    rebuild_memory_md(vault, memory_md_claims)

    total_claims = len(memory_md_claims)
    print(f"Dream complete: {total_claims} in MEMORY.md, {new_raw} new in raw/memory-derived/, {skipped} skipped (dedupe)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidate episodic memory")
    parser.add_argument("--days", type=int, default=30, help="Days of memory to process")
    args = parser.parse_args()
    run_dream(VAULT, days=args.days)
```

- [ ] **Step 2: Run the dream tests**

```bash
python -m pytest tests/unit/test_kb_dream.py -v
```

Expected: all 8 tests PASS.

- [ ] **Step 3: Run all tests**

```bash
python -m pytest tests/unit/ -v
```

Expected: all tests PASS.

- [ ] **Step 4: Commit**

```bash
git add bin/kb-dream bin/kb-dream.py tests/unit/test_kb_dream.py
git commit -m "feat: add kb-dream — episodic memory to MEMORY.md + raw/memory-derived/"
```

---

### Task 6: Update install.sh — dirs, chmod, CLAUDE.md heredoc, summary

**Files:**
- Modify: `setup/install.sh`

- [ ] **Step 1: Add memory dirs in step 7 (vault setup block)**

In `setup/install.sh`, inside the `if [ "$VAULT_REPO_DIR" != "$VAULT_DIR" ]` block after the `cp -r` command (step 7), add:

```bash
mkdir -p "$VAULT_DIR/memory"
touch "$VAULT_DIR/memory/.gitkeep"
mkdir -p "$VAULT_DIR/raw/memory-derived"
touch "$VAULT_DIR/raw/memory-derived/.gitkeep"
if [ ! -f "$VAULT_DIR/MEMORY.md" ]; then
  printf "# Memory\n_Updated: never — run kb dream to populate_\n" > "$VAULT_DIR/MEMORY.md"
fi
```

- [ ] **Step 2: Add kb-dream chmod in step 8 (permissions)**

In `setup/install.sh`, in step 8 (`chmod +x` lines), add:

```bash
chmod +x "$VAULT_DIR/bin/kb-dream"
```

- [ ] **Step 3: Add memory instruction to step 11 CLAUDE.md heredoc**

In `setup/install.sh`, inside the step 11 heredoc (after the USER.md line from Feature 1), add:

```
memory:
  write: "During session, append claims to memory/YYYY-MM-DD.md (incremental, not only at end)"
  format: "- claim: \"...\"\n  memory_type: user-rule|user-preference|decision|technical-finding|temporary-context\n  confidence: low|medium|high\n  context: \"...\""
  load: "Read MEMORY.md at session start for behavioral context"
```

- [ ] **Step 4: Add dream to summary box**

In `setup/install.sh`, in the summary `echo` block at the bottom, add before the closing line:

```bash
echo "│  Set up nightly dream (memory consolidation):            │"
echo "│    \"Configure cron: 0 2 * * * \$KB_VAULT/bin/kb-dream\"   │"
```

- [ ] **Step 5: Verify bash syntax**

```bash
bash -n setup/install.sh && echo "syntax OK"
```

Expected: `syntax OK`

---

### Task 7: Create setup/skills/kb-dream/skill.md

**Files:**
- Create: `setup/skills/kb-dream/skill.md`

- [ ] **Step 1: Write the skill**

```markdown
---
description: "Consolidate episodic memory into MEMORY.md and raw/memory-derived/"
---

Run the dreaming process over the last $ARGUMENTS days (default: 30) of memory files.

**Process:**

1. Run kb-dream:
   ```bash
   ${KB_VAULT:-$HOME/Knowledge}/bin/kb-dream --days ${ARGUMENTS:-30}
   ```

2. Report what was promoted:
   - How many claims are now in `MEMORY.md`
   - How many new files in `raw/memory-derived/`
   - How many skipped (dedupe)

3. If there are new files in `raw/memory-derived/`, list them with their title and confidence.

## Connections

- [[knowledge-base-system]]
- [[memory-system]]
```

---

### Task 8: Update vault CLAUDE.md — add memory/ rules

**Files:**
- Modify: `CLAUDE.md` (in the keybrain repo, at vault root)

- [ ] **Step 1: Add rules to General Rules section**

In `CLAUDE.md` (keybrain repo), in the `## General Rules` section, add:

```markdown
- **memory/ is not inbox**: never process `memory/` files with kb-process. They are episodic session logs, not classifiable content.
- **MEMORY.md is not wiki**: never edit MEMORY.md manually or include it in wiki compilation. It is rebuilt by kb-dream.
```

---

### Task 9: Run full test suite + commit everything

- [ ] **Step 1: Run all tests**

```bash
python -m pytest tests/unit/ -v
```

Expected: all tests PASS.

- [ ] **Step 2: Commit**

```bash
git add setup/install.sh setup/skills/kb-dream/ CLAUDE.md
git commit -m "feat: memory system install — dirs, kb-dream chmod, CLAUDE.md instructions"
```

- [ ] **Step 3: Export plan to KB**

```bash
kb add docs/superpowers/plans/2026-04-18-feature3-memory-dreaming.md
```
