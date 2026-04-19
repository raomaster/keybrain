# tests/unit/test_install_copilot.py
import subprocess
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def source_fn(fn_name, *args):
    arg_str = " ".join(f'"{a}"' for a in args)
    cmd = f'source {REPO_ROOT}/setup/install.sh && {fn_name} {arg_str}'
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)


# ── configure_copilot_instructions ────────────────────────

def test_creates_copilot_file_when_absent(tmp_path):
    copilot_file = tmp_path / ".github" / "copilot-instructions.md"
    result = source_fn("configure_copilot_instructions", str(copilot_file))
    assert result.returncode == 0
    assert copilot_file.exists()
    assert "KeyBrain" in copilot_file.read_text()


def test_copilot_appends_when_exists_without_keybrain(tmp_path):
    copilot_file = tmp_path / "copilot-instructions.md"
    copilot_file.write_text("# Existing instructions\n")
    source_fn("configure_copilot_instructions", str(copilot_file))
    content = copilot_file.read_text()
    assert "Existing instructions" in content
    assert "KeyBrain" in content


def test_copilot_skips_when_keybrain_present(tmp_path):
    copilot_file = tmp_path / "copilot-instructions.md"
    copilot_file.write_text("## KeyBrain\nalready here\n")
    source_fn("configure_copilot_instructions", str(copilot_file))
    assert copilot_file.read_text().count("KeyBrain") == 1


# ── configure_jetbrains_ai ────────────────────────────────

def test_creates_jetbrains_rules_file(tmp_path):
    rules_dir = tmp_path / ".aiassistant" / "rules"
    result = source_fn("configure_jetbrains_ai", str(rules_dir))
    assert result.returncode == 0
    rules_file = rules_dir / "keybrain.md"
    assert rules_file.exists()
    assert "KeyBrain" in rules_file.read_text()


def test_jetbrains_skips_when_file_exists(tmp_path):
    rules_dir = tmp_path / ".aiassistant" / "rules"
    rules_dir.mkdir(parents=True)
    rules_file = rules_dir / "keybrain.md"
    rules_file.write_text("## KeyBrain\nexisting\n")
    source_fn("configure_jetbrains_ai", str(rules_dir))
    assert rules_file.read_text().count("KeyBrain") == 1


def test_jetbrains_creates_parent_dirs(tmp_path):
    rules_dir = tmp_path / ".aiassistant" / "rules"
    result = source_fn("configure_jetbrains_ai", str(rules_dir))
    assert result.returncode == 0
    assert (rules_dir / "keybrain.md").exists()
