import sys
import os
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
VAULT = Path("/tmp/kb-test-vault-index")


def load_kb_index():
    """Load kb-index.py as a module."""
    spec = importlib.util.spec_from_file_location("kb_index", REPO_ROOT / "bin/kb-index.py")
    mod = importlib.util.module_from_spec(spec)
    os.environ["KB_VAULT"] = str(VAULT)
    spec.loader.exec_module(mod)
    return mod


def test_memory_dir_excluded_from_index():
    mod = load_kb_index()
    vault = Path("/tmp/kb-test-vault")
    path = vault / "memory" / "2026-04-18.md"
    assert not mod.should_index(path, vault)


def test_memory_md_excluded_from_index():
    mod = load_kb_index()
    vault = Path("/tmp/kb-test-vault")
    path = vault / "MEMORY.md"
    assert not mod.should_index(path, vault)


def test_regular_article_included():
    mod = load_kb_index()
    vault = Path("/tmp/kb-test-vault")
    path = vault / "raw" / "articles" / "2026-04-18-test.md"
    assert mod.should_index(path, vault)


def test_memory_derived_doc_type():
    mod = load_kb_index()
    path = Path("/tmp/kb-test-vault/raw/memory-derived/2026-04-18-test.md")
    assert mod.get_doc_type(path) == "memory-derived"
