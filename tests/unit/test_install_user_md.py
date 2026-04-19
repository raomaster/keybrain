import subprocess
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def source_fn(fn_name, *args):
    """Source install.sh (guard stops main execution) then call function."""
    arg_str = " ".join(f'"{a}"' for a in args)
    cmd = f'source {REPO_ROOT}/setup/install.sh && {fn_name} {arg_str}'
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)


def test_creates_user_md_when_claude_dir_exists(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    result = source_fn("create_user_md_template", str(claude_dir))
    assert result.returncode == 0
    user_md = claude_dir / "USER.md"
    assert user_md.exists()
    content = user_md.read_text()
    assert "identity:" in content
    assert "expertise:" in content
    assert "style:" in content


def test_skips_when_user_md_already_exists(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    user_md = claude_dir / "USER.md"
    user_md.write_text("existing content")
    source_fn("create_user_md_template", str(claude_dir))
    assert user_md.read_text() == "existing content"


def test_skips_when_claude_dir_does_not_exist(tmp_path):
    claude_dir = tmp_path / ".claude"  # intentionally not created
    source_fn("create_user_md_template", str(claude_dir))
    assert not (claude_dir / "USER.md").exists()
