#!/usr/bin/env python3
"""Lightweight SDAAKernelWiki validator."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wiki_root import WIKI_ROOT  # noqa: E402


REQUIRED_BY_TYPE = {
    "hardware": ["id", "title", "type", "architectures", "tags", "confidence", "sources"],
    "technique": ["id", "title", "type", "architectures", "tags", "confidence", "reproducibility", "sources"],
    "pattern": ["id", "title", "type", "symptoms", "candidate_techniques", "sources"],
    "kernel": ["id", "title", "type", "architectures", "kernel_types", "confidence", "sources"],
}


def load_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)", text, re.DOTALL)
    if not match:
        return None
    return yaml.safe_load(match.group(1)) or {}


def main() -> None:
    errors = []
    ids: dict[str, Path] = {}
    pages = list((WIKI_ROOT / "wiki").rglob("*.md")) + list((WIKI_ROOT / "sources").rglob("*.md")) + list((WIKI_ROOT / "docs").rglob("*.md"))
    for path in pages:
        fm = load_frontmatter(path)
        if fm is None:
            errors.append(f"{path.relative_to(WIKI_ROOT)}: missing YAML frontmatter")
            continue
        pid = fm.get("id")
        if not pid:
            errors.append(f"{path.relative_to(WIKI_ROOT)}: missing id")
        elif pid in ids:
            errors.append(f"{path.relative_to(WIKI_ROOT)}: duplicate id {pid} also in {ids[pid].relative_to(WIKI_ROOT)}")
        else:
            ids[pid] = path
        ptype = fm.get("type")
        if ptype in REQUIRED_BY_TYPE:
            for key in REQUIRED_BY_TYPE[ptype]:
                if key not in fm or fm[key] in ("", None, []):
                    errors.append(f"{path.relative_to(WIKI_ROOT)}: missing required field {key}")
    for path in list((WIKI_ROOT / "wiki").rglob("*.md")) + list((WIKI_ROOT / "docs").rglob("*.md")):
        fm = load_frontmatter(path) or {}
        for sid in fm.get("sources") or []:
            if sid not in ids:
                errors.append(f"{path.relative_to(WIKI_ROOT)}: missing source id {sid}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        sys.exit(1)
    print(f"OK: {len(pages)} pages, {len(ids)} ids")


if __name__ == "__main__":
    main()

