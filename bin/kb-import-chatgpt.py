#!/usr/bin/env python3
"""
kb-import-chatgpt — Import ChatGPT export into the vault and ChromaDB index.

Usage:
  kb-import-chatgpt conversations.json          # import all
  kb-import-chatgpt conversations.json --since 2025-01-01   # since date
  kb-import-chatgpt conversations.json --dry-run            # preview

Get ChatGPT export at: Settings → Data Controls → Export Data
The downloaded file contains conversations.json with full history.

Files are saved to:
  $KB_VAULT/conversations/YYYY-MM/YYYY-MM-DD-conversation-title.md
And automatically indexed in ChromaDB.
"""

import sys
import os
import json
import re
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

VAULT = Path(os.environ.get("KB_VAULT", str(Path.home() / "Knowledge")))
CONV_DIR = VAULT / "conversations"
DB_PATH = VAULT / ".chromadb"


def slugify(text: str, max_len: int = 50) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:max_len].strip('-')


def format_conversation(conv: dict) -> tuple:
    """Convert a ChatGPT conversation to markdown with frontmatter."""
    title = conv.get("title", "Untitled")
    create_ts = conv.get("create_time", 0) or 0
    date = datetime.fromtimestamp(create_ts, tz=timezone.utc).strftime("%Y-%m-%d") if create_ts else "0000-00-00"

    messages = []
    mapping = conv.get("mapping", {})

    def get_children(node_id, visited=None):
        if visited is None:
            visited = set()
        if node_id in visited:
            return []
        visited.add(node_id)
        node = mapping.get(node_id, {})
        msg = node.get("message")
        result = []
        if msg and msg.get("content"):
            content = msg["content"]
            role = msg.get("author", {}).get("role", "unknown")
            if isinstance(content, dict):
                parts = content.get("parts", [])
                text = "\n".join(str(p) for p in parts if isinstance(p, str) and p.strip())
            else:
                text = str(content)
            if text.strip() and role in ("user", "assistant"):
                result.append({"role": role, "text": text.strip()})
        for child_id in node.get("children", []):
            result.extend(get_children(child_id, visited))
        return result

    for node_id, node in mapping.items():
        if node.get("parent") is None:
            messages = get_children(node_id)
            break

    if not messages:
        return None, {}

    md_lines = [
        "---",
        f'title: "{title}"',
        f"date: {date}",
        "source: chatgpt",
        "tags: [conversation, chatgpt]",
        f"messages: {len(messages)}",
        "---",
        "",
        f"# {title}",
        "",
        f"**Source:** ChatGPT export  **Date:** {date}  **Messages:** {len(messages)}",
        "",
        "---",
        "",
    ]

    for msg in messages:
        role_label = "**You:**" if msg["role"] == "user" else "**ChatGPT:**"
        md_lines.append(role_label)
        md_lines.append(msg["text"])
        md_lines.append("")

    return "\n".join(md_lines), {
        "title": title,
        "date": date,
        "messages": len(messages)
    }


def import_conversations(json_path: Path, since: str = None, dry_run: bool = False, index: bool = True):
    data = json.loads(json_path.read_text(encoding="utf-8"))

    if isinstance(data, list):
        conversations = data
    elif isinstance(data, dict):
        conversations = data.get("conversations", [data])
    else:
        print("ERROR: unrecognized export format")
        sys.exit(1)

    since_dt = datetime.fromisoformat(since) if since else None

    imported, skipped = 0, 0
    imported_paths = []

    for conv in conversations:
        create_ts = conv.get("create_time", 0) or 0
        date_str = datetime.fromtimestamp(create_ts, tz=timezone.utc).strftime("%Y-%m-%d") if create_ts else "0000-00-00"

        if since_dt:
            conv_date = datetime.fromtimestamp(create_ts, tz=timezone.utc).replace(tzinfo=None)
            if conv_date < since_dt:
                skipped += 1
                continue

        md_content, meta = format_conversation(conv)
        if not md_content:
            skipped += 1
            continue

        title = meta.get("title", "untitled")
        year_month = date_str[:7]
        filename = f"{date_str}-{slugify(title)}.md"
        dest_dir = CONV_DIR / year_month
        dest_path = dest_dir / filename

        if dry_run:
            print(f"[DRY-RUN] {dest_path.relative_to(VAULT)} ({meta['messages']} messages)")
            imported += 1
            continue

        dest_dir.mkdir(parents=True, exist_ok=True)
        if not dest_path.exists():
            dest_path.write_text(md_content, encoding="utf-8")
            imported_paths.append(dest_path)
            imported += 1
        else:
            skipped += 1

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Imported: {imported} conversations")
    print(f"Skipped (already exist or empty): {skipped}")

    if not dry_run and index and imported_paths:
        print("\nIndexing in ChromaDB...")
        python_bin = str(VAULT / ".venv/bin/python3.12")
        if not Path(python_bin).exists():
            python_bin = "python3"
        result = subprocess.run(
            [python_bin, str(VAULT / "bin/kb-index.py")],
            capture_output=True, text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"WARN: Indexing error: {result.stderr}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import ChatGPT export into vault")
    parser.add_argument("json_file", help="Path to conversations.json from ChatGPT export")
    parser.add_argument("--since", help="Only import since date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    parser.add_argument("--no-index", action="store_true", help="Skip ChromaDB re-indexing")
    args = parser.parse_args()

    json_path = Path(args.json_file).expanduser().resolve()
    if not json_path.exists():
        print(f"ERROR: file not found: {json_path}")
        sys.exit(1)

    import_conversations(
        json_path=json_path,
        since=args.since,
        dry_run=args.dry_run,
        index=not args.no_index
    )
