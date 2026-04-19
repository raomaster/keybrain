#!/usr/bin/env python3
"""
kb-dream — Consolidate episodic memory into MEMORY.md and raw/memory-derived/.
Usage: kb-dream [--days N]
  --days N  How many days of memory files to process (default: 30)
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import date, timedelta

VAULT = Path(os.environ.get("KB_VAULT", str(Path.home() / "Knowledge")))

PROMOTION_MATRIX = {
    ("user-rule",         "high"):   ["memory_md", "raw"],
    ("user-preference",   "high"):   ["memory_md", "raw"],
    ("decision",          "high"):   ["raw"],
    ("technical-finding", "medium"): ["raw"],
    ("technical-finding", "high"):   ["raw"],
}

CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}
MEMORY_MD_MAX_PER_TYPE = 10


def slugify(text: str, max_len: int = 30) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text[:max_len]


def dedupe_key(memory_type: str, claim: str) -> str:
    return f"{memory_type}:{slugify(claim)}"


def parse_memory_file(path: Path) -> list:
    """Parse claims from a memory/YYYY-MM-DD.md file."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    body = re.sub(r"^---.*?---\n?", "", text, flags=re.DOTALL).strip()
    claims = []
    current = {}
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("- claim:"):
            if current:
                claims.append(current)
            claim_val = line.split("claim:", 1)[1].strip().strip('"').strip("'")
            current = {"claim": claim_val, "date": path.stem}
        elif line.startswith("memory_type:") and current:
            current["memory_type"] = line.split(":", 1)[1].strip()
        elif line.startswith("confidence:") and current:
            current["confidence"] = line.split(":", 1)[1].strip()
        elif line.startswith("context:") and current:
            current["context"] = line.split("context:", 1)[1].strip().strip('"').strip("'")
    if current:
        claims.append(current)
    return claims


def get_destinations(memory_type: str, confidence: str) -> list:
    rank = CONFIDENCE_RANK.get(confidence, 0)
    for (mtype, min_conf), dests in PROMOTION_MATRIX.items():
        if mtype == memory_type and CONFIDENCE_RANK.get(min_conf, 0) <= rank:
            return dests
    return []


def existing_dedupe_keys(memory_derived_dir: Path) -> set:
    """Return set of dedupe keys for files already in raw/memory-derived/."""
    keys = set()
    for f in memory_derived_dir.glob("*.md"):
        text = f.read_text(encoding="utf-8", errors="ignore")
        status_match = re.search(r"^status:\s*(\w+)", text, re.MULTILINE)
        status = status_match.group(1) if status_match else "unverified"
        dk_match = re.search(r"^dedupe_key:\s*(.+)", text, re.MULTILINE)
        if dk_match:
            dk = dk_match.group(1).strip()
            if status in ("rejected", "superseded"):
                keys.add(f"__blocked__{dk}")
            else:
                keys.add(dk)
    return keys


def write_memory_derived(vault: Path, claim: dict, memory_derived_dir: Path, existing_keys: set) -> bool:
    """Write a raw/memory-derived/ file. Returns True if written."""
    dk = dedupe_key(claim["memory_type"], claim["claim"])
    if dk in existing_keys or f"__blocked__{dk}" in existing_keys:
        return False
    today = claim.get("date", date.today().isoformat())
    memory_type = claim.get("memory_type", "note")
    confidence = claim.get("confidence", "medium")
    title = claim["claim"][:80].capitalize()
    slug = f"{today}-{memory_type}-{slugify(claim['claim'])}"
    filename = memory_derived_dir / f"{slug}.md"
    content = f"""---
title: "{title}"
date: {today}
source: "memory/{today}.md"
tags: [memory-derived, {memory_type}]
status: unverified
confidence: {confidence}
promoted_by: dream
dedupe_key: {dk}
---

{claim['claim']}

> Context: {claim.get('context', '')}
"""
    filename.write_text(content, encoding="utf-8")
    existing_keys.add(dk)
    return True


def rebuild_memory_md(vault: Path, memory_md_claims: list):
    """Rebuild MEMORY.md from scratch with qualifying claims (max 10 per type)."""
    by_type: dict = {}
    for c in memory_md_claims:
        mt = c.get("memory_type", "unknown")
        by_type.setdefault(mt, []).append(c)
    lines = ["# Memory", f"_Updated: {date.today().isoformat()} by kb-dream_", ""]
    for mt, claims in sorted(by_type.items()):
        for c in claims[:MEMORY_MD_MAX_PER_TYPE]:
            lines.append(f"- [{mt}] {c['claim']}")
    lines.append("")
    (vault / "MEMORY.md").write_text("\n".join(lines), encoding="utf-8")


def run_dream(vault: Path, days: int = 30):
    memory_dir = vault / "memory"
    memory_derived_dir = vault / "raw" / "memory-derived"
    memory_derived_dir.mkdir(parents=True, exist_ok=True)

    cutoff = date.today() - timedelta(days=days)
    memory_md_claims = []
    new_raw = 0
    skipped = 0
    existing_keys = existing_dedupe_keys(memory_derived_dir)

    for f in sorted(memory_dir.glob("*.md")):
        if f.name == ".gitkeep":
            continue
        try:
            file_date = date.fromisoformat(f.stem)
        except ValueError:
            continue
        if file_date < cutoff:
            continue
        for claim in parse_memory_file(f):
            dests = get_destinations(
                claim.get("memory_type", ""),
                claim.get("confidence", "low")
            )
            if "memory_md" in dests:
                memory_md_claims.append(claim)
            if "raw" in dests:
                written = write_memory_derived(vault, claim, memory_derived_dir, existing_keys)
                if written:
                    new_raw += 1
                else:
                    skipped += 1

    rebuild_memory_md(vault, memory_md_claims)

    total_claims = len(memory_md_claims)
    print(f"Dream complete: {total_claims} in MEMORY.md, {new_raw} new in raw/memory-derived/, {skipped} skipped (dedupe)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidate episodic memory")
    parser.add_argument("--days", type=int, default=30, help="Days of memory to process")
    args = parser.parse_args()
    run_dream(VAULT, days=args.days)
