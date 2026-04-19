import subprocess
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def source_fn(fn_name, *args, extra_path=None):
    """Source install.sh (guard stops main execution) then call function."""
    env = os.environ.copy()
    if extra_path:
        env["PATH"] = extra_path + ":" + env.get("PATH", "")
    arg_str = " ".join(f'"{a}"' for a in args)
    cmd = f'source {REPO_ROOT}/setup/install.sh && {fn_name} {arg_str}'
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, env=env)


def make_skills_src(tmp_path):
    """Create a mock skills source with a skill.md file."""
    src = tmp_path / "skills"
    skill_dir = src / "kb-search"
    skill_dir.mkdir(parents=True)
    (skill_dir / "skill.md").write_text("---\ndescription: test\n---\ntest skill")
    return src


# ── install_openclaw_skills ────────────────────────────

def test_installs_skills_when_openclaw_dir_exists(tmp_path):
    src = make_skills_src(tmp_path)
    openclaw_dir = tmp_path / ".openclaw"
    openclaw_dir.mkdir()
    result = source_fn("install_openclaw_skills", str(src), str(openclaw_dir))
    assert result.returncode == 0
    skills_dest = openclaw_dir / "workspace" / "skills"
    assert skills_dest.exists()
    assert (skills_dest / "kb-search").exists()


def test_renames_skill_md_to_uppercase(tmp_path):
    src = make_skills_src(tmp_path)
    openclaw_dir = tmp_path / ".openclaw"
    openclaw_dir.mkdir()
    source_fn("install_openclaw_skills", str(src), str(openclaw_dir))
    skill_dir = openclaw_dir / "workspace" / "skills" / "kb-search"
    filenames = os.listdir(skill_dir)
    assert "SKILL.md" in filenames
    assert "skill.md" not in filenames


def test_returns_error_when_skills_src_missing(tmp_path):
    src = tmp_path / "missing-skills"  # does not exist
    openclaw_dir = tmp_path / ".openclaw"
    openclaw_dir.mkdir()
    result = source_fn("install_openclaw_skills", str(src), str(openclaw_dir))
    assert result.returncode == 1


# ── configure_openclaw_agents_md ──────────────────────

def test_creates_agents_md_when_absent(tmp_path):
    openclaw_dir = tmp_path / ".openclaw"
    openclaw_dir.mkdir()
    result = source_fn("configure_openclaw_agents_md", str(openclaw_dir))
    assert result.returncode == 0
    agents_md = openclaw_dir / "workspace" / "AGENTS.md"
    assert agents_md.exists()
    assert "KeyBrain" in agents_md.read_text()


def test_appends_when_exists_without_keybrain(tmp_path):
    openclaw_dir = tmp_path / ".openclaw"
    workspace = openclaw_dir / "workspace"
    workspace.mkdir(parents=True)
    agents_md = workspace / "AGENTS.md"
    agents_md.write_text("# Existing content\n")
    source_fn("configure_openclaw_agents_md", str(openclaw_dir))
    content = agents_md.read_text()
    assert "Existing content" in content
    assert "KeyBrain" in content


def test_skips_when_keybrain_already_present(tmp_path):
    openclaw_dir = tmp_path / ".openclaw"
    workspace = openclaw_dir / "workspace"
    workspace.mkdir(parents=True)
    agents_md = workspace / "AGENTS.md"
    agents_md.write_text("## KeyBrain\nalready here\n")
    source_fn("configure_openclaw_agents_md", str(openclaw_dir))
    assert agents_md.read_text().count("KeyBrain") == 1


def test_workspace_dir_created_if_absent(tmp_path):
    openclaw_dir = tmp_path / ".openclaw"
    openclaw_dir.mkdir()
    # workspace does not exist yet
    source_fn("configure_openclaw_agents_md", str(openclaw_dir))
    agents_md = openclaw_dir / "workspace" / "AGENTS.md"
    assert agents_md.exists()
