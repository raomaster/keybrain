#!/usr/bin/env python3
"""
kb-search-semantic — Semantic search over the vault using ChromaDB.
Usage: kb-search-semantic "query" [--results N] [--type article|decision|course|...]
Returns the most relevant chunks ready for Claude to read.
"""

import sys
import os
import argparse
from pathlib import Path

VAULT = Path(os.environ.get("KB_VAULT", str(Path.home() / "Knowledge")))
DB_PATH = Path(os.environ.get("KB_CHROMADB", str(VAULT / ".chromadb")))


def search(query: str, n_results: int = 6, doc_type: str = None) -> None:
    import chromadb
    if not DB_PATH.exists():
        print("ERROR: ChromaDB not initialized. Run first: kb-index")
        sys.exit(1)

    client = chromadb.PersistentClient(path=str(DB_PATH))
    col = client.get_or_create_collection("knowledge")

    if col.count() == 0:
        print("Index is empty. Run: kb-index")
        sys.exit(0)

    where = {"type": doc_type} if doc_type else None

    results = col.query(
        query_texts=[query],
        n_results=min(n_results, col.count()),
        where=where,
        include=["documents", "metadatas", "distances"]
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    if not docs:
        print(f"No results for: {query}")
        return

    print(f'\nResults for: "{query}"')
    print(f"   ({len(docs)} most relevant chunks)\n")

    seen_paths = set()
    for doc, meta, dist in zip(docs, metas, distances):
        relevance = round((1 - dist) * 100, 1)
        path = meta.get("source_path", "")
        title = meta.get("title", path)
        dtype = meta.get("type", "")
        chunk_n = meta.get("chunk", 0)
        total = meta.get("total_chunks", 1)

        chunk_label = f" (part {chunk_n + 1}/{total})" if int(total) > 1 else ""
        seen_paths.add(path)

        print(f"{'─' * 60}")
        print(f"  {title}{chunk_label}  [{dtype}]  {relevance}% relevant")
        print(f"   {path}")
        print()
        preview = doc.strip()
        if len(preview) > 600:
            preview = preview[:600] + "…"
        print(preview)
        print()

    print(f"{'─' * 60}")
    print(f"Source files: {', '.join(sorted(seen_paths))}")
    print(f"Total indexed: {col.count()} chunks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Semantic search in the vault")
    parser.add_argument("query", nargs="+", help="Text to search")
    parser.add_argument("--results", "-n", type=int, default=6, help="Number of results")
    parser.add_argument("--type", "-t", help="Filter by type: article, decision, course, research, project, wiki")
    args = parser.parse_args()

    search(
        query=" ".join(args.query),
        n_results=args.results,
        doc_type=args.type
    )
