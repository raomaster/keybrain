# tests/unit/test_install_codex.py
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def source_fn(fn_name, *args):
    arg_str = " ".join(f'"{a}"' for a in args)
    cmd = f'source {REPO_ROOT}/setup/install.sh && {fn_name} {arg_str}'
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)


# ── configure_codex_agents_md ────────────────────────────

def test_creates_codex_agents_md_when_absent(tmp_path):
    agents_md = tmp_path / ".codex" / "AGENTS.md"
    result = source_fn("configure_codex_agents_md", str(agents_md))
    assert result.returncode == 0
    assert agents_md.exists()
    assert "KeyBrain" in agents_md.read_text()
    assert "KB_VAULT" in agents_md.read_text()
    assert "--add-dir" in agents_md.read_text()


def test_codex_appends_when_exists_without_keybrain(tmp_path):
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("# Existing instructions\n")
    source_fn("configure_codex_agents_md", str(agents_md))
    content = agents_md.read_text()
    assert "Existing instructions" in content
    assert "KeyBrain" in content


def test_codex_skips_when_keybrain_present(tmp_path):
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("## KeyBrain\nalready here\n")
    source_fn("configure_codex_agents_md", str(agents_md))
    assert agents_md.read_text().count("KeyBrain") == 1


def test_codex_creates_parent_dirs(tmp_path):
    agents_md = tmp_path / ".codex" / "nested" / "AGENTS.md"
    result = source_fn("configure_codex_agents_md", str(agents_md))
    assert result.returncode == 0
    assert agents_md.exists()
