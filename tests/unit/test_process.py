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


def test_process_inbox_uses_opencode_by_default(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    (vault / "inbox").mkdir()
    (vault / "logs").mkdir()
    (vault / "bin").mkdir()
    (vault / "bin" / "kb-index.py").write_text("print('indexed')")
    (vault / "inbox" / "note.md").write_text("test")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_venv_bin = tmp_path / "venv" / "bin"
    fake_venv_bin.mkdir(parents=True)
    opencode_log = tmp_path / "opencode.log"
    (fake_bin / "opencode").write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$@\" > {opencode_log}\n"
        "rm -f \"$KB_VAULT/inbox/note.md\"\n"
    )
    (fake_bin / "opencode").chmod(0o755)
    (fake_venv_bin / "python3").write_text("#!/usr/bin/env bash\nexit 0\n")
    (fake_venv_bin / "python3").chmod(0o755)

    env = os.environ.copy()
    env["KB_VAULT"] = str(vault)
    env["KB_VENV"] = str(tmp_path / "venv")
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = subprocess.run(
        ["bash", str(REPO_ROOT / "bin/process-inbox.sh")],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )

    assert result.returncode == 0
    assert opencode_log.exists()
    assert "run" in opencode_log.read_text()
    assert not (vault / "inbox" / "note.md").exists()


def test_process_inbox_can_use_claude_when_requested(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    (vault / "inbox").mkdir()
    (vault / "logs").mkdir()
    (vault / "bin").mkdir()
    (vault / "bin" / "kb-index.py").write_text("print('indexed')")
    (vault / "inbox" / "note.md").write_text("test")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_venv_bin = tmp_path / "venv" / "bin"
    fake_venv_bin.mkdir(parents=True)
    claude_log = tmp_path / "claude.log"
    (fake_bin / "claude").write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$@\" > {claude_log}\n"
        "rm -f \"$KB_VAULT/inbox/note.md\"\n"
    )
    (fake_bin / "claude").chmod(0o755)
    (fake_venv_bin / "python3").write_text("#!/usr/bin/env bash\nexit 0\n")
    (fake_venv_bin / "python3").chmod(0o755)

    env = os.environ.copy()
    env["KB_VAULT"] = str(vault)
    env["KB_VENV"] = str(tmp_path / "venv")
    env["KB_PROCESS_AGENT"] = "claude"
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = subprocess.run(
        ["bash", str(REPO_ROOT / "bin/process-inbox.sh")],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )

    assert result.returncode == 0
    assert claude_log.exists()
    assert "--print" in claude_log.read_text()
    assert not (vault / "inbox" / "note.md").exists()


def test_process_inbox_passes_model_to_opencode(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    (vault / "inbox").mkdir()
    (vault / "logs").mkdir()
    (vault / "bin").mkdir()
    (vault / "bin" / "kb-index.py").write_text("print('indexed')")
    (vault / "inbox" / "note.md").write_text("test")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_venv_bin = tmp_path / "venv" / "bin"
    fake_venv_bin.mkdir(parents=True)
    opencode_log = tmp_path / "opencode.log"
    (fake_bin / "opencode").write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$@\" > {opencode_log}\n"
        "rm -f \"$KB_VAULT/inbox/note.md\"\n"
    )
    (fake_bin / "opencode").chmod(0o755)
    (fake_venv_bin / "python3").write_text("#!/usr/bin/env bash\nexit 0\n")
    (fake_venv_bin / "python3").chmod(0o755)

    env = os.environ.copy()
    env["KB_VAULT"] = str(vault)
    env["KB_VENV"] = str(tmp_path / "venv")
    env["KB_PROCESS_MODEL"] = "anthropic/claude-sonnet-4-5"
    env["KB_PROCESS_VARIANT"] = "minimal"
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = subprocess.run(
        ["bash", str(REPO_ROOT / "bin/process-inbox.sh")],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )

    assert result.returncode == 0
    args = opencode_log.read_text()
    assert "--model" in args
    assert "anthropic/claude-sonnet-4-5" in args
    assert "--variant" in args
    assert "minimal" in args


def test_process_inbox_passes_model_to_claude(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    (vault / "inbox").mkdir()
    (vault / "logs").mkdir()
    (vault / "bin").mkdir()
    (vault / "bin" / "kb-index.py").write_text("print('indexed')")
    (vault / "inbox" / "note.md").write_text("test")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_venv_bin = tmp_path / "venv" / "bin"
    fake_venv_bin.mkdir(parents=True)
    claude_log = tmp_path / "claude.log"
    (fake_bin / "claude").write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$@\" > {claude_log}\n"
        "rm -f \"$KB_VAULT/inbox/note.md\"\n"
    )
    (fake_bin / "claude").chmod(0o755)
    (fake_venv_bin / "python3").write_text("#!/usr/bin/env bash\nexit 0\n")
    (fake_venv_bin / "python3").chmod(0o755)

    env = os.environ.copy()
    env["KB_VAULT"] = str(vault)
    env["KB_VENV"] = str(tmp_path / "venv")
    env["KB_PROCESS_AGENT"] = "claude"
    env["KB_PROCESS_MODEL"] = "sonnet"
    env["KB_PROCESS_EFFORT"] = "low"
    env["KB_PROCESS_MAX_BUDGET_USD"] = "0.25"
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = subprocess.run(
        ["bash", str(REPO_ROOT / "bin/process-inbox.sh")],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )

    assert result.returncode == 0
    args = claude_log.read_text()
    assert "--model" in args
    assert "sonnet" in args
    assert "--effort" in args
    assert "low" in args
    assert "--max-budget-usd" in args
    assert "0.25" in args
