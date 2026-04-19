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
    files = list((vault / "raw" / "memory-derived").glob("*.md"))
    content = files[0].read_text().replace("status: unverified", "status: rejected")
    files[0].write_text(content)
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
