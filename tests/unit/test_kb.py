import subprocess
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

def run_kb(args, vault_path):
    env = os.environ.copy()
    env["KB_VAULT"] = str(vault_path)
    result = subprocess.run(
        ["bash", str(REPO_ROOT / "bin/kb")] + args,
        capture_output=True, text=True, cwd=str(REPO_ROOT),
        env=env
    )
    return result

def test_kb_text_saves_to_inbox(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    (vault / "inbox").mkdir()
    result = run_kb(["test content here"], vault)
    assert result.returncode == 0
    md_files = list((vault / "inbox").glob("*.md"))
    assert len(md_files) == 1
    assert "test content here" in md_files[0].read_text()

def test_kb_add_copies_file(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    (vault / "inbox").mkdir()
    source = tmp_path / "article.md"
    source.write_text("# Test Article")
    result = run_kb(["add", str(source)], vault)
    assert result.returncode == 0
    assert (vault / "inbox" / "article.md").exists()

def test_kb_add_missing_file_fails(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    (vault / "inbox").mkdir()
    result = run_kb(["add", "/nonexistent/file.md"], vault)
    assert result.returncode != 0

def test_kb_status_shows_count(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    (vault / "inbox").mkdir()
    (vault / "inbox" / "test.md").write_text("content")
    result = run_kb(["status"], vault)
    assert result.returncode == 0
    assert "1" in result.stdout

def test_kb_no_args_shows_usage(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    result = run_kb([], vault)
    assert result.returncode == 1
    assert "Usage:" in result.stdout

def test_kb_uses_kb_vault_env(tmp_path):
    """KB_VAULT env var overrides default $HOME/Knowledge path"""
    vault = tmp_path / "MyVault"
    vault.mkdir()
    (vault / "inbox").mkdir()
    result = run_kb(["hello from custom vault"], vault)
    assert result.returncode == 0
    md_files = list((vault / "inbox").glob("*.md"))
    assert len(md_files) == 1
    assert "hello from custom vault" in md_files[0].read_text()
