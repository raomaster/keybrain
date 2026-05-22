import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def source_fn(fn_name, *args, home=None, extra_path=None):
    env = os.environ.copy()
    if home:
        env["HOME"] = str(home)
    if extra_path:
        env["PATH"] = str(extra_path) + os.pathsep + env.get("PATH", "")
    arg_str = " ".join(f'"{a}"' for a in args)
    cmd = f"source {REPO_ROOT}/setup/install.sh && {fn_name} {arg_str}"
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, env=env)


def make_universal_skill(tmp_path):
    skills = tmp_path / "skills"
    keybrain = skills / "keybrain"
    keybrain.mkdir(parents=True)
    (keybrain / "SKILL.md").write_text(
        "---\nname: keybrain\ndescription: test\n---\n# KeyBrain\n"
    )
    return skills


def test_manual_install_copies_keybrain_to_global_agent_paths(tmp_path):
    skills = make_universal_skill(tmp_path)
    home = tmp_path / "home"
    home.mkdir()

    result = source_fn("install_keybrain_skill_manual", str(skills), home=home)

    assert result.returncode == 0
    expected = [
        ".claude/skills/keybrain/SKILL.md",
        ".codex/skills/keybrain/SKILL.md",
        ".agents/skills/keybrain/SKILL.md",
        ".config/opencode/skills/keybrain/SKILL.md",
        ".copilot/skills/keybrain/SKILL.md",
        ".cursor/skills/keybrain/SKILL.md",
        ".gemini/skills/keybrain/SKILL.md",
        ".gemini/antigravity/skills/keybrain/SKILL.md",
        ".gemini/antigravity-cli/skills/keybrain/SKILL.md",
    ]
    for relpath in expected:
        assert (home / relpath).exists()


def test_npx_install_targets_keybrain_and_standard_agents(tmp_path):
    skills = make_universal_skill(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    args_file = tmp_path / "npx.args"
    (bin_dir / "npm").write_text("#!/usr/bin/env bash\nexit 0\n")
    (bin_dir / "npx").write_text(
        f"#!/usr/bin/env bash\nprintf '%s\\n' \"$@\" > {args_file}\nexit 0\n"
    )
    (bin_dir / "npm").chmod(0o755)
    (bin_dir / "npx").chmod(0o755)

    result = source_fn("install_keybrain_skill_with_npx", str(skills), extra_path=bin_dir)

    assert result.returncode == 0
    args = args_file.read_text()
    assert "skills@latest" in args
    assert "--skill" in args
    assert "keybrain" in args
    assert "claude-code" in args
    assert "codex" in args
    assert "opencode" in args
    assert "github-copilot" in args
    assert "antigravity" in args
