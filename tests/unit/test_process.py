import subprocess
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

def test_process_empty_inbox_exits_clean(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    (vault / "inbox").mkdir()
    (vault / "logs").mkdir()
    subprocess.run(["git", "init"], cwd=vault, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=vault, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=vault, capture_output=True)
    env = os.environ.copy()
    env["KB_VAULT"] = str(vault)
    result = subprocess.run(
        ["bash", str(REPO_ROOT / "bin/process-inbox.sh")],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
        env=env
    )
    assert result.returncode == 0

def test_process_inbox_skips_gitkeep(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    (vault / "inbox").mkdir()
    (vault / "logs").mkdir()
    (vault / "inbox" / ".gitkeep").write_text("")
    subprocess.run(["git", "init"], cwd=vault, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=vault, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=vault, capture_output=True)
    env = os.environ.copy()
    env["KB_VAULT"] = str(vault)
    result = subprocess.run(
        ["bash", str(REPO_ROOT / "bin/process-inbox.sh")],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
        env=env
    )
    assert result.returncode == 0
