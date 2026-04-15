#!/usr/bin/env python3
"""
kb-index — Index all vault files in ChromaDB for semantic search.
Usage: kb-index [--force]
  --force  Re-index all files even if unchanged
"""

import sys
import os
import re
import json
import hashlib
import argparse
from pathlib import Path

VAULT = Path(os.environ.get("KB_VAULT", str(Path.home() / "Knowledge")))
DB_PATH = VAULT / ".chromadb"
STATE_FILE = VAULT / ".chromadb" / "index_state.json"

SKIP_DIRS = {".git", ".obsidian", ".venv", ".chromadb", "logs", "bin", "setup", "templates"}
SKIP_FILES = {"INSTALL-PROMPT.md"}


def parse_frontmatter(text: str) -> tuple:
    match = re.match(r'^---\n(.*?)\n---\n?', text, re.DOTALL)
    if not match:
        return {}, text
    content = text[match.end():]
    meta = {}
    for line in match.group(1).splitlines():
        if ':' in line:
            key, _, val = line.partition(':')
            meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, content


def chunk_text(text: str, max_size: int = 1200, overlap: int = 150) -> list:
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks, current, current_len = [], [], 0
    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len > max_size and current:
            chunks.append('\n\n'.join(current))
            tail = [current[-1]] if len(current[-1]) < overlap * 2 else []
            current, current_len = tail, sum(len(p) for p in tail)
        current.append(para)
        current_len += para_len
    if current:
        chunks.append('\n\n'.join(current))
    return chunks or [text[:max_size]]


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_doc_type(path: Path) -> str:
    parts = path.parts
    if "articles" in parts: return "article"
    if "courses" in parts:  return "course"
    if "research" in parts: return "research"
    if "projects" in parts: return "project"
    if "decisions" in parts: return "decision"
    if "conversations" in parts: return "conversation"
    if "wiki" in parts:     return "wiki"
    return "note"


def index_vault(force: bool = False):
    import chromadb
    client = chromadb.PersistentClient(path=str(DB_PATH))
    col = client.get_or_create_collection(
        name="knowledge",
        metadata={"hnsw:space": "cosine"}
    )
    state = load_state()
    indexed, skipped, updated = 0, 0, 0

    for md_file in sorted(VAULT.rglob("*.md")):
        if any(skip in md_file.parts for skip in SKIP_DIRS):
            continue
        if md_file.name in SKIP_FILES or md_file.name.startswith('.'):
            continue

        rel_path = str(md_file.relative_to(VAULT))
        fhash = file_hash(md_file)

        if not force and state.get(rel_path) == fhash:
            skipped += 1
            continue

        text = md_file.read_text(encoding='utf-8', errors='ignore')
        if len(text.strip()) < 50:
            continue

        meta, content = parse_frontmatter(text)
        doc_type = get_doc_type(md_file)
        chunks = chunk_text(content)

        try:
            existing = col.get(where={"source_path": rel_path})
            if existing["ids"]:
                col.delete(ids=existing["ids"])
        except Exception:
            pass

        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            chunk_id = f"{rel_path}::chunk_{i}"
            col.upsert(
                documents=[chunk],
                ids=[chunk_id],
                metadatas=[{
                    "source_path": rel_path,
                    "type": doc_type,
                    "title": meta.get("title", md_file.stem),
                    "date": meta.get("date", ""),
                    "tags": str(meta.get("tags", "")),
                    "chunk": i,
                    "total_chunks": len(chunks),
                }]
            )

        state[rel_path] = fhash
        updated += 1

    save_state(state)
    total = col.count()
    print(f"Indexed: {indexed} new, {updated} updated, {skipped} unchanged")
    print(f"  Total chunks in ChromaDB: {total}")
    print(f"  DB: {DB_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index vault in ChromaDB")
    parser.add_argument("--force", action="store_true", help="Re-index everything")
    args = parser.parse_args()
    index_vault(force=args.force)
