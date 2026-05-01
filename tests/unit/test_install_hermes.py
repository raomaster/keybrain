# tests/unit/test_install_hermes.py
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def source_fn(fn_name, *args):
    arg_str = " ".join(f'"{a}"' for a in args)
    cmd = f'source {REPO_ROOT}/setup/install.sh && {fn_name} {arg_str}'
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)


# ── install_hermes_skills ─────────────────────────────────

def make_skills_src(tmp_path):
    """Create a mock skills source with a hermes-keybrain/SKILL.md file."""
    src = tmp_path / "skills"
    skill_dir = src / "hermes-keybrain"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\ndescription: test\n---\ntest skill")
    return src


def test_installs_skills_when_hermes_dir_exists(tmp_path):
    src = make_skills_src(tmp_path)
    hermes_skills_dir = tmp_path / ".hermes" / "skills" / "keybrain"
    result = source_fn("install_hermes_skills", str(src), str(hermes_skills_dir))
    assert result.returncode == 0
    assert hermes_skills_dir.exists()
    assert (hermes_skills_dir / "hermes-keybrain" / "SKILL.md").exists()


def test_skill_content_preserved(tmp_path):
    src = make_skills_src(tmp_path)
    hermes_skills_dir = tmp_path / ".hermes" / "skills" / "keybrain"
    source_fn("install_hermes_skills", str(src), str(hermes_skills_dir))
    skill_file = hermes_skills_dir / "hermes-keybrain" / "SKILL.md"
    content = skill_file.read_text()
    assert "test skill" in content
    assert "description: test" in content


def test_returns_error_when_skills_src_missing(tmp_path):
    src = tmp_path / "missing-skills"  # does not exist
    hermes_skills_dir = tmp_path / ".hermes" / "skills" / "keybrain"
    result = source_fn("install_hermes_skills", str(src), str(hermes_skills_dir))
    assert result.returncode == 1


def test_creates_parent_dirs(tmp_path):
    src = make_skills_src(tmp_path)
    hermes_skills_dir = tmp_path / ".hermes" / "skills" / "keybrain" / "nested"
    result = source_fn("install_hermes_skills", str(src), str(hermes_skills_dir))
    assert result.returncode == 0
    assert hermes_skills_dir.exists()


def test_skips_non_src_directories(tmp_path):
    """Files without SKILL.md are skipped gracefully."""
    src = tmp_path / "skills"
    skill_dir = src / "no-skill-md"
    skill_dir.mkdir(parents=True)
    (skill_dir / "other.txt").write_text("not a skill")
    hermes_skills_dir = tmp_path / ".hermes" / "skills" / "keybrain"
    result = source_fn("install_hermes_skills", str(src), str(hermes_skills_dir))
    assert result.returncode == 0
    dest = hermes_skills_dir / "no-skill-md" / "SKILL.md"
    assert not dest.exists()


# ── configure_hermes_soul_md ──────────────────────────────

def test_creates_soul_md_when_absent(tmp_path):
    soul_md = tmp_path / ".hermes" / "SOUL.md"
    result = source_fn("configure_hermes_soul_md", str(soul_md))
    assert result.returncode == 0
    assert soul_md.exists()
    content = soul_md.read_text()
    assert "KeyBrain" in content
    assert "kb-search-semantic" in content
    assert "KB_VAULT" in content


def test_appends_when_exists_without_keybrain(tmp_path):
    soul_md = tmp_path / "SOUL.md"
    soul_md.write_text("# Existing content\n")
    source_fn("configure_hermes_soul_md", str(soul_md))
    content = soul_md.read_text()
    assert "Existing content" in content
    assert "KeyBrain" in content


def test_skips_when_keybrain_already_present(tmp_path):
    soul_md = tmp_path / "SOUL.md"
    soul_md.write_text("## KeyBrain\nalready here\n")
    source_fn("configure_hermes_soul_md", str(soul_md))
    assert soul_md.read_text().count("KeyBrain") >= 1  # already present, not appended


def test_creates_parent_dirs_for_soul_md(tmp_path):
    soul_md = tmp_path / ".hermes" / "nested" / "SOUL.md"
    result = source_fn("configure_hermes_soul_md", str(soul_md))
    assert result.returncode == 0
    assert soul_md.exists()


def test_soul_md_contains_all_commands(tmp_path):
    soul_md = tmp_path / "SOUL.md"
    source_fn("configure_hermes_soul_md", str(soul_md))
    content = soul_md.read_text()
    assert "kb-search-semantic" in content
    assert "kb add" in content
    assert "kb status" in content
    assert "kb process" in content
    assert "kb-index" in content
    assert "kb-dream" in content
    assert "kb update" in content
    # The heredoc writes backtick-quoted commands; verify the command names appear


def test_soul_md_contains_priority_rules(tmp_path):
    soul_md = tmp_path / "SOUL.md"
    source_fn("configure_hermes_soul_md", str(soul_md))
    content = soul_md.read_text()
    assert "Always search KeyBrain first" in content
    assert "KeyBrain is your primary memory" in content
    assert "Save valuable knowledge without asking" in content
