import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent


def make_executable(path: Path, content: str = "#!/usr/bin/env bash\nexit 0\n"):
    path.write_text(content)
    path.chmod(0o755)


def make_vault(tmp_path):
    vault = tmp_path / "Knowledge"
    for rel in [
        "inbox",
        "raw",
        "wiki",
        "decisions",
        "bin",
        "templates",
        ".obsidian",
        ".chromadb",
        ".venv/bin",
    ]:
        (vault / rel).mkdir(parents=True)

    (vault / "CLAUDE.md").write_text("# Instructions\n")
    (vault / "VERSION").write_text("0.4.0\n")
    (vault / "wiki" / "_index.md").write_text("# Index\n")
    (vault / ".obsidian" / "app.json").write_text(
        '{"userIgnoreFilters":["setup/","CLAUDE.md","INSTALL-PROMPT.md"]}\n'
    )

    for name in [
        "kb",
        "process-inbox.sh",
        "kb-cron",
        "kb-doctor",
        "kb-dream",
        "kb-index",
        "kb-search-semantic",
    ]:
        make_executable(vault / "bin" / name)
    (vault / "bin" / "kb-index.py").write_text("print('index')\n")
    (vault / "bin" / "kb-search-semantic.py").write_text("print('search')\n")

    make_executable(vault / ".venv" / "bin" / "python3")
    return vault


def run_doctor(args, vault, tmp_path, extra_env=None):
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir(exist_ok=True)
    make_executable(fake_bin / "opencode")
    crontab_file = tmp_path / "crontab"
    crontab_file.write_text(
        f"*/15 * * * * KB_VAULT='{vault}' KB_PROCESS_AGENT='opencode' "
        "KB_PROCESS_MODEL='sonnet' "
        f"'{vault}/bin/process-inbox.sh'\n"
        f"0 2 * * * KB_VAULT='{vault}' '{vault}/bin/kb-dream' --days 30\n"
    )
    env = os.environ.copy()
    env.update(
        {
            "KB_VAULT": str(vault),
            "KB_VENV": str(vault / ".venv"),
            "KB_CHROMADB": str(vault / ".chromadb"),
            "KB_PROCESS_AGENT": "opencode",
            "KB_PROCESS_MODEL": "sonnet",
            "KB_CRONTAB_FILE": str(crontab_file),
            "PATH": f"{fake_bin}{os.pathsep}{env.get('PATH', '')}",
        }
    )
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(REPO_ROOT / "bin/kb-doctor")] + args,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )


def test_kb_doctor_reports_healthy_install(tmp_path):
    vault = make_vault(tmp_path)

    result = run_doctor([], vault, tmp_path)

    assert result.returncode == 0
    assert "KeyBrain Doctor" in result.stdout
    assert "process-inbox cron found" in result.stdout
    assert "kb-dream cron found" in result.stdout
    assert "Inbox processing model pinned: sonnet" in result.stdout
    assert "failure(s)" in result.stdout
    assert "0 failure(s)" in result.stdout


def test_kb_doctor_warns_on_framework_remote(tmp_path):
    vault = make_vault(tmp_path)
    subprocess.run(["git", "init"], cwd=vault, capture_output=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "https://github.com/raomaster/keybrain.git"],
        cwd=vault,
        capture_output=True,
    )

    result = run_doctor([], vault, tmp_path)

    assert result.returncode == 0
    assert "framework repo" in result.stdout


def test_kb_doctor_strict_exits_on_warnings(tmp_path):
    vault = make_vault(tmp_path)

    result = run_doctor(["--strict"], vault, tmp_path, extra_env={"KB_PROCESS_MODEL": ""})

    assert result.returncode == 2
    assert "warning(s)" in result.stdout


def test_kb_doctor_fails_when_vault_missing(tmp_path):
    vault = tmp_path / "MissingKnowledge"

    result = run_doctor([], vault, tmp_path)

    assert result.returncode == 1
    assert "[FAIL] Vault missing" in result.stdout


def test_kb_doctor_delegates_from_kb_cli(tmp_path):
    vault = make_vault(tmp_path)
    (vault / "bin" / "kb").write_text((REPO_ROOT / "bin" / "kb").read_text())
    (vault / "bin" / "kb").chmod(0o755)
    (vault / "bin" / "kb-doctor").write_text((REPO_ROOT / "bin" / "kb-doctor").read_text())
    (vault / "bin" / "kb-doctor").chmod(0o755)

    env = os.environ.copy()
    env["KB_VAULT"] = str(vault)
    env["KB_VENV"] = str(vault / ".venv")
    env["KB_CHROMADB"] = str(vault / ".chromadb")
    result = subprocess.run(
        ["bash", str(vault / "bin" / "kb"), "doctor"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )

    assert result.returncode in (0, 2)
    assert "KeyBrain Doctor" in result.stdout
