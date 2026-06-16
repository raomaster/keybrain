import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def source_fn(fn_name, *args):
    """Source install.sh (guard stops main execution) then call function."""
    arg_str = " ".join(f'"{a}"' for a in args)
    cmd = f'source {REPO_ROOT}/setup/install.sh && {fn_name} {arg_str}'
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)


def test_configures_obsidian_ignore_filters(tmp_path):
    vault = tmp_path / "Knowledge"
    vault.mkdir()

    result = source_fn("configure_obsidian_ignores", str(vault), sys.executable)

    assert result.returncode == 0
    app_json = vault / ".obsidian" / "app.json"
    assert app_json.exists()
    config = json.loads(app_json.read_text())
    assert "setup/" in config["userIgnoreFilters"]
    assert "CLAUDE.md" in config["userIgnoreFilters"]
    assert "INSTALL-PROMPT.md" in config["userIgnoreFilters"]


def test_configure_obsidian_ignore_filters_preserves_existing_settings(tmp_path):
    vault = tmp_path / "Knowledge"
    obsidian_dir = vault / ".obsidian"
    obsidian_dir.mkdir(parents=True)
    app_json = obsidian_dir / "app.json"
    app_json.write_text(
        json.dumps(
            {
                "alwaysUpdateLinks": True,
                "userIgnoreFilters": ["logs/"],
            }
        )
    )

    result = source_fn("configure_obsidian_ignores", str(vault), sys.executable)

    assert result.returncode == 0
    config = json.loads(app_json.read_text())
    assert config["alwaysUpdateLinks"] is True
    assert "logs/" in config["userIgnoreFilters"]
    assert "setup/" in config["userIgnoreFilters"]
    assert "CLAUDE.md" in config["userIgnoreFilters"]
    assert "INSTALL-PROMPT.md" in config["userIgnoreFilters"]
    assert config["userIgnoreFilters"].count("setup/") == 1
