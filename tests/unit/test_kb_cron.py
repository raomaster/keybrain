import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent


def run_kb_cron(args, vault, crontab_file):
    env = os.environ.copy()
    env["KB_VAULT"] = str(vault)
    env["KB_CRONTAB_FILE"] = str(crontab_file)
    return subprocess.run(
        ["bash", str(REPO_ROOT / "bin/kb-cron")] + args,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )


def test_kb_cron_status_reports_missing_jobs(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    crontab_file = tmp_path / "crontab"
    crontab_file.write_text("")

    result = run_kb_cron(["status"], vault, crontab_file)

    assert result.returncode == 0
    assert "process-inbox: missing" in result.stdout
    assert "kb-dream: missing" in result.stdout
    assert "deterministic; no LLM call" in result.stdout


def test_kb_cron_print_includes_process_model_and_dream(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    crontab_file = tmp_path / "crontab"

    result = run_kb_cron(
        [
            "print",
            "--process-agent",
            "opencode",
            "--process-model",
            "anthropic/claude-sonnet-4-5",
            "--process-variant",
            "minimal",
            "--dream-days",
            "14",
        ],
        vault,
        crontab_file,
    )

    assert result.returncode == 0
    assert "KB_PROCESS_AGENT='opencode'" in result.stdout
    assert "KB_PROCESS_MODEL='anthropic/claude-sonnet-4-5'" in result.stdout
    assert "KB_PROCESS_VARIANT='minimal'" in result.stdout
    assert "process-inbox.sh" in result.stdout
    assert "kb-dream" in result.stdout
    assert "--days 14" in result.stdout


def test_kb_cron_install_writes_managed_block(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    crontab_file = tmp_path / "crontab"

    result = run_kb_cron(
        ["install", "--process-model", "sonnet", "--dream-days", "7"],
        vault,
        crontab_file,
    )

    assert result.returncode == 0
    content = crontab_file.read_text()
    assert "# BEGIN KEYBRAIN CRON" in content
    assert "KB_PROCESS_MODEL='sonnet'" in content
    assert "process-inbox.sh" in content
    assert "kb-dream" in content
    assert "--days 7" in content


def test_kb_cron_status_reads_model_from_existing_crontab(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()
    crontab_file = tmp_path / "crontab"
    crontab_file.write_text(
        f"*/15 * * * * KB_VAULT='{vault}' KB_PROCESS_AGENT='claude' "
        "KB_PROCESS_MODEL='sonnet' KB_PROCESS_EFFORT='low' "
        f"'{vault}/bin/process-inbox.sh'\n"
        f"0 2 * * * KB_VAULT='{vault}' '{vault}/bin/kb-dream' --days 30\n"
    )

    result = run_kb_cron(["status"], vault, crontab_file)

    assert result.returncode == 0
    assert "process-inbox: configured" in result.stdout
    assert "agent: claude" in result.stdout
    assert "model: sonnet" in result.stdout
    assert "effort: low" in result.stdout
    assert "kb-dream: configured" in result.stdout
    assert "model: none" in result.stdout
