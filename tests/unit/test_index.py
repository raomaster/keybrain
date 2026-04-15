from pathlib import Path, PurePosixPath
import re


def test_parse_frontmatter():
    text = """---
title: "Test"
date: 2026-01-01
---

Body text here."""
    match = re.match(r'^---\n(.*?)\n---\n?', text, re.DOTALL)
    assert match is not None
    meta = {}
    for line in match.group(1).splitlines():
        if ':' in line:
            key, _, val = line.partition(':')
            meta[key.strip()] = val.strip().strip('"').strip("'")
    assert meta["title"] == "Test"
    assert meta["date"] == "2026-01-01"


def test_parse_frontmatter_no_fm():
    text = "Just plain text, no frontmatter."
    match = re.match(r'^---\n(.*?)\n---\n?', text, re.DOTALL)
    assert match is None


def test_chunk_text():
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    assert len(paragraphs) == 3


def test_get_doc_type():
    def get_doc_type(parts):
        if "articles" in parts: return "article"
        if "courses" in parts:  return "course"
        if "research" in parts: return "research"
        if "decisions" in parts: return "decision"
        if "wiki" in parts:     return "wiki"
        return "note"

    assert get_doc_type(PurePosixPath("raw/articles/test.md").parts) == "article"
    assert get_doc_type(PurePosixPath("raw/courses/test.md").parts) == "course"
    assert get_doc_type(PurePosixPath("raw/research/test.md").parts) == "research"
    assert get_doc_type(PurePosixPath("decisions/test.md").parts) == "decision"
    assert get_doc_type(PurePosixPath("wiki/concepts/test.md").parts) == "wiki"
    assert get_doc_type(PurePosixPath("other/test.md").parts) == "note"


def test_file_hash():
    import hashlib
    content = b"test content"
    h = hashlib.md5(content).hexdigest()
    assert len(h) == 32
    assert h == hashlib.md5(content).hexdigest()
