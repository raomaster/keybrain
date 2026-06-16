import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent


def source_fn(fn_name, *args):
    arg_str = " ".join(f'"{a}"' for a in args)
    cmd = f"source {REPO_ROOT}/setup/install.sh && {fn_name} {arg_str}"
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)


def test_copy_framework_to_vault_excludes_git_metadata(tmp_path):
    src = tmp_path / "repo"
    dest = tmp_path / "Knowledge"
    (src / ".git").mkdir(parents=True)
    (src / ".pytest_cache").mkdir()
    (src / "bin").mkdir()
    (src / "raw" / "articles").mkdir(parents=True)
    (src / ".DS_Store").write_text("mac metadata")
    (src / ".git" / "config").write_text("[remote]\n")
    (src / ".pytest_cache" / "cache").write_text("cache")
    (src / "bin" / "kb").write_text("#!/usr/bin/env bash\n")
    (src / "README.md").write_text("# KeyBrain\n")
    (src / "raw" / "articles" / "example.md").write_text("content")

    result = source_fn("copy_framework_to_vault", str(src), str(dest))

    assert result.returncode == 0
    assert (dest / "README.md").exists()
    assert (dest / "bin" / "kb").exists()
    assert (dest / "raw" / "articles" / "example.md").exists()
    assert not (dest / ".git").exists()
    assert not (dest / ".pytest_cache").exists()
    assert not (dest / ".DS_Store").exists()
